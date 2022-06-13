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


def highlight_rows(s):
    if s["Prediction"] == "non-depressed":
        return ['background-color: #04aa6d']*len(s)
    elif s["Prediction"] == "depressed":
        return ['background-color: #f44336']*len(s)


def predict_depression_severity(data):
    data = data.copy()
    classes = ["Normal", "Mild", "Moderate", "Severe", "Extremely Severe"]

    with open("form_details.json") as form_detail_file:
        form_details = json.load(form_detail_file)

    keys = list(data.keys())

    for key in keys:
        if isinstance(data[key], str):
            options = form_details[key]["options"]
            option_index = options.index(data[key]) + 1

            if key == "race":
                option_index *= 10

            data[key] = option_index

    values = list(data.values())
    payload = {"data": values}

    response = requests.post(
        "http://127.0.0.1:5000/predict-dass", json=payload)
    severity = response.json()["prediction"]

    return severity


def predict_tweet_depression(tweethandle):
    # df = pd.read_csv("./Collected_Tweets.csv", encoding='latin-1')

    tweets = scrape_tweets(tweethandle)

    if tweets is None:
        return None, 0

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

    if "@" in tweethandle:
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
    try:
        twint.run.Search(c)

        tweets = twint.output.tweets_list
        tweet_list = [item.tweet for item in tweets]
        tweets.clear()

        return tweet_list

    except:
        st.warning(
            "Unfortunately, that account doesn't exist and we were unable to scrape tweets.")

        return None


def get_next_reply(reply_key, script):
    """ General function to generate the next reply if there is one.

    Args:
        reply_key (int): The index of the next reply.
        script (list): Script list that contains dictionaries of responses.
    """

    reply_options = script[reply_key]["message"]
    next_reply = random.choice(reply_options)

    # Some messages may have things to fill in, eg. the user's name.
    # This required substitution is represented using the <info> syntax, hence the regex pattern below is used.
    contexts = re.findall("\<\w*\>", next_reply)

    if len(contexts) > 0:
        for context in contexts:
            key = context[1:-1]
            next_reply = re.sub(
                context, st.session_state[key], next_reply)

    return next_reply


def slider_callback(**kwargs):
    """ Callback function to handle independent slider input.

    Args:
        **script (list): Script list.

    Note:
        Compared to text input, the user's response in the form of their score is stored in the session state. Hence, the reply is generated from that value rather than the inverse in the text input.
    """

    script = kwargs["script"]
    current_key = st.session_state["reply_index"]
    user_reply = None

    if current_key < len(script):

        # There should always be an expected reply in the form of the score submitted through the slider.
        # This is the reply that is rendered as a chat bubble.
        expected_information = script[current_key]["information_obtained"]
        user_reply = str(st.session_state[expected_information])

    next_reply = None

    # If there are future replies, generate a reply using the script.
    if current_key + 1 < len(script):
        next_reply = get_next_reply(current_key + 1, script)

    if user_reply:
        st.session_state.history.append(
            {"message": user_reply, "is_user": True, "key": f"user_{current_key}"})

    if next_reply:
        st.session_state.history.append(
            {"message": next_reply, "is_user": False, "key": f"bot_{current_key}"})

    st.session_state.reply_index = current_key + 1


def form_callback(**kwargs):
    """ Callback function to handle form input.

    Args:
        **script (list): Script list.

    Note:
        The current behaviour is when a form is filled, there is no reply generated from the user side and only the response values are stored in the session state.
    """

    script = kwargs["script"]
    current_key = st.session_state["reply_index"]

    next_reply = None

    # If there are future replies, generate a reply using the script.
    if current_key + 1 < len(script):
        next_reply = get_next_reply(current_key + 1, script)

    if next_reply:
        st.session_state.history.append(
            {"message": next_reply, "is_user": False, "key": f"bot_{current_key}"})

    st.session_state.reply_index = current_key + 1


def text_callback(**kwargs):
    """ Callback function to handle text input.

    Args:
        **script (list): Script list.
    """

    script = kwargs["script"]

    user_reply = st.session_state["text_input"]
    current_key = st.session_state["reply_index"]

    if current_key < len(script):

        # Check if the current message was supposed to return information we want to keep.
        expected_information = script[current_key]["information_obtained"]

        # Store the information for context and making predictions.
        if expected_information:
            st.session_state[expected_information] = user_reply

    next_reply = None

    # If there are future replies, generate a reply using the script.
    if current_key + 1 < len(script):
        next_reply = get_next_reply(current_key + 1, script)

    if user_reply:
        st.session_state.history.append(
            {"message": user_reply, "is_user": True, "key": f"user_{current_key}"})

    if next_reply:
        st.session_state.history.append(
            {"message": next_reply, "is_user": False, "key": f"bot_{current_key}"})

    st.session_state.reply_index = current_key + 1
