import json
from vgrepo.utils import VJSONEncoder


class VMetadataObject(object):

    def __repr__(self):
        return "{cls}::{obj}".format(cls=self.__class__.__name__, obj=self.to_json())

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __str__(self):
        return "{cls}::".format(cls=self.__class__.__name__) + str(self.__dict__)

    def json_repr(self):
        data = {}
        for k, v in vars(self).items():
            data.update(dict({k: v}))

        return data

    @classmethod
    def from_json(cls, attributes):
        attr = {}
        for k, v in attributes.items():
            attr.update(dict({k: v}))

        return cls(**attr)

    def to_json(self):
        return json.dumps(
            self.json_repr(),
            cls=VJSONEncoder,
            indent=4, sort_keys=True
        )
