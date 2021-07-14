#!/bin/sh

#create a new virtual environment
python3 -m venv venv

#activate the virtual env
. venv/bin/activate

pip install opencv-python==4.5.1.48
pip install tensorflow==2.3.0
pip install keras==2.4

#install deepface
pip install deepface

#install other packages
pip install torch
pip install transformers
pip install matplotlib

# replace old deepface
rm -r venv/lib/python3.8/site-packages/deepface
cp -r deepface venv/lib/python3.8/site-packages