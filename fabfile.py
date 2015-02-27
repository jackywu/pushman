#!/usr/bin/env python
#  -*- coding: UTF-8 -*-

from __future__ import with_statement
import os
import urllib2
import job_demo
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

        fab_utils.run_check_failed('rm -rf %s' % self.instance_dir_cs, "rm remote job env failed")


        result = run('rm -rf %s' % self.instance_dir_cs)
        if result.failed: raise Exception("rm remote job env failed, %s" % result)

        result = run('mkdir -p %s' % self.instance_dir_cs)
        if result.failed: raise Exception("create remote job env failed, %s" % result)
        self.file_path_cs = '%s/%s' % (self.instance_dir_cs, self.file_name)

        result = put(self.file_path_ss, self.file_path_cs)
        if result.failed: raise Exception("upload files to remote failed, %s" % result)


    def prepare(self, resource):
        self.download(resource)


    def pre_deploy(self):
        self.upload()

        # disable server from lb
        if self.pre_deploy_desc['disable_service_from_lb']:
            LoadBalancer().disable_service()

        # disable monitor
        if self.pre_deploy_desc['disable_monitoring']:
            Monitor().disable()

        # execute custom_pre_deploy_script
        custom_script = self.pre_deploy_desc.get('custom_pre_deploy_script', False)
        custom_script_path = '%s/%s' % (self.instance_dir_cs, custom_script)
        if custom_script and fab_files.exists(custom_script_path):
            run('chmod +x %s' % custom_script_path)
            result = run(custom_script_path)
            if result.failed: raise Exception("exec custom_pre_deploy_script %s failed, %s" % (custom_script_path, result))

        pass

    def deploy(self):
        if self.deploy_desc['shutdown_service']:
            result = run(self.global_desc['stop_command'])
            if result.failed: raise Exception("shutdown service failed, %s" % result)

        if self.global_desc['backup_previous_package']:
            backup_dir = "%s/%s" % (self.ClientBackupRoot, self.config['id'])
            result = run("mkdir -p %s" % backup_dir)
            if result.failed: raise Exception("create backup env failed, %s" % result)
            result = run("copy -r %s %s" % (self.global_desc['install_dir'], backup_dir))
            if result.failed: raise Exception("backup previous failed, %s" % result)

        if self.global_desc['remove_previous_package']:
            if self.global_desc['install_action'] == 'rpm':
                package_name = self.global_desc['resour']

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


    job = job_demo.job

    pm = Pushman(job)

    try:
        pm.update()
    except Exception as e:
        if job['desc']['global_desc']['auto_rollback']:
            pm.rollback()



