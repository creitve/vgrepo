#!/usr/bin/env python
# coding: utf8

import hashlib
import json
import os
import shutil
from copy import deepcopy

from packaging.version import Version

from .meta.images import VMetadataImage


class VImageNotFound(Exception):

    def __init__(self, path):
        self.path = path


class VImageVersionFoundError(Exception):

    def __init__(self, name, version):
        self.name = name
        self.version = version


class VRepository:
    """
    Provides methods to manage repository in the storage
    """

    SHA1_BUFFER_SIZE = 65536

    @property
    def is_empty(self):
        """
        Returns is the repository empty (does not contain any versions) or not

        :return: bool
        """
        return self.meta.versions is None or self.meta.versions == []

    @property
    def has_meta(self):
        """
        Returns is the repository has metadata saved on the disk or not

        :return: bool
        """
        try:
            return os.path.isfile(self.meta_path)
        except (OSError, IOError):
            print("Error: unable to read metadata for '{0}'".format(self.meta.name))

    def has_image(self, version=None):
        """
        Returns is the image present or not by given version

        :param version: version of the image
        :return: bool
        """
        try:
            if version:
                path = self.get_image_path(version)
                return os.path.isfile(path)
            else:
                path = self.image_dir
                return os.path.isdir(path)
        except (OSError, IOError):
            print("Error: unable to read image '{0}'".format(self.meta.name))

        return False

    def is_exist(self, version=None):
        """
        Returns is the repository:
        a) Has their own metadata on the disk
        b) Has saved image file in the repository

        :param version: version of the image
        :return: bool
        """
        return self.has_meta and self.has_image(version)

    @property
    def meta_dir(self):
        """
        Returns metadata directory for the repository

        :return: str
        """
        return os.path.join(self.image_dir, "metadata")

    @property
    def meta_path(self):
        """
        Returns full metadata path for the repository

        :return:
        """
        path_format = "{name}.json"

        return os.path.join(self.meta_dir, path_format.format(name=self.meta.name))

    @property
    def image_dir(self):
        """
        Returns directory for the images of the repository

        :return: str
        """
        return os.path.join(self.settings.storage_path, self.meta.name)

    @property
    def repo_url(self):
        """
        Returns URL to the metadata file

        :return:
        """
        url_format = "{url}/{name}"

        return url_format.format(url=self.settings.storage_url, name=self.meta.name)

    def get_image_path(self, version):
        """
        Returns full path to the image

        :param version: version of the image
        :return: str
        """
        path_format = "{name}-{version}.box"

        return os.path.join(self.image_dir, path_format.format(name=self.meta.name, version=version))

    def get_image_url(self, version):
        """
        Returns direct URL to the image

        :param version: version of the image
        :return: str
        """
        url_format = "{url}/{name}-{version}.box"

        return url_format.format(url=self.repo_url, name=self.meta.name, version=version)

    @staticmethod
    def get_sha1_checksum(path):
        """
        Returns SHA1 string of the file by given path

        :param path: path to the hashed file
        :return:
        """
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
        """
        Loads or creates metadata for itself by given name

        :return:
        """
        if self.has_meta:
            return VRepository.parse_meta(self.meta_path, VMetadataImage)
        else:
            return VMetadataImage(name=self.meta.name)

    def dump_meta(self):
        """
        Saves metadata on the disk

        :return:
        """
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
        """
        Parse metadata on JSON format to the object

        :param cnf: path to JSON file
        :param cls: name of class to parse
        :param is_list: is the object list or not
        :return: instance of the class (cls)
        """
        with open(cnf, 'r') as stream:
            target = json.load(stream)
            if is_list:
                return [cls.from_json(resource) for resource in target]
            else:
                return cls.from_json(target)

    @staticmethod
    def is_equal_versions(first, second):
        """
        Returns are versions equal or not

        :param first: first version
        :param second: second version
        :return: bool
        """
        return Version(str(first)) == Version(str(second))

    @staticmethod
    def not_equal_versions(first, second):
        """
        Returns are version not equal or not

        :param first: first version
        :param second: second version
        :return: bool
        """
        return not VRepository.is_equal_versions(first, second)

    def filter_versions(self, func, version=None):
        """
        Returns list of images without versions by given function filter

        :param func: name of the filter function
        :param version: number of version
        :return:
        """
        meta = deepcopy(self.meta)

        if not self.is_empty:
            meta.versions = filter(
                lambda x: func(x.version, version),
                self.meta.versions
            )

        return meta

    def remove_meta(self):
        """
        Removes metadata from disk

        :return:
        """
        try:
            if self.has_meta:
                os.remove(self.meta_path)
        except (OSError, IOError):
            print("Error: unable to delete metadata {0}".format(self.meta_path))
            return False

        return True

    def sync_meta(self, meta):
        """
        Saves meta in memory by given copy

        :param meta: copied meta object
        :return:
        """
        self.meta = deepcopy(meta)

    def has_version(self, version):
        """
        Returns is the repository has version of the image

        :param version: version of the image
        :return:
        """
        entries = self.filter_versions(VRepository.is_equal_versions, version)

        if entries.versions:
            return True
        else:
            return False

    def copy_image(self, src, version):
        """
        Copies image to the repository's directory

        :param src: path to the original image file
        :param version: version of the image
        :return:
        """
        try:
            if not os.path.isdir(self.image_dir):
                os.makedirs(self.image_dir)
            if not os.path.isfile(src):
                raise VImageNotFound(src)

            shutil.copy2(src, self.get_image_path(version))
            return True
        except (OSError, IOError):
            print("Error: unable to move {0} to {1}".format(src, self.get_image_path(version)))

        return False

    def remove_image(self, version):
        """
        Removes image from the repository

        :param version: version of the image
        :return:
        """
        path = self.get_image_path(version)

        try:
            if self.is_exist(version):
                os.remove(path)
                return True
        except (OSError, IOError):
            print("Error: unable to delete {0}".format(path))

        return False

    def destroy(self):
        """
        Destroys all images from the repository

        :return:
        """
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
        """
        Adds image to the repository by given file and metadata

        :param src: source image
        :param img: image's metadata
        :return:
        """
        meta, image = deepcopy(self.meta), deepcopy(img)

        if self.is_empty:
            meta.description = image.description

        for v in image.versions:
            if not self.has_version(v.version):
                for p in v.providers:
                    p.name = p.name or "virtualbox"
                    p.checksum_type = "sha1"
                    p.checksum = VRepository.get_sha1_checksum(src)
                    p.url = self.get_image_url(v.version)

                meta.versions.append(v)
                self.copy_image(src, v.version)
                self.sync_meta(meta)
                self.dump_meta()
            else:
                raise VImageVersionFoundError(image.name, v.version)

        return True

    @property
    def info(self):
        """
        Returns metadata of the repository

        :return:
        """
        return self.meta

    def remove(self, version):
        """
        Removes image by given version

        :param version: version of the image
        :return:
        """
        meta = self.filter_versions(VRepository.not_equal_versions, version)

        self.remove_image(version)
        self.sync_meta(meta)

        if self.is_empty:
            self.remove_meta()
            self.destroy()
            self.meta = VMetadataImage(self.meta.name)
        else:
            self.dump_meta()

        return True
