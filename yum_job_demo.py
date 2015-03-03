#!/usr/bin/env python
# -*- coding: UTF-8 -*-

job = {
    'id': '123',
    'job_id': '13',
    'time': 1424915923,
    'desc':
        {
            'global_desc': {
                # these three itemes are useless for action, but only for desc
                'department': 'ad',
                'server_type': 'web_server',
                'software_module': 'zsh',

                'resource_update_to': 'zsh',
                'resource_rollback_to': 'zsh',
                'version_update_to': '4.3.10-9.el6',
                'version_rollback_to': '4.3.10-7.el6',

                'auto_rollback': True,
            },

            'pre_deploy_desc': {
                'disable_service_from_lb': True,
                'disable_monitoring': True,
            },

            'deploy_desc': {
                'install_dir': '',
                'install_action': 'yum',
                'force_install': True,

                'start_command': '',
                'stop_command': '',
                'restart_command': '',
                'reload_command': '',

                'stop_service': False,
                'backup_previous_package': False,
                'remove_previous_package': True,
                'update_configuration_script': '',
                'custom_deploy_script': '', # [应用方提供]
                'start_service': False,

            },

            'post_deploy_desc': {
                'custom_post_deploy_script': '', # [应用方提供]
                'check_proc_alive': [],
                'check_port_alive': [],
                'enable_monitoring': True,
                'enable_service_from_lb': True,
            },
        }
}
