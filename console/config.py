# coding=utf-8
__author__ = 'chenlei'

import ConfigParser
import os

BASE_PATH = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

CONFIG_PATH = os.path.join(BASE_PATH, 'conf', 'config.ini')


def load_config(config_file=CONFIG_PATH):
    config_file = os.getenv('CONFIG_FILE', config_file)
    config = ConfigParser.SafeConfigParser()
    config.read(config_file)
    return config
