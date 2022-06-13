from lib2to3.pgen2 import token
import nltk
import spacy
import re
import preprocessor as p
import pandas as pd
import numpy as np
import tensorflow as tf
from keras.models import load_model
from keras.preprocessing.sequence import pad_sequences
from keras.preprocessing.text import Tokenizer
from flask import Flask, render_template, url_for, request, jsonify
import os
import pickle

from utils import Preprocessing, clean_text, tweetcleaning, textpadding
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"


app = Flask(__name__)


@app.route('/')
def home():
    return "hshs depressed ke tu"
    # return render_template('home.html')


@app.route('/predict-tweet', methods=['POST'])
def predict():
    if request.method == 'POST':
        # input = request.form['message']
        input = request.json["message"]
        preprocessed_input = Preprocessing(tokenizer, input)
        score = tweet_model.predict(preprocessed_input, verbose=1)[0][0]
        score = eval(str(score))

        if score > 0.5:
            pred = ("non-depressed", score)
        else:
            pred = ("depressed", 1-score)

        return jsonify({'prediction': pred})

    # return render_template('result.html', prediction=pred)


@app.route("/predict-dass", methods=['POST'])
def predict_dass():
    if request.method == "POST":
        classes = ["Normal", "Mild", "Moderate", "Severe", "Extremely Severe"]

        data = [request.json["data"]]

        prediction = dass_model.predict(data)[0]
        severity = classes[prediction]

        return jsonify({"prediction": severity})


if __name__ == '__main__':
    tweet_model = load_model(
        "../../models/depressed_detection_model_final.h5")
    df = pd.read_csv(
        "../../models/Train_Data.csv")

    df['text'] = df['text'].astype(str)
    # Tokenizer
    tokenizer = Tokenizer()
    tokenizer.fit_on_texts(df['text'])

    dass_model = pickle.load(
        open("../../models/dass_demography_lr_pipe_13062022.pkl", 'rb'))

    app.run()
    # Use the debug option below if you want to have live reloading when making changes.
    # app.run(debug=True)
