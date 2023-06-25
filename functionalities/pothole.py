#importing necessary libraries
import cv2 as cv
import time
import os
from utils import dispatch
#reading label name from obj.names file
class_name = []
with open('C:/Users/91701/OneDrive/Documents/Final Year Project/SelfDriving/functionalities/data/obj.names', 'r') as f:
    class_name = [cname.strip() for cname in f.readlines()]

#importing model weights and config file
#defining the model parameters
net1 = cv.dnn.readNet('C:/Users/91701/OneDrive/Documents/Final Year Project/SelfDriving/functionalities/data/yolov4_tiny.weights', 'C:/Users/91701/OneDrive/Documents/Final Year Project/SelfDriving/functionalities/data/yolov4_tiny.cfg')
net1.setPreferableBackend(cv.dnn.DNN_BACKEND_CUDA)
net1.setPreferableTarget(cv.dnn.DNN_TARGET_CUDA_FP16)
model1 = cv.dnn_DetectionModel(net1)
model1.setInputParams(size=(640, 480), scale=1/255, swapRB=True)

#defining the video source (0 for camera or file name for video)
#cap = cv.VideoCapture("pothole1.mp4") 
#width  = cap.get(3)
#height = cap.get(4)
#result = cv.VideoWriter('result.avi', cv.VideoWriter_fourcc(*'MJPG'),10,(int(width),int(height)))

#defining parameters for result saving and get coordinates
#defining initial values for some parameters in the script



Conf_threshold = 0.5
NMS_threshold = 0.4

i = 0
b = 0
# Define the region of interest (ROI) coordinates
roi_x = 0
roi_y = 200
roi_width = 640
roi_height = 400
#detection loop
def pothole_detection(frame):
    #frame_counter += 1
    min_area=500
    #analysis the stream with detection model
    curr_area=-1
    roi = frame[roi_y:roi_height, roi_x:roi_width]
    classes, scores, boxes = model1.detect(roi, Conf_threshold, NMS_threshold)
    data=9
    cv.rectangle(frame, (roi_x, roi_y), (roi_width, roi_height), (0, 0, 255), 2)
    for (classid, score, box) in zip(classes, scores, boxes):
        label = "pothole"
        x, y, w, h = box
        #y+=roi_y
        recarea = w*h
        area = frame.shape[0]*frame.shape[1]
        d1=abs(x-roi_x)
        d2=abs(640-x)

        #drawing detection boxes on frame for detected potholes
        if(len(scores)!=0 and scores[0]>=0.7):
            if((recarea/area)<=0.1 and box[1]<600):
                if recarea>min_area:
                    if d2>d1:
                        data=6
                    else:
                        data=3
                cv.rectangle(roi, (x, y), (x + w, y + h), (0,255,0), 1)
                cv.putText(roi, "%" + str(round(scores[0]*100,2)) + " " + label, (box[0], box[1]-10),cv.FONT_HERSHEY_COMPLEX, 0.5, (255,0,0), 1)
                frame[roi_y:roi_height, roi_x:roi_width]=roi
    return data
                
                
   
    #showing and saving result
    #cv.imshow('frame', frame)
    #result.write(frame)
    #key = cv.waitKey(1)
    #if key == ord('q'):
    #    break
    
#end
#cap.release()
#result.release()
#cv.destroyAllWindows()





