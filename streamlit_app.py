import streamlit as st
from openai import OpenAI
import traceback

st.set_page_config(page_title="💬 Chatbot", page_icon="💬")

# Title & description (모델 설명을 실제 사용 모델과 일치)
st.title("💬 Chatbot")
st.write(
    "This is a simple chatbot that uses OpenAI's **GPT-4o-mini** model to generate responses. "
    "To use this app, provide an OpenAI API key from the "
    "[OpenAI dashboard](https://platform.openai.com/account/api-keys). "
    "Learn how this app is built in Streamlit’s tutorial "
    "[here](https://docs.streamlit.io/develop/tutorials/chat-and-llms/build-conversational-apps)."
)

openai_api_key = st.text_input("OpenAI API Key", type="password")

if not openai_api_key:
    st.info("Please add your OpenAI API key to continue.", icon="🗝️")
    st.stop()

# Create client
client = OpenAI(api_key=openai_api_key)

# Chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Render history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("What is up?"):
    # 1) show user message immediately
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2) build messages with system prompt at the very front
    chat_messages = [
        {
            "role": "system",
            "content": (
                "너는 유명한 여행 유튜버야. "
                "입력받은 지역의 여행지와 맛집을 추천해줘. "
                "여행지와 맛집을 나눠서 숫자 말머리를 넣어 출력해줘."
            ),
        },
        *st.session_state.messages,  # includes the latest user message
    ]

    # 3) call OpenAI with streaming + error handling
    with st.chat_message("assistant"):
        try:
            # 컨텍스트 매니저로 열면 연결 정리가 깔끔합니다.
            stream = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=chat_messages,
                stream=True,
            )
            response_text = st.write_stream(stream)  # typewriter streaming
            # 4) save assistant message
            st.session_state.messages.append(
                {"role": "assistant", "content": response_text}
            )
        except Exception as e:
            st.error("⚠️ Error while generating a response. Check your API key, model access, or network.")
            with st.expander("Show error details"):
                st.code("".join(traceback.format_exception_only(type(e), e)))
