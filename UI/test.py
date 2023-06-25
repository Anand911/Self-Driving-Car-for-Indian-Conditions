import sys
import cv2
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QImage, QPixmap, QKeySequence, QAction, QPalette, QColor, QIcon
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit, QMessageBox
from enum import Enum

# Constants
VIDEO_WIDTH = 640
VIDEO_HEIGHT = 480

# Driving Modes
class DrivingMode(Enum):
    AUTO = 1
    MANUAL = 2

# Main Application Window
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Initialize variables
        self.logged_in = False
        self.driving_mode = None
        self.video_label = QLabel()
        self.camera = None
        self.camera_frame_timer = QTimer()

        # Set window style
        self.setWindowStyle()

        # Create login widget
        self.login_widget = QWidget()
        self.login_layout = QVBoxLayout()
        self.username_edit = QLineEdit()
        self.password_edit = QLineEdit()
        self.login_button = QPushButton("Login")
        self.login_button.clicked.connect(self.login)
        self.login_layout.addWidget(QLabel("Username:"))
        self.login_layout.addWidget(self.username_edit)
        self.login_layout.addWidget(QLabel("Password:"))
        self.login_layout.addWidget(self.password_edit)
        self.login_layout.addWidget(self.login_button)
        self.login_widget.setLayout(self.login_layout)

        # Create driving mode widget
        self.mode_widget = QWidget()
        self.mode_layout = QVBoxLayout()
        self.mode_widget.setLayout(self.mode_layout)

        # Create driving mode buttons
        self.auto_mode_button = QPushButton(QIcon("car_icon.png"), "Auto Mode")
        self.auto_mode_button.clicked.connect(lambda: self.select_mode(DrivingMode.AUTO))
        self.manual_mode_button = QPushButton(QIcon("car_icon.png"), "Manual Mode")
        self.manual_mode_button.clicked.connect(lambda: self.select_mode(DrivingMode.MANUAL))
        self.mode_layout.addWidget(self.auto_mode_button)
        self.mode_layout.addWidget(self.manual_mode_button)

        # Create exit button for manual mode
        self.manual_mode_exit_button = QPushButton("Exit")
        self.manual_mode_exit_button.clicked.connect(self.exit_manual_mode)
        self.manual_mode_exit_button.setObjectName("ExitButton")

        # Create title label for manual mode
        self.manual_mode_title_label = QLabel("Self-Driving Car Application - Manual Mode")
        self.manual_mode_title_label.setObjectName("TitleLabel")

        # Create top layout for title label and exit button in manual mode
        self.manual_mode_top_layout = QHBoxLayout()
        self.manual_mode_top_layout.addWidget(self.manual_mode_title_label)
        self.manual_mode_top_layout.addStretch()
        self.manual_mode_top_layout.addWidget(self.manual_mode_exit_button)
        self.manual_mode_top_layout.setContentsMargins(10, 10, 10, 0)

        # Create manual mode layout
        self.manual_mode_layout = QVBoxLayout()
        self.manual_mode_layout.addLayout(self.manual_mode_top_layout)
        self.manual_mode_layout.addWidget(self.video_label)

        # Create main layout
        self.main_layout = QVBoxLayout()
        self.main_layout.addWidget(self.mode_widget)
        self.main_layout.addLayout(self.manual_mode_layout)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        # Create central widget
        self.central_widget = QWidget()
        self.central_widget.setLayout(self.main_layout)

        # Configure main window
        self.setCentralWidget(self.login_widget)
        self.setWindowTitle("Self-Driving Car Application")

        # Check login status
        self.check_login_status()

    def setWindowStyle(self):
        self.setStyleSheet(
            """
            QMainWindow {
                background-color: #141414;
            }
            QWidget {
                background-color: #141414;
            }
            QPushButton {
                background-color: #E50914;
                color: white;
                font-size: 14px;
                font-weight: bold;
                border-radius: 5px;
                padding: 10px;
                border: none;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #E50914;
            }
            QLineEdit {
                background-color: #1F1F1F;
                color: white;
                font-size: 14px;
                padding: 8px;
                border: none;
                border-radius: 5px;
            }
            QLabel {
                color: white;
                font-size: 18px;
            }
            #ExitButton {
                background-color: #141414;
            }
            #ExitButton:hover {
                background-color: #E50914;
            }
            #TitleLabel {
                font-size: 24px;
                font-weight: bold;
                padding: 5px;
                color: #E50914;
            }
            """
        )

    def check_login_status(self):
        # TODO: Implement your own logic to check login status (e.g., check if user credentials are saved)
        # If the user is already logged in, show the driving mode widget
        if self.logged_in:
            self.show_driving_mode_widget()
        else:
            self.show_login_widget()

    def show_login_widget(self):
        self.setCentralWidget(self.login_widget)
        self.setWindowTitle("Self-Driving Car Application - Login")

    def show_driving_mode_widget(self):
        self.setCentralWidget(self.central_widget)
        self.setWindowTitle("Self-Driving Car Application - Select Mode")

    def login(self):
        # Check login credentials here
        # Replace this with your own authentication logic
        username = self.username_edit.text()
        password = self.password_edit.text()
        if username == "admin" and password == "password":
            self.logged_in = True
            self.show_driving_mode_widget()
        else:
            QMessageBox.warning(self, "Login Failed", "Invalid username or password.")

    def select_mode(self, mode):
        if self.logged_in:
            self.driving_mode = mode
            if self.driving_mode == DrivingMode.AUTO:
                self.start_auto_mode()
            elif self.driving_mode == DrivingMode.MANUAL:
                print("Starting Manual Mode")
                self.start_manual_mode()

    def start_auto_mode(self):
        # TODO: Implement auto mode functionality
        pass

    def start_manual_mode(self):
        if self.camera:
            return

        self.camera = cv2.VideoCapture(0)
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, VIDEO_WIDTH)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, VIDEO_HEIGHT)
        self.camera_frame_timer.timeout.connect(self.display_camera_frame)
        self.camera_frame_timer.start(30)  # Update frame every 30ms

        # Enable keyboard input within the screen
        self.manual_mode_action = QAction(self)
        self.manual_mode_action.setShortcut(QKeySequence(Qt.Key.Key_Escape))
        self.manual_mode_action.triggered.connect(self.exit_manual_mode)
        self.addAction(self.manual_mode_action)

    def display_camera_frame(self):
        ret, frame = self.camera.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image = QImage(frame.data, frame.shape[1], frame.shape[0], QImage.Format.Format_RGB888)
            pixmap = QPixmap.fromImage(image)
            pixmap = pixmap.scaled(VIDEO_WIDTH, VIDEO_HEIGHT, Qt.AspectRatioMode.KeepAspectRatio)
            self.video_label.setPixmap(pixmap)

    def exit_manual_mode(self):
        if self.camera:
            self.camera.release()
            self.camera = None
            self.camera_frame_timer.stop()
            self.setCentralWidget(self.mode_widget)
            self.setWindowTitle("Self-Driving Car Application - Select Mode")

    def exit_mode(self):
        self.logged_in = False
        self.driving_mode = None
        self.camera = None
        self.camera_frame_timer.stop()
        self.setCentralWidget(self.login_widget)
        self.setWindowTitle("Self-Driving Car Application - Login")

# Create the application
app = QApplication(sys.argv)

# Create and show the main window
window = MainWindow()
window.show()

# Start the event loop
sys.exit(app.exec())
