#!/usr/bin/env python
# coding: utf8

import os

from .settings import VSettings
from .repository import VRepository
from .meta.images import VMetadataImage, VMetadataVersion, VMetadataProvider


class VStorage:
    """
    Manages Vagrant repositories
    """

    @staticmethod
    def list_dirs(path):
        """
        Provides a simple directories list by given path

        :param path: directory
        :type path: str
        :return: list of directories
        """

        dirs = []
        try:
            dirs = [d for d in os.listdir(path)
                    if os.path.isdir(os.path.join(path, d))
                    ]
        except [OSError, IOError]:
            # TODO: add an exception
            print("Error: unable to read {0}".format(path))

        return dirs

    def __init__(self, cnf):
        """
        Initializes repository instance and metadata

        :param cnf: path to configuration file
        """

        self.settings = VSettings(cnf)

    def add(self, src, name, version, desc='', provider='virtualbox'):
        """
        Adds new image to the repository by given parameters.

        :param src: path to the loadable image file
        :type src: str
        :param name: identifier of the image
        :type name: str
        :param version: version of the image
        :type version: str
        :param desc: description of the image
        :type desc: str
        :param provider: provide or the image (e.g. virtualbox)
        :type provider: str
        """

        if not name:
            name = os.path.basename(src).replace(".box", "")

        # Create new or use existing repository based by their metadata
        r = VRepository(name, self.settings)

        img = VMetadataImage(
            name=name,
            description=desc,
            versions=[VMetadataVersion(
                version=version,
                providers=[VMetadataProvider(
                    name=provider
                )]
            )]
        )

        r.add(src, img)

    def list(self, name=None):
        """
        Provides list of the repositories on the storage

        :param name: identifier of image (optional)
        :type name: str
        :return: list of repositories
        """

        if name:
            repos = [VRepository(name, self.settings)]
        else:
            repos = [VRepository(d, self.settings)
                     for d in VStorage.list_dirs(self.settings.storage_path)
                     ]

        return repos

    def remove(self, name, version):
        """
        Removes repository or particular image from the repository

        :param name: identified of the image
        :param version: version of the image
        """

        r = VRepository(name, self.settings)

        r.remove(version)
