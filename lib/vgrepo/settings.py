#!/usr/bin/env python
# encoding: utf8

import yaml


class VSettings:

    @staticmethod
    def read(cnf):
        try:
            with open(cnf, 'r') as s:
                return yaml.load(s)
        except (yaml.YAMLError, IOError) as e:
            print(e)

        return False

    def __init__(self, cnf):
        self.settings = VSettings.read(cnf)

    @property
    def repo_url(self):
        return self.settings.get('storage').get('url').strip('/')

    @property
    def repo_path(self):
        return self.settings.get('storage').get('path')
