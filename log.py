#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import logging
import logging.handlers
import os.path

class Log(object):
    def __init__(self, log_path, logger_name='Log', max_size=1000**3, backup_count=7):
        """
        Args:
            log_path: path to put log file
            logger_name: logger name which is a standard concept in logging module
            max_size: max size of the log file, if exceed, a new file will be created
            keeps: how many old log files should be kept
        """
        self.log_path = log_path
        self.logger_name = logger_name
        self.max_size = max_size
        self.backup_count = backup_count

    def open_log(self):

        log_dir = os.path.dirname(self.log_path)
        if len(log_dir.strip()) != 0:
            if not os.path.exists(log_dir):
                os.makedirs(log_dir)

        self.logger = logging.getLogger(self.logger_name)
        self.logger.setLevel(logging.DEBUG)

        self.file_handler = logging.handlers.RotatingFileHandler(self.log_path, maxBytes=self.max_size, backupCount=self.backup_count)
        formatter = logging.Formatter("%(asctime)s | %(name)s | %(levelname)s | [%(process)s:%(filename)s:%(lineno)d] | %(message)s")
        self.file_handler.setFormatter(formatter)
        self.logger.addHandler(self.file_handler)
        return self.logger

    def debug(self, msg):
        self.logger.debug(msg)

    def info(self, msg):
        self.logger.info(msg)

    def warn(self, msg):
        self.logger.warning(msg)

    def error(self, msg):
        self.logger.error(msg)

    def critical(self, msg):
        self.logger.critical(msg)

    def expetion(self, msg):
        self.logger.exception(msg)

    def get_logger(self):
        return self.logger

if __name__ == '__main__':
    logger = Log('test.log', 'L').open_log()

    logger.info('test')