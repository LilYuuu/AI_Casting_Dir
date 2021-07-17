# AI_Casting_Dir

Make sure you have python3 installed. If not, go to https://www.python.org/downloads/ and download the installer (.

## Step 1: Download files

1. Download/clone this github repository "AI_Casting_Dir"
2. Download models and embeddings from https://drive.google.com/file/d/1ZS3I7xaIpKluNQi7MOsj8pvQE6t-wjwb/view?usp=sharing 
3. Unzip the supplement file. You should see five folders. Move them into the "AI_Casting_Dir" folder.

## Step 2: Set up the environment
    
1. Open a terminal window.

2. Go to your user folder by using this command line in your terminal
```
cd /Users/user123
```

3. Drag the file named "setup.sh" into your terminal. You should see the path to the file. Hit enter. 
```
{{path}}/AI_Casting_Dir/setup.sh 
```
This will start installing all the packages needed to run the project in a virtual environment.

## Step 3: Run

1. After the installation finishes, activate the virtual environment
```
. venv/bin/activate
```

2. Run the main python script. 
``` 
python3 main.py
```
This will start the server. Wait for a few minutes until you see "Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)" in the terminal. 

3. Open a browser window and go to http://127.0.0.1:5000/. You should be able to run the project now.

## Step 4: Stop / Restart

* To stop the server, press "control + C".

* To restart the server, press "control + C" and run the main script again.
``` 
python3 main.py
```

* To deactivate the virtual env, use:
```
deactivate
```
