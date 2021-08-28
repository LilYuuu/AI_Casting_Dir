from numpy.lib.function_base import meshgrid
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import json
import shutil
import datetime, time
import os, sys

import cv2

from flask import Flask, render_template, Response, jsonify

####################################
############### FLASK ##############
####################################    

def crop(frame):
    ori_w = frame.shape[1]
    ori_h = frame.shape[0]
    frame=cv2.resize(frame, (int(ori_w*480/ori_h), 480))
    print(frame.shape)

    w = 178*2
    h = 218*2
    startX = int((frame.shape[1]-w)/2)
    endX = int(startX+w)
    startY = int((frame.shape[0]-h)/2)
    endY = int(startY+h)
    
    return frame[startY:endY, startX:endX]

# def gen_frames():  # generate frame by frame from camera
#     global capture, camera
#     camera = cv2.VideoCapture(0)

#     while True:
#         success, frame = camera.read() 
#         if success:              
#             frame= crop(frame)

#             if(capture):
#                 capture=0
#                 print(datetime.datetime.now())
#                 # p = os.path.sep.join(['shots', "shot_{}.jpg".format(str(now).replace(":",''))])
#                 p = 'static/shots/photo.jpg'
#                 resize_frame=cv2.resize(frame, (178, 218))
#                 cv2.imwrite(p, resize_frame)

#                 # turn off camera
#                 camera.release()
#             try:
#                 ret, buffer = cv2.imencode('.jpg', cv2.flip(frame,1))
#                 frame = buffer.tobytes()
#                 yield (b'--frame\r\n'
#                        b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
#             except Exception as e:
#                 pass
                
#         else:
#             pass


global capture, camera
capture=0

#instatiate flask app  
app = Flask(__name__, template_folder='./templates')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/capture', methods=['GET', 'POST'])
def capture():
    return render_template('capture.html')
    
# @app.route('/video_feed')
# def video_feed():
#     return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

# background process happening without any refreshing
@app.route('/result', methods=['GET', 'POST'])
def result():

    # TAKE A PHOTO
    camera = cv2.VideoCapture(0)
    success, frame = camera.read()

    if success:
        frame= crop(frame)
        print(frame.shape)

        p = 'static/shots/photo.jpg'
        resize_frame=cv2.resize(frame, (178, 218))
        cv2.imwrite(p, resize_frame)

        # turn off camera
        camera.release()
    else:
        pass

    # MACHINE LEARNING
    
    char_lst = ['/static/movie_char/asian_366.jpg', '/static/movie_char/asian_283.jpg', '/static/movie_char/86.jpg', '/static/movie_char/asian_382.jpg', '/static/movie_char/asian_166.jpg', '/static/movie_char/latin_108.jpg', '/static/movie_char/midEast_68.jpg', '/static/movie_char/83.jpg', '/static/movie_char/latin_157.jpg', '/static/movie_char/105.jpg', '/static/movie_char/578.jpg']
    scores = [6.086907718421764, 5.153456317607482, 4.577737596041771, 4.572096871313132, 4.501126827569908, 0.10255539132035124, -1.5061899593218946, -1.2092001622091804, -6.718977960861039, -3.8970722108017997, -3.9102703622803556]

    msg = 'The images on the papel picado come to life to illustrate a \n father, a mother, and a little girl. The family is happy. \n\n MIGUEL (V.O.) \n The pap, he was a musician.\n\nThe pap plays guitar while the mother dances with her\ndaughter.'
    msg = msg.replace('\n', '<br>')

    # time.sleep(2)
    return render_template('result.html', msg=msg, char_lst=char_lst, scores=scores)

if __name__ == '__main__':
    app.run()
    
# camera.release()
# cv2.destroyAllWindows()    