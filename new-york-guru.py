
import streamlit as st
from openai import OpenAI
import time
import streamlit as st
import openai
from uuid import uuid4
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
ASSISTANT_ID = st.secrets["NY_ADVISOR"]

# Create columns for the logo and the title
col1, col2 = st.columns([1, 4])

# In the first column, display the logo
with col1:
    st.image('ny.png', width=150)  # Adjust the width as needed

# In the second column, display the title and subtitle
with col2:
    st.markdown("<h2 style='margin-top: 0;padding-left: 10px;'> NY Solar Advisor</h2>", unsafe_allow_html=True)
    st.markdown("<em><p style='margin-top: 0; padding-left: 10px;'>Your interactive AI-powered guide to Solar policies and incentives in the state of NY</p></em>", unsafe_allow_html=True)

# Information box with AI assistant capabilities and knowledge base
info_text = """
This AI assistant leverages GPT-4 technology with a knowledge cutoff in April 2024 to provide expert guidance on solar energy policies and incentives in New York. It integrates detailed document analysis for tailored, strategic advice.

Key Documents in the Knowledge Base:
- 2024 Solar and Wind Tax Model: Guidance on tax models for solar and wind projects. Published by the New York State Tax Department.
- 2024_Solar_and_Wind_Appraisal_Model_User_Guide: Details on how to appraise solar and wind projects. Published by the New York State Tax Department.
- 2024-Gold-Book-Public: Comprehensive industry data and standards. Published by NYISO.
- New York Community Solar Policy Guide for Asset Owners & Developers: Guidelines for community solar projects. Created by Perch Energy’s internal policy team.
- NY SUN Long Island + Upstate-Program-Manual: Program details for NY SUN's initiatives. Published by NYSERDA.
- NYSEG Queue Order by Substation: Latest queue order by substation for NYSEG. Published by NYSEG itself.
- Residential-SC-Program-Manual: Information on the residential solar credit program.
- Net Metering rules
- Value Stack Overview, Reference Guide: Published by NYSERDA.
"""


st.info(info_text, icon="ℹ️")

def send_message_get_response(assistant_id, user_message):
    # Create a new thread
    thread_id = st.session_state['thread']

    # Add user message to the thread
    message = client.beta.threads.messages.create(
        thread_id=thread_id, role="user", content=user_message
    )

    # Run the assistant
    run = client.beta.threads.runs.create(
        thread_id=thread_id,
        assistant_id=assistant_id
    )

    # Retrieve the assistant's response
    while True:
        run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)
        if run.status == "completed":
            messages = client.beta.threads.messages.list(thread_id=thread_id)
            latest_message = messages.data[0]
            text = latest_message.content[0].text.value
            return text



def main():
    # Initialize session state variables if not already initialized
    if 'thread' not in st.session_state:
        st.session_state['thread'] = client.beta.threads.create().id
    if 'messages' not in st.session_state:
        st.session_state['messages'] = []
    if 'awaiting_response' not in st.session_state:
        st.session_state['awaiting_response'] = False

    # Display messages using st.chat_message
    for msg in st.session_state.messages:
        if msg['role'] == 'user':
            with st.chat_message("user", avatar="🧑‍💻"):
                st.write(msg["content"])
        else:
            with st.chat_message("assistant", avatar="☀️"):
                st.write(msg["content"])

    # Inform the user if a response is currently being processed
    if st.session_state['awaiting_response']:
        st.spinner('Working on this for you now...')
    else:
        # Get user input from st.chat_input
        user_input = st.chat_input("Please ask me your question...", key="new_message")
        if user_input is not None:
            handle_user_input(user_input)

def handle_user_input(user_input):
    # Append the user message to the session state and update the awaiting response flag
    st.session_state['messages'].append({'role': 'user', 'content': user_input})
    st.session_state['awaiting_response'] = True
    # Refresh the page to show the user message immediately
    st.experimental_rerun()

    # Process the message to get a response
    with st.spinner('Working on this for you now...'):
        response = send_message_get_response(ASSISTANT_ID, user_input)
        # Once response is received, update the session state and the UI
        st.session_state['messages'].append({'role': 'assistant', 'content': response})
        st.session_state['awaiting_response'] = False
        st.experimental_rerun()  # Refresh the page to show the assistant's message

if __name__ == "__main__":
    main()
