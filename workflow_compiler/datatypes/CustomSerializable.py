from typing import *
import json
from datetime import datetime
import io

class CustomSerializable:
    def _json_dict(self) -> Dict:
        dict = {k: v for k, v in self.__dict__.items() if v is not None}
        return dict

    def to_json(self, indent: int = None) -> str:
        return self._custom_to_json(indent)
    
    def _custom_to_json(self, indent: int = None) -> str:
        return json.dumps(self._json_dict(), default = CustomSerializable._custom_default, indent=indent)

    def write_json(self, file: io.TextIOBase, indent=None):
        json.dump(self._json_dict(), file, indent=indent, default = CustomSerializable._custom_default)

    @staticmethod
    def _custom_default(o: any) -> Dict:
        
        if isinstance(o, CustomSerializable):
            return o._json_dict()

        if isinstance(o, datetime):
            return o.isoformat()

        return o.__dict__
    
    @staticmethod
    def write_json_native(obj: List, file: io.TextIOBase, indent=None):
        json.dump(obj, file, indent=indent, default = CustomSerializable._custom_default)