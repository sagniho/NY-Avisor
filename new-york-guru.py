import streamlit as st
from openai import OpenAI
import time

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# Define the advisors
ADVISORS = {
    "NY Solar Advisor": {
        "id": st.secrets["NY_ADVISOR"],
        "image": "ny.png",
        "info_text": """
        This AI assistant leverages GPT-4 technology with a knowledge cutoff in April 2024 to provide expert guidance on solar energy policies and incentives in New York. It integrates detailed document analysis for tailored, strategic advice.

        Key Documents in the Knowledge Base:
        - 2024 Solar and Wind Tax Model: Guidance on tax models for solar and wind projects. Published by the New York State Tax Department.
        - 2024_Solar_and_Wind_Appraisal_Model_User_Guide: Details on how to appraise solar and wind projects. Published by the New York State Tax Department.
        - 2024-Gold-Book-Public: Comprehensive industry data and standards. Published by NYISO.
        - New York Community Solar Policy Guide for Asset Owners & Developers: Guidelines for community solar projects. Created by Perch Energy's internal policy team.
        - NY SUN Long Island + Upstate-Program-Manual: Program details for NY SUN's initiatives. Published by NYSERDA.
        - NYSEG Queue Order by Substation: Latest queue order by substation for NYSEG. Published by NYSEG itself.
        - Residential-SC-Program-Manual: Information on the residential solar credit program.
        - Net Metering rules
        - Value Stack Overview, Reference Guide: Published by NYSERDA.
        """
    },
    "MD Solar Advisor": {
        "id": st.secrets["MD_ADVISOR"],
        "image": "maryland.png",
        "info_text": """
        This AI assistant provides guidance on solar energy policies and incentives in Maryland.
        """
    }
}

def display_advisors():
    cols = st.columns(len(ADVISORS))
    for i, (advisor, data) in enumerate(ADVISORS.items()):
        with cols[i]:
            st.image(data["image"], width=150)
            st.write(advisor)
            if st.button(f"Select {advisor}", key=f"select_{i}"):
                st.session_state.selected_advisor = advisor

def display_selected_advisor():
    advisor = st.session_state.selected_advisor
    data = ADVISORS[advisor]

    col1, col2 = st.columns([1, 4])
    with col1:
        st.image(data["image"], width=150)
    with col2:
        st.markdown(f"<h2 style='margin-top: 0;padding-left: 10px;'>{advisor}</h2>", unsafe_allow_html=True)
        st.markdown("<em><p style='margin-top: 0; padding-left: 10px;'>Your interactive AI-powered guide to Solar policies and incentives</p></em>", unsafe_allow_html=True)

    st.info(data["info_text"], icon="ℹ️")

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
    st.sidebar.title("Select Advisor")
    selected_advisor = st.sidebar.selectbox("Choose an advisor", list(ADVISORS.keys()))
    st.session_state.selected_advisor = selected_advisor

    if "selected_advisor" not in st.session_state:
        display_advisors()
    else:
        display_selected_advisor()

        if 'thread' not in st.session_state:
            st.session_state['thread'] = client.beta.threads.create().id
        if 'messages' not in st.session_state:
            st.session_state['messages'] = []

        for msg in st.session_state.messages:
            if msg['role'] == 'user':
                with st.chat_message("user", avatar="🧑‍💻"):
                    st.write(msg["content"])
            else:
                with st.chat_message("assistant", avatar="☀️"):
                    st.write(msg["content"])

        user_input = st.chat_input(placeholder="Please ask me your question…")

        if user_input:
            st.session_state['messages'].append({'role': 'user', 'content': user_input})
            with st.chat_message("user", avatar="🧑‍💻"):
                    st.write(user_input)

            with st.spinner('Working on this for you now...'):
                response = send_message_get_response(ADVISORS[selected_advisor]["id"], user_input)
                st.session_state['messages'].append({'role': 'assistant', 'content': response})
                with st.chat_message("assistant", avatar="☀️"):
                    st.write(response)

if __name__ == "__main__":
    main()
