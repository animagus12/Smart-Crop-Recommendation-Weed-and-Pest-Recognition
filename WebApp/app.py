from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
import numpy as np
from keras.models import load_model
from pickle import load
from API import *
import sys, os
import cv2
from werkzeug.utils import secure_filename
import tensorflow as tf
from tensorflow.keras.models import load_model

model = load_model('CropRecommend.h5')
scaler = load(open('scaler.pkl', 'rb'))

helper = {
        0 : 'Apple',
        1 : 'Banana',
        2 : 'Blackgram',
        3 : 'Chickpea',
        4 : 'Coconut',
        5 : 'Coffee',
        6 : 'Cotton',
        7 : 'Grapes',
        8 : 'Jute',
        9 : 'KidneyBeans',
        10 : 'Lentil',
        11 : 'Maize',
        12 : 'Mango',
        13 : 'Mothbeans',
        14 : 'Mungbean',
        15 : 'Muskmelon',
        16 : 'Orange',
        17 : 'Papaya',
        18 : 'Pigeonpeas',
        19 : 'Pomegranate',
        20 : 'Rice',
        21 : 'Watermelon',
}

weeds = {
    0: "Black-grass",
    1: "Charlock",
    2: "Cleavers",
    3: "Common Chickweed",
    4: "Common wheat",
    5: "Fat Hen",
    6: "Loose Silky-bent",
    7: "Maize",
    8: "Scentless Mayweed",
    9: "Shepherd's Purse",
    10: "Small-flowered Cranesbill",
    11: "Sugar beet",
}

pests = {
    0: 'aphids',
    1: 'armyworm',
    2: 'beetle',
    3: 'bollworm',
    4: 'grasshopper',
    5: 'mites',
    6: 'mosquito',
    7: 'sawfly',
    8: 'stem_borer',
}

app = Flask(__name__)

app.secret_key = " key"

# Enter your database connection details below
app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = "admin"
app.config["MYSQL_DB"] = "LOGIN"

# Intialize MySQL
mysql = MySQL(app)

@app.route("/auth/<string:register>/", defaults={'register' : 'login'}, methods=["GET", "POST"])    
@app.route("/auth/<string:register>/", methods=["GET", "POST"])
def auth(register):
    if(register == 'login'):
        # Output message if something goes wrong...
        loginMsg = ''
        if (request.method == "POST" and "username" in request.form and "password" in request.form):
            # Create variables for easy access
            username = request.form["username"]
            password = request.form["password"]

            if(username == "" and password == ""):
                loginMsg = ""
            
            # Check if form exists using MySQL
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute(
                "SELECT * FROM form WHERE username = %s AND password = %s",
                (
                    username,
                    password,
                ),
            )

            if account := cursor.fetchone():
                # Create session data, we can access this data in other routes
                session["loggedin"] = True
                session["id"] = account["id"]
                session["username"] = account["username"]
                # Redirect to home page
                return redirect(url_for('home'))
            else:
                # Account doesnt exist or username/password incorrect
                loginMsg = "Incorrect username/password!"

        return render_template("login.html", msg = loginMsg)
    
    elif(register == 'signup'):
        # Output message if something goes wrong...
        registerMsg = ''
        # Check if "username", "password" and "email" POST requests exist (user submitted form)
        if request.method == 'POST' and 'newUsername' in request.form and 'newPassword' in request.form and 'newEmail' in request.form:
            # Create variables for easy access
            username = request.form['newUsername']
            password = request.form['newPassword']
            email = request.form['newEmail']

            # Check if account exists using MySQL
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM form WHERE username = %s', (username,))
            account = cursor.fetchone()
            # If account exists show error and validation checks
            if account:
                registerMsg = 'Account already exists!'
            elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
                registerMsg = 'Invalid email address!'
            elif not re.match(r'[A-Za-z0-9]+', username):
                registerMsg = 'Username must contain only characters and numbers!'
            elif not username or not password or not email:
                registerMsg = 'Please fill out the form!'
            else:
                # Account doesnt exists and the form data is valid, now insert new account into accounts table
                cursor.execute('INSERT INTO form VALUES (NULL, %s, %s, %s)', (username, password, email,))
                mysql.connection.commit()
                registerMsg = 'You have successfully registered!'
                return redirect(url_for('auth', register = "login"))
        elif request.method == 'POST':
            # Form is empty... (no POST data)
            registerMsg = 'Please fill out the form!'
        # Show registration form with message (if any)
        return render_template('login.html', msg=registerMsg)
    else: 
        return "404 Not Found"

# <--------------------------------------------Crop Recommendation-------------------------------------------->

def genrateCropDesc(cropName):
    path = 'CropDesc\Crop.json'
    contents = {}
    with open(path, 'r') as j:
        contents = json.loads(j.read())
    return contents[cropName] if cropName in contents else "404 Not Found"
    

@app.route('/auth/login/home/', methods=["GET", "POST"])
def home():
    # Check if user is loggedin
    # if 'loggedin' not in session:
    if 'loggedin' in session:
        N=request.form.get('N', False)
        P=request.form.get('P', False)
        K=request.form.get('K', False)
        ph=request.form.get('ph', False)
        
        print([N, P, K, ph], file=sys.stderr)
        if(N == P == K == ph == 0):
            return render_template('main.html', username=session['username'])
        
        def predicter(data):
            data = data.reshape(-1, 7)
            scaledData = scaler.transform(data)
            predictedData = (model.predict(scaledData) > 0.5).astype("int32")
            output = np.argmax(predictedData, axis=1)
            if int(output) in helper:
                return helper[int(output)]
            else:
                return "Error! Enter valid inputs!"

        city, long, lat = location()
        locationId = LocationID(city)
        temp, rain = tempRain(locationId)
        # print("Temp" + type(temp), file=sys.stderr)
        # temp, rain = 90.24324, 50.2344444
        humid = humidity(lat, long)
        
        initData = np.array((N, P, K, temp, humid, ph, rain))
        data = initData.astype(np.float)
        print(data, file=sys.stderr)
        cropName = predicter(data)
        desc = genrateCropDesc(cropName.lower())
        return render_template('main.html', username=session['username'], cropName = cropName.title(), desc = desc, temp = round(temp, 3), humid = humid, rain = rain, city = city)
    
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

# <--------------------------------------------Pest Recognization-------------------------------------------->

def PestRecog(img):
    # Load the model
    pestModel = load_model('Models/PestModel.hdf5')
    print('Model loaded. Check http://127.0.0.1:5000/')

    resize = tf.image.resize(img, (256, 256))
    yhat = pestModel.predict(np.expand_dims(resize / 255, 0))
    yhat = np.argmax(yhat, axis = 1)
    if yhat[0] in pests.keys():
        return pests[yhat[0]]

def genratePestDesc(pestName):
    path = 'CropDesc/Pests.json'
    contents = {}
    with open(path, 'r') as j:
        contents = json.loads(j.read())
    print(contents, file=sys.stderr)
    return contents[pestName] if pestName in contents else "404 Not Found"
    

@app.route('/auth/login/PestPredictor/', methods = ['GET', 'POST'])
def pest():
    # Check if user is loggedin
    if 'loggedin' not in session:
        # User is not loggedin redirect to login page
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        f = request.files['file']

        basepath = os.path.dirname(__file__)
        file_path = os.path.join(basepath, 'uploads', secure_filename(f.filename))
        f.save(file_path)

        # image = cv2.imshow(file_path)
        pestName = PestRecog(cv2.imread(file_path))
        print(pestName, file=sys.stderr)
        pestDesc = genratePestDesc(pestName.lower())
        return render_template('pestPred.html', pestName = pestName.title(), pestDesc = pestDesc)
    return render_template('pestPred.html')


# <--------------------------------------------Weed Recognization-------------------------------------------->
def WeedRecog(img):
    # Load the model
    weedModel = load_model('Models/WeedModel.hdf5')
    print('Model loaded. Check http://127.0.0.1:5000/')
    
    resize = tf.image.resize(img, (256, 256))
    yhat = weedModel.predict(np.expand_dims(resize / 255, 0))
    yhat = np.argmax(yhat, axis = 1)
    if yhat[0] in weeds.keys():
        return weeds[yhat[0]]

def genrateDesc(weedName):
    path = 'CropDesc/Weed.json'
    contents = {}
    with open(path, 'r') as j:
        contents = json.loads(j.read())
    return contents[weedName] if weedName in contents else "404 Not Found"

@app.route('/auth/login/WeedPredictor/', methods = ['GET', 'POST'])
def weed():
    # Check if user is loggedin
    if 'loggedin' not in session:
        # User is not loggedin redirect to login page
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        f = request.files['file']

        basepath = os.path.dirname(__file__)
        file_path = os.path.join(basepath, 'uploads', secure_filename(f.filename))
        f.save(file_path)

        weedName = WeedRecog(cv2.imread(file_path))
        print(weedName, file=sys.stderr)
        weedDesc = genrateDesc(weedName)
        return render_template('weedPredictor.html', weedName = weedName.title(), weedDesc = weedDesc)
    return render_template('weedPredictor.html')

@app.route('/auth/login/')
def logout():
    # Remove session data, this will log the user out
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    # Redirect to login page
    return render_template('login.html')

if __name__ == "__main__":
    app.run(debug=True)
