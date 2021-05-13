import pyopenjtalk
import soundfile
from PySide2.QtCore import QThread, QUrl, Signal
from PySide2.QtMultimedia import QMediaPlayer

from yukarin_tts_software.audio_model import AudioItem


class AudioSynthesisAndPlayThread(QThread):

    reportPath = Signal(str)

    def __init__(self, audio_item: AudioItem, player: QMediaPlayer):
        super().__init__(parent=None)

        self.audio_item = audio_item
        self.player = player

    def run(self):
        path = self.audio_item.generate_unique_audio_path()
        if not path.exists():
            wave, sr = pyopenjtalk.tts(self.audio_item.text)
            wave /= 2 ** 16
            soundfile.write(path, wave, sr)

        # self.reportPath.emit(str(path))

        self.player.setMedia(QUrl.fromLocalFile(str(path)))
        self.player.play()

        self.player.
        playerを待つためにイベントループ作る？
