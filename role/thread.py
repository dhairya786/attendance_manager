import threading
from attendance_management.settings import BASE_DIR
import os
import cv2
import numpy as np
import base64
import tensorflow 
from glob import glob
import os
from tensorflow import keras
from .models import AttendanceDetail 
from keras.applications.vgg16 import VGG16,preprocess_input
from keras.applications import Xception
#from keras.models import Model
from keras.layers import Input, Lambda, Dense, Flatten
from keras.preprocessing import image
from keras.preprocessing.image import ImageDataGenerator
import cv2
import numpy as np
from .models import *
from io import BytesIO
import datetime
from django.core.mail import send_mail

class Makedataset(threading.Thread):

	def run(self):
		try:
			INPUT_SHAPE = [224,224,3]
			xc = Xception(include_top =False,input_shape = INPUT_SHAPE,weights = 'imagenet')
			for layer in xc.layers:    
				layer.trainable = False
			temp =  r'%s/media/data/train/*'%(BASE_DIR)
			temp1 =  r'%s/media/data/train'%(BASE_DIR)
			no_of_categories = len(glob(temp))
			print(no_of_categories)
			flatten = Flatten()(xc.output)
			last_layer = Dense(no_of_categories,activation = 'softmax')(flatten)
			custom_model = tensorflow.keras.Model(inputs = xc.input, outputs = last_layer)
			custom_model.compile(loss = 'categorical_crossentropy',
			        optimizer = "adam",
			        metrics = ['accuracy'])
			train_datagen = ImageDataGenerator(rescale = 1./255, 
			                      shear_range = 0.2,
			                      zoom_range = 0.2,
			                      horizontal_flip = True)
			test_datagen = ImageDataGenerator(rescale = 1./255)

			train = train_datagen.flow_from_directory(temp1,
			                             target_size = (224,224),
			                             batch_size = 32,
			                             class_mode = 'categorical')
			custom_model.fit_generator(train,epochs=10,steps_per_epoch=len(train))
			custom_model.save(r'%s/saved_models/XceptionModel_10epo'%BASE_DIR)
		except Exception as e:
			print(e)


class Sendmail(threading.Thread):

	def __init__(self,teacher):
		self.teacher = teacher
		threading.Thread.__init__(self)

	def run(self):
		try:
			print('heyyy')
			#teacher = Teacher.objects.filter(user=request.user)[0]
			b= Batch.objects.filter(teacher = self.teacher)
			cc = Course.objects.filter(teacher_assigned=self.teacher)[0]
			students = []
			batches= []
			d = datetime.datetime.now().date()
			for bb in b:
				for s in bb.student.all():
				    students.append(s)
			for s in students:
				att = Attendance.objects.filter(student = s,course = cc)[0]
				det = AttendanceDetail.objects.filter(attendance_field=att,date__year = d.year,date__month = d.month,date__day = d.day)
				if det.count()!=0:
					if det.last().status:
						send_mail('Greetings','Your attendance has been successfully marked.','dhairyaa315@gnail.com',[s.email],fail_silently = False)
					else:
						send_mail('Greetings','Your attendance has not been marked. Present in the class?? Contact your teacher for manual attendance','dhairyaa315@gnail.com',[s.email],fail_silently = False)
		except Exception as e:
			print(e)


