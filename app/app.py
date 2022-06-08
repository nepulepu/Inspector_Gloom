import streamlit as st
from streamlit_chat import message as st_message
import json
import re
import random

st.set_page_config(page_title="ManulBot")
st.title("ManulBot")

with open("dialog.json", "r") as dialog_file:
    script = json.load(dialog_file)

filler_replies = ["hshshs", "ehhhhh", "naim, nak code", "nepu tolong buatkan makasih",
                  "haihhhh", "jom fifa, ehhh jap ada update", "aku ni rajin sebenarnya"]

if not st.session_state:
    st.session_state["consented"] = False

    # Initialise the introduction message
    st.session_state["history"] = [
        {"message": script[0]["message"], "is_user": False}]

    # Initialise the current bot message index
    st.session_state["reply_index"] = 0


def handle_other_input():

    current_key = st.session_state["reply_index"]

    if current_key + 1 < len(script):

        reply_options = script[current_key + 1]["message"]
        next_reply = random.choice(reply_options)
        contexts = re.findall("\<\w*\>", next_reply)

        if len(contexts) > 0:
            for context in contexts:
                key = context[1:-1]
                next_reply = re.sub(
                    context, st.session_state[key], next_reply)

    else:
        next_reply = random.choice(filler_replies)

    st.session_state.history.append(
        {"message": next_reply, "is_user": False, "key": f"bot_{current_key}"})
    st.session_state.reply_index = current_key + 1


def handle_text_input():

    user_reply = st.session_state["text_input"]
    current_key = st.session_state["reply_index"]

    # Handle the situation where there are further script options.
    if current_key + 1 < len(script):

        # Check if the current message was supposed to return information we want to keep.
        expected_information = script[current_key]["information_obtained"]

        # Store the information for context and making predictions.
        if expected_information:
            st.session_state[expected_information] = user_reply

        reply_options = script[current_key + 1]["message"]
        next_reply = random.choice(reply_options)
        contexts = re.findall("\<\w*\>", next_reply)

        if len(contexts) > 0:
            for context in contexts:
                key = context[1:-1]
                next_reply = re.sub(
                    context, st.session_state[key], next_reply)

    else:
        next_reply = random.choice(filler_replies)

    st.session_state.history.append(
        {"message": user_reply, "is_user": True, "key": f"user_{current_key}"})
    st.session_state.history.append(
        {"message": next_reply, "is_user": False, "key": f"bot_{current_key}"})
    st.session_state.reply_index = current_key + 1


# If the user has not consented for data use in the app, direct them to a consent disclaimer first.
if not st.session_state["consented"]:
    consent_message = "I want to steal your data, do you agree?"
    st_message(consent_message)
    agree = st.button("Yes or Yes?")

    if agree:
        st.session_state["consented"] = True
        st.experimental_rerun()

else:
    # Iterate over the chat history and render the message boxes.
    for chat in st.session_state["history"]:
        st_message(**chat)  # unpacking

    current_reply_index = st.session_state["reply_index"]

    # If the bot still has dialogs to reply, generate the reply fields accordingly.
    if current_reply_index < len(script):
        response_type = script[current_reply_index]["response_type"]

        if response_type == "text":
            st.text_input("Type your reply:", key="text_input",
                          on_change=handle_text_input)

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
                        st.selectbox(question, options, key=key)

                    elif field_type == "slider":
                        st.slider(question, key=key)

                submitted = st.form_submit_button(
                    "Submit", on_click=handle_other_input)

        elif response_type == "slider":
            st.slider("Score", 0, 3,
                      key=script[current_reply_index]["information_obtained"])
            st.write("(0 = Did not apply to me at all, 1 = Applied to me to some degree, or some of the time, 2 = Applied to me to a considerable degree, or a good part of the time, 3 = Applied to me very much, or most of the time)")
            submitted = st.button("Submit", on_click=handle_other_input)

    # If the end of the script is reached, allow the user to reply anything and reply with a choice from the filler list.
    # This theoretically should not happen but helps in error handling in case it does.
    else:
        st.text_input("Type your reply:", key="text_input",
                      on_change=handle_text_input)
