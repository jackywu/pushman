#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from __future__ import with_statement
import os
from fabric.api import local, settings, abort, cd
from fabric.operations import run, put

def run_check_failed(cmd, exp):
    if not cmd:
        raise Exception('command is none')

    with settings(warn_only=True):
        result = run(cmd)
        if result.failed:
            raise Exception("%s, cmd %s, result %s" % (exp, cmd, result))

def extract_check_failed(file_path, install_dir):
    base_name = os.path.basename(file_path) # nginx-1.0.15-11.el6.x86_64.zip
    dir_name = os.path.dirname(file_path)   # /path/to/parent/dir/
    package_name = base_name.split('-')[0]  # nginx

    if file_path.endswith('tar.gz'):
        cmd = 'tar xzf %s' % file_path
    elif file_path.endswith('tar'):
        cmd = 'tar xf %s' % file_path
    elif file_path.endswith('tar.bz2'):
        cmd = 'tar xjf %s' % file_path
    elif file_path.endswith('zip'):
        cmd = 'unzip %s' % file_path
    else:
        raise Exception('%s extraction is not suported' % base_name)

    with cd(dir_name):
        run_check_failed(cmd, 'extract %s failed' % file_path)
        run_check_failed('mv package_name %s' % install_dir, 'mv to install_dir %s failed' % install_dir)

def run_custom_script(script_path='', path_root='', install_action='rpm', stage='deploy'):
    custom_script = script_path.strip()
    if path_root.endswith('/'):
        path_root = path_root.rstrip('/')

    if custom_script != '':
        if os.path.isabs(custom_script):
            custom_script_path = custom_script
        else:
            if install_action == 'rpm':
                raise Exception('when install by rpm, script path should be a absolute path at stage %s' % stage)
            custom_script_path = '%s/%s' % (path_root, custom_script)

        if fab_files.exists(custom_script_path):
            # TODO: chmod does not work on windows
            fab_utils.run_check_failed('chmod +x %s' % custom_script_path, 'chmod x failed at stage %s' % stage)
            fab_utils.run_check_failed(custom_script_path, 'exec custom_pre_deploy_script failed at stage %s' % stage)
        else:
            raise Exception('custom_pre_deploy_script %s does not exist' % custom_script_path)

