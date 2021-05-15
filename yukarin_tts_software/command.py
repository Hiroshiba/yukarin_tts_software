from PySide2.QtWidgets import QUndoCommand

from yukarin_tts_software.audio_model import AudioItem, AudioModel
from yukarin_tts_software.thread import AudioSynthesisController


class AppendAudioItemCommand(QUndoCommand):
    def __init__(self, audio_model: AudioModel, audio_item: AudioItem):
        super().__init__()

        self.audio_model = audio_model
        self.audio_item = audio_item

        self.setText(str(self))

        self.index = audio_model.rowCount()

    def __repr__(self):
        return (
            "<AppendAudioItemCommand "
            f"audio_model={self.audio_model} "
            f"audio_item={self.audio_item}>"
        )

    def redo(self):
        self.audio_model.append_item(self.audio_item)

    def undo(self):
        self.audio_model.remove_item(self.index)


class ModifyAudioItemCommand(QUndoCommand):
    def __init__(self, audio_model: AudioModel, index: int, key: str, value: str):
        super().__init__()

        self.audio_model = audio_model
        self.index = index
        self.key = key
        self.value = value

        self.setText(str(self))

        self.before_value = None

    def __repr__(self):
        return (
            "<ModifyAudioItemCommand "
            f"audio_model={self.audio_model} "
            f"index={self.index} "
            f"key={self.key} "
            f"value={self.value}>"
        )

    def redo(self):
        self.before_value = self.audio_model.get_data(self.index, self.key)
        self.audio_model.modify_item(index=self.index, key=self.key, value=self.value)

    def undo(self):
        self.audio_model.modify_item(
            index=self.index, key=self.key, value=self.before_value
        )
