import streamlit as st
import random
import re
import json
import pickle


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

    values = [list(data.values())]

    clf = pickle.load(
        open("../models/dass_demography_lr_pipe_09062022.pkl", 'rb'))

    prediction = clf.predict(values)[0]
    severity = classes[prediction]

    return severity


def predict_tweet_depression():
    return


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
