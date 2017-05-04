#!/usr/bin/env python
# encoding: utf-8

####################################################################################################

from .manager import VRepositoryManager
from .usage import VCLIUsage

from clint.arguments import Args
from clint.textui import colored, puts, min_width, max_width

####################################################################################################


class VCLIApplication:

    APP = "vgrepo"
    VER = "1.0.1"
    DESC = "Utility for managing Vagrant images written in Python"

    def process(self):
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
        self.manager = VRepositoryManager(cnf)
        self.cli = Args()

        self.process()

    def add_command(self):
        box = {
            'path': self.cli.files[0] if self.cli.files and len(self.cli.files) > 0 else None,
            'name': self.cli.value_after('-n') or self.cli.value_after('--name'),
            'version': self.cli.value_after('-v') or self.cli.value_after('--version'),
            'desc': self.cli.value_after('-d') or self.cli.value_after('--desc'),
            'provider': self.cli.value_after('-p') or self.cli.value_after('--provider'),
        }

        if box['path'] and box['version']:
            puts("Adding image to the repository... ", newline=False)

            self.manager.add(src=box['path'], name=box['name'], version=box['version'], desc=box['desc'])

            puts(colored.green("OK"))
        else:
            self.help_command()

        return True

    def list_command(self):
        name = self.cli.value_after('-n') or self.cli.value_after('--name')
        repos = self.manager.list(name)

        if repos:
            pretty_print("NAME", "VERSION", "CHECKSUM")
            for r in repos:
                for ver in r.versions:
                    checksum = ver.providers[0].checksum if ver.providers else None
                    pretty_print(
                        name=r.name,
                        version=ver.version,
                        checksum=checksum
                    )
        else:
            puts("There is no boxes yet.")

    def remove_command(self):
        image = {
            'name': self.cli.value_after('r') or self.cli.value_after('remove'),
            'version': self.cli.value_after('-v') or self.cli.value_after('--version'),
        }

        if image['name'] and image['version']:
            puts("Removing image from the repository... ", newline=False)

            self.manager.remove(name=image['name'], version=image['version'])

            puts(colored.green("OK"))
        else:
            self.help_command()

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

####################################################################################################


def pretty_print(name, version, checksum):
    puts(min_width(max_width("{name}".format(
        name=name
    ), 20), 20), newline=False)

    puts(min_width(max_width("{version}".format(
        version=version
    ), 20), 20), newline=False)

    puts(min_width(max_width("{checksum}".format(
        checksum=checksum
    ), 40), 40))
