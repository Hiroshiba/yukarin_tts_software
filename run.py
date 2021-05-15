import os
import platform
import sys
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Optional

import pyopenjtalk
import soundfile
from PySide2.QtCore import QSettings, QThread, QUrl, Slot
from PySide2.QtGui import QGuiApplication, QIcon
from PySide2.QtMultimedia import QMediaPlayer
from PySide2.QtQml import QQmlApplicationEngine, QQmlContext
from PySide2.QtQuickControls2 import QQuickStyle
from PySide2.QtWidgets import QApplication, QUndoCommand, QUndoStack, QUndoView

from yukarin_tts_software.audio_model import AudioItem, AudioModel
from yukarin_tts_software.command import AppendAudioItemCommand, ModifyAudioItemCommand
from yukarin_tts_software.thread import AudioSynthesisController

if __name__ == "__main__":
    app = QApplication()

    engine = QQmlApplicationEngine()

    audio_synthesis_controller = AudioSynthesisController()

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

    def convertAndPlay(index: int):
        audio_item = audio_model.fetch_item(index)

        def reportPath(path: str):
            audio_synthesis_controller.reportPath.disconnect(reportPath)
            player.setMedia(QUrl.fromLocalFile(path))
            play(index)

        audio_synthesis_controller.reportPath.connect(reportPath)

        text = audio_item.text
        path = audio_item.generate_unique_audio_path()
        audio_synthesis_controller.synthesis(text, str(path))

    def play(index: int):
        def stateChanged(state: QMediaPlayer.State):
            if state == QMediaPlayer.State.PlayingState:
                audio_model.modify_item(index, "playing", True)
            elif state == QMediaPlayer.State.StoppedState:
                player.stateChanged.disconnect(stateChanged)
                audio_model.modify_item(index, "playing", False)

        player.stateChanged.connect(stateChanged)
        player.play()

    def stop(index: int):
        player.stop()

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

    window.convertAndPlay.connect(convertAndPlay)
    # window.play.connect(play)
    window.stop.connect(stop)
    window.addAudioItem.connect(addAudioItem)
    window.modifyAudioItem.connect(modifyAudioItem)
    window.undo.connect(undo)
    window.redo.connect(redo)
    window.showUndoStack.connect(showUndoStack)

    sys.exit(app.exec_())
