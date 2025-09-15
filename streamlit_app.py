import streamlit as st
from openai import OpenAI
import traceback
import os
from dotenv import load_dotenv

st.set_page_config(page_title="💬 Chatbot", page_icon="💬")

# Load API key from chatgpt.env
load_dotenv("chatgpt.env")

# Title & description (모델 설명을 실제 사용 모델과 일치)
st.title("💬 Chatbot")
st.write(
    "This chatbot uses OpenAI's **GPT-4o-mini** model. "
    "The OpenAI API key is automatically loaded from the local `chatgpt.env` file (variable: `OPENAI_API_KEY`). "
    "If the key is missing, you'll see a notice below."
)

# Sidebar: Chatbot self description
with st.sidebar:
    st.header("About this chatbot")
    st.markdown(
        """
        **이 챗봇은 여행 추천에 특화된 비서입니다.**\
        스스로를 유명한 여행 유튜버로 소개하고, 사용자가 입력한 지역을 바탕으로
        • 볼거리/명소\
        • 현지 맛집\
        을 구분하여 깔끔한 리스트로 제안합니다.

        특징
        - 친근하고 명확한 톤으로 설명합니다.
        - 핵심 정보(이유, 위치/특징, 팁)를 간단히 요약합니다.
        - 중복을 피하고, 여행 동선까지 고려하려 노력합니다.

        사용 방법
        - 예: "오사카 2박 3일 맛집과 명소 추천" / "제주도 비 오는 날 갈 곳" 등
        - 더 구체적일수록 맞춤 추천이 좋아집니다.
        """
    )

openai_api_key = os.getenv("OPENAI_API_KEY")

if not openai_api_key:
    st.info(
        "chatgpt.env 파일에 `OPENAI_API_KEY` 값을 설정한 뒤 앱을 다시 실행하세요.",
        icon="🗝️",
    )
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
