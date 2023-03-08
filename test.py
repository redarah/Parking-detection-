import cv2
import pickle
#import cvzone
import numpy as np
import psycopg2
import psycopg2.extras

# Video feed
cap = cv2.VideoCapture("carPark.mp4")

with open("CarParkPos", "rb") as f:
    posList = pickle.load(f)

width, height = 38, 97

# database connection details
hostname = 'localhost'
database = 'Car_detection'
username = 'postgres'
pwd = 'Glace82649'
port_id = 5432
conn = None

name = 'new.PNG'
num = '1'

empty = 'false'


def update_database(num, empty, total, free, full, name):
    
    conn = psycopg2.connect(
        host=hostname,
        dbname=database,
        user=username,
        password=pwd,
        port=port_id)
    cur = conn.cursor()
    update_script = 'UPDATE place SET is_empty = %s, total_place=%s, availabl_spot=%s, full_spot=%s, name=%s WHERE id =%s'
    value = (empty, total, free, full, name, num)
    cur.execute(update_script, value)
    conn.commit()



def checkParkingSpace(imgPro):
    spaceCounter = 0 
    freeCounter = 0
    occupiedCounter = 0

    for pos in posList:
        x, y = pos

        # diviser les images
        imgCrop = imgPro[y : y + height, x : x + width]
        count = cv2.countNonZero(imgCrop)

        if count < 1000:
            color = (0, 255, 0)  # green: free
            thickness = 5
            freeCounter += 1
            spaceCounter += 1
        else:
            color = (0, 0, 255)  # red: occupied
            thickness = 2
            occupiedCounter += 1
            spaceCounter += 1

        cv2.rectangle(img, pos, (pos[0] + width, pos[1] + height), color, thickness)
    
    update_database(num, empty, spaceCounter, freeCounter, occupiedCounter, name)

    cv2.putText(
        img,
        f"Free: {freeCounter}",
        (10, 30),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (0, 255, 0),
        2,
        cv2.LINE_AA,
    )

    cv2.putText(
        img,
        f"Occupied: {occupiedCounter}",
        (10, 70),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (0, 0, 255),
        2,
        cv2.LINE_AA,
    )

    cv2.putText(
        img,
        f"Total: {spaceCounter}",
        (10, 110),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (255, 255, 255),
        2,
        cv2.LINE_AA,
    )


# initialiser le compteur d'images
img_counter = 0
while True:

    if cap.get(cv2.CAP_PROP_POS_FRAMES) == cap.get(cv2.CAP_PROP_FRAME_COUNT):
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
    success, img = cap.read()
    imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    imgBlur = cv2.GaussianBlur(imgGray, (3, 3), 1)
    # make it black and white
    imgThreshold = cv2.adaptiveThreshold(
        imgBlur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 25, 16
    )
    # remove noise
    imgMedian = cv2.medianBlur(imgThreshold, 5)
    # make it a bit thiker
    kernel = np.ones((3, 3), np.uint8)
    imgDilate = cv2.dilate(imgMedian, kernel, iterations=1)

    checkParkingSpace(imgDilate)
    cv2.imshow("Image", img)
    # cv2.imshow("ImageBlur", imgBlur)
    cv2.imshow("ImageThres", imgMedian)
    cv2.waitKey(200)
