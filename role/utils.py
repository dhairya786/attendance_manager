
import cv2
import numpy as np
from attendance_management.settings import BASE_DIR
# Load HAAR face classifier


def face_extractor(img,face_classifier):
    # Function detects faces and returns the cropped face
    # If no face detected, it returns the input image

    #gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    faces = face_classifier.detectMultiScale(img, 1.3, 5)

    if faces is ():
        return None

    # Crop all faces found
    for (x,y,w,h) in faces:
        x=x-10
        y=y-10
        cropped_face = img[y:y+h+50, x:x+w+50]

    return cropped_face





def facestore(request):
    face_classifier = cv2.CascadeClassifier(r'%s/media/haarcascade_frontalface_default.xml' %(BASE_DIR))
    print(face_classifier)
    print('wow')
    # Load functions
    

    # Initialize Webcam
    cap = cv2.VideoCapture(0)
    count = 0

    # Collect 100 samples of your face from webcam input
    while True:
        ret, frame = cap.read()
        if face_extractor(frame,face_classifier) is not None:
            count += 1
            face = cv2.resize(face_extractor(frame,face_classifier), (400, 400))
            #face = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY)

            # Save file in specified directory with unique name
            cv2.imwrite(r'/Users/dhairyaahuja/Desktop/image/User.'+ str(1) + '.' + str(count) + ".jpg", face)
            print('found ' + str(count))
            # Put count on images and display live count
            cv2.putText(face, str(count), (50, 50), cv2.FONT_HERSHEY_COMPLEX, 1, (0,255,0), 2)
            cv2.imshow('Face Cropper', face)
        
        else:
            print("Face not found")
            pass

        if cv2.waitKey(1) == 13 or count == 30: 
            break
            
    cap.release()
    cv2.destroyAllWindows()      
    print("Collecting Samples Complete")






