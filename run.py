import os
import platform
import sys
from pathlib import Path
from tempfile import NamedTemporaryFile

import pyopenjtalk
import soundfile
from PySide2.QtCore import QSettings, QUrl
from PySide2.QtGui import QGuiApplication, QIcon
from PySide2.QtMultimedia import QMediaPlayer
from PySide2.QtQml import QQmlApplicationEngine, QQmlContext
from PySide2.QtQuickControls2 import QQuickStyle
from PySide2.QtWidgets import QApplication, QUndoCommand, QUndoStack, QUndoView

from yukarin_tts_software.audio_model import AudioItem, AudioModel
from yukarin_tts_software.command import (
    AppendAudioItemCommand,
    ModifyAudioItemCommand,
    ThreadCommand,
)
from yukarin_tts_software.thread import AudioSynthesisAndPlayThread

if __name__ == "__main__":
    app = QApplication()

    engine = QQmlApplicationEngine()

    audio_model = AudioModel()
    audio_model.append_item(AudioItem(text="テキスト１"))
    audio_model.append_item(AudioItem(text="テキスト２"))
    audio_model.append_item(AudioItem(text="テキスト３"))

    engine.setInitialProperties({"audioModel": audio_model})
    engine.load("view.qml")

    undo_stack = QUndoStack()

    rootObjects = engine.rootObjects()
    window = rootObjects[0]

    undo_view = QUndoView(undo_stack)

    player = QMediaPlayer()

    def play(index: int):
        audio_item = audio_model.fetch_item(index)
        thread = AudioSynthesisAndPlayThread(audio_item=audio_item, player=player)

        def reportPath(path: str):
            player.setMedia(QUrl.fromLocalFile(str(path)))
            player.play()

        thread.reportPath.connect(reportPath)

        thread.started.connect(lambda: audio_model.modify_item(index, "playing", True))
        thread.finished.connect(
            lambda: audio_model.modify_item(index, "playing", False)
        )

        command = ThreadCommand(thread)
        undo_stack.push(command)

    def addAudioItem():
        command = AppendAudioItemCommand(
            audio_model=audio_model, audio_item=AudioItem(text="ほげ")
        )
        undo_stack.push(command)

    def modifyAudioItem(index: int, key: str, value: str):
        command = ModifyAudioItemCommand(
            audio_model=audio_model, index=index, key=key, value=value
        )
        undo_stack.push(command)

    def undo():
        for _ in range(1000):
            if (
                undo_stack.index() > 0
                and undo_stack.command(undo_stack.index() - 1).isObsolete()
            ):
                undo_stack.undo()
            else:
                undo_stack.undo()
                break
        else:
            raise NotImplementedError()

    def redo():
        undo_stack.redo()

    def showUndoStack():
        undo_view.show()

    window.play.connect(play)
    window.addAudioItem.connect(addAudioItem)
    window.modifyAudioItem.connect(modifyAudioItem)
    window.undo.connect(undo)
    window.redo.connect(redo)
    window.showUndoStack.connect(showUndoStack)

    sys.exit(app.exec_())
