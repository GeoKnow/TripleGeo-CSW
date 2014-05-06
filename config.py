import os
import logging
import logging.config
import ConfigParser as configparser

logging.config.fileConfig('config.ini')

_config = configparser.ConfigParser()
_config.read('config.ini')

def get(section, key, default_value=None):
    return _config.get(section, key, default_value)

