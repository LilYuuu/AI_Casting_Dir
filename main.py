from numpy.lib.function_base import meshgrid
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import json
import shutil
import datetime, time
import os, sys

from pandas.core.base import NoNewAttributesMixin

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

import random
import torch
from transformers import AutoConfig, AutoTokenizer
from transformers import AutoModelForCausalLM


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

    def find_images(self, query_embs, coe_ls, max_n=1):

        df = pd.DataFrame(self.emb_score(query_embs))

        # normal
        for i in range(1, 7):
            self.normalize_col(df, i)

        # total score
        df['score'] = df.apply(lambda x: self.total_score(x, coe_ls), axis=1)
        
        return df.nlargest(max_n, 'score')[0].to_list()

class ImgRetrieval_MovieChar:

    def __init__(self):
        self.face_emb = np.load('emb_movie/face_emb.npy', allow_pickle=True)
        self.num_char = len(self.face_emb)
        self.dic_list_vgg = []

    def get_emb_dic(self, emb):
        dic = {}
        for ele in emb:
            dic[ele[0]] = ele[1]
        return dic

    def load_dic(self):
        face_dic = self.get_emb_dic(self.face_emb)

        emotion_dic = self.get_emb_dic(np.load('emb_movie/emotion_emb.npy', allow_pickle=True))
        age_dic = self.get_emb_dic(np.load('emb_movie/age_emb.npy', allow_pickle=True))
        gender_dic = self.get_emb_dic(np.load('emb_movie/gender_emb.npy', allow_pickle=True))
        race_dic = self.get_emb_dic(np.load('emb_movie/race_emb.npy', allow_pickle=True))

        hair_vgg_dic = self.get_emb_dic(np.load('emb_movie/vgg_hair_emb.npy', allow_pickle=True))

        self.dic_list_vgg = [face_dic, emotion_dic, age_dic, gender_dic, race_dic, hair_vgg_dic]

    def cos_sim(self, query_emb, img, dic):
        return dot(query_emb, dic[img])/(norm(query_emb)*norm(dic[img]))

    def emb_score(self, query_embs):
        all_emb_sc = []
        for i in range(self.num_char):
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
        
        return df.nlargest(max_n, 'score')[0].to_list(), df.nlargest(max_n, 'score')['score'].to_list()

class ScriptGPT:

    def __init__(self):

        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        seed = 42
        random.seed(seed)
        np.random.seed(seed)
        torch.manual_seed(seed)

        self.sum_config = AutoConfig.from_pretrained('gpt2_model/')
        
        self.sum_tokenizer = AutoTokenizer.from_pretrained('gpt2_model/')
        self.sum_tokenizer.add_special_tokens({'pad_token': '[PAD]'})
        self.sum_tokenizer.add_special_tokens({'sep_token': '[SEP]'})
        self.sum_tokenizer.model_max_length = 256

        self.gpt2_movie = AutoModelForCausalLM.from_pretrained('gpt2_model/')
        self.gpt2_movie.to(self.device)

print(datetime.datetime.now())
print('DeepFace')
face = DeepFace()

print('HairSeg')
hair = HairSeg()

print('ImgRetrieval')
imgRe = ImgRetrieval()
imgRe.load_dic()

charRe = ImgRetrieval_MovieChar()
charRe.load_dic()

print('ScriptGPT')
script = ScriptGPT()

print('--------------')


# query_embs = face.get_face_emb('shots/test.jpg')
# hair.extract_hair('shots/test.jpg', 'shots/test_mask.jpg', 'shots/test_hair.jpg')
# query_embs.append(hair.get_hair_emb('shots/test_hair.jpg'))

# coe_ls = [0.8, 0.2, 0.25, 0.02, 0.3, 1.5]
# results, scores = charRe.find_images(query_embs, coe_ls)
# print(results)

# fig, axs = plt.subplots(1, 6, figsize=(15, 9))
# im = plt.imread('shots/test.jpg')
# axs[0].imshow(im)
# for i in range(5):
#     im = plt.imread('static/movie_char/' + results[i])
#     axs[i+1].imshow(im)

# plt.show()

'''
fn = results[0]
# inputs = sum_tokenizer(imgRe.f2t_dic[fn], add_special_tokens=False, return_tensors='pt')
input_1st_sent = imgRe.f2t_dic[fn].split('.')[0]
inputs = script.sum_tokenizer(input_1st_sent, add_special_tokens=False, return_tensors='pt')

input_ids = inputs.input_ids.to(script.device)
bad_words_ids = [script.sum_tokenizer(bad_word).input_ids for bad_word in ["EXT.", "INT.", "CONT'D", "CUT"]]
forced_eos_token_id = script.sum_tokenizer('.').input_ids
result = script.gpt2_movie.generate(input_ids=input_ids, no_repeat_ngram_size=2, do_sample=True, max_length=120, early_stopping=True, num_beams=10, repetition_penalty=1.2, bad_words_ids=bad_words_ids, forced_eos_token_id=forced_eos_token_id)
print('.'.join(script.sum_tokenizer.batch_decode(result)[0].split('.')[:-2])+ '.')
'''

from flask import Flask, render_template, Response, request
from threading import Thread

global capture, rec_frame, switch, out 
capture=0
switch=1

global msg, char_lst, scores
msg = None
char_lst = None
scores = None


#instatiate flask app  
app = Flask(__name__, template_folder='./templates')

camera = cv2.VideoCapture(0)

def crop(frame):
    w = 178*3
    h = 218*3
    startX = int((1280-w)/2)
    endX = int(startX+w)
    startY = int((720-h)/2)
    endY = int(startY+h)
    try:
        # frame = cv2.rectangle(frame, (startX, startY), (endX, endY), (255,255,255), 2)
        frame=frame[startY:endY, startX:endX]
    except Exception as e:
        pass
    return frame

def gen_frames():  # generate frame by frame from camera
    global out, capture, rec_frame
    while True:
        success, frame = camera.read() 
        if success:              
            frame= crop(frame)

            if(capture):
                capture=0
                print(datetime.datetime.now())
                # p = os.path.sep.join(['shots', "shot_{}.jpg".format(str(now).replace(":",''))])
                p = 'shots/test.jpg'
                resize_frame=cv2.resize(frame, (178, 218))
                cv2.imwrite(p, resize_frame)
                
            try:
                ret, buffer = cv2.imencode('.jpg', cv2.flip(frame,1))
                frame = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            except Exception as e:
                pass
                
        else:
            pass


@app.route('/')
def index():
    global msg, char_lst, scores
    return render_template('index.html', msg=msg, char_lst=char_lst, scores=scores)
    
@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/requests',methods=['POST','GET'])
def tasks():
    global switch, camera, msg, char_lst, scores
    if request.method == 'POST':
        if request.form.get('click') == 'Capture':
            global capture
            capture=1
            msg='Captured' 
            char_lst = None
            scores = None

        elif request.form.get('ml') == 'RunML':

            print('RunML')
            query_embs = face.get_face_emb('shots/test.jpg')
            hair.extract_hair('shots/test.jpg', 'shots/test_mask.jpg', 'shots/test_hair.jpg')
            query_embs.append(hair.get_hair_emb('shots/test_hair.jpg'))

            coe_ls = [0.8, 0.2, 0.25, 0.02, 0.3, 1.5]
            results, scores = charRe.find_images(query_embs, coe_ls, max_n=5)
            char_lst = ['/static/movie_char/' + fn for fn in results]

            coe_ls = [0.8, 0.2, 0.25, 0.02, 0.3, 1.5]
            results = imgRe.find_images(query_embs, coe_ls)

            fn = results[0]
            input_1st_sent = imgRe.f2t_dic[fn].split('.')[0]
            inputs = script.sum_tokenizer(input_1st_sent, add_special_tokens=False, return_tensors='pt')

            input_ids = inputs.input_ids.to(script.device)
            bad_words_ids = [script.sum_tokenizer(bad_word).input_ids for bad_word in ["EXT.", "INT.", "CONT'D", "CUT"]]
            forced_eos_token_id = script.sum_tokenizer('.').input_ids

            result = script.gpt2_movie.generate(input_ids=input_ids, no_repeat_ngram_size=2, do_sample=True, max_length=120, early_stopping=True, num_beams=10, repetition_penalty=1.2, bad_words_ids=bad_words_ids, forced_eos_token_id=forced_eos_token_id)
            
            msg = '.'.join(script.sum_tokenizer.batch_decode(result)[0].split('.')[:-2])+ '.'
            msg = msg.replace('\n', '<br>')
            return render_template('index.html', msg=msg, char_lst=char_lst, scores=scores)

                 
    elif request.method=='GET':
        return render_template('index.html', msg=msg, char_lst=char_lst, scores=scores)
    return render_template('index.html', msg=msg, char_lst=char_lst, scores=scores)


if __name__ == '__main__':
    app.run()
    
camera.release()
cv2.destroyAllWindows()    