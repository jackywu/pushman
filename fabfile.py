#!/usr/bin/env python
#  -*- coding: UTF-8 -*-

from __future__ import with_statement
import os
import urllib2
from fabric.operations import run, put
from fabric.api import local, settings, abort, env
from lb import LoadBalancer
from monitor import Monitor
from installer import InstallerFactory
import fabric.contrib.files as fab_files
import fab_utils
import sys
from log import Log
from checker import Checker

glog = Log('pushman.log', 'PushMan').open_log()

env.hosts = ['client']

class Pushman(object):

    ROOT = '/data0/pushman'
    ServerRoot = ROOT + '/server'
    ClientRoot = ROOT + '/client'
    ClientBackupRoot = ROOT + '/backup'

    def __init__(self, config):
        self.resource = ''
        self.version = ''
        self.config = config
        self.global_desc = self.config['desc']['global_desc']
        self.pre_deploy_desc = self.config['desc']['pre_deploy_desc']
        self.deploy_desc = self.config['desc']['deploy_desc']
        self.post_deploy_desc = self.config['desc']['post_deploy_desc']

    def download(self, resource):
        if self.deploy_desc.get('install_action') == InstallerFactory.FLAG_YUM:
            return None

        self.instance_dir_ss = '%s/%s' % (self.ServerRoot, self.config['id'])
        try:
            if not os.path.exists(self.instance_dir_ss):
                os.makedirs(self.instance_dir_ss)
        except Exception as e:
            raise Exception("create server-side job env failed, %s" % e)

        self.file_name = resource.split('/')[-1]
        self.file_path_ss = '%s/%s' % (self.instance_dir_ss, self.file_name)

        try:
            response = urllib2.urlopen(resource, timeout=3).read()
            with open(self.file_path_ss, 'wb') as fp:
                fp.write(response)
        except Exception as e:
            raise Exception("download package failed, %s" % e)

    def upload(self):
        if self.deploy_desc.get('install_action') == InstallerFactory.FLAG_YUM:
            return None

        self.instance_dir_cs = '%s/%s' % (self.ClientRoot, self.config['id'])

        fab_utils.run_check_failed('rm -rf %s' % self.instance_dir_cs, 'rm remote job env failed')

        fab_utils.run_check_failed('mkdir -p %s' % self.instance_dir_cs, 'create remote job env failed')

        self.file_path_cs = '%s/%s' % (self.instance_dir_cs, self.file_name)

        result = put(self.file_path_ss, self.file_path_cs)
        if result.failed: raise Exception("upload files to remote failed, %s" % result)


    def prepare(self, resource, version):
        self.download(resource)
        self.version = version


    def pre_deploy(self):
        self.upload()

        # TODO: check if already deployed

        # disable server from lb
        if self.pre_deploy_desc.get('disable_service_from_lb'):
            LoadBalancer().disable_service()

        # disable monitor
        if self.pre_deploy_desc.get('disable_monitoring'):
            Monitor().disable()

        pass

    def deploy(self):
        if self.deploy_desc.get('stop_service'):
           fab_utils.run_check_failed(self.deploy_desc['stop_command'], 'shutdown service failed')

        # validate install_dir if it is legal
        protected_dir = ['/', '/usr', '/var', '/boot', '/bin', '/etc']
        protected_dir.extend(['/home', '/lib64', '/root', '/sys', '/dev'])
        protected_dir.extend(['/lib', '/mnt', '/proc', '/sbin', '/tmp'])
        check_slash_depth = 4

        install_dir = self.deploy_desc.get('install_dir', '')

        for i in range(check_slash_depth):
            if install_dir in [s+'/'*i for s in protected_dir]:
                raise Exception('illegal install dir %s' % install_dir)

        # backup previous package
        if self.deploy_desc.get('backup_previous_package'):
            backup_dir = "%s/%s" % (self.ClientBackupRoot, self.config['id'])
            fab_utils.run_check_failed("mkdir -p %s" % backup_dir, 'create backup env failed')

            fab_utils.run_check_failed("copy -r %s %s" % (install_dir, backup_dir),
                                      'backup previous package failed')

        # init installer
        install_action = self.deploy_desc.get('install_action')
        if install_action == InstallerFactory.FLAG_YUM:
            resource = self.global_desc.get('resource_update_to')
        else:
            resource = self.file_path_cs

        installer = InstallerFactory(resource, self.version,
                                     install_action, install_dir,
                                     self.deploy_desc.get('force_install')).config()

        # remove previous package
        if self.deploy_desc.get('remove_previous_package'):
            installer.remove_previous()

        # install
        installer.install()

        # update configuration
        fab_utils.run_custom_script(self.deploy_desc.get('update_configuration_script', ''),
                                    self.deploy_desc.get('install_dir', ''),
                                    'rpm',
                                    'deploy')

        # bring up service
        if self.deploy_desc.get('stop_service'):
            if self.deploy_desc.get('start_service'):
                fab_utils.run_check_failed(self.deploy_desc['start_command'], 'start service failed')
        else:
            if self.deploy_desc.get('start_service'):
                if self.deploy_desc.get('restart_command'):
                    fab_utils.run_check_failed(self.deploy_desc.get('restart_command'),
                                               'restart service failed')
                else:
                    cmd = '%s && %s' % (self.deploy_desc.get('stop_command'), self.deploy_desc.get('start_command'))
                    if cmd.strip() == '&&':
                        cmd = ''
                    fab_utils.run_check_failed('%s' % cmd, 'restart(stop-start) service failed')


        pass

    def post_deploy(self):
        # exec custom script
        fab_utils.run_custom_script(self.post_deploy_desc.get('custom_post_deploy_script', ''),
                                    self.deploy_desc.get('install_dir', ''),
                                    'rpm',
                                    'post_deploy')


        # check process alive
        proc_for_check = self.post_deploy_desc.get('check_proc_alive')
        if proc_for_check:
            Checker().check_process(proc_for_check)


        # check port alive
        port_for_check = self.post_deploy_desc.get('check_port_alive')
        if port_for_check:
            Checker().check_port(port_for_check)

        # enable monitor
        if self.post_deploy_desc.get('enable_monitoring'):
            Monitor().enable()

        # enable server from lb
        if self.post_deploy_desc.get('enable_service_from_lb'):
            LoadBalancer().enable_service()



    def do_deploy(self, resource, version):
        self.prepare(resource, version)
        self.pre_deploy()
        self.deploy()
        self.post_deploy()

    def update(self):
        resource = self.global_desc['resource_update_to']
        version = self.global_desc['version_update_to']
        self.do_deploy(resource, version)

    def rollback(self):
        resource = self.global_desc['resource_rollback_to']
        version = self.global_desc['version_rollback_to']
        self.do_deploy(resource, version)

def handle(action='update', desc_file=''):
    allowed_action = ['update', 'rollback']
    if action not in allowed_action:
        sys.exit('action %s is illegal, allowed action are %s' % (action, allowed_action))

    if desc_file.endswith('.py'):
        file_name = desc_file
        module_name = desc_file.rstrip('.py')
    else:
        file_name = '%s.py' % desc_file
        module_name = desc_file

    if not os.path.exists(file_name):
        sys.exit('desc file does not exist')

    sys.path.append('.')
    module = __import__(module_name)

    job_desc = module.job

    pm = Pushman(job_desc)

    try:
        if action == 'update':
            pm.update()
        elif action == 'rollback':
            pm.rollback()
    except Exception as e:
        if job_desc['desc']['global_desc']['auto_rollback']:
            pm.rollback()



