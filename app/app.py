import streamlit as st
from streamlit_chat import message as st_message
import json
import re
import random
from utils import slider_callback, text_callback, form_callback, predict_depression_severity, predict_tweet_depression, highlight_rows
import pandas as pd

st.set_page_config(page_title="Inspector Gloom")
st.title("Inspector Gloom")

with open("dialog.json", "r") as dialog_file:
    script = json.load(dialog_file)

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
    consent_message = "Hi there! I'm Inspecter Gloom and I'm an application which could help to detect your depression severity and to identify if you have any signs of depression based on social media activity. In order to do that, I might need to obtain some personal information from you and also access your personal Twitter account if you have one. All of the data collected will not be saved for safety purposes. If you are agree please press the 'Proceed' button below."

    st.info(consent_message)
    agree = st.button("Proceed")

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
                          on_change=text_callback, kwargs={"script": script})

        # Generate the form to collect demographic data
        elif response_type == "form":

            with open("form_details.json") as detail_file:
                form_details = json.load(detail_file)
                key_list = list(form_details.keys())

            with st.form("form_container"):
                for key in key_list:
                    field_type, question, options = form_details[key]["field_type"], form_details[
                        key]["question"], form_details[key]["options"]

                    if field_type == "selectbox":
                        select_input = st.selectbox(question, options)
                        st.session_state[key] = select_input

                    elif field_type == "slider":
                        slider_input = st.slider(question)
                        st.session_state[key] = slider_input

                submitted = st.form_submit_button("Submit")

                if submitted:
                    form_callback(script=script)
                    st.experimental_rerun()

        elif response_type == "slider":
            slider_key = script[st.session_state["reply_index"]
                                ]["information_obtained"]
            score = st.slider(
                "Score", 0, 3)
            st.write("(0 = Did not apply to me at all, 1 = Applied to me to some degree, or some of the time, 2 = Applied to me to a considerable degree, or a good part of the time, 3 = Applied to me very much, or most of the time)")

            st.session_state[slider_key] = score

            submitted = st.button(
                "Submit", on_click=slider_callback, kwargs={"script": script})

    # If the end of the script is reached, perform analysis and generate the results.
    else:
        data_columns = personal_columns + question_columns
        data_dict = {}

        for column in data_columns:
            data_dict[column] = st.session_state[column]

        st.write("Entered information:")
        df = pd.DataFrame(data_dict, index=[0])
        st.dataframe(df)

        severe_list = ["Moderate", "Severe", "Extremely Severe"]
        predicted_severity = predict_depression_severity(data_dict)
        st.metric(label="Depression Severity", value=predicted_severity)

        if st.session_state["twitter_handle"].lower() != "none":
            tweet_df, tweet_prediction = predict_tweet_depression(
                st.session_state["twitter_handle"])

        if tweet_df is not None:
            tweet_df = tweet_df.style.apply(highlight_rows, axis=1)
            st.write("Most Recent Tweets")
            st.dataframe(tweet_df)
            st.metric(
                label="Percentage of Recent Tweets with Depressive Tendencies", value=tweet_prediction)

        with open("advice.json") as advice_file:
            advice_options = json.load(advice_file)

        if tweet_prediction > 0.5 and predicted_severity in severe_list:
            st.info(advice_options["both_depressed"])

        elif tweet_prediction < 0.5 and predicted_severity not in severe_list:
            st.info(advice_options["none_depressed"])

        else:
            st.info(advice_options["one_depressed"])
