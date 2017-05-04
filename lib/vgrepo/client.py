#!/usr/bin/env python
# encoding: utf-8

####################################################################################################

import sys

from .repository import VImageVersionFoundError
from .manager import VRepositoryManager
from .usage import VCLIUsage

from clint.arguments import Args
from clint.textui import colored, puts, min_width, max_width

####################################################################################################


class VCLIUnsupportedOptionError(Exception):
    pass


class VCLIUnsupportedCommandError(Exception):
    pass


class VCLIApplication:

    APP = "vgrepo"
    VER = "1.0.1"
    DESC = "Utility for managing Vagrant images written in Python"

    COLUMN_WIDTH = 16

    @staticmethod
    def display_success(msg):
        puts(colored.green(msg))

    @staticmethod
    def display_failure(msg):
        puts(colored.red(msg))
        sys.exit(1)

    @staticmethod
    def display_status(msg, res=False):
        puts(msg, newline=False)
        if res:
            VCLIApplication.display_success("OK")
        else:
            VCLIApplication.display_failure("FAIL")

    @staticmethod
    def print_column(text, size):
        puts(min_width(text, size), newline=False)

    @staticmethod
    def print_row(els):
        for f in els:
            VCLIApplication.print_column(f['name'], f['width'])
        puts()

    def process(self):
        try:
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
        except VCLIUnsupportedOptionError as e:
            self.help_command()

    def __init__(self, cnf):
        self.manager = VRepositoryManager(cnf)
        self.cli = Args()

        self.process()

    def add_command(self):
        src = self.cli.files[0] if self.cli.files and len(self.cli.files) > 0 else None
        name = self.cli.value_after('-n') or self.cli.value_after('--name')
        version = self.cli.value_after('-v') or self.cli.value_after('--version')
        desc = self.cli.value_after('-d') or self.cli.value_after('--desc')
        provider = self.cli.value_after('-p') or self.cli.value_after('--provider')

        if not src:
            raise VCLIUnsupportedOptionError("--source option is not specified")

        if not version:
            raise VCLIUnsupportedOptionError("--version option is not specified")

        try:
            self.manager.add(
                src=src,
                name=name,
                version=version,
                desc=desc,
                provider=provider,
            )
        except VImageVersionFoundError:
            VCLIApplication.display_failure("Version is already exists")


    def list_command(self):
        name = self.cli.value_after('-n') or self.cli.value_after('--name')

        self.print_row([
            {'name': colored.yellow("NAME"), 'width': self.COLUMN_WIDTH},
            {'name': colored.yellow("VERSION"), 'width': self.COLUMN_WIDTH},
            {'name': colored.yellow("PROVIDER"), 'width': self.COLUMN_WIDTH},
            {'name': colored.yellow("URL"), 'width': self.COLUMN_WIDTH * 4},
        ])

        for repo in self.manager.list(name):
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
        name = self.cli.value_after('r') or self.cli.value_after('remove')
        version = self.cli.value_after('-v') or self.cli.value_after('--version')

        if not name:
            raise VCLIUnsupportedOptionError("--name option is not specified")

        if not version:
            raise VCLIUnsupportedOptionError("--version option is not specified")

        try:
            self.manager.remove(
                name=name,
                version=version,
            )
        except Exception:
            VCLIApplication.display_failure("Unable to remove image")

    @staticmethod
    def help_command():
        usage = VCLIUsage(VCLIApplication.APP, VCLIApplication.VER, VCLIApplication.DESC)

        usage.add_command(cmd="a:add", desc="Add image into the Vagrant's repository")
        usage.add_command(cmd="l:list", desc="Show list of available images")
        usage.add_command(cmd="r:remove", desc="Remove image from the repository")
        usage.add_command(cmd="h:help", desc="Show detailed information about command")

        usage.add_option(option="v:version", desc="Value of version of the box")
        usage.add_option(option="n:name", desc="Name of box in the repository")
        usage.add_option(option="d:desc", desc="Description of the box in the repository")
        usage.add_option(option="p:provider", desc="Name of provider (e.g. virtualbox)")

        usage.add_example("{app} add image.box --name box --version 1.0.1".format(app=VCLIApplication.APP))
        usage.add_example("{app} remove powerbox --version 1.1.0".format(app=VCLIApplication.APP))
        usage.add_example("{app} list".format(app=VCLIApplication.APP))

        usage.render()
