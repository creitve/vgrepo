#!/usr/bin/env python
# coding: utf-8

####################################################################################################

import sys

from .repository import VImageVersionFoundError
from .storage import VStorage
from .usage import VCLIUsage

from clint.arguments import Args
from clint.textui import colored, puts, min_width

####################################################################################################


class VCLIApplication:

    APP = "vgrepo"
    VER = "1.1.0"
    DESC = "Utility for managing Vagrant repositories written in Python"

    COLUMN_WIDTH = 16

    @staticmethod
    def success(msg="OK"):
        """
        Displays message with a green color

        :param msg: message string
        :type msg: str
        :return:
        """
        puts(colored.green(msg))

    @staticmethod
    def error(msg="FAIL"):
        """
        Displays message with a red color and then exit

        :param msg: message string
        :type msg: str
        :return:
        """
        puts(colored.red(msg))
        sys.exit(1)

    @staticmethod
    def print_column(text, size):
        """
        Displays text in the column with a specified width

        :param text: message string
        :type text: str
        :param size: width of the column
        :type size: int
        :return:
        """
        puts(min_width(text, size), newline=False)

    @staticmethod
    def print_row(els):
        """
        Display line with a set of columns

        :param els: list of columns
        :type els: list
        :return:
        """
        for f in els:
            VCLIApplication.print_column(f['name'], f['width'])
        puts()

    def process(self):
        """
        Handles arguments and execute commands

        :return:
        """
        if self.cli.contains(['h', 'help']):
            self.help_command()
        elif self.cli.contains(['a', 'add']):
            self.add_command()
        elif self.cli.contains(['l', 'list']):
            self.list_command()
        elif self.cli.contains(['r', 'remove']):
            self.remove_command()
        else:
            self.help_command()

    def __init__(self, cnf):
        """
        Initializes storage client by given configuration file

        :param cnf: path to configuration file
        :type cnf: str
        """
        self.storage = VStorage(cnf)
        self.cli = Args()
        self.process()

    def add_command(self):
        """
        Adds image or repository to the storage

        :return:
        """
        args = {
            'src': self.cli.files[0] if self.cli.files and len(self.cli.files) > 0 else None,
            'name': self.cli.value_after('-n') or self.cli.value_after('--name'),
            'version': self.cli.value_after('-v') or self.cli.value_after('--version'),
            'desc': self.cli.value_after('-d') or self.cli.value_after('--desc'),
            'provider': self.cli.value_after('-p') or self.cli.value_after('--provider')
        }

        if not args['src']:
            self.error("Error: source is not specified")

        if not args['version']:
            self.error("Error: version is not specified")

        try:
            self.storage.add(
                src=args['src'],
                name=args['name'],
                version=args['version'],
                desc=args['desc'],
                provider=args['provider'],
            )
        except VImageVersionFoundError:
            self.error("Error: version is already exists")
        else:
            self.success()

    def list_command(self):
        """
        Displays list of available repositories and images inside of them

        :return:
        """
        args = {
            'name': self.cli.value_after('-n') or self.cli.value_after('--name')
        }

        self.print_row([
            {'name': colored.yellow("NAME"), 'width': self.COLUMN_WIDTH},
            {'name': colored.yellow("VERSION"), 'width': self.COLUMN_WIDTH},
            {'name': colored.yellow("PROVIDER"), 'width': self.COLUMN_WIDTH},
            {'name': colored.yellow("URL"), 'width': self.COLUMN_WIDTH * 4},
        ])

        for repo in self.storage.list(args['name']):
            meta = repo.info

            for version in meta.versions:
                for provider in version.providers:

                    self.print_row([
                        {'name': meta.name, 'width': self.COLUMN_WIDTH},
                        {'name': version.version, 'width': self.COLUMN_WIDTH},
                        {'name': provider.name, 'width': self.COLUMN_WIDTH},
                        {'name': repo.repo_url, 'width': self.COLUMN_WIDTH * 4},
                    ])

    def remove_command(self):
        """
        Removes image or repository from the storage

        :return:
        """
        args = {
            'name': self.cli.value_after('r') or self.cli.value_after('remove'),
            'version': self.cli.value_after('-v') or self.cli.value_after('--version')
        }

        if not args['name']:
            self.error("Error: name is not specified")

        if not args['version']:
            self.error("Error: version is not specified")

        try:
            self.storage.remove(
                name=args['name'],
                version=args['version'],
            )
        except [IOError, OSError]:
            self.error("Error: unable to delete image or repository")
        else:
            self.success()

    @staticmethod
    def help_command():
        """
        Displays usage message

        :return:
        """
        usage = VCLIUsage(VCLIApplication.APP, VCLIApplication.VER, VCLIApplication.DESC)

        usage.add_command(cmd="a:add", desc="Add image into the Vagrant's repository")
        usage.add_command(cmd="l:list", desc="Show list of available images")
        usage.add_command(cmd="r:remove", desc="Remove image from the repository")
        usage.add_command(cmd="h:help", desc="Display current help message")

        usage.add_option(option="v:version", desc="Value of version of the box")
        usage.add_option(option="n:name", desc="Name of box in the repository")
        usage.add_option(option="d:desc", desc="Description of the box in the repository")
        usage.add_option(option="p:provider", desc="Name of provider (e.g. virtualbox)")

        usage.add_example("{app} add image.box --name box --version 1.0.1".format(app=VCLIApplication.APP))
        usage.add_example("{app} remove powerbox --version 1.1.0".format(app=VCLIApplication.APP))
        usage.add_example("{app} list".format(app=VCLIApplication.APP))

        usage.render()
