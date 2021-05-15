import traceback
from pathlib import Path

import pyopenjtalk
import soundfile
from PySide2.QtCore import QObject, QThread, Signal, Slot


class AudioSynthesisWorker(QObject):
    reportPath = Signal(str)

    @Slot()
    def load(self):
        pass

    @Slot()
    def synthesis(self, text: str, outputPath: str):
        try:
            if Path(outputPath).exists():
                self.reportPath.emit(outputPath)
                return

            wave, sr = pyopenjtalk.tts(text)
            wave /= 2 ** 16
            soundfile.write(outputPath, wave, sr)

            self.reportPath.emit(outputPath)
        except:
            traceback.print_exc()

            self.reportPath.emit("")


class AudioSynthesisController(QObject):
    def __init__(self):
        super().__init__(parent=None)
        self.thread = QThread(parent=self)
        self.worker = AudioSynthesisWorker()

        self.thread.started.connect(self.worker.load)

        self.thread.start()

    @property
    def synthesis(self):
        return self.worker.synthesis

    @property
    def reportPath(self):
        return self.worker.reportPath
