#!/usr/bin/env python
# encoding: utf8

import os
import shutil
import json
import hashlib

from copy import deepcopy
from packaging.version import Version
from .meta.images import VMetadataImage


class VRepository:

    SHA1_BUFFER_SIZE = 65536

    @property
    def is_empty(self):
        return self.meta.versions is None or self.meta.versions == []

    @property
    def has_meta(self):
        try:
            return os.path.isfile(self.meta_path)
        except (OSError, IOError):
            print("unable to read metadata for '{0}'".format(self.meta.name))

    def has_image(self, version=None):
        try:
            if version:
                path = self.get_image_path(version)
                return os.path.isfile(path)
            else:
                path = self.image_dir
                return os.path.isdir(path)
        except (OSError, IOError):
            print("Error: unable to read image '{0}'".format(self.meta.name))

    def is_exist(self, version=None):
        return self.has_meta and self.has_image(version)

    @property
    def meta_dir(self):
        return os.path.join(self.image_dir, "metadata")

    @property
    def meta_path(self):
        path_format = "{name}.json"

        return os.path.join(self.meta_dir, path_format.format(name=self.meta.name))

    @property
    def image_dir(self):
        return os.path.join(self.settings.repo_path, self.meta.name)

    def get_image_path(self, version):
        path_format = "{name}-{version}.box"

        return os.path.join(self.image_dir, path_format.format(name=self.meta.name, version=version))

    def get_image_url(self, version):
        url_format = "{url}/{name}/{name}-{version}.box"

        return url_format.format(url=self.settings.repo_url, name=self.meta.name, version=version)

    @staticmethod
    def get_sha1_checksum(path):
        sha1 = hashlib.sha1()

        try:
            with open(path, 'r') as stream:
                while True:
                    chunk = stream.read(VRepository.SHA1_BUFFER_SIZE)
                    if not chunk:
                        break
                    sha1.update(chunk)
        except [OSError, IOError]:
            print("Error: unable to read file {0}".format(path))

        return sha1.hexdigest() if sha1 else sha1

    def load_meta(self):
        if self.has_meta:
            return VRepository.parse_meta(self.meta_path, VMetadataImage)
        else:
            return VMetadataImage(name=self.meta.name)

    def dump_meta(self):
        path = self.meta_dir
        try:
            if not os.path.isdir(path):
                os.makedirs(path)

            with open(self.meta_path, 'w') as stream:
                stream.write(self.meta.to_json())
        except (OSError, IOError):
            print("Error: unable to write metadata to '{0}'".format(self.meta_path))
            return False

        return True

    @staticmethod
    def parse_meta(cnf, cls, is_list=False):
        with open(cnf, 'r') as stream:
            target = json.load(stream)
            if is_list:
                return [cls.from_json(resource) for resource in target]
            else:
                return cls.from_json(target)

    @staticmethod
    def is_equal_versions(cur, new):
        return Version(cur) == Version(new)

    @staticmethod
    def not_equal_versions(cur, new):
        return not VRepository.is_equal_versions(cur, new)

    def filter_versions(self, func, version=None):
        meta = deepcopy(self.meta)

        if not self.is_empty:
            meta.versions = filter(
                lambda x: func(x.version, version),
                self.meta.versions
            )

        return meta

    def remove_meta(self):
        try:
            if self.has_meta:
                os.remove(self.meta_path)
        except (OSError, IOError):
            print("Error: unable to delete metadata {0}".format(self.meta_path))
            return False

        return True

    def sync_meta(self, meta):
        self.meta = deepcopy(meta)

    def has_version(self, version):
        entries = self.filter_versions(VRepository.is_equal_versions, version)

        if entries.versions:
            return True
        else:
            return False

    def copy_image(self, src, version):
        try:
            if not os.path.isdir(self.image_dir):
                os.makedirs(self.image_dir)
            shutil.copy2(src, self.get_image_path(version))
            return True
        except (OSError, IOError):
            print("Error: unable to move {0} to {1}".format(src, self.get_image_path(version)))

        return False

    def remove_image(self, version):
        path = self.get_image_path(version)

        try:
            if self.is_exist(version):
                os.remove(path)
                return True
        except (OSError, IOError):
            print("Error: unable to delete {0}".format(path))

        return False

    def destroy_image(self):
        try:
            shutil.rmtree(self.image_dir, ignore_errors=True)
        except (OSError, IOError):
            print("Error: unable to delete {0} recursively".format(self.image_dir))
            return False

        return True

    def __init__(self, name, settings=None):
        self.settings = settings
        self.meta = VMetadataImage(name=name)

        self.meta = self.load_meta()

    def add(self, src, img):
        meta, image = deepcopy(self.meta), deepcopy(img)

        if self.is_empty:
            meta.description = img.description

        for v in image.versions:
            if not self.has_version(v.version):
                for p in v.providers:
                    p.checksum_type = "sha1"
                    p.checksum = VRepository.get_sha1_checksum(src)
                    p.url = self.get_image_url(v.version)

                meta.versions.append(v)
                self.copy_image(src, v.version)
                self.sync_meta(meta)
                self.dump_meta()

    def list(self):
        return self.meta.name

    def remove(self, version):
        meta = self.filter_versions(VRepository.not_equal_versions, version)
        self.remove_image(version)
        self.remove_meta()
        self.sync_meta(meta)

        if self.is_empty:
            self.destroy_image()
            self.meta = VMetadataImage(self.meta.name)
