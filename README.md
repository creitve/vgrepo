# About

[![Build Status](https://travis-ci.org/gongled/vgrepo.svg?branch=master)](https://travis-ci.org/gongled/vgrepo)
[![codebeat badge](https://codebeat.co/badges/016cae98-9953-4f0e-9495-d9a91969b6ef)](https://codebeat.co/projects/github-com-gongled-vgrepo-master)
[![PyPI](https://img.shields.io/pypi/v/vgrepo.svg)]()

`vgrepo` is a tool for managing Vagrant repositories written in Python.

## Requirements

- Python 2.6 or higher
- [clint](https://github.com/kennethreitz/clint) 0.5.0 or higher
- [PyYAML](https://github.com/yaml/pyyaml) 3.10 or higher

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
Usage: vgrepo [command] [options]

Commands

    add or a                     Add image into the Vagrant's repository
    list or l                    Show list of available images
    remove or r                  Remove image from the repository
    help or h                    Display current help message

Options

    -v, --version                Value of version of the box
    -n, --name                   Name of box in the repository
    -d, --desc                   Description of the box in the repository
    -p, --provider               Name of provider (e.g. virtualbox)

Examples

    vgrepo add image.box --name box --version 1.0.1
    vgrepo remove powerbox --version 1.1.0
    vgrepo list
```

## License

[MIT](LICENSE)
