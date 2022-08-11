import json
import types
from abc import ABC

from django.core import serializers
from django.db import models
from django.core.serializers.json import DjangoJSONEncoder


def _objectify(s):
    if isinstance(s, str):
        return json.loads(s)

    return s


class DjangoModelJSONEncoder(DjangoJSONEncoder):

    def encode(self, o):
        if isinstance(o, models.Model):
            return serializers.serialize("json", [o])

        return super().default(o)


class DjangoModelJSONDecoder(json.JSONDecoder):

    def decode(self, json_string, **kwargs):
        if "\"model\"" in json_string:
            decoded = serializers.deserialize("json", json_string)
            if isinstance(decoded, types.GeneratorType):
                decoded_list = list(item.object for item in decoded)
                if len(decoded_list) == 1:
                    return decoded_list[0]
            return decoded
        return super().decode(json_string, **kwargs)


class SimpleJSONEncoder(ABC, json.JSONEncoder):
    type = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        assert self.type is not None

    def default(self, o):
        if not hasattr(o, '__dict__'):
            return super().default()
        res = dict(**o.__dict__)
        res['__type__'] = self.type_name()
        return res

    def type_name(self):
        return self.type.__name__


class SimpleJSONDecoder(ABC, json.JSONDecoder):

    type = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        assert self.type is not None

    def decode(self, json_string, **kwargs):
        o = _objectify(json_string)
        if '__type__' in o and self.type_name() == o['__type__']:
            o.pop('__type__')
            return self.type(**o)
        return super().decode(o, **kwargs)

    def type_name(self):
        return self.type.__name__
