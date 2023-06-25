def start_pothole_mode(self):
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
        self.pothole_mode_video_layout.addWidget(self.video_label)

    

def exit_pothole_mode(self):
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