#!/usr/bin/env python
#  -*- coding: UTF-8 -*-

from __future__ import with_statement
import os
import urllib2
import rpm_job_demo
from fabric.operations import run, put
from fabric.api import local, settings, abort, env
from lb import LoadBalancer
from monitor import Monitor
import fabric.contrib.files as fab_files
import fab_utils
from log import Log

glog = Log('pushman.log', 'PushMan').open_log()

env.hosts = ['client']

class Pushman(object):

    ROOT = '/data0/pushman'
    ServerRoot = ROOT + '/server'
    ClientRoot = ROOT + '/client'
    ClientBackupRoot = ROOT + '/backup'

    def __init__(self, config):
        self.config = config
        self.global_desc = self.config['desc']['global_desc']
        self.pre_deploy_desc = self.config['desc']['pre_deploy_desc']
        self.deploy_desc = self.config['desc']['deploy_desc']
        self.post_deploy_desc = self.config['desc']['post_deploy_desc']

    def download(self, resource):
        self.instance_dir_ss = '%s/%s' % (self.ServerRoot, self.config['id'])
        try:
            if not os.path.exists(self.instance_dir_ss):
                os.makedirs(self.instance_dir_ss)
        except Exception as e:
            raise Exception("create job env failed, %s" % e)

        self.file_name = resource.split('/')[-1]
        self.file_path_ss = '%s/%s' % (self.instance_dir_ss, self.file_name)

        try:
            response = urllib2.urlopen(resource, timeout=3).read()
            with open(self.file_path_ss, 'wb') as fp:
                fp.write(response)
        except Exception as e:
            raise Exception("download package failed, %s" % e)

    def upload(self):
        self.instance_dir_cs = '%s/%s' % (self.ClientRoot, self.config['id'])

        fab_utils.run_check_failed('rm -rf %s' % self.instance_dir_cs, 'rm remote job env failed')

        fab_utils.run_check_failed('mkdir -p %s' % self.instance_dir_cs, 'create remote job env failed')

        self.file_path_cs = '%s/%s' % (self.instance_dir_cs, self.file_name)

        result = put(self.file_path_ss, self.file_path_cs)
        if result.failed: raise Exception("upload files to remote failed, %s" % result)


    def prepare(self, resource):
        self.download(resource)


    def pre_deploy(self):
        self.upload()

        # TODO: check if already deployed

        # disable server from lb
        if self.pre_deploy_desc['disable_service_from_lb']:
            LoadBalancer().disable_service()

        # disable monitor
        if self.pre_deploy_desc['disable_monitoring']:
            Monitor().disable()

        # execute custom_pre_deploy_script
        custom_script = self.pre_deploy_desc.get('custom_pre_deploy_script')
        custom_script_path = '%s/%s' % (self.instance_dir_cs, custom_script)
        if custom_script and fab_files.exists(custom_script_path):
            # TODO: chmod does not work on windows
            fab_utils.run_check_failed('chmod +x %s' % custom_script_path, 'chmod x failed')
            fab_utils.run_check_failed(custom_script_path, 'exec custom_pre_deploy_script failed')

        pass

    def deploy(self):
        if self.deploy_desc['stop_service']:
           fab_utils.run_check_failed(self.global_desc['stop_command'], 'shutdown service failed')

        # validate install_dir if it is legal
        protected_dir = ['/', '/usr', '/var', '/boot', '/bin', '/etc']
        protected_dir.extend(['/home', '/lib64', '/root', '/sys', '/dev'])
        protected_dir.extend(['/lib', '/mnt', '/proc', '/sbin', '/tmp'])
        check_slash_depth = 4

        install_dir = self.global_desc['install_dir']

        for i in range(check_slash_depth):
            if install_dir in [s+'/'*i for s in protected_dir]:
                raise Exception('illegal install dir %s' % install_dir)

        # backup previous package
        if self.global_desc['backup_previous_package']:
            backup_dir = "%s/%s" % (self.ClientBackupRoot, self.config['id'])
            fab_utils.run_check_failed("mkdir -p %s" % backup_dir, 'create backup env failed')

            fab_utils.run_check_failed("copy -r %s %s" % (self.global_desc['install_dir'], backup_dir),
                                      'backup previous failed')

        # remove previous package
        if self.global_desc['remove_previous_package']:
            if self.global_desc['install_action'] == 'rpm':
                package_full_name = self.global_desc['resource_update_to'].split('/')[-1]
                package_name = package_full_name.split('-')[0]
                fab_utils.run_check_failed('rpm -e %s' % package_name, 'rpm remove previous package failed')
            else:
                fab_utils.run_check_failed('rm -rf %s' % install_dir, 'rm previous package failed')

        # install
        if self.global_desc['install_action'] == 'rpm':
            if self.deploy_desc['force_install']:
                extra_param = ' --force --nodeps '
            else:
                extra_param = ''
            fab_utils.run_check_failed('rpm -i %s %s' % (extra_param, self.file_path_cs), 'rpm install failed')
        else:
            fab_utils.extract_check_failed(self.file_path_cs, install_dir)

        # update configuration
        update_config_script = self.deploy_desc.get('update_configuration_script', '').strip()
        if update_config_script.strip() != '':
            if os.path.isabs(update_config_script):
                update_config_script_path = update_config_script
            else:
                if self.global_desc['install_action'] == 'rpm':
                    raise Exception('when install by rpm, update_configuration_script should be a absolute path')
                update_config_script_path = '%s/%s' % (install_dir, update_config_script)

            fab_utils.run_check_failed(update_config_script_path, 'run update_configuration_script failed')

        # bring up service
        if self.deploy_desc['stop_service']:
            if self.deploy_desc['start_service']:
                fab_utils.run_check_failed(self.global_desc['start_command'], 'start service failed')
        else:
            if self.deploy_desc['start_service']:
                if self.global_desc.get('restart_command'):
                    fab_utils.run_check_failed(self.global_desc['restart_command'], 'restart service failed')
                else:
                    fab_utils.run_check_failed('%s && %s' % (self.global_desc['stop_command'], self.global_desc['start_command']), 'stop of restart service failed')


        pass

    def post_deploy(self):
        pass

    def do_deploy(self, resource):
        self.prepare(resource)
        self.pre_deploy()
        self.deploy()
        self.post_deploy()

    def update(self):
        resource = self.global_desc['resource_update_to']
        self.do_deploy(resource)

    def rollback(self):
        resource = self.global_desc['resource_rollback_to']
        self.do_deploy(resource)

def handle():


    job = rpm_job_demo.job

    pm = Pushman(job)

    try:
        pm.update()
    except Exception as e:
        if job['desc']['global_desc']['auto_rollback']:
            pm.rollback()



