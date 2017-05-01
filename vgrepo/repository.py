#!/usr/bin/env python
# encoding: utf8

import os
import shutil
import json

from .utils import list_dirs, load_yaml_config, get_sha1_checksum

from .vmetadata.vbox import VMetadataBox, VMetadataVersion, VMetadataProvider

from clint.textui import puts, colored, min_width


class VRepository:

    box_name_fmt = "{box_name}-{box_version}.box"
    meta_name_fmt = "{box_name}.json"
    box_url_fmt = "{repo_url}/{box_name}/{box_name}-{box_version}.box"
    meta_url_fmt = "{repo_url}/{box_name}/metadata/{box_name}.json"

    def get_repo_url(self):
        return self.settings.get('storage').get('url').strip('/')

    def get_repo_path(self):
        return self.settings.get('storage').get('path') or \
               os.path.dirname(os.path.abspath(__file__))

    def get_metadata_url(self, box):
        return self.meta_url_fmt.format(
            repo_url=self.get_repo_url(),
            box_name=box
        )

    def get_metadata_path(self, box):
        return os.path.join(
            self.get_box_path(box),
            "metadata"
        )

    def get_metadata_fullpath(self, box):
        return os.path.join(
            self.get_metadata_path(box),
            self.meta_name_fmt.format(
                box_name=box
            )
        )

    @staticmethod
    def load_meta(path):
        return VRepository.parse_metadata(path, VMetadataBox)

    @staticmethod
    def dump_meta(path, meta):
        try:
            with open(path, 'w') as stream:
                stream.write(meta.to_json())
            return True
        except (OSError, IOError):
            puts("Error: unable to write metadata to '{0}'".format(path))

        return False

    @staticmethod
    def parse_metadata(cnf, cls, is_list=False):
        with open(cnf, 'r') as stream:
            target = json.load(stream)
            if is_list:
                return [cls.from_json(resource) for resource in target]
            else:
                return cls.from_json(target)

    def dump_box_meta(self, meta):
        path = self.get_metadata_path(meta.name)

        if not os.path.isdir(path):
            os.makedirs(path)

        return self.dump_meta(self.get_metadata_fullpath(meta.name), meta)

    def load_box_meta(self, box):
        if self.has_metadata(box):
            meta = self.load_meta(self.get_metadata_fullpath(box))
        else:
            meta = None

        return meta

    def filter_box_meta(self, box, version=None):
        meta = self.load_box_meta(box) if self.is_box_exist(box, version) else None

        if isinstance(meta, VMetadataBox):
            meta.versions = filter(lambda x: x.version != version, meta.versions)

        return meta

    def delete_box_meta(self, box):
        is_deleted = False
        path = self.get_metadata_fullpath(box)
        try:
            if self.has_metadata(box):
                os.remove(path)
                is_deleted = True
        except (OSError, IOError):
            puts("Error: unable to delete metadata {0}".format(path))

        return is_deleted

    def has_metadata(self, box):
        has_metadata = False
        try:
            path = self.get_metadata_fullpath(box)
            has_metadata = os.path.isfile(path)
        except (OSError, IOError):
            puts("Error: unable to read metadata for '{0}'".format(box))

        return has_metadata

    def get_box_url(self, box, version):
        return self.box_url_fmt.format(
            repo_url=self.get_repo_url(),
            box_name=box,
            box_version=version
        )

    def get_box_path(self, box):
        return os.path.join(self.get_repo_path(), box)

    def get_box_fullpath(self, box, version):
        return os.path.join(
            self.get_box_path(box),
            self.box_name_fmt.format(
                box_name=box,
                box_version=version
            )
        )

    def has_box(self, box, version=None):
        has_box = False
        try:
            if version:
                path = self.get_box_fullpath(box, version)
                has_box = os.path.isfile(path)
            else:
                path = self.get_box_path(box)
                has_box = os.path.isdir(path)
        except (OSError, IOError):
            puts("Error: unable to find box with name '{0}'".format(box))

        return has_box

    def is_box_exist(self, box, version=None):
        return self.has_metadata(box) and self.has_box(box, version)

    def has_version(self, box, version):
        meta = self.load_box_meta(box)
        has_version = None
        if isinstance(meta, VMetadataBox):
            has_version = filter(lambda x: x.version == version, meta.versions)

        return True if has_version else False

    @staticmethod
    def add_box(src_path, dest_path):
        is_added = False

        try:
            box_path = os.path.dirname(dest_path)
            if not os.path.isdir(box_path):
                os.makedirs(box_path)
            shutil.copy2(src_path, dest_path)
            is_added = True
        except (OSError, IOError):
            puts("Error: unable to move {0} to {1}".format(
                src_path,
                dest_path
            ))

        return is_added

    def list_boxes(self):
        boxes = [self.load_box_meta(b)
                 for b in list_dirs(self.get_repo_path())
                 if self.is_box_exist(b)]

        return boxes

    def delete_box(self, box, version):
        is_deleted = False
        path = self.get_box_fullpath(box, version)

        try:
            if self.is_box_exist(box, version):
                os.remove(path)
                is_deleted = True
        except (OSError, IOError):
            puts("Error: unable to delete {0}".format(path))

        return is_deleted

    def __init__(self, cnf):
        self.settings = load_yaml_config(cnf)

    def add(self, src_path, name='', version='', description=''):
        box_name = name if name \
            else os.path.basename(src_path).replace(".box", "")
        box_path = self.get_box_fullpath(box_name, version)

        box_meta = self.load_box_meta(box_name)
        if not box_meta:
            box_meta = VMetadataBox(
                name=box_name,
                description=description,
                versions=[]
            )

        box_version = VMetadataVersion(
            version=version,
            providers=[VMetadataProvider(
                name="virtualbox",
                checksum=get_sha1_checksum(src_path),
                checksum_type="sha1",
                url=self.get_box_url(box_name, version)
            )]
        )

        puts(min_width("\nChecking duplicated versions", 40), newline=False)
        if not self.has_version(box_name, version):
            puts(colored.green("done"))

            puts(min_width("Adding box to the repository", 40), newline=False)
            if self.add_box(src_path, box_path):
                puts(colored.green("done"))
            else:
                puts(colored.red("error"))

            puts(min_width("Updating metadata", 40), newline=False)
            box_meta.versions.insert(0, box_version)
            if self.dump_box_meta(box_meta):
                puts(colored.green("done"))
            else:
                puts(colored.red("error"))
        else:
            puts(colored.red("error"))
            return False

        return True

    def list(self):
        return self.list_boxes()

    def delete(self, box, version):

        meta = self.filter_box_meta(box, version)
        puts(min_width("\nChecking metadata", 40), newline=False)
        if meta:
            puts(colored.green("done"))

            puts(min_width("\nDeleting box", 40), newline=False)
            if self.delete_box(box, version):
                puts(colored.green("done"))
            else:
                puts(colored.red("error"))

            puts(min_width("Updating meta", 40), newline=False)
            if self.dump_box_meta(meta):
                puts(colored.green("done"))
            else:
                puts(colored.red("error"))
        else:
            puts(colored.red("error"))
            puts("\nError: box with the name {box_name} and version {box_version} does not exist".format(
                box_name=colored.cyan(box),
                box_version=colored.cyan(version)
            ))

        return False

    def kill(self, box):
        is_killed = False
        path = self.get_box_path(box)

        puts(min_width("Removing box collection", 40), newline=False)
        try:
            if self.is_box_exist(box):
                shutil.rmtree(path, ignore_errors=True)
            is_killed = True
            puts(colored.green("done"))
        except (OSError, IOError):
            puts(colored.red("error"))
            puts("\nError: unable to delete {0}".format(path))

        return is_killed
