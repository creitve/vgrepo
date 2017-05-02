#!/usr/bin/env python
# encoding: utf8

import os
import shutil
import json

from copy import deepcopy

from .utils import list_dirs, load_yaml_config, get_sha1_checksum

from .meta.images import VMetadataImage, VMetadataVersion, VMetadataProvider


class VImageAccessException(Exception):
    pass


class VMetaAccessException(Exception):
    pass


########################################################################################################################

class VRepository:

    @property
    def repo_url(self):

        return self.settings.get('storage').get('url').strip('/')

    @property
    def repo_path(self):
        return self.settings.get('storage').get('path') or os.path.dirname(os.path.abspath(__file__))

    @property
    def is_empty(self):
        return self.meta.versions is None

    @property
    def has_meta(self):
        try:
            path = self.meta_path
            return os.path.isfile(path)
        except (OSError, IOError):
            raise VMetaAccessException("unable to read metadata for '{0}'".format(self.meta.name))

    @property
    def meta_dir(self):
        return os.path.join(self.image_dir, "metadata")

    @property
    def meta_path(self):
        path_format = "{name}.json"

        return os.path.join(self.meta_dir, path_format.format(name=self.meta.name))

    @property
    def image_dir(self):
        return os.path.join(self.repo_path, self.meta.name)

    def image_path(self, version):
        path_format = "{name}-{version}.box"

        return os.path.join(
            self.image_dir,
            path_format.format(name=self.meta.name, version=version)
        )

    def get_image_url(self, version):
        url_format = "{url}/{name}/{name}-{version}.box"

        return url_format.format(url=self.repo_url, name=self.meta.name, version=version)

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

    def has_version(self, version):
        entries = filter(lambda x: x.version == version, self.meta.versions)

        if entries:
            return True
        else:
            return False

    def copy_image(self, src, version):
        try:
            if not os.path.isdir(self.image_dir):
                os.makedirs(self.image_dir)
            shutil.copy2(src, self.image_path(version))
            return True
        except (OSError, IOError):
            print("Error: unable to move {0} to {1}".format(src, self.image_path(version)))

        return False

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
                    p.checksum = get_sha1_checksum(src)
                    p.url = self.get_image_url(v.version)

                meta.versions.append(v)
                self.copy_image(src, v.version)
                self.save_meta(meta)

    def list(self):
        pass

    def remove(self):
        pass

    def destroy(self):
        pass

    def save_meta(self, meta):
        self.meta = deepcopy(meta)
        self.dump_meta()


########################################################################################################################

class VRepositoryManager:

    @property
    def repo_url(self):

        return self.settings.get('storage').get('url').strip('/')

    @property
    def repo_path(self):

        return self.settings.get('storage').get('path') or os.path.dirname(os.path.abspath(__file__))

    def get_meta_url(self, img):
        url_format = "{repo_url}/{img}/metadata/{img}.json"

        return url_format.format(repo_url=self.repo_url, img=img)

    def get_meta_dir(self, img):
        return os.path.join(self.get_image_dir(img), "metadata")

    def get_meta_path(self, img):
        path_format = "{name}.json"

        return os.path.join(self.get_meta_dir(img), path_format.format(name=img))

    @staticmethod
    def load_meta(path):

        return VRepositoryManager.parse_meta(path, VMetadataImage)

    @staticmethod
    def dump_meta(path, meta):
        try:
            with open(path, 'w') as stream:
                stream.write(meta.to_json())
        except (OSError, IOError):
            print("Error: unable to write metadata to '{0}'".format(path))
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

    def dump_image_meta(self, meta):
        path = self.get_meta_dir(meta.name)

        if not os.path.isdir(path):
            os.makedirs(path)

        return self.dump_meta(self.get_meta_path(meta.name), meta)

    def load_image_meta(self, img):
        if self.has_meta(img):
            meta = self.load_meta(self.get_meta_path(img))
        else:
            meta = None

        return meta

    def filter_image_meta(self, img, version=None):
        meta = self.load_image_meta(img) if self.is_image_exist(img, version) else None

        if isinstance(meta, VMetadataImage):
            meta.versions = filter(lambda x: x.version != version, meta.versions)

        return meta

    def delete_image_meta(self, img):
        is_deleted = False
        path = self.get_meta_path(img)
        try:
            if self.has_meta(img):
                os.remove(path)
                is_deleted = True
        except (OSError, IOError):
            print("Error: unable to delete metadata {0}".format(path))

        return is_deleted

    def has_meta(self, img):
        try:
            path = self.get_meta_path(img)
            return os.path.isfile(path)
        except (OSError, IOError):
            raise VMetaAccessException("unable to read metadata for '{0}'".format(img))

    def get_image_url(self, img, version):
        url_format = "{url}/{name}/{name}-{version}.box"

        return url_format.format(url=self.repo_url, name=img, version=version)

    def get_image_dir(self, img):
        return os.path.join(self.repo_path, img)

    def get_image_path(self, img, version):
        path_format = "{name}-{version}.box"

        return os.path.join(self.get_image_dir(img), path_format.format(name=img, version=version))

    def has_image(self, img, version=None):
        try:
            if version:
                path = self.get_image_path(img, version)
                return os.path.isfile(path)
            else:
                path = self.get_image_dir(img)
                return os.path.isdir(path)
        except (OSError, IOError):
            raise VImageAccessException("Error: unable to read image '{0}'".format(img))

    def is_image_exist(self, img, version=None):
        return self.has_meta(img) and self.has_image(img, version)

    def has_version(self, img, version):
        meta = self.load_image_meta(img)

        entries = filter(lambda x: x.version == version, meta.versions) if \
            isinstance(meta, VMetadataImage) else \
            None

        if entries:
            return True
        else:
            return False

    @staticmethod
    def add_image(src_path, dst_path):
        try:
            image_path = os.path.dirname(dst_path)
            if not os.path.isdir(image_path):
                os.makedirs(image_path)
            shutil.copy2(src_path, dst_path)
            return True
        except (OSError, IOError):
            print("Error: unable to move {0} to {1}".format(src_path, dst_path))

        return False

    def add_image_version(self, name='', desc='', version='', checksum=''):
        meta = self.load_image_meta(name)

        if not meta:
            meta = VMetadataImage(
                name=name,
                description=desc,
                versions=[]
            )

        meta.insert(0, VMetadataVersion(
            version=version,
            providers=[VMetadataProvider(
                name="virtualbox",
                checksum=checksum,
                checksum_type="sha1",
                url=self.get_image_url(name, version)
            )]
        ))

        return meta

    def list_images(self):
        return [self.load_image_meta(b) for b in list_dirs(self.repo_path) if self.is_image_exist(b)]

    def remove_image(self, img, version):
        path = self.get_image_path(img, version)

        try:
            if self.is_image_exist(img, version):
                os.remove(path)
                return True
        except (OSError, IOError):
            print("Error: unable to delete {0}".format(path))

        return False

    def __init__(self, cnf):
        self.settings = load_yaml_config(cnf)
        print self.settings
        repo = VRepository('powerbox', self.settings)

        image = VMetadataImage(
            name="powerbox",
            versions=[VMetadataVersion(
                version="0.0.2",
                providers=[VMetadataProvider(
                    name="virtualbox"
                )]
            )]
        )

        repo.add("images/centos7.box", image)
        # print repo.foo()

    def add(self, src, name='', version='', desc=''):
        if name:
            image_name = name
        else:
            image_name = os.path.basename(src).replace(".box", "")

        image_path = self.get_image_path(image_name, version)

        if not self.has_version(image_name, version):
            self.add_image(src, image_path)
            sha1_checksum = get_sha1_checksum(src)
            meta = self.add_image_version(
                name=image_name,
                desc=desc,
                version=version,
                checksum=sha1_checksum
            )
            self.dump_image_meta(meta)
        else:
            return False

        return True

    def list(self):
        return self.list_images()

    def remove(self, img, version):
        meta = self.filter_image_meta(img, version)

        if meta:
            self.remove_image(img, version)
            self.dump_image_meta(meta)
        else:
            return False

        return True

    def destroy(self, img):
        is_destroyed = False
        if img:
            path = self.get_image_dir(img)
            try:
                if self.is_image_exist(img):
                    shutil.rmtree(path, ignore_errors=True)
                is_destroyed = True
            except (OSError, IOError):
                return False

        return is_destroyed
