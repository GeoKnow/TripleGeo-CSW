import os
import logging
import logging.config
import ConfigParser as configparser

logging.config.fileConfig('config.ini')

_config = configparser.ConfigParser()
_config.read('config.ini')

def get(section, key, default_value=None):
    return _config.get(section, key, default_value)

def gets(section, key):
    return _config.get(section, key)

def getb(section, key):
    return _config.getboolean(section, key)

def geti(section, key):
    return _config.getint(section, key)

def getf(section, key):
    return _config.getfloat(section, key)

