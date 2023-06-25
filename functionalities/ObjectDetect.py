import cv2
import numpy as np
import time,pickle
#from server import *
#thres = 0.45 # Threshold to detect object

classNames = []
classFile = "C:/Users/91701/OneDrive/Documents/Final Year Project/SelfDriving/functionalities/data/coco.names"
with open(classFile,"rt") as f:
    classNames = f.read().rstrip("\n").split("\n")

configPath = "C:/Users/91701/OneDrive/Documents/Final Year Project/SelfDriving/functionalities/data/ssd_mobilenet_v3_large_coco_2020_01_14.pbtxt"
weightsPath = "C:/Users/91701/OneDrive/Documents/Final Year Project/SelfDriving/functionalities/data/frozen_inference_graph.pb"

net = cv2.dnn_DetectionModel(weightsPath,configPath)
net.setInputSize(320,320)
net.setInputScale(1.0/ 127.5)
net.setInputMean((127.5, 127.5, 127.5))
net.setInputSwapRB(True)

#using GPU
net.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)


def calculate_distance_cm( frame, cord):
        obj_points = np.float32([[0, 0, 0], [0, 1, 0], [1, 1, 0], [1, 0, 0]])
#np.float32([[0, 0, 0], [0, 100, 0], [100, 100, 0], [100, 0, 0]])
        image_points = np.float32([[cord[0], cord[1]], [cord[2], cord[1]], [cord[2], cord[3]], [cord[0], cord[3]]])
        camera_matrix = np.float32([[600, 0, frame.shape[1] / 2], [0, 600, frame.shape[0] / 2], [0, 0, 1]])
        dist_coeffs = np.zeros((4, 1))
        _, rvecs, tvecs = cv2.solvePnP(obj_points, image_points, camera_matrix, dist_coeffs)
        tvec = tvecs.flatten()
        distance = np.linalg.norm(tvec) / 10.0  # Convert distance to centimeters
        return distance

def getObjects(img, thres, nms, draw=True, objects=[]):
    classIds, confs, bbox = net.detect(img,confThreshold=thres,nmsThreshold=nms)
    #print(classIds,bbox)
    min_distance=1000000
    all_objects=False
    min_area=0
    if len(objects) == 0: objects = classNames
    objectInfo =[]
    all_objects=False
    if len(classIds) != 0:
        all_objects=True
        for classId, confidence,box in zip(classIds.flatten(),confs.flatten(),bbox):
            className = classNames[classId - 1]
            if className in objects:
                objectInfo.append([box,className])
                if (draw):
                    cv2.rectangle(img,box,color=(0,255,0),thickness=2)
                    dist=calculate_distance_cm(img,box)
                    if dist<min_distance:
                         min_distance=dist
                         min_area=box[2]*box[3]
                    #dist=1
                    cv2.putText(img,classNames[classId-1].upper()+" dist="+str(round(dist,2)),(box[0]+10,box[1]+30),
                    cv2.FONT_HERSHEY_COMPLEX,1,(0,255,0),2)
                    #print(box[2]*box[3])
                    #cv2.putText(img,str(round(confidence*100,2)),(box[0]+200,box[1]+30),cv2.FONT_HERSHEY_COMPLEX,1,(0,255,0),2)
    results={'objects':all_objects,'distance':min_distance,'area':min_area}
    return img,results

def send_obj(data,server):
    if data is not None and data["objects"] and (data["distance"]<0.5):
        msg={"mode":"auto","function":"object"}
    else:
        msg={"mode":"auto","function":"no object"}
    msg=pickle.dumps(msg)
    msg=bytes(f"{len(msg):<10}","utf-8")+msg
    server.send(msg)

def identify_obj():
    
    cap = cv2.VideoCapture('http://192.168.1.4:5000/video_feed')
    cap.set(3,640)
    cap.set(4,480)
    #cap.set(10,70)
    frame_count=0
    start_time=time.time()

    while True:

        
        success, img = cap.read()
        result, objectInfo = getObjects(img,0.65,0.2, objects=[])#['person','car'])
        #print(objectInfo)
        
        frame_count += 1
        elapsed_time = time.time() - start_time
        fps = frame_count / elapsed_time

        fps_text = f"FPS: {fps:.2f}"
        cv2.putText(img, fps_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.imshow("Output",img)
        if cv2.waitKey(1) == ord('q'):
            closeSocket()
            break


if __name__ == "__main__":
    identify_obj()