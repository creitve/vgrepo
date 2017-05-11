# About

[![Build Status](https://travis-ci.org/gongled/vgrepo.svg?branch=master)](https://travis-ci.org/gongled/vgrepo)
[![codebeat badge](https://codebeat.co/badges/016cae98-9953-4f0e-9495-d9a91969b6ef)](https://codebeat.co/projects/github-com-gongled-vgrepo-master)
[![PyPI](https://img.shields.io/pypi/v/vgrepo.svg)]()

`vgrepo` is a CLI tool for managing Vagrant repositories.

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

## Configuration

Specify storage settings in the `/etc/vgrepo.conf` configuration file:

```
storage:

  path: "/srv/vagrant"

  url: "http://localhost:8080"
```

Run NGINX with the following configuration of virtual host:

```
server {
    listen 8080;
    server_name localhost;

    root /srv/vagrant;

    location ~ ^/([^\/]+)/$ {
        index /metadata/$1.json;
        try_files /$1/metadata/$1.json =404;
    }

    location ~ \.json$ {
        add_header Content-Type application/json;
    }

    location ~ \.box$ {
        add_header Content-Type application/octet-stream;
    }

    location / {
	    autoindex off;
        expires -1;
    }
}
```

Now you can use `http://localhost:8080/boxname` in the `config.vm.box_url` parameter.

## Usage

```
Usage: vgrepo [command] [options]

Commands

    add or a                     Add image to the Vagrant repository
    list or l                    Show the list of available images
    remove or r                  Remove the image from the repository
    help or h                    Display the current help message

Options

    -v, --version                Version of the box
    -n, --name                   Name of box
    -d, --desc                   Description of the box
    -p, --provider               Name of provider

Examples

    vgrepo add image.box --name box --version 1.0.1
    vgrepo remove powerbox --version 1.1.0
    vgrepo list
```

## License

[MIT](LICENSE)
