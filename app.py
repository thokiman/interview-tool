import streamlit as st
import ollama
from streamlit_js_eval import streamlit_js_eval

st.set_page_config(page_title="Streamlit Chat", page_icon="💬")
st.title("Chatbot")

if "setup_complete" not in st.session_state:
    st.session_state.setup_complete = False
if "user_message_count" not in st.session_state:
    st.session_state.user_message_count = 0
if "feedback_shown" not in st.session_state:
    st.session_state.feedback_shown = False
if "messages" not in st.session_state:
    st.session_state.messages = []
if "chat_complete" not in st.session_state:
    st.session_state.chat_complete = False

def complete_setup():
    st.session_state.setup_complete = True

def show_feedback():
    st.session_state.feedback_shown = True

if not st.session_state.setup_complete:

    st.subheader("Personal information", divider="rainbow")

    if "name" not in st.session_state:
        st.session_state.name = ""
    if "experience" not in st.session_state:
        st.session_state.experience = ""
    if "skills" not in st.session_state:
        st.session_state.skills = ""

    st.session_state.name = st.text_input("Name", max_chars=40, value=st.session_state.name, placeholder="Enter your name")
    st.session_state.experience = st.text_area("Experience", value=st.session_state.experience, height=None, max_chars=200, placeholder="Describe your experience")
    st.session_state.skills = st.text_area("Skills", value=st.session_state.skills, max_chars=200, placeholder="List your skills")

    st.write(f"**Your Name**: {st.session_state.name}")
    st.write(f"**Your Experience**: {st.session_state.experience}")
    st.write(f"**Your Skills**: {st.session_state.skills}")

    st.subheader("Company and Position", divider="rainbow")

    if "level" not in st.session_state:
        st.session_state.level = "Junior"
    if "position" not in st.session_state:
        st.session_state.position = "Data Scientist"
    if "company" not in st.session_state:
        st.session_state.company = "Amazon"

    col1, col2 = st.columns(2)
    with col1:
        st.session_state.level = st.radio("Choose level", key="visibility", options=["Junior", "Mid-level", "Senior"])
    with col2:
        st.session_state.position = st.selectbox("Choose a position", options=["Data Scientist", "Data Engineer", "ML Engineer", "BI Analyst", "Financial Analyst"])

    st.session_state.company = st.selectbox(
        "Choose a company", options=("Amazon", "Meta", "Udemy", "365 Company", "Nestle", "LinkedIn", "Spotify")
    )

    st.write(f"**Your Information**: {st.session_state.level} {st.session_state.position} at {st.session_state.company}")

    if st.button("Start Interview", on_click=complete_setup):
        st.write("Setup complete. Starting interview...")

if st.session_state.setup_complete and not st.session_state.feedback_shown and not st.session_state.chat_complete and not st.session_state.chat_complete:

    st.info(
        """
        Start by introducing yourself.
        """,
        icon="👋"
    )

    if "ollama_model" not in st.session_state:
        st.session_state.ollama_model = 'llama3.1:8b'
    if "ollama_temperature" not in st.session_state:
        st.session_state.ollama_temperature = 0
    if "ollama_max_token" not in st.session_state:
        st.session_state.ollama_max_token = 1000

    if not st.session_state.messages:
        st.session_state.messages = [
            {"role": "system", "content": f"You are an HR executive that interviews an interviewee called {st.session_state.name} with experience {st.session_state.experience} and skills {st.session_state.skills}. You should interview him for the position {st.session_state.level} {st.session_state.position} at the company {st.session_state.company}"}
        ]

    for message in st.session_state.messages:
        if message["role"] != "system":
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    if st.session_state.user_message_count < 5:

        # That's the walrus operator (:=), introduced in Python 3.8.

        # What it does
        # It assigns a value to a variable and returns that value in a single expression — useful inside conditions like if or while.
        # if prompt := st.session_state.ollama_model:
            # this block runs if prompt is truthy
            # AND prompt is now assigned the value of st.session_state.ollama_model

        # Equivalent without walrus

        # prompt = st.session_state.ollama_model
        # if prompt:
        #     ...

        if prompt := st.chat_input("Your answer.", max_chars=1000):
            st.session_state.messages.append({
                "role" : "user",
                "content" : prompt,
            })
            with st.chat_message("user"):
                st.markdown(prompt)

            if st.session_state.user_message_count < 4:
                with st.chat_message("assistant"):
                    max_token = 1000
                    temperature = 0
                    stream = ollama.chat(
                        model=st.session_state.ollama_model,
                        messages=[
                            {"role": m['role'], "content": m["content"]} for m in st.session_state.messages
                        ],
                        stream=True,
                        options={
                            'num_predict': st.session_state.ollama_max_token,
                            'temperature': st.session_state.ollama_temperature
                        }
                    )

                    response = st.write_stream((chunk["message"]["content"] for chunk in stream))
                    print(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
            st.session_state.user_message_count += 1

    if st.session_state.user_message_count >= 5:
        st.session_state.chat_complete = True

if st.session_state.chat_complete and not st.session_state.feedback_shown:
    if st.button("Get Feedback", on_click=show_feedback):
        st.write("Fetching feedback...")

if st.session_state.feedback_shown:
    st.subheader("Feedback")

    conversation_history = "\n".join(f"{msg['role']}: {msg['content']}" for msg in st.session_state.messages)

    feedback_completion = ollama.chat(
        model = st.session_state.ollama_model,
        messages = [
            {"role": "system", "content": """You are a helpful tool that provides feedback on an interviewee perfomance.
            Before the Feedback give a score of 1 to 10.
            Follow this format:
            Overall score: //Your score
            Feedback: //Here you put your feedback
            Give only the feedback do not ask any additional questions.
            """},
            {"role": "user",
             "content": f"This is the interview you need to evaluate. Keep in mind that you are only a tool. And you shouldn't engage in any conversation: {conversation_history}"}
        ],
    )

    st.write(feedback_completion.message.content.strip())

    if st.button("Restart Interview", type="primary"):
        streamlit_js_eval(js_expression="parent.window.location.reload()")


# streamlit run /home/thomas/Documents/Knowledge/ai/code/generative-ai/llm-app/ollama/prototype/app.py