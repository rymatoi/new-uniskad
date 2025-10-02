import ast
import json
from typing import Any

from PySide2.QtCore import QSettings, QByteArray, qUncompress


class UserSettings:

    ORGANIZATION = "Uniskad"
    APPLICATION = "NewUniskad"

    BINARY_PREFIX = "b64:"
    LIST_PREFIX = "json:"

    def __init__(self):
        self._settings = QSettings(self.ORGANIZATION, self.APPLICATION)
        self._cache = {}
        self.load_settings()

    @staticmethod
    def _attr_name(key: str) -> str:
        return key.replace('/', '_')

    @classmethod
    def _decode_binary_string(cls, value: str) -> QByteArray:
        if not value:
            return QByteArray()

        if value.startswith(cls.BINARY_PREFIX):
            payload = value[len(cls.BINARY_PREFIX):]
        elif value.startswith('@ByteArray(') and value.endswith(')'):
            payload = value[len('@ByteArray('):-1]
        elif value.startswith('@Variant(') and value.endswith(')'):
            return cls._decode_binary_string(value[len('@Variant('):-1])
        elif value.startswith('z:'):
            payload = value[2:]
            try:
                compressed = QByteArray.fromBase64(payload.encode('ascii'))
                decompressed = qUncompress(compressed)
                if decompressed.isNull():
                    return QByteArray()
                result = QByteArray()
                result.append(decompressed)
                return result
            except Exception:
                return QByteArray()
        else:
            payload = value

        try:
            return QByteArray.fromBase64(payload.encode('ascii'))
        except Exception:
            return QByteArray()

    @classmethod
    def _encode_value(cls, value: Any) -> Any:
        if isinstance(value, QByteArray):
            return cls.BINARY_PREFIX + bytes(value.toBase64()).decode('ascii')
        if isinstance(value, (bytes, bytearray)):
            encoded = QByteArray(value).toBase64().data().decode('ascii')
            return cls.BINARY_PREFIX + encoded
        if isinstance(value, (list, tuple, set)):
            return cls.LIST_PREFIX + json.dumps(list(value))
        return value

    @classmethod
    def _decode_value(cls, value: Any) -> Any:
        if isinstance(value, QByteArray):
            return QByteArray(value)
        if isinstance(value, (bytes, bytearray)):
            return QByteArray(value)
        if isinstance(value, str):
            if value.startswith(cls.BINARY_PREFIX) or value.startswith('@ByteArray(') or \
                    value.startswith('@Variant(') or value.startswith('z:'):
                return cls._decode_binary_string(value)
            if value.startswith(cls.LIST_PREFIX):
                try:
                    return json.loads(value[len(cls.LIST_PREFIX):])
                except json.JSONDecodeError:
                    return value
            if value and value[0] in '[({' and value[-1] in '])}':
                try:
                    return ast.literal_eval(value)
                except (ValueError, SyntaxError):
                    return value
        return value

    def _store_decoded(self, name: str, value: Any) -> None:
        attr_name = self._attr_name(name)
        self._cache[name] = value
        setattr(self, attr_name, value)

    def update(self):
        self.load_settings()

    def load_settings(self):
        self._cache.clear()
        for key in self._settings.allKeys():
            decoded = self._decode_value(self._settings.value(key))
            self._store_decoded(key, decoded)

    def get(self, name: str, default: Any = None):
        attr_name = self._attr_name(name)
        if hasattr(self, attr_name):
            return getattr(self, attr_name)

        value = self._settings.value(name, default)
        if value is None:
            return default

        decoded = self._decode_value(value)
        self._store_decoded(name, decoded)
        return decoded

    def get_bytes(self, name: str) -> QByteArray:
        value = self.get(name)
        if isinstance(value, QByteArray):
            return QByteArray(value)
        if isinstance(value, (bytes, bytearray)):
            return QByteArray(value)
        if isinstance(value, str):
            return self._decode_binary_string(value)
        return QByteArray()

    def set(self, name: str, value: Any):
        encoded = self._encode_value(value)
        self._settings.setValue(name, encoded)
        decoded = self._decode_value(encoded)
        self._store_decoded(name, decoded)
        self._settings.sync()

    def remove(self, name: str) -> None:
        self._settings.remove(name)
        attr_name = self._attr_name(name)
        if hasattr(self, attr_name):
            delattr(self, attr_name)
        self._cache.pop(name, None)
        self._settings.sync()
