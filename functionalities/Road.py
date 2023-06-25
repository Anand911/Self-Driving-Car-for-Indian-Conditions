import cv2
import numpy as np
import time
from threading import Thread
from .ObjectDetect import getObjects
from utils import dispatch
class LaneLine():
    def __init__(self):
        self.running=True
        self.frame = None
        self.Matrix = None
        self.framePers = None
        self.frameGray = None
        self.frameThresh = None
        self.frameEdge = None
        self.frameFinal = None
        self.frameFinalDuplicate = None
        self.ROILane = None
        self.LeftLanePos = None
        self.RightLanePos = None
        self.frameCenter = None
        self.laneCenter = None
        self.Result = None

        self.ss = None

        self.histrogramLane = []

        self.Source = np.float32([(120, 145), (500, 145), (90, 195), (540, 195)])#np.float32([(40, 145), (400, 145), (10, 195), (440, 195)])
        self.Destination = np.float32([(100, 0), (280, 0), (100, 240), (280, 240)])

        self.Camera = None


    def Setup(self):
        

        self.Camera = cv2.VideoCapture('http://192.168.1.2:5000/video_feed')
        self.Camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.Camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.Camera.set(cv2.CAP_PROP_BRIGHTNESS, 50)
        self.Camera.set(cv2.CAP_PROP_CONTRAST, 50)
        self.Camera.set(cv2.CAP_PROP_SATURATION, 50)
        self.Camera.set(cv2.CAP_PROP_GAIN, 150)
        self.Camera.set(cv2.CAP_PROP_FPS, 100)


    def Capture(self):
        

        ret, self.frame = self.Camera.read()
        self.frame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)


    def Perspective(self):
        
        #print(self.Source[0])
        
        cv2.line(self.frame, tuple(self.Source[0].astype(int)), tuple(self.Source[1].astype(int)), (0, 0, 255), 2)
        cv2.line(self.frame, tuple(self.Source[1].astype(int)), tuple(self.Source[3].astype(int)), (0, 0, 255), 2)
        cv2.line(self.frame, tuple(self.Source[3].astype(int)), tuple(self.Source[2].astype(int)), (0, 0, 255), 2)
        cv2.line(self.frame, tuple(self.Source[2].astype(int)), tuple(self.Source[0].astype(int)), (0, 0, 255), 2)

        self.Matrix = cv2.getPerspectiveTransform(self.Source, self.Destination)
        self.framePers = cv2.warpPerspective(self.frame, self.Matrix, (400, 240))


    def Threshold(self):
        

        self.frameGray = cv2.cvtColor(self.framePers, cv2.COLOR_RGB2GRAY)
        _, self.frameThresh = cv2.threshold(self.frameGray, 200, 255, cv2.THRESH_BINARY)
        self.frameEdge = cv2.Canny(self.frameGray, 900, 900, apertureSize=3)
        self.frameFinal = cv2.add(self.frameThresh, self.frameEdge)
        self.frameFinal = cv2.cvtColor(self.frameFinal, cv2.COLOR_GRAY2RGB)
        self.frameFinalDuplicate = cv2.cvtColor(self.frameFinal, cv2.COLOR_RGB2BGR)


    def Histrogram(self):
        
        self.histrogramLane = np.zeros(400)

        for i in range(400):
            self.ROILane = self.frameFinalDuplicate[140:240, i:i + 1]
            self.ROILane = cv2.divide(255, self.ROILane)
            self.histrogramLane[i] = np.sum(self.ROILane)


    def LaneFinder(self):
        

        self.LeftLanePos = np.argmax(self.histrogramLane[:150])
        self.RightLanePos = np.argmax(self.histrogramLane[250:]) + 250

        cv2.line(self.frameFinal, (self.LeftLanePos, 0), (self.LeftLanePos, 240), (0, 255, 0), 2)
        cv2.line(self.frameFinal, (self.RightLanePos, 0), (self.RightLanePos, 240), (0, 255, 0), 2)


    def LaneCenter(self):
        

        self.laneCenter = int((self.RightLanePos - self.LeftLanePos) / 2 + self.LeftLanePos)
        self.frameCenter = 188

        cv2.line(self.frameFinal, (self.laneCenter, 0), (self.laneCenter, 240), (0, 255, 0), 3)
        cv2.line(self.frameFinal, (self.frameCenter, 0), (self.frameCenter, 240), (255, 0, 0), 3)

        self.Result = self.laneCenter - self.frameCenter

    def LineFollow(self,server):
        result, data = getObjects(self.frame,0.60,0.2, objects=['person','car'])
        msg=dispatch(0,"LANE DETECTION")
        if data is not None and data["objects"] and (data["distance"]<0.5):
            #msg={"mode":"LANE DETETCTION","function":"object"}
            msg=dispatch(0,"LANE DETECTION")
        else:
            if (self.Result == 0):
                msg=dispatch(9,"LANE DETECTION")
            elif (self.Result >0 and self.Result <10):
                msg=dispatch(4,"LANE DETECTION")
            elif (self.Result >=10 and self.Result <20): 
                msg=dispatch(5,"LANE DETECTION")
            elif (self.Result >20):    
                msg=dispatch(6,"LANE DETECTION")
            elif (self.Result <0 and self.Result >-10):
                msg=dispatch(1,"LANE DETECTION")
            elif (self.Result <=-10 and self.Result >-20):
                msg=dispatch(2,"LANE DETECTION")
            elif (self.Result <-20):
                msg=dispatch(3,"LANE DETECTION")
            #msg={"mode":"LANE DETETCTION","function":"no object"}
        #print(msg)
        server.send(msg)

    def results(self):
        self.ss = "Result = " + str(self.Result)
        cv2.putText(self.frame, self.ss, (1, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        cv2.namedWindow("Original", cv2.WINDOW_KEEPRATIO)
        cv2.moveWindow("Original", 0, 100)
        cv2.resizeWindow("Original", 640, 480)
        cv2.imshow("Original", self.frame)

        cv2.namedWindow("Perspective", cv2.WINDOW_KEEPRATIO)
        cv2.moveWindow("Perspective", 640, 100)
        cv2.resizeWindow("Perspective", 640, 480)
        cv2.imshow("Perspective", self.framePers)

        cv2.namedWindow("Final", cv2.WINDOW_KEEPRATIO)
        cv2.moveWindow("Final", 1000, 100)
        cv2.resizeWindow("Final", 640, 480)
        cv2.imshow("Final", self.frameFinal)

    def road_toggle_state(self):
        self.running= not self.running

    def LaneCalibration(self):
        if not self.running:
            self.road_toggle_state()

        while self.running:
            start = time.time()
            self.Capture()
            self.Perspective()
            self.Threshold()
            self.Histrogram()
            self.LaneFinder()
            self.LaneCenter()
            self.results()

            

            cv2.waitKey(1)
            end = time.time()
            elapsed_seconds = end - start
            FPS = int(1 / elapsed_seconds)
            print("FPS =", FPS)

        self.Camera.release()
        cv2.destroyAllWindows()

    def LaneDetection(self,server):
        if not self.running:
            self.road_toggle_state()

        while self.running:
            start = time.time()
            self.Capture()
            self.Perspective()
            self.Threshold()
            self.Histrogram()
            self.LaneFinder()
            self.LaneCenter()
            self.LineFollow(server)
            self.results()
            cv2.waitKey(1)
            end = time.time()
            elapsed_seconds = end - start
            FPS = int(1 / elapsed_seconds)
            print("FPS =", FPS)
        self.Camera=None
        cv2.destroyAllWindows()
        print("Release")
        




if __name__ == "__main__":
    road=LaneLine()
    road.Setup()
    t1=Thread(target=road.LaneCalibration,args=[])
    t1.start()
    t1.join(10)
    road.road_toggle_state()