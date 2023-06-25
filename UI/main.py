import sys,time,pickle
sys.path.insert(1,"C://Users//91701//OneDrive//Documents//Final Year Project//SelfDriving")
import cv2
from PyQt6.QtCore import Qt, QTimer,QEvent,QUrl
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtGui import QImage, QPixmap, QKeySequence, QAction, QPalette,QMovie
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit, QMessageBox, QStackedWidget
from enum import Enum
from threading import Thread
from config import WEBCAM
from utils import dispatch
from functionalities.manual import ManualDriving
from functionalities.server import Server
from functionalities.Road import LaneLine
from functionalities.ObjectDetect import *
from functionalities.pothole import pothole_detection,send_data
# Constants
VIDEO_WIDTH = 640
VIDEO_HEIGHT = 480
t1=None
# Driving Modes
class DrivingMode(Enum):
    AUTO = 1
    MANUAL = 2
    OBJECT_DETECTION=3
    LANE_DETECTION=4
    LANE_CALIBRATION=5
    POTHOLE_DETECTION=6

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
        self.server=None
        self.frame_count=0
        self.start_time=None
        self.pothole=0
        self.running=False

        # Set window style
        self.setWindowStyle()

        # Create login page
        self.login_widget = QWidget()
        self.login_page=QVBoxLayout()
        self.login_layout = QHBoxLayout()
        self.login_title_label = QLabel("Let's Self Drive India!")
        self.login_title_label.setObjectName("loginTitle")
        self.login_title_label.setStyleSheet(
            """
            QLabel#loginTitle {
                color: white;
                font-size: 34px;
                font-family: Bebas;
                padding: 10px;
            }
            """
        )
        self.login_title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.login_page.addWidget(self.login_title_label)
        self.login_container = QWidget()
        self.login_container.setObjectName("loginContainer")
        self.login_container.setFixedWidth(self.width() // 2)  # Set the width to 50% of the window width
        self.login_container.setFixedHeight((self.width() * 3) // 4)  # Set the height to 3/4 of the window width
        self.login_box_layout = QVBoxLayout(self.login_container)
        self.login_input_layout = QVBoxLayout()
        self.login_button_layout = QVBoxLayout()
        self.login_input_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.login_button_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.username_edit = QLineEdit()
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.login_button = QPushButton("Login")
        self.login_button.setObjectName("loginButton")
        self.login_button.clicked.connect(self.login)

        user_label=QLabel("Username:")
        user_label.setStyleSheet("background-color: rgba(255, 255, 255, 0)")
        pass_label=QLabel("Password:")
        pass_label.setStyleSheet("background-color: rgba(255, 255, 255, 0)")
        self.login_input_layout.addWidget(user_label)
        self.login_input_layout.addWidget(self.username_edit)
        self.login_input_layout.addWidget(pass_label)
        self.login_input_layout.addWidget(self.password_edit)
        # Set the label color to match the container background
        
        self.password_edit.setStyleSheet("color: #E50914;")

        self.login_button_layout.addWidget(self.login_button)

        self.login_box_layout.addLayout(self.login_input_layout)
        self.login_box_layout.addLayout(self.login_button_layout)
        self.login_layout.addWidget(self.login_container)

        self.car_image_label = QLabel()
        self.car_image_label.setFixedHeight((self.width() * 3) // 4)
        car_image=QPixmap("Asset 2.png")
        scaled_car_image = car_image.scaledToWidth(500)  # Adjust the width as per your requirement
        self.car_image_label.setPixmap(scaled_car_image)
        self.car_image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.login_layout.addWidget(self.car_image_label)
        self.login_page.addLayout(self.login_layout)
        self.login_widget.setLayout(self.login_page)

        # Create select mode page
        self.select_mode_widget = QWidget()
        self.select_mode_layout = QVBoxLayout()
        self.auto_mode_button = QPushButton("Auto Mode")
        self.auto_mode_button.clicked.connect(lambda: self.select_mode(DrivingMode.AUTO))
        self.manual_mode_button = QPushButton("Manual Mode")
        self.manual_mode_button.clicked.connect(lambda: self.select_mode(DrivingMode.MANUAL))
        self.object_detection_mode_button = QPushButton("Object Detection Mode")
        self.object_detection_mode_button.clicked.connect(lambda: self.select_mode(DrivingMode.OBJECT_DETECTION))
        self.lane_detection_mode_button = QPushButton("Lane Detection Mode")
        self.lane_detection_mode_button.clicked.connect(lambda: self.select_mode(DrivingMode.LANE_DETECTION))
        self.lane_calibration_mode_button = QPushButton("Lane Calibration Mode")
        self.lane_calibration_mode_button.clicked.connect(lambda: self.select_mode(DrivingMode.LANE_CALIBRATION))
        self.pothole_mode_button = QPushButton("Pothole Detection Mode")
        self.pothole_mode_button.clicked.connect(lambda: self.select_mode(DrivingMode.POTHOLE_DETECTION))
        self.select_mode_layout.addWidget(self.auto_mode_button)
        self.select_mode_layout.addWidget(self.manual_mode_button)
        self.select_mode_layout.addWidget(self.object_detection_mode_button)
        self.select_mode_layout.addWidget(self.lane_detection_mode_button)
        self.select_mode_layout.addWidget(self.pothole_mode_button)
        self.select_mode_layout.addWidget(self.lane_calibration_mode_button)
        self.select_mode_widget.setLayout(self.select_mode_layout)

        # Create auto mode page
        self.auto_mode_widget = QWidget()
        self.auto_mode_layout = QVBoxLayout()
        self.auto_mode_top_layout = QHBoxLayout()
        self.auto_mode_sidebar_layout = QVBoxLayout()
        self.auto_mode_video_layout = QVBoxLayout()
        self.auto_mode_top_layout.addLayout(self.auto_mode_sidebar_layout)
        self.auto_mode_top_layout.addLayout(self.auto_mode_video_layout)
        self.auto_mode_layout.addLayout(self.auto_mode_top_layout)
        self.auto_mode_widget.setLayout(self.auto_mode_layout)

        # Create exit button and title label for auto mode
        self.auto_mode_exit_button = QPushButton("Exit")
        self.auto_mode_exit_button.clicked.connect(self.exit_auto_mode)
        # Create widget and layout
        

        # Create input fields
        self.input1_label = QLabel("Latitude:")
        self.input1_edit = QLineEdit()
        self.input2_label = QLabel("Longitude:")
        self.input2_edit = QLineEdit()

        # Create submit button
        self.submit_button = QPushButton("Submit")
        self.submit_button.clicked.connect(self.submit_auto_mode)

        # Add UI elements to the layout
        self.auto_mode_layout.addWidget(self.input1_label)
        self.auto_mode_layout.addWidget(self.input1_edit)
        self.auto_mode_layout.addWidget(self.input2_label)
        self.auto_mode_layout.addWidget(self.input2_edit)
        self.auto_mode_layout.addWidget(self.submit_button)
        
        self.auto_mode_title_label = QLabel("Self-Driving Car Application - Auto Pilot Mode")
        self.auto_mode_sidebar_layout.addWidget(self.auto_mode_title_label)
        self.auto_mode_sidebar_layout.addWidget(self.auto_mode_exit_button)
        # Create mode buttons for auto mode
        self.auto_mode_auto_button = QPushButton("Auto Mode")
        self.auto_mode_auto_button.clicked.connect(lambda: self.select_mode(DrivingMode.AUTO))
        self.auto_mode_sidebar_layout.addWidget(self.auto_mode_auto_button)
        self.auto_mode_od_button = QPushButton("Object Detection Mode")
        self.auto_mode_od_button.clicked.connect(lambda: self.select_mode(DrivingMode.OBJECT_DETECTION))
        self.auto_mode_sidebar_layout.addWidget(self.auto_mode_od_button)

        self.auto_mode_manual_button = QPushButton("Manual Mode")
        self.auto_mode_manual_button.clicked.connect(lambda: self.select_mode(DrivingMode.MANUAL))
        self.auto_mode_sidebar_layout.addWidget(self.auto_mode_manual_button)
        # Create manual mode page
        self.manual_mode_widget = QWidget()
        self.manual_mode_layout = QVBoxLayout()
        self.manual_mode_top_layout = QHBoxLayout()
        self.manual_mode_sidebar_layout = QVBoxLayout()
        self.manual_mode_video_layout = QVBoxLayout()
        self.manual_mode_top_layout.addLayout(self.manual_mode_sidebar_layout)
        self.manual_mode_top_layout.addLayout(self.manual_mode_video_layout)
        self.manual_mode_layout.addLayout(self.manual_mode_top_layout)
        self.manual_mode_widget.setLayout(self.manual_mode_layout)

        # Create exit button and title label for manual mode
        self.manual_mode_exit_button = QPushButton("Exit")
        self.manual_mode_exit_button.clicked.connect(self.exit_manual_mode)
        
        self.manual_mode_title_label = QLabel("Self-Driving Car Application - Manual Mode")
        self.manual_mode_sidebar_layout.addWidget(self.manual_mode_title_label)
        self.manual_mode_sidebar_layout.addWidget(self.manual_mode_exit_button)
        # Create mode buttons for manual mode
        self.manual_mode_auto_button = QPushButton("Auto Mode")
        self.manual_mode_auto_button.clicked.connect(lambda: self.select_mode(DrivingMode.AUTO))
        self.manual_mode_sidebar_layout.addWidget(self.manual_mode_auto_button)
        self.manual_mode_od_button = QPushButton("Object Detection Mode")
        self.manual_mode_od_button.clicked.connect(lambda: self.select_mode(DrivingMode.OBJECT_DETECTION))
        self.manual_mode_sidebar_layout.addWidget(self.manual_mode_od_button)

        self.manual_mode_manual_button = QPushButton("Manual Mode")
        self.manual_mode_manual_button.clicked.connect(lambda: self.select_mode(DrivingMode.MANUAL))
        self.manual_mode_sidebar_layout.addWidget(self.manual_mode_manual_button)
        
        # Create object detection mode page
        self.object_detection_mode_widget = QWidget()
        self.object_detection_mode_layout = QVBoxLayout()
        self.object_detection_mode_top_layout = QHBoxLayout()
        self.object_detection_mode_sidebar_layout = QVBoxLayout()
        self.object_detection_mode_video_layout = QVBoxLayout()
        self.object_detection_mode_top_layout.addLayout(self.object_detection_mode_sidebar_layout)
        self.object_detection_mode_top_layout.addLayout(self.object_detection_mode_video_layout)
        self.object_detection_mode_layout.addLayout(self.object_detection_mode_top_layout)
        self.object_detection_mode_widget.setLayout(self.object_detection_mode_layout)

        self.object_detection_mode_exit_button = QPushButton("Exit")
        self.object_detection_mode_exit_button.clicked.connect(self.exit_object_detection_mode)
        self.object_detection_mode_title_label = QLabel("Self-Driving Car Application - Object Detection Mode")
        self.object_detection_mode_sidebar_layout.addWidget(self.object_detection_mode_title_label)
        self.object_detection_mode_sidebar_layout.addWidget(self.object_detection_mode_exit_button)

        # Create lane calibration mode page
        self.lane_calibration_mode_widget = QWidget()
        self.lane_calibration_mode_layout = QVBoxLayout()
        self.lane_calibration_mode_top_layout = QHBoxLayout()
        self.lane_calibration_mode_sidebar_layout = QVBoxLayout()
        self.lane_calibration_mode_illustration_layout = QVBoxLayout()
        self.lane_calibration_mode_top_layout.addLayout(self.lane_calibration_mode_sidebar_layout)
        self.lane_calibration_mode_top_layout.addLayout(self.lane_calibration_mode_illustration_layout)
        self.lane_calibration_mode_layout.addLayout(self.lane_calibration_mode_top_layout)
        self.lane_calibration_mode_widget.setLayout(self.lane_calibration_mode_layout)

        # Create exit button and title label for lane calibration mode
        self.lane_calibration_mode_exit_button = QPushButton("Exit")
        self.lane_calibration_mode_exit_button.clicked.connect(self.exit_lane_calibration_mode)
        self.lane_calibration_mode_title_label = QLabel("Lane Calibration Mode")
        self.lane_calibration_mode_sidebar_layout.addWidget(self.lane_calibration_mode_title_label)
        self.lane_calibration_mode_sidebar_layout.addWidget(self.lane_calibration_mode_exit_button)

        # Create mode buttons for lc mode
        self.lane_calibration_mode_auto_button = QPushButton("Auto Mode")
        self.lane_calibration_mode_auto_button.clicked.connect(lambda: self.select_mode(DrivingMode.AUTO))
        self.lane_calibration_mode_sidebar_layout.addWidget(self.lane_calibration_mode_auto_button)
        self.lane_calibration_mode_od_button = QPushButton("Object Detection Mode")
        self.lane_calibration_mode_od_button.clicked.connect(lambda: self.select_mode(DrivingMode.OBJECT_DETECTION))
        self.lane_calibration_mode_sidebar_layout.addWidget(self.lane_calibration_mode_od_button)
        self.lane_calibration_mode_manual_button = QPushButton("Manual Mode")
        self.lane_calibration_mode_manual_button.clicked.connect(lambda: self.select_mode(DrivingMode.MANUAL))
        self.lane_calibration_mode_sidebar_layout.addWidget(self.lane_calibration_mode_manual_button)

        # Create lane detection mode page
        self.lane_detection_mode_widget = QWidget()
        self.lane_detection_mode_layout = QVBoxLayout()
        self.lane_detection_mode_top_layout = QHBoxLayout()
        self.lane_detection_mode_sidebar_layout = QVBoxLayout()
        self.lane_detection_mode_illustration_layout = QVBoxLayout()
        self.lane_detection_mode_top_layout.addLayout(self.lane_detection_mode_sidebar_layout)
        self.lane_detection_mode_top_layout.addLayout(self.lane_detection_mode_illustration_layout)
        self.lane_detection_mode_layout.addLayout(self.lane_detection_mode_top_layout)
        self.lane_detection_mode_widget.setLayout(self.lane_detection_mode_layout)
        

        # Create exit button and title label for lane detection mode
        self.lane_detection_mode_exit_button = QPushButton("Exit")
        self.lane_detection_mode_exit_button.clicked.connect(self.exit_lane_detection_mode)
        self.lane_detection_mode_title_label = QLabel("Lane Detection Mode")
        self.lane_detection_mode_sidebar_layout.addWidget(self.lane_detection_mode_title_label)
        self.lane_detection_mode_sidebar_layout.addWidget(self.lane_detection_mode_exit_button)

        # Create mode buttons for ld mode
        self.lane_detection_mode_auto_button = QPushButton("Auto Mode")
        self.lane_detection_mode_auto_button.clicked.connect(lambda: self.select_mode(DrivingMode.AUTO))
        self.lane_detection_mode_sidebar_layout.addWidget(self.lane_detection_mode_auto_button)
        self.lane_detection_mode_od_button = QPushButton("Object Detection Mode")
        self.lane_detection_mode_od_button.clicked.connect(lambda: self.select_mode(DrivingMode.OBJECT_DETECTION))
        self.lane_detection_mode_sidebar_layout.addWidget(self.lane_detection_mode_od_button)
        self.lane_detection_mode_manual_button = QPushButton("Manual Mode")
        self.lane_detection_mode_manual_button.clicked.connect(lambda: self.select_mode(DrivingMode.MANUAL))
        self.lane_detection_mode_sidebar_layout.addWidget(self.lane_detection_mode_manual_button)
        # Create Pothole mode page
        self.pothole_mode_widget = QWidget()
        self.pothole_mode_layout = QVBoxLayout()
        self.pothole_mode_top_layout = QHBoxLayout()
        self.pothole_mode_sidebar_layout = QVBoxLayout()
        self.pothole_mode_video_layout = QVBoxLayout()
        self.pothole_mode_top_layout.addLayout(self.pothole_mode_sidebar_layout)
        self.pothole_mode_top_layout.addLayout(self.pothole_mode_video_layout)
        self.pothole_mode_layout.addLayout(self.pothole_mode_top_layout)
        self.pothole_mode_widget.setLayout(self.pothole_mode_layout)

        # Create exit button and title label for Pothole mode
        self.pothole_mode_exit_button = QPushButton("Exit")
        self.pothole_mode_exit_button.clicked.connect(self.exit_pothole_mode)
        
        self.pothole_mode_title_label = QLabel("Self-Driving Car Application - Pothole Detect Mode")
        self.pothole_mode_sidebar_layout.addWidget(self.pothole_mode_title_label)
        self.pothole_mode_sidebar_layout.addWidget(self.pothole_mode_exit_button)
        # Create mode buttons for Pothole mode
        self.pothole_mode_auto_button = QPushButton("Auto Mode")
        self.pothole_mode_auto_button.clicked.connect(lambda: self.select_mode(DrivingMode.AUTO))
        self.pothole_mode_sidebar_layout.addWidget(self.pothole_mode_auto_button)
        self.pothole_mode_od_button = QPushButton("Object Detection Mode")
        self.pothole_mode_od_button.clicked.connect(lambda: self.select_mode(DrivingMode.OBJECT_DETECTION))
        self.pothole_mode_sidebar_layout.addWidget(self.pothole_mode_od_button)

        self.pothole_mode_manual_button = QPushButton("Manual Mode")
        self.pothole_mode_manual_button.clicked.connect(lambda: self.select_mode(DrivingMode.MANUAL))
        self.pothole_mode_sidebar_layout.addWidget(self.pothole_mode_manual_button)

        # Create loading animation
        self.loading_movie = QMovie("loader.gif")
        self.loading_label = QLabel()
        self.loading_label.setMovie(self.loading_movie)
        self.loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Create connecting message label
        self.connecting_label = QLabel("Attempting to connect with the car...")
        self.connecting_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.connecting_label.setStyleSheet("font-size: 18px; color: white;")

        # Create loading widget
        self.loading_widget = QWidget()
        self.loading_layout = QVBoxLayout()
        self.loading_layout.addWidget(self.loading_label)
        self.loading_layout.addWidget(self.connecting_label)
        self.loading_widget.setLayout(self.loading_layout)

        # Create stacked widget to manage different pages
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.addWidget(self.login_widget)
        self.stacked_widget.addWidget(self.loading_widget)
        self.stacked_widget.addWidget(self.select_mode_widget)
        self.stacked_widget.addWidget(self.auto_mode_widget)
        self.stacked_widget.addWidget(self.manual_mode_widget)
        self.stacked_widget.addWidget(self.object_detection_mode_widget)
        self.stacked_widget.addWidget(self.lane_calibration_mode_widget)
        self.stacked_widget.addWidget(self.lane_detection_mode_widget)
        self.stacked_widget.addWidget(self.pothole_mode_widget)
        self.setCentralWidget(self.stacked_widget)

        # Configure main window
        self.setWindowTitle("Self-Driving Car Application")
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
            #loginContainer {
                background-color: rgba(255, 255, 255, 0.01);
                border-radius: 10px;
                padding: 20px;
            }
            """
        )

    def check_state(self):
        # Check the state variable here
        if not self.server.state:
            QMessageBox.warning(self, "Warning", "The Car is not Connected... Please Check the car")
            #self.close()
    def check_login_status(self):
        if self.logged_in:
            self.stacked_widget.setCurrentWidget(self.select_mode_widget)
        else:
            self.stacked_widget.setCurrentWidget(self.login_widget)

    def login(self):
        # Check login credentials here
        # Replace this with your own authentication logic
        username = self.username_edit.text()
        password = self.password_edit.text()
        if username == "" and password == "":
            self.logged_in = True
            self.check_login_status()
            self.server=Server()
            self.show_loading_animation()
            QTimer.singleShot(2000, self.end_loading_animation)  # End loading animation after 2 seconds
            
        else:
            QMessageBox.warning(self, "Login Failed", "Invalid username or password.")
    def show_loading_animation(self):
        self.stacked_widget.setCurrentWidget(self.loading_widget)
        self.loading_movie.start()

    def end_loading_animation(self):
        self.loading_movie.stop()
        self.stacked_widget.setCurrentWidget(self.select_mode_widget)
        
    """def select_mode(self, mode):
        if self.logged_in:
            self.check_state()
            if self.driving_mode == DrivingMode.MANUAL and mode != DrivingMode.MANUAL:
                self.exit_manual_mode()
            self.driving_mode = mode
            if self.driving_mode == DrivingMode.AUTO:
                self.start_auto_mode()
            elif self.driving_mode == DrivingMode.MANUAL:
                self.stacked_widget.setCurrentWidget(self.manual_mode_widget)
                self.start_manual_mode()"""
    def select_mode(self, mode):
        manual.stop(self.server)
        if self.logged_in:
            self.check_state()
            if self.driving_mode == DrivingMode.AUTO and mode != DrivingMode.AUTO:
                self.exit_auto_mode()
            elif self.driving_mode == DrivingMode.MANUAL and mode != DrivingMode.MANUAL:
                self.exit_manual_mode()
            elif self.driving_mode == DrivingMode.OBJECT_DETECTION and mode != DrivingMode.OBJECT_DETECTION:
                self.exit_object_detection_mode()

            self.driving_mode = mode
            
            if self.driving_mode == DrivingMode.AUTO:
                self.start_auto_mode()
                self.stacked_widget.setCurrentWidget(self.auto_mode_widget)
            elif self.driving_mode == DrivingMode.MANUAL:
                self.stacked_widget.setCurrentWidget(self.manual_mode_widget)
                self.start_manual_mode()
            elif self.driving_mode == DrivingMode.OBJECT_DETECTION:
                self.stacked_widget.setCurrentWidget(self.object_detection_mode_widget)
                self.start_object_detection_mode()
            elif self.driving_mode == DrivingMode.LANE_CALIBRATION:
                self.stacked_widget.setCurrentWidget(self.lane_calibration_mode_widget)
                self.start_lane_calibration_mode()
            elif self.driving_mode == DrivingMode.LANE_DETECTION:
                self.stacked_widget.setCurrentWidget(self.lane_detection_mode_widget)
                self.start_lane_detection_mode()
            elif self.driving_mode == DrivingMode.POTHOLE_DETECTION:
                self.stacked_widget.setCurrentWidget(self.pothole_mode_widget)
                self.start_pothole_mode()


    def start_auto_mode(self):
        # TODO: Implement auto mode functionality
        self.map_view = QWebEngineView()
        self.auto_mode_video_layout.addWidget(self.map_view)
        
        # Load the Google Maps webpage
        url = "https://maps.google.com/maps"
        #url = "http://127.0.1.1:5500/Website%20Tracking/index.html"
        self.map_view.load(QUrl(url))

    def exit_auto_mode(self):

        msg={"mode":"AUTO","function":"stop","latitude":0.0,"longitude":0.0}
        msg=pickle.dumps(msg)
        msg=bytes(f"{len(msg):<10}","utf-8")+msg
        self.server.send(msg)
        self.submit_button.setEnabled(True)
        self.stacked_widget.setCurrentWidget(self.select_mode_widget)
        self.auto_mode_video_layout.removeWidget(self.map_view)
        #self.map_view.close()
        manual.stop(self.server)
        
        self.map_view = None
    def submit_auto_mode(self):
        # Retrieve the input values
        url = "http://127.0.1.1:5500/Website%20Tracking/index.html"
        self.map_view.load(QUrl(url))
        self.submit_button.setEnabled(False)
        self.input1_value = self.input1_edit.text()
        self.input2_value = self.input2_edit.text()
        if self.input1_value=='' or self.input2_value=='':
            lat,lng=10.004599, 76.279348#worked10.004594, 76.279300#Work10.004590, 76.279310#10.004497166666667,76.27928266666666#10.004579, 76.279323#10.004563, 76.279322#10.004574, 76.279320#0.0,0.0
        else:
            lat=float(self.input1_value)
            lng=float(self.input2_value)
        print(lat,lng)
        
        msg={"mode":"AUTO","function":"start","latitude":lat,"longitude":lng}
        msg=pickle.dumps(msg)
        msg=bytes(f"{len(msg):<10}","utf-8")+msg
        self.server.send(msg)

        # Perform any necessary processing with the self.input values
        # ...

        # Clear the self.input fields
        self.input1_edit.clear()
        self.input2_edit.clear()

    def start_manual_mode(self):
        if self.camera:
            return
        self.check_state()
        self.camera = cv2.VideoCapture('http://'+WEBCAM+':5000/video_feed')
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, VIDEO_WIDTH)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, VIDEO_HEIGHT)
        self.camera_frame_timer.timeout.connect(self.display_camera_frame)
        self.camera_frame_timer.start(30)  # Update frame every 30ms

        # Enable keyboard input within the screen
        self.manual_mode_action = QAction(self)
        self.manual_mode_action.setShortcut(QKeySequence(Qt.Key.Key_Escape))
        self.manual_mode_action.triggered.connect(self.exit_manual_mode)
        self.addAction(self.manual_mode_action)

        self.video_label.setFixedSize(VIDEO_WIDTH, VIDEO_HEIGHT)
        self.manual_mode_video_layout.addWidget(self.video_label)

        # Install event filter to capture keyboard events
        self.installEventFilter(self)

    def eventFilter(self, obj, event):
        if obj is self and event.type() == QEvent.Type.KeyPress:
            key = event.key()
            try:
                print("Key pressed:", chr(key))
            except:
                pass
        
            manual.run(key,self.server)
        return super().eventFilter(obj, event)

    def display_camera_frame(self):
        ret, frame = self.camera.read()
        if ret and self.driving_mode==DrivingMode.MANUAL:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image = QImage(frame.data, frame.shape[1], frame.shape[0], QImage.Format.Format_RGB888)
            pixmap = QPixmap.fromImage(image)
            pixmap = pixmap.scaled(VIDEO_WIDTH, VIDEO_HEIGHT, Qt.AspectRatioMode.KeepAspectRatio)
            self.video_label.setPixmap(pixmap)

        elif ret and self.driving_mode==DrivingMode.OBJECT_DETECTION:
            result, objectInfo = getObjects(frame,0.60,0.2, objects=['person','car'])
            send_obj(objectInfo,self.server)
            self.frame_count+=1
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            elapsed_time = time.time() - self.start_time
            fps = self.frame_count / elapsed_time
            fps_text = f"FPS: {fps:.2f}"
            cv2.putText(frame, fps_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            image = QImage(frame.data, frame.shape[1], frame.shape[0], QImage.Format.Format_RGB888)
            pixmap = QPixmap.fromImage(image)
            pixmap = pixmap.scaled(VIDEO_WIDTH, VIDEO_HEIGHT, Qt.AspectRatioMode.KeepAspectRatio)
            self.video_label.setPixmap(pixmap)

        elif ret and self.driving_mode==DrivingMode.POTHOLE_DETECTION:
            self.frame_count+=1
            data=pothole_detection(frame)
            if self.frame_count>=10:
                send_data(self.server,data)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            elapsed_time = time.time() - self.start_time
            fps = self.frame_count / elapsed_time
            fps_text = f"FPS: {fps:.2f}"
            cv2.putText(frame, fps_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            image = QImage(frame.data, frame.shape[1], frame.shape[0], QImage.Format.Format_RGB888)
            pixmap = QPixmap.fromImage(image)
            pixmap = pixmap.scaled(VIDEO_WIDTH, VIDEO_HEIGHT, Qt.AspectRatioMode.KeepAspectRatio)
            self.video_label.setPixmap(pixmap)

    def exit_manual_mode(self):
        
        
        #self.camera.release()
        self.camera = None
        self.camera_frame_timer.stop()
        self.removeAction(self.manual_mode_action)
        self.manual_mode_video_layout.removeWidget(self.video_label)
        manual.stop(self.server)
        self.stacked_widget.setCurrentWidget(self.select_mode_widget)

    def exit_mode(self):
        self.logged_in = False
        self.driving_mode = None
        if self.camera:
            self.camera.release()
            self.camera = None
            self.camera_frame_timer.stop()
            self.removeAction(self.manual_mode_action)
        self.check_login_status()
    
    def start_object_detection_mode(self):
    # Perform setup or actions specific to the object detection mode
    # For example, you can start the object detection algorithm or enable specific functionalities
        if self.camera:
            return
        self.check_state()
        self.camera = cv2.VideoCapture('http://'+WEBCAM+':5000/video_feed')
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, VIDEO_WIDTH)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, VIDEO_HEIGHT)
        self.start_time=time.time()
        self.camera_frame_timer.timeout.connect(self.display_camera_frame)
        self.camera_frame_timer.start(10)  # Update frame every 30ms
        self.video_label.setFixedSize(VIDEO_WIDTH, VIDEO_HEIGHT)
        self.object_detection_mode_video_layout.addWidget(self.video_label)

    

    def exit_object_detection_mode(self):
    # Clean up resources or stop processes related to the object detection mode
    
        self.frame_count=0
        #self.camera.release()
        self.camera = None
        self.camera_frame_timer.stop()
        #self.removeAction(self.manual_mode_action)
        time.sleep(1)
        msg={"mode":"OBJECT DETECTION","function":"stop"}
        msg=pickle.dumps(msg)
        msg=bytes(f"{len(msg):<10}","utf-8")+msg
        self.server.send(msg)
        self.stacked_widget.setCurrentWidget(self.select_mode_widget)
        print("Stop Object detect")
        

    def start_lane_detection_mode(self):
        global t1
        road.Setup()
        t1=Thread(target=road.LaneDetection,args=[self.server])
        t1.start()

    def start_lane_calibration_mode(self):
        road.Setup()
        t2.start()

    def exit_lane_detection_mode(self):
        global t1
        road.road_toggle_state()
        t1.join()
        manual.stop(self.server)
        msg={"mode":"LANE DETECTION","function":"stop"}
        msg=pickle.dumps(msg)
        msg=bytes(f"{len(msg):<10}","utf-8")+msg
        self.server.send(msg)
        self.stacked_widget.setCurrentWidget(self.select_mode_widget)
       

    def exit_lane_calibration_mode(self):
        road.road_toggle_state()
        t2.join()
        manual.stop(self.server)
        self.stacked_widget.setCurrentWidget(self.select_mode_widget)

    def start_pothole_mode(self):
    # Perform setup or actions specific to the object detection mode
    # For example, you can start the object detection algorithm or enable specific functionalities
        global t3
        if self.camera:
            return
        self.check_state()
        self.camera = cv2.VideoCapture('http://'+WEBCAM+':5000/video_feed')
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, VIDEO_WIDTH)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, VIDEO_HEIGHT)
        self.start_time=time.time()
        self.camera_frame_timer.timeout.connect(self.display_camera_frame)
        self.camera_frame_timer.start(10)  # Update frame every 30ms
        self.video_label.setFixedSize(VIDEO_WIDTH, VIDEO_HEIGHT)
        self.pothole_mode_video_layout.addWidget(self.video_label)
        self.running=True
        t3=Thread(target=self.pothole_avoid)
        t3.start()


    

    def exit_pothole_mode(self):
    # Clean up resources or stop processes related to the object detection mode
        global t3
        self.frame_count=0
        #self.camera.release()
        self.camera = None
        self.camera_frame_timer.stop()
        #self.removeAction(self.manual_mode_action)
        self.pothole=0
        self.running=False
        t3.join()
        time.sleep(1)
        msg={"mode":"POTHOLE DETECTION","function":"stop"}
        msg=pickle.dumps(msg)
        msg=bytes(f"{len(msg):<10}","utf-8")+msg
        self.server.send(msg)
        self.stacked_widget.setCurrentWidget(self.select_mode_widget)
        print("Stop Pothole detect")

    
    def pothole_avoid(self):
        while self.running:
            self.if_pothole()

    def if_pothole(self):
        msg=dispatch(str(self.pothole),"POTHOLE DETECTION")
        
        if self.pothole==0:
            pass
        elif self.pothole==9:
            self.server.send(msg)
        elif self.pothole!=9:
            print("in")
            self.server.send(msg)
            time.sleep(1)
            if self.pothole==6:
                msg=dispatch(str(3),"POTHOLE DETECTION")
                self.server.send(msg)
            elif self.pothole==3:
                msg=dispatch(str(6),"POTHOLE DETECTION")
                self.server.send(msg)
            time.sleep(1)
            msg=dispatch(str(0),"POTHOLE DETECTION")
            self.server.send(msg)
        


# Create the application
app = QApplication(sys.argv)

# Create and show the main window
window = MainWindow()
window.resize(VIDEO_WIDTH + 200, max(VIDEO_HEIGHT, 600))

window.show()

#Create Manual Driving Object
manual=ManualDriving()
road=LaneLine()
t2=Thread(target=road.LaneCalibration)

# Start the event loop
sys.exit(app.exec())

