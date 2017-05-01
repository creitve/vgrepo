# About

[![Build Status](https://travis-ci.org/gongled/vgrepo.svg?branch=master)](https://travis-ci.org/gongled/vgrepo)
[![PyPI](https://img.shields.io/pypi/v/vgrepo.svg)]()

`vgrepo` is a tool for managing Vagrant repositories written in Python.

## Installation

#### From PyPI

```bash
pip install vgrepo
```

#### From source

```bash
git clone git@github.com:gongled/vgrepo
python vgrepo/setup.py install
```

## Usage

```
Usage: vgrepo command options

Utility for managing Vagrant's repository.

Commands:

  a or add                        Add box into the Vagrant's repository
  l or list                       Show list of available boxes
  d or delete                     Delete box from the repository
  k or kill                       Destroy all boxes with metadata from the repository
  h or help                       Show detailed information about command

Options:

  -v or --version [ver]           Value of version of the box
  -n or --name [box]              Name of box in the repository
  -d or --description [descr]     Description of the box in the repository

Examples:

  vgrepo add $HOME/vagrant/centos7-x86_64.box --name powerbox --version 1.0.1
  vgrepo delete powerbox --version 1.1.0
  vgrepo list
  vgrepo kill powerbox

See vgrepo help <command> for information on a specific command.
```

## License

[MIT](LICENSE)
