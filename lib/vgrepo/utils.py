import collections
import sys
import datetime

try:
    import json
except ImportError:
    import simplejson as json


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
