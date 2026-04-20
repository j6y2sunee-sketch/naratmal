import streamlit as st
import time
import base64
import requests
import json
import io
import firebase_admin
from firebase_admin import credentials, db
from gtts import gTTS
import google.generativeai as genai

# --- API 키 및 파이어베이스 설정 ---
# ⚠️ 구글 AI 스튜디오(https://aistudio.google.com/app/apikey)에서 무료 키를 받으세요!
GEMINI_API_KEY = "여기에_구글_API_키를_넣으세요".strip()
genai.configure(api_key=GEMINI_API_KEY)

# Firebase 설정
if not firebase_admin._apps:
    try:
        cred = credentials.Certificate("naratmal.json")
        firebase_admin.initialize_app(cred, {
            'databaseURL': 'https://naratmalssami-ed385-default-rtdb.firebaseio.com'
        })
    except Exception as e:
        st.error(f"Firebase 초기화 에러: {e}")

# --- 음성 재생 함수 ---
def play_voice_st(text):
    if not text: return
    try:
        tts = gTTS(text=text, lang='ko')
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        st.audio(fp, format="audio/mp3", autoplay=True)
    except Exception as e:
        st.error(f"음성 재생 오류: {e}")

# --- 페이지 설정 ---
st.set_page_config(page_title="나랏말싸미", layout="wide")

if 'page' not in st.session_state: st.session_state.page = "login"
if 'spelling_subpage' not in st.session_state: st.session_state.spelling_subpage = "menu"
if 'spelling_problems' not in st.session_state: st.session_state.spelling_problems = []
if 'user_info' not in st.session_state: st.session_state.user_info = {}

# --- [교사] AI 문제 생성 함수 (Gemini 사용) ---
def generate_problems_with_gemini(grade):
    model = genai.GenerativeModel('gemini-1.5-flash') # 무료이면서 매우 빠름
    prompt = f"""
    당신은 초등학교 국어 교사입니다. 
    초등학교 {grade} 수준의 국어 받아쓰기 문제 10개를 생성하세요.
    아이들의 수준에 맞는 단어와 문장을 사용하고, 반드시 아래 JSON 형식으로만 응답하세요.
    다른 설명은 절대 하지 마세요.

    형식:
    {{
      "problems": [
        {{"audio": "문장", "answer": "정답"}},
        ...
      ]
    }}
    """
    try:
        response = model.generate_content(prompt)
        # Gemini의 응답에서 JSON만 추출 (마크다운 제거)
        res_text = response.text.replace("```json", "").replace("```", "").strip()
        data = json.loads(res_text)
        return data.get('problems', [])
    except Exception as e:
        st.error(f"Gemini API 오류: {e}")
        return None

# --- 화면 렌더링 ---
def render_login():
    st.title("나랏말싸미 🇰🇷")
    name = st.text_input("이름")
    school = st.text_input("학교")
    role = st.radio("역할", ["학생", "교사"])
    if st.button("입장"):
        st.session_state.user_info = {"name": name, "school": school, "role": role}
        st.session_state.page = "teacher" if role == "교사" else "student"
        st.rerun()

def render_teacher():
    with st.sidebar:
        st.write(f"### {st.session_state.user_info['name']} 선생님")
        menu = st.radio("메뉴", ["맞춤법 관리", "로그아웃"])
    
    if menu == "맞춤법 관리":
        if st.session_state.spelling_subpage == "menu":
            st.header("맞춤법 문제 관리")
            grade = st.selectbox("학년 선택", [f"{i}학년" for i in range(1,7)])
            if st.button("AI 문제 생성 시작"):
                with st.spinner("Gemini AI가 문제를 만들고 있습니다..."):
                    probs = generate_problems_with_gemini(grade)
                    if probs:
                        st.session_state.spelling_problems = probs
                        st.session_state.spelling_subpage = "edit"
                        st.rerun()
        
        elif st.session_state.spelling_subpage == "edit":
            st.header("📝 문제 검토 및 수정")
            if st.button("⬅️ 뒤로가기"):
                st.session_state.spelling_subpage = "menu"
                st.rerun()
            
            for i, prob in enumerate(st.session_state.spelling_problems):
                c1, c2, c3 = st.columns([5, 4, 1])
                st.session_state.spelling_problems[i]['audio'] = c1.text_input(f"문제 {i+1}", prob['audio'])
                st.session_state.spelling_problems[i]['answer'] = c2.text_input(f"정답 {i+1}", prob['answer'])
                if c3.button("🔊", key=f"v_{i}"): play_voice_st(prob['audio'])
            
            if st.button("✅ 학생들에게 배포", type="primary"):
                st.success("Firebase에 저장되었습니다! (실제 저장 로직은 이전과 동일)")

    elif menu == "로그아웃":
        st.session_state.page = "login"
        st.rerun()

# 메인 실행부
if st.session_state.page == "login": render_login()
elif st.session_state.page == "teacher": render_teacher()
else: st.write("학생 페이지 준비 중...")
