from numpy.lib.function_base import meshgrid
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import json
import shutil
import datetime, time
import os, sys

# from deepface import DeepFace
from deepface.commons import functions
from deepface.basemodels import Facenet

from deepface.extendedmodels import Emotion
from deepface.extendedmodels import Age
from deepface.extendedmodels import Gender
from deepface.extendedmodels import Race

import cv2
from keras.models import load_model
from keras.utils import CustomObjectScope

from utils.custom_objects import custom_objects

import tensorflow as tf
from numpy import dot
from numpy.linalg import norm


class DeepFace:

    def __init__(self):
        self.face_model = Facenet.loadModel()
        self.emotion_model = Emotion.loadModel()
        self.age_model = Age.loadModel()
        self.gender_model = Gender.loadModel()
        self.race_model = Race.loadModel()

    def get_face_emb(self, face_p):
        impre = functions.preprocess_face(img=face_p, detector_backend='mtcnn', target_size=(160, 160))
        query_face_emb = self.face_model.predict(impre)[0, :]

        impre = functions.preprocess_face(img=face_p, target_size=(48, 48), grayscale=True, detector_backend='mtcnn')
        query_emotion_emb = self.emotion_model.predict(impre)[0, :]

        impre = functions.preprocess_face(img=face_p, target_size=(224, 224), detector_backend='mtcnn')
        query_age_emb = self.age_model.predict(impre)[0, :]
        query_gender_emb = self.gender_model.predict(impre)[0, :]
        query_race_emb = self.race_model.predict(impre)[0, :]

        return [query_face_emb, query_emotion_emb, query_age_emb, query_gender_emb, query_race_emb]

class HairSeg:

    def __init__(self):

        model_path = './models/CelebA_DeeplabV3plus_256_hair_seg_model.h5'
        with CustomObjectScope(custom_objects()):
            self.hair_seg_model = load_model(model_path)

        shape_img = (218, 178, 3)
        self.vgg_model = tf.keras.applications.VGG19(weights='imagenet', include_top=False,
                                                input_shape=shape_img)

        self.input_shape_model = tuple([int(x) for x in self.vgg_model.input.shape[1:]])
        self.output_shape_model = tuple([int(x) for x in self.vgg_model.output.shape[1:]])

    def extract_hair(self, face_p, mask_p, hair_p):
        img = cv2.imread(face_p)
        img_shape = img.shape
        input_data = img.astype('float32')
        input_data = cv2.resize(img, (256,256))
        input_data = input_data / 255.
        input_data = (input_data - input_data.mean()) / input_data.std()
        input_data = np.expand_dims(input_data, axis=0)

        output = self.hair_seg_model.predict(input_data)

        mask = cv2.resize(output[0,:,:,0], (img_shape[1], img_shape[0]), interpolation=cv2.INTER_LINEAR)
        cv2.imwrite(mask_p, 255*mask)

        mask = cv2.imread(mask_p)
        final = cv2.bitwise_and(img, mask)
        cv2.imwrite(hair_p, final)

    def get_hair_emb(self, hair_p):
        hair = cv2.imread(hair_p)
        hair_transformed = [hair/255]
                                                
        X_hair = np.array(hair_transformed).reshape((-1,) + self.input_shape_model)
        E_hair = self.vgg_model.predict(X_hair)
        E_hair_flatten = E_hair.reshape((-1, np.prod(self.output_shape_model)))

        query_hair_emb = E_hair_flatten[0]
        return query_hair_emb

class ImgRetrieval:

    def __init__(self):

        with open('raw.json', 'r') as f:
            data = json.loads(f.read())
        temp_df = pd.DataFrame(data)

        self.f2t_dic = {}
        for i, row in temp_df.iterrows():
            self.f2t_dic[row['filename']] = row['description']
        
        self.face_emb = np.load('emb/face_emb.npy', allow_pickle=True)
        self.num_f2t = len(self.face_emb)
        self.dic_list_vgg = []

    def get_emb_dic(self, emb):
        dic = {}
        for ele in emb:
            dic[ele[0]] = ele[1]
        return dic

    def load_dic(self):
        face_dic = self.get_emb_dic(self.face_emb)

        emotion_dic = self.get_emb_dic(np.load('emb/emotion_emb.npy', allow_pickle=True))
        age_dic = self.get_emb_dic(np.load('emb/age_emb.npy', allow_pickle=True))
        gender_dic = self.get_emb_dic(np.load('emb/gender_emb.npy', allow_pickle=True))
        race_dic = self.get_emb_dic(np.load('emb/race_emb.npy', allow_pickle=True))

        hair_vgg_dic = self.get_emb_dic(np.load('emb/vgg_hair_emb.npy', allow_pickle=True))

        self.dic_list_vgg = [face_dic, emotion_dic, age_dic, gender_dic, race_dic, hair_vgg_dic]

    def cos_sim(self, query_emb, img, dic):
        return dot(query_emb, dic[img])/(norm(query_emb)*norm(dic[img]))

    def emb_score(self, query_embs):
        all_emb_sc = []
        for i in range(self.num_f2t):
            img = self.face_emb[i][0]
            row = [img]
            for j in range(6):
                row.append(self.cos_sim(query_embs[j], img, self.dic_list_vgg[j]))
            all_emb_sc.append(row)
        
        return all_emb_sc

    def total_score(self, row, coe_ls):
        sc = 0
        for i in range(len(coe_ls)):
            sc += coe_ls[i] * row[i+1]
        return sc

    def normalize_col(self, df, col):
        mean = df[col].mean()
        std = df[col].std()
        df[col] = df[col].apply(lambda x: (x-mean)/std)

    def find_images(self, query_embs, coe_ls, max_n=5):

        df = pd.DataFrame(self.emb_score(query_embs))

        # normal
        for i in range(1, 7):
            self.normalize_col(df, i)

        # total score
        df['score'] = df.apply(lambda x: self.total_score(x, coe_ls), axis=1)
        
        return df.nlargest(max_n, 'score')[0].to_list()


print(datetime.datetime.now())
print('DeepFace')
face = DeepFace()

print('HairSeg')
hair = HairSeg()

print('ImgRetrieval')
imgRe = ImgRetrieval()
imgRe.load_dic()

print('--------------')

query_embs = face.get_face_emb('shots/test.jpg')
hair.extract_hair('shots/test.jpg', 'shots/test_mask.jpg', 'shots/test_hair.jpg')
query_embs.append(hair.get_hair_emb('shots/test_hair.jpg'))

coe_ls = [0.8, 0.2, 0.25, 0.02, 0.3, 1.5]
results = imgRe.find_images(query_embs, coe_ls, max_n=5)
print(results)