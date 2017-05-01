#!/usr/bin/env python
# encoding: utf-8

from .repository import VRepository

from clint.arguments import Args

from clint.textui import colored, puts, indent, min_width, max_width


class VCLIApp:

    @staticmethod
    def add_usage_command(cmd, short_cmd, descr):
        puts(min_width("{short_cmd} or {cmd}".format(
            short_cmd=colored.yellow(short_cmd),
            cmd=colored.yellow(cmd)
        ), 30), newline=False)
        puts(max_width(min_width("{descr}".format(descr=descr), 60), 90))

    def show_usage_header(self):
        puts("\n{usage}: {app} {commands} {options}\n\n{descr}\n".format(
            usage=colored.white("Usage", bold=True),
            app=self.app,
            descr="Utility for managing Vagrant's repository.",
            commands=colored.yellow("command"),
            options=colored.green("options")),
        )

    def show_usage_common(self, cmd=None):
        self.show_usage_header()

        puts(colored.yellow("Commands:\n"))
        with indent(2):
            self.show_usage_commands(cmd)

        puts(colored.yellow("\nOptions:\n"))
        with indent(2):
            self.show_usage_options(cmd)

        puts(colored.yellow("\nExamples:\n"))
        with indent(2):
            puts("{app} add $HOME/vagrant/centos7-x86_64.box --name powerbox --version 1.0.1".format(
                app=self.app
            ))
            puts("{app} delete powerbox --version 1.1.0".format(
                app=self.app
            ))
            puts("{app} list".format(
                app=self.app
            ))
            puts("{app} kill powerbox".format(
                app=self.app
            ))

        puts("\nSee {app} help <command> for information on a specific command.".format(
            app=colored.yellow(self.app)
        ))

    def show_usage_commands(self, cmd=None):
        if not cmd or cmd == "add":
            self.add_usage_command(
                short_cmd="a",
                cmd="add",
                descr="Add box into the Vagrant's repository"
            )

        if not cmd or cmd == "list":
            self.add_usage_command(
                short_cmd="l",
                cmd="list",
                descr="Show list of available boxes"
            )

        if not cmd or cmd == "delete":
            self.add_usage_command(
                short_cmd="d",
                cmd="delete",
                descr="Delete box from the repository"
            )

        if not cmd or cmd == "kill":
            self.add_usage_command(
                short_cmd="k",
                cmd="kill",
                descr="Destroy all boxes with metadata from the repository"
            )

        if not cmd or cmd == "help":
            self.add_usage_command(
                short_cmd="h",
                cmd="help",
                descr="Show detailed information about command"
            )

    def show_usage_options(self, cmd):

        if not cmd or cmd == "add" or cmd == "delete":
            self.add_usage_command(
                short_cmd="-v",
                cmd="--version [ver]",
                descr="Value of version of the box"
            )
        if not cmd or cmd == "add":
            self.add_usage_command(
                short_cmd="-n",
                cmd="--name [box]",
                descr="Name of box in the repository"
            )
            self.add_usage_command(
                short_cmd="-d",
                cmd="--description [descr]",
                descr="Description of the box in the repository"
            )
        if cmd == "list":
            puts("There is no extra options")

    def __init__(self, app, cnf):

        self.app = app
        self.repo = VRepository(cnf)
        self.cli = Args()

        if self.cli.contains('help') or self.cli.contains('h'):
            self.usage()
        elif self.cli.contains('add') or self.cli.contains('a'):
            self.add_command()
        elif self.cli.contains('list') or self.cli.contains('l'):
            self.list_command()
        elif self.cli.contains('delete') or self.cli.contains('d'):
            self.delete_command()
        elif self.cli.contains('kill') or self.cli.contains('k'):
            self.kill_command()
        else:
            self.usage()

    def add_command(self):

        box_path = self.cli.files[0] if self.cli.files and len(self.cli.files) > 0 else None

        box_name = self.cli.value_after('--name') or self.cli.value_after('-n') or None

        box_version = self.cli.value_after('--version') or self.cli.value_after('-v') or None

        box_description = self.cli.value_after('--description') or self.cli.value_after('-d') or None

        if box_path and box_version:
            if self.repo.add(
                src_path=box_path,
                name=box_name,
                version=box_version,
                description=box_description
            ):
                puts(colored.green("\nCompleted"))
            else:
                puts(colored.red("\nFailed"))
        else:
            self.show_usage_common()

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

    def delete_command(self):
        box_name = self.cli.value_after('delete') or self.cli.value_after('d') or None
        box_version = self.cli.value_after('--version') or self.cli.value_after('-v') or None

        if box_name and box_version:
            self.repo.delete(box_name, box_version)
        else:
            self.show_usage_common()

    def kill_command(self):
        box_name = self.cli.value_after('kill') or \
                   self.cli.value_after('k') or \
                   None

        if box_name:
            self.repo.kill(box_name)
        else:
            self.show_usage_common()

    def usage(self):
        cmd = self.cli.value_after("help") or None

        self.show_usage_common(cmd)


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
