#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from __future__ import with_statement
import os
import re
import fab_utils
from fabric.api import local, settings, abort, cd, quiet
from fabric.operations import run, put


class BaseInstaller(object):

    def __init__(self, **args):
        for k,v in args.items():
            setattr(self, k, v)

    def check_params(self, params):
    # every param should not be empty or None
        for k in params:
            if not k:
                raise Exception('param should not be empty or None')

    def remove_previous(self):
        raise Exception("this method should be implemented in subclass")

    def install(self):
        raise Exception("this method should be implemented in subclass")

class RpmInstaller(BaseInstaller):

    def __init__(self, **args):
        super(RpmInstaller, self).__init__(**args)

    def check_params(self):
        super(RpmInstaller, self).check_params([
            self.resource,
        ])

    def remove_previous(self):
        package_full_name = os.path.basename(self.resource) # nginx-1.6.1-1.el6.ngx.x86_64.rpm
        package_name = package_full_name.split('-')[0] # nginx
        package_prefix = package_full_name.rstrip('.rpm') # nginx-1.6.1-1.el6.ngx.x86_64

        # package does exist and remove it
        with quiet():
            if run('rpm -q --quiet %s' % package_name).succeeded:
                fab_utils.run_check_failed('rpm -e %s' % package_name, 'rpm remove previous package failed')

    def install(self):
        if self.force_install:
            extra_param = ' --force --nodeps '
        else:
            extra_param = ''
        fab_utils.run_check_failed('rpm -U %s %s' % (extra_param, self.resource), 'rpm install failed')


class ArchiveInstaller(BaseInstaller):
    def __init__(self, **args):
        super(ArchiveInstaller, self).__init__(**args)

    def check_params(self):
        super(RpmInstaller, self).check_params([
            self.resource,
            self.install_dir,
        ])

    def remove_previous(self):
        fab_utils.run_check_failed('rm -rf %s' % self.install_dir, 'rm previous package failed')
        pass

    def install(self):
        fab_utils.extract_check_failed(self.resource, self.install_dir)
        pass


class YumInstaller(BaseInstaller):
    '''
    for YumInstaller, resource is pacakge name, e.g. nginx
    '''
    def __init__(self, **args):
        super(YumInstaller, self).__init__(**args)


    def check_params(self):
        super(RpmInstaller, self).check_params([
            self.resource,
            self.version,
        ])

    def remove_previous(self):
        fab_utils.run_check_failed('yum remove -y %s' % self.resource, 'yum remove previous package failed')
        pass

    def install(self):
        fab_utils.run_check_failed('yum install -y %s-%s' % (self.resource, self.version), 'yum install package failed')


class InstallerFactory(object):

    FLAG_RPM = 'rpm'
    FLAG_YUM = 'yum'
    FLAG_ARCHIVE = 'archive'

    CLASS_MAP = {
        FLAG_RPM: RpmInstaller,
        FLAG_YUM: YumInstaller,
        FLAG_ARCHIVE: ArchiveInstaller,
    }

    def __init__(self, resource='', version='', install_action='',
                 install_dir='', force_install=False):
        self.args = {
            'resource': resource,
            'version': version,
            'install_action': install_action,
            'install_dir': install_dir,
            'force_install': force_install,
        }
        for k,v in self.args.items():
            setattr(self, k, v)
        self.installer = None

    def config(self):
        flag = None

        if self.install_action == self.FLAG_RPM:
            flag = self.FLAG_RPM
        elif self.install_action == self.FLAG_YUM:
            flag = self.FLAG_YUM
        elif self.install_action == self.FLAG_ARCHIVE:
            flag = self.FLAG_ARCHIVE
        elif self.install_action == '':
            # we will guess next step
            pass
        else:
            raise Exception('invalid install action')

        # if install_action is not supplied, guess by resource name
        if self.resource.endswith('.rpm'):
            flag = self.FLAG_RPM
        elif re.match(r'.*(tar\.gz|tar|tar\.bz2|zip)$', self.resource):
            flag = self.FLAG_ARCHIVE
        else:
            flag = self.FLAG_YUM

        installer = self.CLASS_MAP[flag](**self.args)
        installer.check_params()
        return installer



if __name__ == '__main__':
    installer = InstallerFactory('http://a.com/nginx.rar').config()
    #print installer
    installer.remove_previous()
    installer.install()
