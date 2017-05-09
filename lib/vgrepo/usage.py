#!/usr/bin/env python
# coding: utf8

from clint.textui import colored, puts, indent, min_width, max_width


class VCLIUsage:
    """
    Class which provides interface to build usage helper.
    """

    # Amount of symbols for indentation
    INDENT_SIZE = 4

    # Width of left column in symbols
    LEFT_COLUMN_WIDTH = 25

    # Width of right column in symbols
    RIGHT_COLUMN_WIDTH = 55

    # Total width of the table
    TOTAL_WIDTH = LEFT_COLUMN_WIDTH + RIGHT_COLUMN_WIDTH

    @staticmethod
    def parse_command(cmd):
        """
        Divide given command string to long and short pieces

        :param cmd: command string divided by colon
        :type cmd: str
        :return: formatted command string
        """
        if cmd.find(':') != -1:
            cmd_slice = cmd.split(':')
            return "{long} or {short}".format(long=cmd_slice[1], short=cmd_slice[0])

        return "{long}".format(long=cmd)

    @staticmethod
    def parse_option(option):
        """
        Divides given option string to long and short pieces

        :param option: command option divided by colon
        :type option: str
        :return: formatted option string
        """
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
        """
        Adds given command with their description to the usage menu

        :param cmd: command string with a colon as a separator
        :type cmd: str
        :param desc: description of the command
        :type desc: str
        :return:
        """
        self.commands.append({'cmd': self.parse_command(cmd), 'desc': desc})

    def add_option(self, option, desc):
        """
        Adds given option with their description to the usage menu

        :param option: option string with a colon as a separator
        :type option: str
        :param desc: description of the option
        :type desc: str
        :return:
        """
        self.options.append({'option': self.parse_option(option), 'desc': desc})

    def add_example(self, desc):
        """
        Adds given string into the submenu with an examples

        :param desc: string of the example
        :type desc: str
        :return:
        """
        self.examples.append({'desc': desc})

    @staticmethod
    def render_title(text):
        """
        Displays block title

        :param text: text which should be displayed
        :type text: str
        :return:
        """
        puts(colored.yellow("{0}\n".format(text)))

    def render_line(self, body):
        """
        Displays line in one column

        :param body:
        :return:
        """
        puts(min_width(body, self.TOTAL_WIDTH))

    @staticmethod
    def render_line2(left, right):
        """
        Displays line in two columns

        :param left: left part of the row
        :type left: str
        :param right: right part of the row
        :type right: str
        :return:
        """
        def render_left_column(text):
            """
            Displays left column

            :param text: text which should be displayed on the left side
            :type text: str
            :return:
            """
            puts(min_width(text, VCLIUsage.LEFT_COLUMN_WIDTH), newline=False)

        def render_right_column(text):
            """
            Displays right column

            :param text: text which should be displayed on the right side
            :type text: str
            :return:
            """
            puts(max_width(min_width(text, VCLIUsage.RIGHT_COLUMN_WIDTH), VCLIUsage.TOTAL_WIDTH))

        render_left_column(left)
        render_right_column(right)

    def render(self):
        """
        Renders usage menu

        :return:
        """
        self.render_header()
        self.render_commands()
        self.render_options()
        self.render_examples()

    def render_header(self):
        """
        Renders submenu with an info about application

        :return:
        """
        header_template = "\n{usage}: {app} {commands} {options}\n\n{desc}\n"

        puts(header_template.format(
            usage=colored.white("Usage", bold=True),
            app=self.app,
            desc=self.desc,
            commands=colored.yellow("command"),
            options=colored.green("options")),
        )

    def render_commands(self):
        """
        Renders submenu with an info about available commands

        :return:
        """
        if self.commands:
            self.render_title("Commands")

            with indent(self.INDENT_SIZE):
                for c in self.commands:
                    self.render_line2(c['cmd'], c['desc'])
            puts("")

    def render_options(self):
        """
        Renders submenu with an info about available options

        :return:
        """
        if self.options:
            self.render_title("Options")

            with indent(self.INDENT_SIZE):
                for o in self.options:
                    self.render_line2(o['option'], o['desc'])
            puts("")

    def render_examples(self):
        """
        Renders commands submenu with an examples

        :return:
        """
        if self.examples:
            self.render_title("Examples")

            with indent(self.INDENT_SIZE):
                for e in self.examples:
                    self.render_line(e['desc'])

            puts("")
