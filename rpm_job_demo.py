#!/usr/bin/env python
# -*- coding: UTF-8 -*-

job = {
    'id': '123',
    'job_id': '10',
    'time': 1424915926,
    'desc':
        {
            'global_desc': {
                'department': 'ad',
                'server_type': 'web_server',
                'software_module': 'nginx',
                'resource_update_to': 'http://172.28.128.40/nginx-1.6.2-1.el6.ngx.x86_64.rpm',
                'resource_rollback_to': 'http://172.28.128.40/nginx-1.6.1-1.el6.ngx.x86_64.rpm',
                'version_update_to': '',
                'version_rollback_to': '',

                'auto_rollback': True,
                'install_dir': '',
                'install_action': 'rpm',

                'start_command': '/etc/init.d/nginx start',
                'stop_command': '/etc/init.d/nginx stop',
                'restart_command': '/etc/init.d/nginx restart',
                'reload_command': '/etc/init.d/nginx reload',
            },

            'pre_deploy_desc': {
                'disable_service_from_lb': True,
                'disable_monitoring': True,
            },

            'deploy_desc': {
                'stop_service': True,
                'update_configuration_script': '',
                'custom_deploy_script': '', # [应用方提供]
                'start_service': True,

                'force_install': True,
                'backup_previous_package': False,
                'remove_previous_package': True,

            },

            'post_deploy_desc': {
                'custom_post_deploy_script': '', # [应用方提供]
                'check_proc_alive': ['nginx'],
                'check_port_alive': [80],
                'enable_monitoring': True,
                'enable_service_from_lb': True,
            },
        }
}
