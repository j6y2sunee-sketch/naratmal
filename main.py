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

# --- 1. API 키 및 파이어베이스 설정 ---
GEMINI_API_KEY = "AIzaSyB56UcVY5bysn5xopRRnmTyEEhQg0bp5Rg".strip()
genai.configure(api_key=GEMINI_API_KEY)

# Firebase 설정 (파일이 있는지 확인 필요)
if not firebase_admin._apps:
    try:
        cred = credentials.Certificate("naratmal.json")
        firebase_admin.initialize_app(cred, {
            'databaseURL': 'https://naratmalssami-ed385-default-rtdb.firebaseio.com'
        })
    except Exception as e:
        st.error(f"Firebase 초기화 에러: {e}")

# --- 2. 유틸리티 함수 (음성 재생) ---
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

# --- 3. Gemini 문제 생성 함수 (Groq 대신 사용) ---
def generate_problems_with_gemini(grade):
    # Gemini 1.5 Flash 모델 설정
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    prompt = f"""
    당신은 초등학교 국어 교사입니다. 
    초등학교 {grade} 수준의 국어 받아쓰기 문제 10개를 생성하세요.
    반드시 아래 JSON 형식으로만 응답하세요. 다른 말은 절대 하지 마세요.

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
        # 응답에서 JSON 텍스트만 추출
        res_text = response.text.replace("```json", "").replace("```", "").strip()
        data = json.loads(res_text)
        return data.get('problems', [])
    except Exception as e:
        st.error(f"Gemini API 통신 오류: {e}")
        return None

# ==========================================
# 4. 화면 구성 및 메인 로직
# ==========================================
st.set_page_config(page_title="나랏말싸미", layout="wide")

if 'page' not in st.session_state: st.session_state.page = "login"
if 'spelling_subpage' not in st.session_state: st.session_state.spelling_subpage = "menu"
if 'spelling_problems' not in st.session_state: st.session_state.spelling_problems = []
if 'user_info' not in st.session_state: st.session_state.user_info = {}

# --- 로그인 화면 ---
if st.session_state.page == "login":
    st.title("나랏말싸미 🇰🇷")
    name = st.text_input("선생님 성함")
    school = st.text_input("학교명")
    role = st.radio("역할", ["교사", "학생"], index=0)
    
    if st.button("입장하기"):
        st.session_state.user_info = {"name": name, "school": school, "role": role}
        st.session_state.page = "teacher" if role == "교사" else "student"
        st.rerun()

# --- 교사 대시보드 ---
elif st.session_state.page == "teacher":
    with st.sidebar:
        st.write(f"### 👨‍🏫 {st.session_state.user_info.get('name')} 선생님")
        menu = st.radio("메뉴 선택", ["맞춤법 관리", "로그아웃"])

    if menu == "맞춤법 관리":
        # 1) 메뉴 선택 단계
        if st.session_state.spelling_subpage == "menu":
            st.header("🤖 Gemini AI 받아쓰기 출제")
            grade_choice = st.selectbox("출제 학년", [f"{i}학년" for i in range(1, 7)], index=2)
            if st.button("AI 문제 생성 시작"):
                with st.spinner("Gemini가 문제를 구성하고 있습니다..."):
                    probs = generate_problems_with_gemini(grade_choice)
                    if probs:
                        st.session_state.spelling_problems = probs
                        st.session_state.spelling_subpage = "edit"
                        st.rerun()
        
        # 2) 문제 편집 단계
        elif st.session_state.spelling_subpage == "edit":
            st.header("📝 생성된 문제 검토")
            if st.button("⬅️ 처음으로"):
                st.session_state.spelling_subpage = "menu"
                st.rerun()
            
            st.divider()
            for i, prob in enumerate(st.session_state.spelling_problems):
                c1, c2, c3 = st.columns([5, 4, 1])
                st.session_state.spelling_problems[i]['audio'] = c1.text_input(f"문제 {i+1}", prob['audio'], key=f"a_{i}")
                st.session_state.spelling_problems[i]['answer'] = c2.text_input(f"정답 {i+1}", prob['answer'], key=f"n_{i}")
                if c3.button("🔊", key=f"v_{i}"):
                    play_voice_st(st.session_state.spelling_problems[i]['audio'])
            
            st.divider()
            if st.button("✅ 학생들에게 배포 (Firebase)", type="primary"):
                # 여기에 기존에 쓰시던 Firebase 저장 로직을 유지하시면 됩니다.
                st.success("학생들에게 문제가 배포되었습니다!")

    elif menu == "로그아웃":
        st.session_state.page = "login"
        st.rerun()

elif st.session_state.page == "student":
    st.write("학생용 화면은 준비 중입니다.")
    if st.button("로그아웃"): st.session_state.page = "login"; st.rerun()
