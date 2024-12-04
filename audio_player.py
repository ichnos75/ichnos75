import sys
import io
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QProgressBar, 
                             QFileDialog, QLabel, QHBoxLayout, QSizePolicy, QListWidget, QListWidgetItem, QCheckBox)
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtCore import QUrl, Qt
from PyQt5.QtGui import QFont
from Crypto.Cipher import AES

class AudioPlayer(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Audio Player")
        self.setGeometry(100, 100, 600, 400)

        self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.StreamPlayback)
        self.initUI()

    def initUI(self):
        self.playButton = QPushButton("Play")
        self.stopButton = QPushButton("Stop")
        self.pauseButton = QPushButton("Pause")
        self.nextButton = QPushButton("Next")
        self.previousButton = QPushButton("Previous")
        self.loadButton = QPushButton("Load File or Folder")
        self.saveButton = QPushButton("Save Decrypted File")
        self.fileList = QListWidget()
        
        self.fileNameLabel = QLabel("No file loaded")
        self.fileNameLabel.setFont(QFont("Arial", 12))
        self.fileNameLabel.setStyleSheet("background-color: lightgreen; border-radius: 10px; padding: 4px;")
        self.fileNameLabel.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.fileNameLabel.setAlignment(Qt.AlignCenter)

        self.progressBar = QProgressBar(self)
        self.progressBar.setGeometry(30, 40, 200, 25)

        layout = QVBoxLayout()
        layout.addWidget(self.progressBar)
        layout.addWidget(self.playButton)
        layout.addWidget(self.stopButton)
        layout.addWidget(self.pauseButton)
        layout.addWidget(self.nextButton)
        layout.addWidget(self.previousButton)
        layout.addWidget(self.loadButton)
        layout.addWidget(self.saveButton)
        layout.addWidget(self.fileList)

        fileStatusLayout = QHBoxLayout()
        fileStatusLayout.addWidget(self.fileNameLabel)
        fileStatusLayout.setAlignment(Qt.AlignCenter)
        layout.addLayout(fileStatusLayout)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.playButton.clicked.connect(self.playAudio)
        self.stopButton.clicked.connect(self.stopAudio)
        self.pauseButton.clicked.connect(self.pauseAudio)
        self.nextButton.clicked.connect(self.nextAudio)
        self.previousButton.clicked.connect(self.previousAudio)
        self.loadButton.clicked.connect(self.loadFilesOrFolder)
        self.saveButton.clicked.connect(self.saveDecryptedFile)

        self.decrypted_data = None
        self.files = []

    def playAudio(self):
        selected_items = self.fileList.selectedItems()
        if selected_items:
            self.decryptAndLoad(selected_items[0].text())
            self.mediaPlayer.play()

    def stopAudio(self):
        self.mediaPlayer.stop()

    def pauseAudio(self):
        self.mediaPlayer.pause()

    def nextAudio(self):
        # Implement next audio logic
        pass

    def previousAudio(self):
        # Implement previous audio logic
        pass

    def loadFilesOrFolder(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileDialog = QFileDialog()
        fileDialog.setFileMode(QFileDialog.ExistingFiles)
        fileDialog.setOptions(options)
        fileDialog.setNameFilter("Audio Files (*.wav)")
        fileDialog.setViewMode(QFileDialog.Detail)
        if fileDialog.exec_():
            files = fileDialog.selectedFiles()
            if len(files) == 1 and os.path.isdir(files[0]):
                files = [os.path.join(files[0], f) for f in os.listdir(files[0]) if f.endswith('.wav')]
            self.files = files
            self.fileList.clear()
            for file in self.files:
                item = QListWidgetItem(file)
                checkbox = QCheckBox()
                checkbox.stateChanged.connect(lambda state, f=file: self.onCheckboxStateChanged(state, f))
                self.fileList.addItem(item)
                self.fileList.setItemWidget(item, checkbox)

    def onCheckboxStateChanged(self, state, file_path):
        if state == Qt.Checked:
            for i in range(self.fileList.count()):
                item = self.fileList.item(i)
                checkbox = self.fileList.itemWidget(item)
                if checkbox and checkbox != self.sender():
                    checkbox.setChecked(False)
            self.decryptAndLoad(file_path)

    def decryptAndLoad(self, file_path):
        key = b'\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0A\x0B\x0C\x0D\x0E\x0F\x10\x11\x12\x13\x14\x15\x16\x17\x18\x19\x1A\x1B\x1C\x1D\x1E\x1F'
        iv = b'\xA0\xB1\xC2\xD3\xE4\xF5\xA6\xB7\xC8\xD9\xE0\xF1\xA2\xB3\xC4\xD5'

        cipher = AES.new(key, AES.MODE_CBC, iv)

        with open(file_path, "rb") as encrypted_file:
            encrypted_data = encrypted_file.read()
            decrypted_data = cipher.decrypt(encrypted_data)

            # Skip the first 32 bytes of the decrypted data
            self.decrypted_data = decrypted_data[32:]

            audio_data = io.BytesIO(self.decrypted_data)
            audio_data.seek(0)

            url = QUrl.fromLocalFile(file_path)
            self.mediaPlayer.setMedia(QMediaContent(url))

            self.fileNameLabel.setText(f"Loaded file: {os.path.basename(file_path)}")

    def saveDecryptedFile(self):
        if self.decrypted_data:
            save_path, _ = QFileDialog.getSaveFileName(self, "Save Decrypted Audio File", "", "Audio Files (*.wav)")
            if save_path:
                with open(save_path, "wb") as audio_file:
                    audio_file.write(self.decrypted_data)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    player = AudioPlayer()
    player.show()
    sys.exit(app.exec_())
