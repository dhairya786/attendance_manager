import cv2
import numpy as np
import base64
from .models import * 
import datetime
from attendance_management.settings import BASE_DIR
from io import BytesIO
import matplotlib.pyplot as plt
import seaborn as sns
import tensorflow as tf
from tensorflow import keras
from attendance_management.settings import BASE_DIR
import os
import face_recognition
import time
# Load HAAR face classifier


def face_extractor(img,face_classifier):
    # Function detects faces and returns the cropped face
    # If no face detected, it returns the input image

    #gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    faces = face_classifier.detectMultiScale(img, 1.3, 5)

    if faces == ():
        return None

    # Crop all faces found
    for (x,y,w,h) in faces:
        x=x-10
        y=y-10
        cropped_face = img[y:y+h+50, x:x+w+50]

    return cropped_face





def face(request):
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
            cv2.imwrite(r'%s/media/image/User.' %(BASE_DIR)+ str(1) + '.' + str(count) + ".jpg", face)
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

def maxIndex(arr):
    maxx = 0
    for idx,a in enumerate(arr):
        if a>maxx:
            maxx=a
            sol = idx
    return sol
    
def take(request):
    res = set()
    print('here')
    IMAGE_DESTINATION_DIR = r'%s/media/data/train'%(BASE_DIR)
    mypk = request.user.pk
    mylist = os.listdir(IMAGE_DESTINATION_DIR)
    print(mylist)
    model = keras.models.load_model(r'%s/saved_models/XceptionModel_10epo'%BASE_DIR)
    cap = cv2.VideoCapture(0)
    num_of_pictures = 5
    while True:
        if num_of_pictures==0:    break
        ret, frame = cap.read()

        face_locations = face_recognition.face_locations(frame)
        for top,right,bottom,left in (face_locations):
            face = frame[top:bottom, left:right]
            img = cv2.resize(face,(224,224))
            img = img.astype(np.float32)
            img = img/255
            img = np.expand_dims(img,axis=0)
            pred = maxIndex(model.predict(img)[0])
            res.add(int(mylist[pred+1]))
            #cv2.rectangle(frame, (right,top), (left,bottom), (255, 0, 0), 2)
            cv2.putText(frame,str(pred),(right,top),cv2.FONT_HERSHEY_SIMPLEX,1,(255, 255, 255),2)
        name = str(mypk) + '_' + str(num_of_pictures)+'.jpg'
        path1 = (r'%s/role/static/role/attendance_pics/'%BASE_DIR)
        path = (r'%s/media/attendance_pics/'%BASE_DIR)
        path2 = '/attendance_pics/' + name
        cv2.imwrite(os.path.join(path,name),frame)
        teach = Teacher.objects.filter(user=request.user)[0]
        att = Attendancepic.objects.filter(teacher=teach,number=num_of_pictures,image=path2)
        if att.count()==0:
            Attendancepic.objects.create(teacher=teach,number=num_of_pictures,image=path2)
        else:
            att[0].image = frame
            print('here')
        cv2.imshow('frame', frame)
        if cv2.waitKey(2000) & 0xFF == ord('q'):
            cv2.destroyAllWindows()

        num_of_pictures-=1
    print(res)

    students = []
    teacher = Teacher.objects.filter(user=request.user)[0]
    cc = Course.objects.filter(teacher_assigned=teacher)[0]
    d = datetime.datetime.now().date()
    for p in res:
        print(p)
        p=p+1
        user = User.objects.get(pk=p)
        s = Student.objects.filter(user=user)[0]
        print(s)
        att = Attendance.objects.filter(student = s,course = cc)[0]
        det = AttendanceDetail.objects.filter(attendance_field=att,date__year = d.year,date__month = d.month,date__day = d.day)
        if(det.count()== 0):
            obj = AttendanceDetail.objects.create(attendance_field=att,date = d,status = True)
            obj.save()
        else:
            oo = det.last()
            oo.status = True
            oo.save()
        det = AttendanceDetail.objects.filter(attendance_field=att)
        count=0
        tot = 0
        for obj in det:
            if obj.status:
                count = count+1
            tot = tot+1
        att.class_attended = count
        att.total_classes = tot
        att.save()
    print(res)
    


def facestore(request):
    PERSON_NAME = str(request.user.pk)  # TODO: C H A N G E    T H I S   N A M E
    TYPE = "train"  # TODO: C H A N G E    T H I S   T Y P E (test or train)

    IMAGE_DESTINATION_DIR = r'%s/media/data/train'%(BASE_DIR)
    CASCADE = cv2.CascadeClassifier(r'%s/cascades/data/haarcascade_frontalface_default.xml' %(BASE_DIR))

    if not os.path.exists(os.path.join(IMAGE_DESTINATION_DIR, PERSON_NAME)):
        des = os.path.join(IMAGE_DESTINATION_DIR, PERSON_NAME)
        # grey_des = os.path.join(des,'grey')
        # color_des = os.path.join(des,'color')

        os.makedirs(des)
        # os.makedirs(grey_des)
        # os.makedirs(color_des)

        cap = cv2.VideoCapture(0)
        run = True
        k = 0
        while run:
            _, color = cap.read()
            grey = cv2.cvtColor(color, cv2.COLOR_BGR2GRAY)

            face = CASCADE.detectMultiScale(grey, 1.3, 5)

            for (x, y, w, h) in face:
                # roi_grey = grey[y:y+h,x:x+w]
                roi_color = color[y:y + h, x:x + w]

                # roi_grey=cv2.resize(roi_grey,(224,224))
                roi_color = cv2.resize(roi_color, (224, 224))

                im_name = f'imag{k}.jpg'
                # cv2.imwrite(os.path.join(grey_des,im_name),roi_grey)
                cv2.imwrite(os.path.join(des, im_name), roi_color)
                k += 1

            cv2.imshow('lol', color)
            cv2.waitKey(10)
            if TYPE == 'train' and k == 30:
                run = False
            elif TYPE == 'test' and k == 50:
                run = False

        print("ALL IMAGES HAVE BEEN TAKEN")

    else:
        print("DIRECTORY ALREADY EXISTS, DELETE IT FIRST")



def get_attendance_from_id(val):
    att = AttendanceDetail.objects.get(id=val)
    return att


def get_graph():
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    graph = base64.b64encode(image_png)
    graph = graph.decode('utf-8')
    buffer.close()
    return graph

def get_chart(chart_type, data, results_by, **kwargs):
    plt.switch_backend('AGG')
    fig = plt.figure(figsize=(10, 4))
    key = results_by
    d = data
    if chart_type == '#1':
        print('bar chart')
        #plt.bar(d[key], da['total_price'])
        sns.barplot(x=key, y='status', data=d)
    elif chart_type == '#2':
        print('pie chrt')
        plt.pie(data=d, x='status', labels=d[key].values)
    elif chart_type == '#3':
        print('line chart')
        plt.plot(d[key], d['status'],
                 color='green', marker='o', linestyle='dashed')
    else:
        print('ups...failed o identify the chart type')
    plt.tight_layout()
    chart = get_graph()
    return chart



