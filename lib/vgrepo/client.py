#!/usr/bin/env python
# encoding: utf-8

####################################################################################################

from .repository import VRepository
from .manager import VRepositoryManager
from clint.arguments import Args
from clint.textui import colored, puts, indent, min_width, max_width

####################################################################################################

APP = "vgrepo"
VER = "1.0.1"
DESC = "Utility for operating Vagrant images"

####################################################################################################


class VCLIUsage:

    _INDENT_SIZE = 4
    _MIN_COLUMN_WIDTH = 25
    _MAX_COLUMN_WIDTH = 80

    @staticmethod
    def parse_command(cmd):
        if cmd.find(':') != -1:
            cmd_slice = cmd.split(':')
            return "{long} or {short}".format(long=cmd_slice[1], short=cmd_slice[0])

        return "{long}".format(long=cmd)

    @staticmethod
    def parse_option(option):
        if option.startswith('-'):
            return option

        if option.find(":") != -1:
            option_slice = option.split(':')
            return "-{short}, --{long}".format(long=option_slice[1], short=option_slice[0])

        return "--{long}".format(long=option)

    def __init__(self, app, version, desc):
        self.app = app
        self.version = version
        self.desc = desc
        self.commands = []
        self.options = []
        self.examples = []

    def add_command(self, cmd, desc):
        self.commands.append({
            'cmd': self.parse_command(cmd),
            'desc': desc
        })

    def add_option(self, option, desc):
        self.options.append({
            'option': self.parse_option(option),
            'desc': desc
        })

    def add_example(self, example):
        self.examples.append({
            'example': example
        })

    def render(self):
        self.render_header()
        self.render_commands()
        self.render_options()
        self.render_examples()

    def render_header(self):
        header_template = "\n{usage}: {app} {commands} {options}\n\n{desc}\n"

        puts(header_template.format(
            usage=colored.white("Usage", bold=True),
            app=self.app,
            desc=self.desc,
            commands=colored.yellow("command"),
            options=colored.green("options")),
        )

    def render_commands(self):
        if self.commands:
            puts(colored.yellow("Commands:\n"))

            with indent(self._INDENT_SIZE):
                for c in self.commands:
                    puts(min_width(c['cmd'], self._MIN_COLUMN_WIDTH), newline=False)
                    puts(max_width(min_width(
                        c['desc'],
                        self._MAX_COLUMN_WIDTH - self._MIN_COLUMN_WIDTH),
                        self._MAX_COLUMN_WIDTH),
                        newline=True
                    )
            puts("")

    def render_options(self):
        if self.options:
            puts(colored.yellow("Options:\n"))

            with indent(self._INDENT_SIZE):
                for o in self.options:
                    puts(min_width(o['option'], self._MIN_COLUMN_WIDTH), newline=False)
                    puts(max_width(min_width(
                        o['desc'],
                        self._MAX_COLUMN_WIDTH - self._MIN_COLUMN_WIDTH),
                        self._MAX_COLUMN_WIDTH),
                        newline=True
                    )
            puts("")

    def render_examples(self):
        if self.examples:
            puts(colored.yellow("Examples:\n"))

            with indent(self._INDENT_SIZE):
                for e in self.examples:
                    puts(min_width(e['example'], self._MAX_COLUMN_WIDTH))

            puts("")

####################################################################################################


class VCLIApplication:

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
        self.app = APP
        self.repo = VRepositoryManager(cnf)
        self.usage = VCLIUsage(APP, VER, DESC)
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

            self.repo.add(src=box['path'], name=box['name'], version=box['version'], desc=box['desc'])

            puts(colored.green("OK"))
        else:
            self.help_command()

        return True

    def list_command(self):
        boxes = self.repo.list()

        if boxes:
            pretty_print("NAME", "VERSION", "CHECKSUM")
            for box in boxes:
                for ver in box.versions:
                    checksum = ver.providers[0].checksum if ver.providers else None
                    pretty_print(
                        name=box.name,
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

            self.repo.remove(name=image['name'], version=image['version'])

            puts(colored.green("OK"))
        else:
            self.help_command()

    def help_command(self):
        self.usage.add_command(cmd="a:add", desc="Add image into the Vagrant's repository")
        self.usage.add_command(cmd="l:list", desc="Show list of available images")
        self.usage.add_command(cmd="r:remove", desc="Remove image from the repository")
        self.usage.add_command(cmd="h:help", desc="Show detailed information about command")

        self.usage.add_option(option="v:version", desc="Value of version of the box")
        self.usage.add_option(option="n:name", desc="Name of box in the repository")
        self.usage.add_option(option="d:desc", desc="Description of the box in the repository")
        self.usage.add_option(option="p:provider", desc="Name of provider (e.g. virtualbox)")

        self.usage.add_example("{app} add $HOME/centos7-x86_64.box --name powerbox --version 1.0.1".format(app=APP))
        self.usage.add_example("{app} remove powerbox --version 1.1.0".format(app=APP))
        self.usage.add_example("{app} list".format(app=APP))

        self.usage.render()

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
