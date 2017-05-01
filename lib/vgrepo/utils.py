import collections
import sys
import os
import datetime
import hashlib
import yaml

try:
    import json
except ImportError:
    import simplejson as json

SHA1_BUFFER_SIZE = 65536


class VJSONEncoder(json.JSONEncoder):

    @staticmethod
    def is_string(obj):
        is_python3 = sys.version_info[0] == 3
        string_types = str if is_python3 else basestring
        return isinstance(obj, string_types)

    def default(self, obj):
        if hasattr(obj, 'json_repr'):
            return self.default(obj.json_repr())

        if isinstance(obj, datetime.datetime):
            return obj.strftime('%Y-%m-%dT%H:%M:%S.%fZ')

        if isinstance(obj, collections.Iterable) and not self.is_string(obj):
            try:
                data = {}
                for k, v in obj.items():
                    data.update(dict({k: self.default(v)}))
                return data
            except AttributeError:
                return [self.default(e) for e in obj]

        return obj


def get_sha1_checksum(path):
    sha1 = None

    try:
        sha1 = hashlib.sha1()
        with open(path, 'r') as stream:
            while True:
                chunk = stream.read(SHA1_BUFFER_SIZE)
                if not chunk:
                    break
                sha1.update(chunk)
    except [OSError, IOError]:
        print("Error: unable to read file {0}".format(path))

    return sha1.hexdigest() if sha1 else sha1


def load_yaml_config(cnf):
    try:
        with open(cnf, 'r') as s:
            return yaml.load(s)
    except (yaml.YAMLError, IOError) as e:
        print(e)

    return False


def list_dirs(path):
    dirs = []
    try:
        dirs = [d for d in os.listdir(path)
                if os.path.isdir(os.path.join(path, d))
                ]
    except [OSError, IOError]:
        print("Error: unable to read {0}".format(path))

    return dirs
