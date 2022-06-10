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
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"


def Preprocessing(tokenizer, input):
    #cleanedinput = clean_text(input)
    cleanedinput = tweetcleaning(input)
    inputpadded = textpadding(tokenizer, cleanedinput)

    return inputpadded


def clean_text(input):
    # Initialize
    nlp = spacy.load("en_core_web_sm")
    stop_words = ['i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', "you're", "you've", "you'll", "you'd", 'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', "she's", 'her', 'hers', 'herself', 'it', "it's", 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves', 'what', 'which', 'who', 'whom', 'this', 'that', "that'll", 'these', 'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or',
                  'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'nor', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'should', "should've", 'now', 'd', 'll', 'm', 'o', 're', 've', 'y', 'ma']
    text_cleaning_regex = "@S+|https?:S+|http?:S|[^A-Za-z0-9]+"
    tokens = []
    input = input.lower()
    doc = nlp(input)
    for token in doc:
        if not token.is_punct and not token.is_space and not token.is_digit and not token.like_url:
            if token.text not in stop_words:
                tokens.append(token.lemma_)
    input = " ".join(tokens)
    # Passing the text through the regex equation
    input = p.clean(input)
    input = re.sub(text_cleaning_regex, ' ', str(input)).strip()
    # Converting text to array
    ar = []
    ar.append(input)
    return ar


def tweetcleaning(text):
    text = text.lower()
    text = p.clean(text)
    # # Converting text to array
    # ar = []
    # ar.append(text)
    return text


def textpadding(tokenizer, input):
    # Converting the text to a list of numerical sequences and padding them with 50 as the maxlength
    sequence_input = tokenizer.texts_to_sequences(input)
    x_input_pad = pad_sequences(sequence_input, maxlen=30)

    return x_input_pad
