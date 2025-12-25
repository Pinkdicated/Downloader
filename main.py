import sys
import subprocess
import threading
import urllib.request
from pathlib import Path

from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QLineEdit,
    QPushButton,
    QLabel,
)
from PyQt6.QtCore import Qt


# -----------------------------
# Configuration
# -----------------------------
BIN_DIR = Path("bin")

FILES = {
    "ffmpeg.exe": "https://github.com/Pinkdicated/Mirror/raw/refs/heads/main/ffmpeg.exe",
    "node.exe": "https://github.com/Pinkdicated/Mirror/raw/refs/heads/main/node.exe",
    "yt-dlp.exe": "https://github.com/Pinkdicated/Mirror/raw/refs/heads/main/yt-dlp.exe",
}


# -----------------------------
# Helper functions
# -----------------------------
def ensure_bin_and_files(status_callback, ready_callback):
    BIN_DIR.mkdir(exist_ok=True)

    for filename, url in FILES.items():
        file_path = BIN_DIR / filename
        if not file_path.exists():
            status_callback(f"Downloading {filename}...")
            urllib.request.urlretrieve(url, file_path)

    status_callback("Ready.")
    ready_callback()


def run_yt_dlp(url, status_callback):
    command = [
        str(BIN_DIR / "yt-dlp.exe"),
        "--ffmpeg-location",
        str(BIN_DIR / "ffmpeg.exe"),
        "--js-runtimes",
        f"node:{BIN_DIR / 'node.exe'}",
        url,
    ]

    status_callback("Downloading...")
    try:
        subprocess.run(command, check=True)
        status_callback("Download finished.")
    except subprocess.CalledProcessError:
        status_callback("Error during download.")


# -----------------------------
# Main Window
# -----------------------------
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("YouTube Downloader")
        self.setFixedSize(420, 180)

        layout = QVBoxLayout()
        layout.setSpacing(12)

        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Enter YouTube URL")
        self.url_input.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.status_label = QLabel("Initializing...")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.download_button = QPushButton("Download")
        self.download_button.setEnabled(False)  # 🔒 Disabled until ready
        self.download_button.clicked.connect(self.start_download)

        layout.addWidget(self.url_input)
        layout.addWidget(self.status_label)
        layout.addWidget(self.download_button)

        self.setLayout(layout)

        # Start initialization thread
        threading.Thread(
            target=ensure_bin_and_files,
            args=(self.set_status, self.enable_download),
            daemon=True,
        ).start()

    def set_status(self, text):
        self.status_label.setText(text)

    def enable_download(self):
        self.download_button.setEnabled(True)

    def start_download(self):
        url = self.url_input.text().strip()
        if not url:
            self.set_status("Please enter a URL.")
            return

        self.download_button.setEnabled(False)

        threading.Thread(
            target=self._download_thread,
            args=(url,),
            daemon=True,
        ).start()

    def _download_thread(self, url):
        run_yt_dlp(url, self.set_status)
        self.download_button.setEnabled(True)


# -----------------------------
# Dark Theme
# -----------------------------
def apply_dark_theme(app):
    app.setStyleSheet(
        """
        QWidget {
            background-color: #121212;
            color: #ffffff;
            font-size: 14px;
        }

        QLineEdit {
            background-color: #1e1e1e;
            border: 1px solid #333;
            border-radius: 6px;
            padding: 8px;
        }

        QPushButton {
            background-color: #2d89ef;
            border: none;
            border-radius: 6px;
            padding: 10px;
            font-weight: bold;
        }

        QPushButton:disabled {
            background-color: #555555;
        }

        QPushButton:hover:!disabled {
            background-color: #1b5fa7;
        }

        QPushButton:pressed:!disabled {
            background-color: #174a82;
        }
        """
    )


# -----------------------------
# Entry Point
# -----------------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    apply_dark_theme(app)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())
