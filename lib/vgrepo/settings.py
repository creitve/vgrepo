#!/usr/bin/env python
# coding: utf8

import yaml


class VSettings:

    @staticmethod
    def read(cnf):
        """
        Parses YAML configuration file

        :param cnf: path to the configuration file
        :type cnf: str
        :return:
        """
        try:
            with open(cnf, 'r') as s:
                return yaml.load(s)
        except (yaml.YAMLError, IOError) as e:
            print(e)

        return False

    def __init__(self, cnf):
        self.settings = VSettings.read(cnf)

    @property
    def storage_url(self):
        """
        Returns URL of the published images

        :return: str
        """
        return self.settings.get('storage').get('url').strip('/')

    @property
    def storage_path(self):
        """
        Returns path for the repositories

        :return: str
        """
        return self.settings.get('storage').get('path')
