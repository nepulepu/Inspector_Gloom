import streamlit as st
from streamlit_chat import message as st_message
import json
import re
import random

st.set_page_config(page_title="ManulBot")
st.title("ManulBot")

with open("dialog.json", "r") as dialog_file:
    script = json.load(dialog_file)

keys = list(script.keys())

if not st.session_state:
    st.session_state["consented"] = False

    # Update to add more information that we want the bot to remember.
    st.session_state["context_memory"] = {"name": None}
    st.session_state["past_key"] = -1

    # Initialise the introduction message
    st.session_state.history = [
        {"message": script[keys[0]]["message"], "is_user": False}]

    # Initialise the current bot message index
    st.session_state.reply_index = 0


def generate_reply():

    user_message = st.session_state.input_text

    current_key = st.session_state.reply_index
    # Needs error handling for when the script has reached the end.
    expected_information = script[keys[current_key]]["information_obtained"]

    if expected_information in st.session_state["context_memory"]:
        st.session_state["context_memory"][expected_information] = user_message

    reply_options = script[keys[current_key + 1]]["message"]
    next_reply = random.choice(reply_options)
    contexts = re.findall("\<\w*\>", next_reply)

    if len(contexts) > 0:
        for context in contexts:
            key = context[1:-1]
            next_reply = re.sub(
                context, st.session_state["context_memory"][key], next_reply)

    st.session_state.history.append({"message": user_message, "is_user": True})
    st.session_state.history.append({"message": next_reply, "is_user": False})
    st.session_state.reply_index = current_key + 1


if not st.session_state["consented"]:
    st.info("Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed hendrerit felis in nulla fermentum fringilla. Praesent aliquam dui lectus, accumsan viverra ex rutrum non. Curabitur ipsum purus, aliquet eget pretium et, blandit id quam. Praesent facilisis, nisi quis viverra vestibulum, mauris orci feugiat sapien, eu bibendum lectus dolor et urna. Maecenas fringilla arcu risus, a eleifend sapien pulvinar id. Donec mattis nisl odio, fringilla fringilla risus fermentum vel. Donec ipsum urna, mollis vitae facilisis et, imperdiet a odio. Nullam eu porta diam. Donec et turpis mi. Ut at lectus rutrum, mollis nulla nec, fermentum nisl. Nunc et erat iaculis odio.")

    agree_button = st.button("I agree")

    if agree_button:
        st.session_state["consented"] = True

else:
    st.text_input("Type your reply:", key="input_text",
                  on_change=generate_reply)

    for chat in reversed(st.session_state.history):
        st_message(**chat)  # unpacking
