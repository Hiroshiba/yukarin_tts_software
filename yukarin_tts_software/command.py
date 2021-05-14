from PySide2.QtCore import QThread, Slot
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


class AudioSynthesisCommand(QUndoCommand):
    def __init__(
        self, controller: AudioSynthesisController, audio_model: AudioModel, index: int
    ):
        super().__init__(parent=None)

        self.controller = controller
        self.index = index

        self.setText(str(self))

        self.audio_item = audio_model.fetch_item(index)

    def __repr__(self):
        return f"<AudioSynthesisCommand index={self.index}>"

    @property
    def reportPath(self):
        return self.controller.reportPath

    def redo(self):
        text = self.audio_item.text
        path = self.audio_item.generate_unique_audio_path()
        if not path.exists():
            self.controller.synthesis(text, str(path))
        else:
            self.reportPath.emit(str(path))

        self.setObsolete(True)


class ThreadCommand(QUndoCommand):
    def __init__(self, thread: QThread):
        super().__init__(parent=None)

        self.thread = thread

        self.setText(str(self))

        thread.finished.connect(self.finished)

    def __repr__(self):
        return "<ThreadCommand>"

    @Slot()
    def finished(self):
        self.setObsolete(True)

    def redo(self):
        self.thread.start()

    def undo(self):
        if not self.thread.isFinished():
            self.thread.terminate()
            self.thread.wait()

        self.setObsolete(True)
