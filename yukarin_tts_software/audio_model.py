from dataclasses import dataclass, fields
from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

from PySide2.QtCore import Qt
from PySide2.QtGui import QStandardItem, QStandardItemModel

temp_dir = TemporaryDirectory()


@dataclass
class AudioItem:
    text: str
    playing: bool = False

    def generate_unique_audio_path(self):
        name = sha256(self.text.encode()).hexdigest()
        return Path(temp_dir.name).joinpath(f"{name}.wav")


class AudioModel(QStandardItemModel):
    def __init__(self):
        super().__init__(parent=None)

        self.role_to_key = {
            Qt.UserRole + i: f.name for i, f in enumerate(fields(AudioItem))
        }
        self.key_to_role = {key: role for role, key in self.role_to_key.items()}
        self.setItemRoleNames(
            {role: key.encode() for role, key in self.role_to_key.items()}
        )

    def append_item(self, audio_item: AudioItem):
        item = QStandardItem()
        for role, key in self.role_to_key.items():
            item.setData(getattr(audio_item, key), role)
        self.appendRow(item)

    def fetch_item(self, index: int):
        item = self.item(index)
        data = {}
        for role, key in self.role_to_key.items():
            data[key] = item.data(role)
        return AudioItem(**data)

    def modify_item(self, index: int, key: str, value: Any):
        item = self.item(index)
        item.setData(value, self.key_to_role[key])

    def remove_item(self, index: int):
        self.removeRow(index)

    def get_data(self, index: int, key: str):
        item = self.item(index)
        return item.data(self.key_to_role[key])
