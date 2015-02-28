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
