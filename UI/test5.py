import sys
from PyQt6.QtCore import QUrl
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtWebEngineWidgets import QWebEngineView


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Initialize the Google Maps WebView
        self.map_view = QWebEngineView()
        self.setCentralWidget(self.map_view)

        # Load the Google Maps webpage
        self.load_google_maps()

    def load_google_maps(self):
        # Load the Google Maps webpage
        url = "http://127.0.1.1:5500/Website%20Tracking/index.html"
        self.map_view.load(QUrl(url))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
