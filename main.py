import cv2
import pickle
import numpy as np
import psycopg2
import psycopg2.extras
import time
import os
from PIL import Image
import datetime

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

num = '1'
empty = 'false'

# variable to store previous free and occupied counts
prev_free_count = 0
prev_occupied_count = 0

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

def checkParkingSpace(imgPro, img):
    global prev_free_count, prev_occupied_count
    # timestamp = datetime.datetime.now()
    timestamp = str(time.time()).replace(".", "")

    spaceCounter = 0 
    freeCounter = 0
    occupiedCounter = 0

    filename = ""

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
    
    # initialiser un compteur
    counter = 0
    
    # dans la boucle de détection des places de stationnement
    if freeCounter != prev_free_count or occupiedCounter != prev_occupied_count:
        # incrémenter le compteur
        counter += 1
        # prendre une capture d'écran
        #timestamp = str(time.time()).replace(".", "")
        filename = f"screenshot_{timestamp}_{counter}.png"
        cv2.imwrite(filename, img)
        
        # sauvegarder la capture d'écran dans un répertoire
        photo = Image.open(filename)
        os.chdir('C:/Users/Owner/Desktop/automne 2022/capstone/version 2/Symfony/public/assets/uploads')
        photo.save(filename)
        update_database(num, empty, spaceCounter, freeCounter, occupiedCounter, filename)
        
        #mettre à jour les valeurs de comptage précédentes
        prev_free_count = freeCounter
        prev_occupied_count = occupiedCounter
    
    

    

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




while True:
    if cap.get(cv2.CAP_PROP_POS_FRAMES) == cap.get(cv2.CAP_PROP_FRAME_COUNT):
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
    success, img = cap.read()
    if not success:
        break

    imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    imgBlur = cv2.GaussianBlur(imgGray, (3, 3), 1)

    # Appliquer le seuillage adaptatif pour transformer l'image en noir et blanc
    imgThreshold = cv2.adaptiveThreshold(
        imgBlur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 25, 16
    )

    # Supprimer le bruit de l'image
    imgMedian = cv2.medianBlur(imgThreshold, 5)

    # Ajouter un peu d'épaisseur aux contours pour mieux les détecter
    kernel = np.ones((3, 3), np.uint8)
    imgDilate = cv2.dilate(imgMedian, kernel, iterations=1)

    # Appeler la fonction pour détecter les places de stationnement
    checkParkingSpace(imgDilate, img)

    # Afficher l'image avec les contours des places de stationnement
    cv2.imshow("Parking Lot Detection", img)

    # Attendre 200ms avant de passer à l'image suivante
    if cv2.waitKey(200) & 0xFF == ord("q"):
        break

# Libérer la capture vidéo et fermer toutes les fenêtres
cap.release()
cv2.destroyAllWindows()

