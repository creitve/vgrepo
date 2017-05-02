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

Utility for operating Vagrant images.

Commands:

  a or add                        Add image into the Vagrant's repository
  l or list                       Show list of available images
  d or delete                     Delete image from the repository
  k or kill                       Destroy all images with metadata from the repository
  h or help                       Show detailed information about command

Options:

  -v or --version [ver]           Value of version of the image
  -n or --name [box]              Name of image in the repository
  -d or --description [descr]     Description of the image in the repository

Examples:

  vgrepo add $HOME/vagrant/centos7-x86_64.box --name powerbox --version 1.0.1
  vgrepo delete powerbox --version 1.1.0
  vgrepo list
  vgrepo kill powerbox

See vgrepo help <command> for information on a specific command.
```

## License

[MIT](LICENSE)
