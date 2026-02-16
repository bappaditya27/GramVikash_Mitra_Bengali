import streamlit as st
import google.generativeai as genai
import time

# --- ১. কনফিগারেশন ---
st.set_page_config(page_title="গ্রামবিকাশ মিত্র AI", page_icon="🧘")

API_KEY = "AIzaSyAHfvmd1RzoKDynWGPmBrd572Qmm6qHomM" 
genai.configure(api_key=API_KEY)

# আপনার দেওয়া লিস্ট অনুযায়ী সঠিক মডেল
MODEL_NAME = 'models/gemini-2.5-flash'

# সিস্টেম প্রম্পটে আমরা বলে দিচ্ছি যাতে সে বাংলায় উত্তর দেয়
SYSTEM_PROMPT = (
    "You are 'GramVikas Mitra', an empathetic AI mentor. The user has an MSc in Math, "
    "works night shifts at Concentrix, and is studying Data Analytics. "
    "His dream is to build a concrete home in his village and he supports an NGO. "
    "Primary Instruction: ALWAYS respond in Bengali (বাংলা) unless asked otherwise. "
    "Be logical, use math analogies, and prioritize mental health. "
    "একজন বন্ধুর মতো কথা বলো যে তাকে সাহস দেবে।"
)

# --- ২. সেশন স্টেট ---
if "messages" not in st.session_state:
    st.session_state.messages = []

if "chat" not in st.session_state:
    try:
        model = genai.GenerativeModel(MODEL_NAME)
        st.session_state.chat = model.start_chat(history=[])
        st.session_state.chat.send_message(SYSTEM_PROMPT)
    except Exception as e:
        st.error(f"সেটআপে সমস্যা হয়েছে: {e}")

# --- ৩. অটো-রিট্রাই লজিক ---
def send_message_with_retry(prompt, max_retries=3, delay=25):
    for i in range(max_retries):
        try:
            response = st.session_state.chat.send_message(prompt)
            return response.text
        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg:
                st.warning(f"কোটা শেষ হয়েছে। {delay} সেকেন্ড অপেক্ষা করছি... (চেষ্টা {i+1}/{max_retries})")
                time.sleep(delay)
            else:
                raise e
    return "এখনও সার্ভার ব্যস্ত। দয়া করে কিছুক্ষণ পর আবার চেষ্টা করুন।"

# --- ৪. ইউজার ইন্টারফেস (UI) ---
st.title("🤖 গ্রামবিকাশ মিত্র")
st.caption("এখন এটি বাংলায় কথা বলতে প্রস্তুত")

# সাইডবার
if st.sidebar.button("🗑️ চ্যাট ক্লিয়ার করুন"):
    st.session_state.messages = []
    st.session_state.chat = genai.GenerativeModel(MODEL_NAME).start_chat(history=[])
    try: st.session_state.chat.send_message(SYSTEM_PROMPT)
    except: pass
    st.rerun()

# চ্যাট হিস্ট্রি প্রদর্শন
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ইউজার ইনপুট
if prompt := st.chat_input("আপনার মনের কথা বাংলায় লিখুন..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("ভাবছি..."):
            try:
                ai_response = send_message_with_retry(prompt)
                st.markdown(ai_response)
                st.session_state.messages.append({"role": "assistant", "content": ai_response})
            except Exception as e:
                st.error(f"ত্রুটি: {e}")
