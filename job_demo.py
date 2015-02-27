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
                'software_module': 'web_front',
                'resource_update_to': 'http://172.28.128.40/lshw-2.16-1.el6.rf.x86_64.rpm',
                'resource_rollback_to': 'http://172.28.128.40/lshw-2.15-1.el6.rf.x86_64.rpm',
                'install_action': 'rpm',
                'version_update_to': '',
                'version_rollback_to': '',
                'auto_rollback': True,
                'install_dir': '/usr/local/lshw',
                'start_command': '/etc/init.d/nginx start',
                'stop_command': '/etc/init.d/nginx stop',
                'restart_command': '/etc/init.d/nginx restart',
                'reload_command': '/etc/init.d/nginx reload',
                'backup_previous_package': True,
                'remove_previous_package': True,
            },

            'pre_deploy_desc': {
                # [*] check_if_deployed
                'disable_service_from_lb': True,
                'disable_monitoring': True,
                'custom_pre_deploy_script': 'path/to/custom_pre_deploy_script',
            },

            'deploy_desc': {
                'shutdown_service': True,
                'update_configuration': 'path/to/update_config_script',
                # [*] do deploy action
                'custom_deploy_script': 'path/to/custom_deploy_script', # [应用方提供]
                'restart_service': True,
            },

            'post_deploy_desc': {
                'custom_post_deploy_script': 'path/to/custom_post_deploy_script', # [应用方提供]
                'check_proc_alive': ['nginx', 'xxx'],
                'check_port_alive': [80, 443],
                'enable_monitoring': True,
                'enable_service_from_lb': True,
            },
        }
}