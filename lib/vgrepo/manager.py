#!/usr/bin/env python
# encoding: utf8

import os

from .settings import VSettings
from .repository import VRepository
from .meta.images import VMetadataImage, VMetadataVersion, VMetadataProvider


class VRepositoryManager:

    @staticmethod
    def list_dirs(path):
        dirs = []
        try:
            dirs = [d for d in os.listdir(path)
                    if os.path.isdir(os.path.join(path, d))
                    ]
        except [OSError, IOError]:
            print("Error: unable to read {0}".format(path))

        return dirs

    def __init__(self, cnf):
        self.settings = VSettings(cnf)

    def add(self, src, name, version, desc='', provider='virtualbox'):
        if not name:
            name = os.path.basename(src).replace(".box", "")

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

        return True

    def list(self, name=None):
        if name:
            repos = [VRepository(name, self.settings)]
        else:
            repos = [VRepository(d, self.settings)
                     for d in VRepositoryManager.list_dirs(self.settings.storage_path)
                     ]

        return repos

    def remove(self, name, version):
        r = VRepository(name, self.settings)

        r.remove(version)

        return True
