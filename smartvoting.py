# !/uspeech_recognition/bin/env python3
# coding= UTF-8

# ------------------------------------------------------------------------------------------------------------------------------------#
#                                                  Installing Packages Needed                                                         #
# ------------------------------------------------------------------------------------------------------------------------------------#

# This is used to dump the models into an object
import pickle
import datetime
# For creating directories
import os
# For deleting directories
import shutil
# from collections import defaultdict

import matplotlib.pyplot as plt
import numpy
import scipy.cluster
import scipy.io.wavfile
# For the speech detection alogrithms
import speech_recognition
# For the fuzzy matching algorithms
from fuzzywuzzy import fuzz
# For using the MFCC feature selection
from python_speech_features import mfcc
# For generating random words
from sklearn import preprocessing
# For using the Gausian Mixture Models
from sklearn.mixture import GaussianMixture

# RANDOM WORD
import random

# TIME
import time

# MongoDB
import pymongo

# Security
import hashlib

words_store = ["hello", "name", "market", "english", "election", "goodbye"]

import config

# Web Service
from flask import Flask, render_template, request, url_for, redirect, abort, json, jsonify
from waitress import serve

# Global Variables
random_words = ""
random_string = ""
user_vote_directory = "Users/"
user_directory = "Users/Test"
filename = ""
filename_wav = ""
my_word = ""

ip_username = ""
ip_password = ''
ip_fname = ''
ip_lname = ''
ip_email = ''

app = Flask(__name__)


@app.route('/')
@app.route('/home')
def home():
    return render_template('main.html')


@app.route('/votehome')
def votehome():
    return render_template('votehome.html')


@app.route('/votenow', methods=['GET', 'POST'])
def votenow():
    global user_vote_directory
    global filename_wav

    print("[ DEBUG ] : directory : ", user_vote_directory)

    if request.method == 'POST':

        global random_words
        global ip_username
        global my_word

        ts = time.time()

        filename_wav = user_vote_directory + str(ts) + '.wav'
        f = open(filename_wav, 'wb')
        f.write(request.data)
        f.close()

        r = speech_recognition.Recognizer()

        with speech_recognition.WavFile(filename_wav) as source:
            # reads the audio file. Here we use record instead of
            # listen

            audio = r.record(source)

        try:
            my_word = r.recognize_google(audio, language="th-TH")
            print("The audio file contains: " + my_word)

        except speech_recognition.RequestError as e:
            print("Google Speech Recognition could not understand audio")

        return my_word

    else:
        return render_template('votenow.html')


@app.route('/enroll', methods=["GET", "POST"])
def enroll():
    global ip_username
    global ip_password
    global ip_fname
    global ip_lname
    global ip_email
    global user_directory

    if request.method == 'POST':
        data = request.get_json()

        ip_username = data['username']
        ip_password = data['password']
        ip_fname = data['fname']
        ip_lname = data['lname']
        ip_email = data['email']

        salt = os.urandom(32)  # A new salt for this user
        key = hashlib.pbkdf2_hmac('sha256', ip_password.encode('utf-8'), salt, 100000)

        myclient = pymongo.MongoClient("mongodb://localhost:27017/")
        mydb = myclient["votedatabase"]
        mycol = mydb["voteuser"]

        doccount = mydb.voteuser.find({'username': ip_username, 'bio-enroll': '1'}).count()

        if doccount < 1:

            doccount2 = mydb.voteuser.find({'username': ip_username, 'bio-enroll': '0'}).count()
            if doccount2 > 0:
                x = mycol.delete_many({'username': ip_username, 'bio-enroll': '0'})
                print(x.deleted_count, " documents deleted.")

            mydict = {"username": ip_username, "password": key, "salt": salt, "fname": ip_fname, "lname": ip_lname,
                      "email": ip_email, "bio-enroll": "0", "role": "user"}

            x = mycol.insert_one(mydict)

            user_directory = "Users/" + ip_username + "/"

            # Create target directory & all intermediate directories if don't exists
            if not os.path.exists(user_directory):
                os.makedirs(user_directory)
                print("[ * ] Directory ", ip_username, " Created ...")
                # return redirect(url_for('voice'))
            else:
                print("[ * ] Directory ", ip_username, " already exists ...")

                print("[ * ] Overwriting existing directory ...")
                shutil.rmtree(user_directory, ignore_errors=False, onerror=None)
                os.makedirs(user_directory)
                print("[ * ] Directory ", ip_username, " Created ...")
                # return redirect(url_for('voice'))

            # return redirect(url_for('voice'))
            return 'OK007'

        else:
            # return render_template('enroll.html')
            return 'ERR001'

    else:
        return render_template('enroll.html')


@app.route('/auth', methods=['POST', 'GET'])
def auth():
    global ip_username
    global ip_password
    global user_directory
    global filename

    user_exist = False
    login_valid = False
    user_found = 0

    if request.method == 'POST':

        data = request.get_json()
        print(data)

        user_directory = 'Models/'
        ip_username = data['username']
        ip_password = data['password']

        myclient = pymongo.MongoClient("mongodb://localhost:27017/")
        mydb = myclient["votedatabase"]
        mycol = mydb["voteuser"]

        user_found = mydb.voteuser.find({'username': ip_username, 'bio-enroll': '1'}).count()

        if user_found > 0:

            user_exist = True

            mysalt = mydb.voteuser.find({'username': ip_username}, {'_id': 0, 'salt': 1})
            mykey = mydb.voteuser.find({'username': ip_username}, {'_id': 0, 'password': 1})
            new_key = hashlib.pbkdf2_hmac('sha256', ip_password.encode('utf-8'), mysalt[0]['salt'], 100000)

            try:
                assert mykey[0]['password'] == new_key
                login_valid = True

            except AssertionError as error:
                # Output expected AssertionErrors.
                login_valid = False
                print(error)
            except Exception as exception:
                print(exception)

        if user_exist:
            if login_valid:
                return "OK007"
            elif login_valid is False:
                return "ERR001"
        else:
            return "ERR002"

    else:
        print('its coming here')
        return render_template('auth.html')


@app.route('/vad', methods=['GET', 'POST'])
def vad():
    if request.method == 'POST':
        global random_words

        f = open('./static/audio/background_noise.wav', 'wb')
        f.write(request.data)
        f.close()

        background_noise = speech_recognition.AudioFile(
            './static/audio/background_noise.wav')
        with background_noise as source:
            speech_recognition.Recognizer().adjust_for_ambient_noise(source, duration=5)

        print("Voice activity detection complete ...")

        # RANDOM WORD CONFIG
        # random_words = RandomWords().random_words(count=1)
        random_words = random.choice(words_store)
        print(random_words)

        return random_words
        # return "  ".join(random_words)

    else:
        background_noise = speech_recognition.AudioFile(
            './static/audio/background_noise.wav')
        with background_noise as source:
            speech_recognition.Recognizer().adjust_for_ambient_noise(source, duration=5)

        print("Voice activity detection complete ...")

        # RANDOM WORD CONFIG
        # random_words = RandomWords().random_words(count=1)
        random_words = random.choice(words_store)
        print(random_words)

        return random_words
        # return "  ".join(random_words)


@app.route('/voice', methods=['GET', 'POST'])
def voice():
    global user_directory
    global filename_wav

    print("[ DEBUG ] : User directory at voice : ", user_directory)

    if request.method == 'POST':
        #    global random_string
        global random_words
        global ip_username

        data = request.get_json()
        print(data)

        user_directory = 'Users/' + ip_username + '/'
        # ip_username = data['username']
        # password = data['password']

        filename_wav = user_directory + "-".join(random_words) + '.wav'
        f = open(filename_wav, 'wb')
        f.write(request.data)
        f.close()

        r = speech_recognition.Recognizer()

        with speech_recognition.AudioFile(open(filename_wav, 'rb')) as source:
            # reads the audio file. Here we use record instead of
            # listen

            audio = r.record(source)
            recognised_words = r.recognize_google(audio)

        try:

            print("The audio file contains: " + recognised_words)

            print("Fuzzy partial score : " + str(fuzz.partial_ratio(random_words, recognised_words)))
            print("Fuzzy score : " + str(fuzz.ratio(random_words, recognised_words)))

        except speech_recognition.UnknownValueError:
            print("Speech Recognition could not understand audio")

        # WORD SCORING * 65%
        if fuzz.ratio(random_words, recognised_words) < 70:
            print(
                "\nThe words you have spoken aren't entirely correct. Please try again ...")
            # os.remove(filename_wav)
            return "fail"
        else:
            pass

        return "pass"

    else:
        return render_template('voice.html')


@app.route('/identify', methods=['GET', 'POST'])
def identify():
    global user_directory
    global filename_wav

    print("[ DEBUG ] : User directory at voice : ", user_directory)

    if request.method == 'POST':
        #    global random_string
        global random_words
        global ip_username

        filename_wav = user_directory + '/' + '-'.join(random_words) + '.wav'
        f = open(filename_wav, 'wb')
        f.write(request.data)
        f.close()

        r = speech_recognition.Recognizer()

        with speech_recognition.AudioFile(open(filename_wav, 'rb')) as source:
            # reads the audio file. Here we use record instead of
            # listen
            audio = r.record(source)
            recognised_words = r.recognize_google(audio)
            # recognised_words = str(recognised_words['results'][0]['alternatives'][0]['transcript'])

        try:
            print("The audio file contains: " + recognised_words)

            print("Fuzzy partial score : " + str(fuzz.partial_ratio(random_words, recognised_words)))
            print("Fuzzy score : " + str(fuzz.ratio(random_words, recognised_words)))

        except speech_recognition.UnknownValueError:
            print("Speech Recognition could not understand audio")

        except speech_recognition.RequestError as e:
            print("Could not request results from Google Speech  Recognition service;".format(e))

            # audio2 = r.record(audio_file)
            # recognised_word = r.recognize_google(audio2)

        # WORD SCORING * 65%
        if fuzz.ratio(random_words, recognised_words) < 70:
            print(
                "\nThe words you have spoken aren't entirely correct. Please try again ...")
            # os.remove(filename_wav)
            return "fail"
        else:
            pass

        return "pass"

    else:
        return render_template('identify.html')


@app.route('/biometrics', methods=['GET', 'POST'])
def biometrics():
    global user_directory
    global ip_username
    print("[ DEBUG ] : User directory is : ", user_directory)

    if request.method == 'POST':
        pass
    else:
        # MFCC
        print("Into the biometrics route.")

        directory = os.fsencode(user_directory)
        features = numpy.asarray(())

        for file in os.listdir(directory):
            filename_wav = os.fsdecode(file)
            if filename_wav.endswith(".wav"):
                print("[biometrics] : Reading audio files for processing ...")
                (rate, signal) = scipy.io.wavfile.read(user_directory + filename_wav)

                extracted_features = extract_features(rate, signal)

                if features.size == 0:
                    features = extracted_features
                else:
                    features = numpy.vstack((features, extracted_features))

            else:
                continue

        # GaussianMixture Model
        print("[ * ]"
              " Building Gaussian Mixture Model ...")

        gmm = GaussianMixture(n_components=16,
                              max_iter=200,
                              covariance_type='diag',
                              n_init=3)

        gmm.fit(features)
        print("[ * ] Modeling completed for user :" + ip_username +
              " with data point = " + str(features.shape))

        # dumping the trained gaussian model
        # picklefile = path.split("-")[0]+".gmm"
        print("[ * ] Saving model object ...")
        pickle.dump(gmm, open("Models/" + str(ip_username) +
                              ".gmm", "wb"), protocol=None)
        print("[ * ] Object has been successfully written to Models/" +
              ip_username + ".gmm ...")
        print("\n\n[ * ] User has been successfully enrolled ...")

        features = numpy.asarray(())

        myclient = pymongo.MongoClient("mongodb://localhost:27017/")
        mydb = myclient["votedatabase"]
        mycol = mydb["voteuser"]

        myquery = {'username': ip_username}
        newvalues = {"$set": {'bio-enroll': '1'}}

        mycol.update_one(myquery, newvalues)

        return "User has been successfully enrolled ...!!"


@app.route("/verify", methods=['GET'])
def verify():
    global ip_username
    global filename
    global user_directory
    global filename_wav

    print("[ DEBUG ] : user directory : ", user_directory)
    print("[ DEBUG ] : filename : ", filename)
    print("[ DEBUG ] : filename_wav : ", filename_wav)

    # ------------------------------------------------------------------------------------------------------------------------------------#
    #                                                                   LTSD and MFCC                                                     #
    # ------------------------------------------------------------------------------------------------------------------------------------#

    # (rate, signal) = scipy.io.wavfile.read(audio.get_wav_data())
    (rate, signal) = scipy.io.wavfile.read(filename_wav)

    extracted_features = extract_features(rate, signal)

    # ------------------------------------------------------------------------------------------------------------------------------------#
    #                                                          Loading the Gaussian Models                                                #
    # ------------------------------------------------------------------------------------------------------------------------------------#

    gmm_models = [os.path.join(user_directory, user)
                  for user in os.listdir(user_directory)
                  if user.endswith('.gmm')]

    # print("GMM Models : " + str(gmm_models))

    # Load the Gaussian user Models
    models = [pickle.load(open(user, 'rb')) for user in gmm_models]

    user_list = [user.split("/")[-1].split(".gmm")[0]
                 for user in gmm_models]

    log_likelihood = numpy.zeros(len(models))

    for i in range(len(models)):
        gmm = models[i]  # checking with each model one by one
        scores = numpy.array(gmm.score(extracted_features))
        log_likelihood[i] = scores.sum()

    print("Log liklihood : " + str(log_likelihood))

    identified_user = numpy.argmax(log_likelihood)

    print("[ * ] Identified User : " + str(identified_user) +
          " - " + user_list[identified_user])

    auth_message = ""

    if user_list[identified_user] == ip_username:
        print("[ * ] You have been authenticated!")
        auth_message = "success"
    else:
        print("[ * ] Sorry you have not been authenticated")
        auth_message = "fail"

    return auth_message


def calculate_delta(array):
    """Calculate and returns the delta of given feature vector matrix
    (https://appliedmachinelearning.blog/2017/11/14/spoken-speaker-identification-based-on-gaussian-mixture-models-python-implementation/)"""

    print("[Delta] : Calculating delta")

    rows, cols = array.shape
    deltas = numpy.zeros((rows, 20))
    N = 2
    for i in range(rows):
        index = []
        j = 1
        while j <= N:
            if i - j < 0:
                first = 0
            else:
                first = i - j
            if i + j > rows - 1:
                second = rows - 1
            else:
                second = i + j
            index.append((second, first))
            j += 1
        deltas[i] = (array[index[0][0]] - array[index[0][1]] +
                     (2 * (array[index[1][0]] - array[index[1][1]]))) / 10
    return deltas


def extract_features(rate, signal):
    print("[extract_features] : Exctracting featureses ...")

    mfcc_feat = mfcc(signal,
                     rate,
                     winlen=0.020,  # remove if not requred
                     preemph=0.95,
                     numcep=20,
                     nfft=1024,
                     ceplifter=15,
                     highfreq=6000,
                     nfilt=55,

                     appendEnergy=False)

    mfcc_feat = preprocessing.scale(mfcc_feat)

    delta_feat = calculate_delta(mfcc_feat)

    combined_features = numpy.hstack((mfcc_feat, delta_feat))

    return combined_features


if __name__ == '__main__':
    # app.run(host='0.0.0.0', port=8000, debug=True, ssl_context='adhoc')
    app.run(host=config.HOST, port=config.PORT, debug=config.DEBUG_MODE)
    # serve(app, host=config.HOST, port=config.PORT)
