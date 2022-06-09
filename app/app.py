import streamlit as st
from streamlit_chat import message as st_message
import json
import re
import random
from utils import handle_user_input, predict_depression_severity, predict_tweet_depression
import pandas as pd

st.set_page_config(page_title="ManulBot")
st.title("Johnny Depp-regression")

with open("dialog.json", "r") as dialog_file:
    script = json.load(dialog_file)

filler_replies = ["hshshs", "ehhhhh", "naim, nak code", "nepu tolong buatkan makasih",
                  "haihhhh", "jom fifa, ehhh jap ada update", "aku ni rajin sebenarnya"]

personal_columns = ['education', 'urban', 'gender', 'engnat', 'age', 'hand', 'religion',
                    'orientation', 'race', 'married', 'familysize', 'major']
question_columns = ['q1', 'q2', 'q3', 'q4', 'q5', 'q6', 'q7', 'q8', 'q9',
                    'q10', 'q11', 'q12', "q13", "q14"]

if not st.session_state:
    st.session_state["consented"] = False

    # Initialise the introduction message
    st.session_state["history"] = [
        {"message": script[0]["message"], "is_user": False}]

    # Initialise the current bot message index
    st.session_state["reply_index"] = 0

# If the user has not consented for data use in the app, direct them to a consent disclaimer first.
if not st.session_state["consented"]:
    consent_message = "I want to steal your data, do you agree?"
    st_message(consent_message)
    agree = st.button("Yes or Yes?")

    if agree:
        st.session_state["consented"] = True
        st.experimental_rerun()

else:

    current_reply_index = st.session_state["reply_index"]

    # If the bot still has dialogs to reply, generate the reply fields accordingly.
    if current_reply_index < len(script):

        # Iterate over the chat history and render the message boxes.
        for chat in st.session_state["history"]:
            st_message(**chat)  # unpacking

        response_type = script[current_reply_index]["response_type"]

        if response_type == "text":
            st.text_input("Type your reply:", key="text_input",
                          on_change=handle_user_input, kwargs={
                              "response_type": response_type, "script": script, "filler_replies": filler_replies})

        # Generate the form to collect demographic data
        elif response_type == "form":
            with open("form_details.json") as detail_file:
                form_details = json.load(detail_file)
                key_list = list(form_details.keys())

            form_response = {}

            with st.form("form_container"):
                for key in key_list:
                    field_type, question, options = form_details[key]["field_type"], form_details[
                        key]["question"], form_details[key]["options"]

                    if field_type == "selectbox":
                        form_response[key] = st.selectbox(
                            question, options)

                    elif field_type == "slider":
                        form_response[key] = st.slider(question)

                submitted = st.form_submit_button("Submit")

                if submitted:
                    for column in personal_columns:
                        st.session_state[column] = form_response[column]

                    handle_user_input(response_type=response_type,
                                      script=script, filler_replies=filler_replies)
                    st.experimental_rerun()

        elif response_type == "slider":
            score = st.slider("Score", 0, 3)
            st.write("(0 = Did not apply to me at all, 1 = Applied to me to some degree, or some of the time, 2 = Applied to me to a considerable degree, or a good part of the time, 3 = Applied to me very much, or most of the time)")

            submitted = st.button("Submit")

            if submitted:
                st.session_state[script[current_reply_index]
                                 ["information_obtained"]] = score
                handle_user_input(response_type=response_type,
                                  script=script, filler_replies=filler_replies)
                st.experimental_rerun()

    # If the end of the script is reached, perform analysis and generate the results.
    else:
        data_columns = personal_columns + question_columns
        data_dict = {}

        for column in data_columns:
            data_dict[column] = st.session_state[column]

        st.write("Entered information:")
        df = pd.DataFrame(data_dict, index=[0])
        st.dataframe(df)

        predicted_severity = predict_depression_severity(data_dict)
        st.metric(label="Depression Severity", value=predicted_severity)

        tweet_df, prediction = predict_tweet_depression(
            st.session_state["twitter_handle"])

        st.write("Most Recent Tweets")
        st.dataframe(tweet_df)
        st.metric(label="Depression Based on Recent Tweets", value=prediction)
