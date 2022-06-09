import streamlit as st
import random
import re
import json
import pickle
import asyncio
import twint
import pandas as pd
import numpy as np
import requests


def predict_depression_severity(data):
    data = data.copy()
    classes = ["Normal", "Mild", "Moderate", "Severe", "Extremely Severe"]

    with open("form_details.json") as form_detail_file:
        form_details = json.load(form_detail_file)

    keys = list(data.keys())

    for key in keys:
        if isinstance(data[key], str):
            options = form_details[key]["options"]
            option_index = options.index(data[key])

            data[key] = option_index

    values = list(data.values())
    payload = {"data": values}

    # clf = pickle.load(
    #     open("../models/dass_demography_lr_pipe_09062022.pkl", 'rb'))

    response = requests.post(
        "http://127.0.0.1:5000/predict-dass", json=payload)
    severity = response.json()["prediction"]

    return severity


def predict_tweet_depression(tweethandle):
    # df = pd.read_csv("./Collected_Tweets.csv", encoding='latin-1')

    tweets = scrape_tweets(tweethandle)

    pred_list = []

    scores = []
    for tweet in tweets:
        # sentence = df["tweet"][i]

        body = {"message": tweet}
        response = requests.post(
            "http://127.0.0.1:5000/predict-tweet", json=body)

        sentence_prediction = response.json()["prediction"]
        pred_item = {
            "Tweet": tweet, "Prediction": sentence_prediction[0], "Confidence": sentence_prediction[1]}

        if sentence_prediction[0] == "depressed":
            scores.append(1)
        else:
            scores.append(0)

        pred_list.append(pred_item)

    overall_mean = np.sum(scores) / len(scores)
    tweet_df = pd.DataFrame(pred_list)

    return tweet_df, overall_mean


def scrape_tweets(tweethandle):
    tweethandle = tweethandle[1:]
    # nest_asyncio.apply()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    c = twint.Config()
    c.Username = str(tweethandle)
    # c.Custom["tweet"] = ["id", "tweet"]
    # c.Store_csv = True
    c.Limit = 50
    c.Store_object = True
    c.Hide_output = True
    c.Media = False
    c.Search = "-filter:replies"
    # c.Output = "Collected_Tweets.csv"
    twint.run.Search(c)

    tweets = twint.output.tweets_list
    tweet_list = [item.tweet for item in tweets]
    tweets.clear()

    return tweet_list


def handle_user_input(**kwargs):
    """ Callback function to handle user input.

    Args:
        **response_type (str): The response type.
        **script (list): Script list.
        **filler_replies (list): List of filler replies when the bot runs out of dialog.
    """

    response_type, script, filler_replies = kwargs["response_type"], kwargs["script"], kwargs["filler_replies"]
    user_reply = None

    if response_type == "text":
        user_reply = st.session_state["text_input"]

    current_key = st.session_state["reply_index"]

    if current_key < len(script):

        # Check if the current message was supposed to return information we want to keep.
        expected_information = script[current_key]["information_obtained"]

        # Store the information for context and making predictions.
        if expected_information and response_type == "text":
            st.session_state[expected_information] = user_reply

        # Get the user reply based on the response stored in the state.
        elif expected_information and response_type == "slider":
            user_reply = str(st.session_state[expected_information])

    # If there are future replies, generate a reply using the script.
    if current_key + 1 < len(script):
        reply_options = script[current_key + 1]["message"]
        next_reply = random.choice(reply_options)
        contexts = re.findall("\<\w*\>", next_reply)

        if len(contexts) > 0:
            for context in contexts:
                key = context[1:-1]
                next_reply = re.sub(
                    context, st.session_state[key], next_reply)

    # Else, generate a random reply using the filler list.
    else:
        next_reply = random.choice(filler_replies)

    if user_reply:
        st.session_state.history.append(
            {"message": user_reply, "is_user": True, "key": f"user_{current_key}"})

    st.session_state.history.append(
        {"message": next_reply, "is_user": False, "key": f"bot_{current_key}"})

    st.session_state.reply_index = current_key + 1
