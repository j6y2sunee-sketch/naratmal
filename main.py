import streamlit as st
import time
import base64
import requests
import json
import io
import firebase_admin
from firebase_admin import credentials, db
from gtts import gTTS

# --- API 키 및 파이어베이스 설정 ---
# ⚠️ 아래 큰따옴표 안에 새로 발급받은 'gsk_'로 시작하는 키를 붙여넣으세요!
GROQ_API_KEY = "여기에_새로_발급받은_API_키를_넣어주세요".strip()
TARGET_URL = "https://api.groq.com/openai/v1/chat/completions".strip()

# Firebase가 이미 초기화되었는지 확인 후 초기화 (중복 방지)
if not firebase_admin._apps:
    try:
        # Streamlit Cloud에 naratmal.json 파일이 업로드되어 있어야 합니다.
        cred = credentials.Certificate("naratmal.json")
        firebase_admin.initialize_app(cred, {
            'databaseURL': 'https://naratmalssami-ed385-default-rtdb.firebaseio.com'
        })
    except Exception as e:
        st.error(f"Firebase 초기화 에러: {e}")

# --- 웹용 TTS (음성 재생) 함수 ---
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

# ==========================================
# 1. 페이지 및 기본 설정
# ==========================================
st.set_page_config(page_title="나랏말싸미", layout="wide")

if 'page' not in st.session_state:
    st.session_state.page = "login"
if 'spelling_subpage' not in st.session_state:
    st.session_state.spelling_subpage = "menu"
if 'spelling_problems' not in st.session_state:
    st.session_state.spelling_problems = []
if 'ai_grade' not in st.session_state:
    st.session_state.ai_grade = "3학년"
if 'user_info' not in st.session_state:
    st.session_state.user_info = {"name": "", "role": "", "school": "", "grade": "", "class": ""}

# 테스트용 데이터
if 'mock_users' not in st.session_state:
    st.session_state.mock_users = {
        "uid_001": {"role": "학생", "school": "테스트초", "grade": "3", "class": "1", "name": "김꿈틀", "scores": {"total": 420, "spelling": 100, "literacy": 90, "writing": 80, "jiphyeon": 150}, "ai_report": "분석 전입니다."},
        "uid_002": {"role": "학생", "school": "테스트초", "grade": "3", "class": "1", "name": "이새싹", "scores": {"total": 350, "spelling": 80, "literacy": 85, "writing": 75, "jiphyeon": 110}, "ai_report": "분석 전입니다."}
    }

# ==========================================
# 2. 화면 구성 함수들
# ==========================================

def render_login_page():
    try:
        with open("bg.png", "rb") as f:
            data = f.read()
            bin_str = base64.b64encode(data).decode()
    except: bin_str = ""

    st.markdown(f"""
        <style>
        .stApp {{ background: url("data:image/png;base64,{bin_str}"); background-size: cover; }}
        .block-container {{ background-color: rgba(255, 255, 255, 0.95); padding: 40px; border-radius: 20px; max-width: 420px; margin-top: 10vh; box-shadow: 0 4px 15px rgba(0,0,0,0.2); }}
        .title-main {{ font-size: 50px; font-weight: bold; color: #5D4037; text-align: center; margin: 0; }}
        .title-sub {{ font-size: 30px; font-weight: bold; color: #5D4037; text-align: center; margin-bottom: 20px; }}
        .stButton>button {{ width: 100%; background-color: #8D6E63; color: white; }}
        </style>
        """, unsafe_allow_html=True)

    st.markdown('<p class="title-main">나랏말싸미</p><p class="title-sub">:꿈틀이의 문해력 키우기</p>', unsafe_allow_html=True)
    school = st.text_input("학교명")
    col1, col2 = st.columns(2)
    with col1: grade = st.selectbox("학년", ["1", "2", "3", "4", "5", "6"])
    with col2: classroom = st.text_input("반")
    name = st.text_input("이름")
    role = st.radio("역할", ["학생", "교사"], horizontal=True)
    
    if st.button("입장하기"):
        st.session_state.user_info = {"name": name, "role": role, "school": school, "grade": grade, "class": classroom}
        st.session_state.page = "teacher" if role == "교사" else "student"
        st.rerun()

def render_teacher_dashboard():
    with st.sidebar:
        st.markdown(f"### 👨‍🏫 {st.session_state.user_info['name']} 선생님")
        menu = st.radio("메뉴", ["학생 관리", "맞춤법 및 받아쓰기 관리", "로그아웃"])

    if menu == "학생 관리":
        st.header("학생 관리")
        for uid, data in st.session_state.mock_users.items():
            st.subheader(f"👤 {data['name']} (총점: {data['scores']['total']})")
            st.info(data['ai_report'])
            st.divider()

    elif menu == "맞춤법 및 받아쓰기 관리":
        if st.session_state.spelling_subpage == "menu":
            c1, c2 = st.columns(2)
            with c1:
                st.info("🤖 AI 자동 출제")
                st.session_state.ai_grade = st.selectbox("학년 수준", ["1학년", "2학년", "3학년", "4학년", "5학년", "6학년"])
                if st.button("AI 출제 시작"):
                    st.session_state.spelling_subpage = "ai_loading"
                    st.rerun()
            with c2:
                st.info("✍️ 직접 출제")
                if st.button("직접 출제하기"):
                    st.session_state.spelling_problems = [{"audio": "", "answer": ""} for _ in range(10)]
                    st.session_state.spelling_subpage = "manual"
                    st.rerun()

        elif st.session_state.spelling_subpage == "ai_loading":
            with st.spinner("AI가 문제를 만들고 있습니다..."):
                try:
                    payload = {
                        "model": "llama-3.3-70b-versatile",
                        "messages": [
                            {"role": "system", "content": "You are a helpful assistant that outputs only JSON."},
                            {"role": "user", "content": f"초등학교 {st.session_state.ai_grade} 수준 국어 받아쓰기 문제 10개를 JSON으로 만들어줘. 형식: {{'problems': [{{'audio': '문장', 'answer': '정답'}}]}}"}
                        ],
                        "response_format": {"type": "json_object"}
                    }
                    res = requests.post(TARGET_URL, json=payload, headers={"Authorization": f"Bearer {GROQ_API_KEY}"})
                    if res.status_code == 200:
                        data = res.json()
                        st.session_state.spelling_problems = json.loads(data['choices'][0]['message']['content'])['problems']
                        st.session_state.spelling_subpage = "ai_edit"
                        st.rerun()
                    else:
                        st.error(f"에러 코드: {res.status_code}")
                        st.write(res.json())
                        if st.button("돌아가기"): st.session_state.spelling_subpage = "menu"; st.rerun()
                except Exception as e:
                    st.error(f"오류: {e}")
                    if st.button("돌아가기"): st.session_state.spelling_subpage = "menu"; st.rerun()

        elif st.session_state.spelling_subpage in ["ai_edit", "manual"]:
            st.subheader("📝 문제 확인 및 수정")
            if st.button("⬅️ 뒤로가기"): st.session_state.spelling_subpage = "menu"; st.rerun()
            
            for i, prob in enumerate(st.session_state.spelling_problems):
                col1, col2, col3 = st.columns([5, 4, 1])
                st.session_state.spelling_problems[i]["audio"] = col1.text_input(f"소리 {i+1}", prob['audio'])
                st.session_state.spelling_problems[i]["answer"] = col2.text_input(f"정답 {i+1}", prob['answer'])
                if col3.button("🔊", key=f"v_{i}"): play_voice_st(prob['audio'])
            
            if st.button("✅ 학생들에게 배포 (Firebase 저장)", type="primary"):
                try:
                    u = st.session_state.user_info
                    path = f"spelling_tests/{u['school']}/{u['grade']}/{u['class']}"
                    db.reference(path).set({"problems": st.session_state.spelling_problems, "created_at": time.time()})
                    st.success("배포 완료!")
                except Exception as e: st.error(f"저장 실패: {e}")

    elif menu == "로그아웃":
        st.session_state.page = "login"; st.rerun()

# --- 실행 ---
if st.session_state.page == "login": render_login_page()
elif st.session_state.page == "teacher": render_teacher_dashboard()
elif st.session_state.page == "student": st.write("학생 페이지 준비 중입니다.")
