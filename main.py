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
# API 설정 (가장 안정적인 v1 버전 사용 시도)
genai.configure(api_key=GEMINI_API_KEY)

# Firebase 초기화
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

# ==========================================
# 1. 페이지 및 기본 설정
# ==========================================
st.set_page_config(page_title="나랏말싸미", layout="wide")

if 'page' not in st.session_state: st.session_state.page = "login"
if 'spelling_subpage' not in st.session_state: st.session_state.spelling_subpage = "menu"
if 'spelling_problems' not in st.session_state: st.session_state.spelling_problems = []
if 'ai_grade' not in st.session_state: st.session_state.ai_grade = "3학년"
if 'user_info' not in st.session_state: st.session_state.user_info = {"name": "", "role": "", "school": "", "grade": "", "class": ""}

# 테스트용 데이터
if 'mock_users' not in st.session_state:
    st.session_state.mock_users = {
        "uid_001": {"role": "학생", "school": "테스트초", "grade": "3", "class": "1", "name": "김꿈틀", "scores": {"total": 420, "spelling": 100, "literacy": 90, "writing": 80, "jiphyeon": 150}, "ai_report": "버튼을 눌러 현재 학습 데이터를 분석해보세요."},
        "uid_002": {"role": "학생", "school": "테스트초", "grade": "3", "class": "1", "name": "이새싹", "scores": {"total": 350, "spelling": 80, "literacy": 85, "writing": 75, "jiphyeon": 110}, "ai_report": "버튼을 눌러 현재 학습 데이터를 분석해보세요."},
        "uid_003": {"role": "학생", "school": "테스트초", "grade": "3", "class": "1", "name": "박나무", "scores": {"total": 390, "spelling": 90, "literacy": 80, "writing": 100, "jiphyeon": 120}, "ai_report": "버튼을 눌러 현재 학습 데이터를 분석해보세요."}
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
        .stApp {{ background: url("data:image/png;base64,{bin_str}"); background-size: cover; background-position: center; background-attachment: fixed; }}
        .block-container {{ background-color: rgba(255, 255, 255, 0.95) !important; padding: 40px !important; border-radius: 20px !important; max-width: 420px !important; margin-top: 10vh !important; box-shadow: 0 4px 15px rgba(0,0,0,0.2) !important; }}
        .title-main {{ font-size: 50px !important; font-weight: bold !important; color: #5D4037 !important; text-align: center; margin-bottom: 0px; line-height: 1.2; }}
        .title-sub {{ font-size: 30px !important; font-weight: bold !important; color: #5D4037 !important; text-align: center; margin-top: 0px; margin-bottom: 20px; }}
        div.stButton {{ display: flex; justify-content: center; }}
        .stButton>button {{ width: 350px !important; height: 50px !important; background-color: #8D6E63 !important; color: white !important; border-radius: 8px !important; font-size: 18px !important; font-weight: bold !important; border: none !important; margin-top: 20px !important; }}
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
        if not school or not name: st.error("학교명과 이름을 입력해주세요.")
        else:
            st.session_state.user_info = {"name": name, "role": role, "school": school, "grade": grade, "class": classroom}
            st.session_state.page = "teacher" if role == "교사" else "student"
            st.rerun()

def render_teacher_dashboard():
    st.markdown("""<style>.stApp { background: #F8F9FA !important; } .score-box { display: inline-block; padding: 6px 14px; border-radius: 15px; margin-right: 10px; margin-bottom: 8px; font-weight: bold; font-size: 14px; color: #333; } .bg-spelling { background-color: #FDEEF4; } .bg-literacy { background-color: #EBF4FA; } .bg-writing { background-color: #F0F9ED; } .bg-jiphyeon { background-color: #FFF9E5; }</style>""", unsafe_allow_html=True)

    with st.sidebar:
        st.markdown(f"### 👨‍🏫 {st.session_state.user_info['name']} 선생님")
        st.caption(f"{st.session_state.user_info['school']} {st.session_state.user_info['grade']}학년 {st.session_state.user_info['class']}반")
        st.divider()
        menu = st.radio("이동할 메뉴 선택", ["홈", "학생 관리", "맞춤법 및 받아쓰기 관리", "로그아웃"], index=2)

    if menu == "홈":
        st.header("나랏말싸미 교사 대시보드")
        st.info("👈 왼쪽 메뉴를 선택해주세요.")

    elif menu == "학생 관리":
        st.header("[학생 관리]")
        for uid, data in st.session_state.mock_users.items():
            st.subheader(f"👤 {data['name']} (총점: {data['scores']['total']}점)")
            st.info(data['ai_report'])
            st.divider()

    elif menu == "맞춤법 및 받아쓰기 관리":
        st.header("[맞춤법 및 받아쓰기 관리]")
        
        if st.session_state.spelling_subpage == "menu":
            col1, col2 = st.columns(2)
            with col1:
                st.info("🤖 AI 자동 출제")
                ai_grade = st.selectbox("학년 수준", [f"{i}학년" for i in range(1, 7)], index=2)
                if st.button("AI 출제 시작"):
                    st.session_state.ai_grade = ai_grade
                    st.session_state.spelling_subpage = "ai_loading"
                    st.rerun()
            with col2:
                st.info("✍️ 교사 직접 출제")
                if st.button("직접 출제하기"):
                    st.session_state.spelling_problems = [{"audio": "", "answer": ""} for _ in range(10)]
                    st.session_state.spelling_subpage = "manual"
                    st.rerun()

        elif st.session_state.spelling_subpage == "ai_loading":
            with st.spinner(f"Gemini AI가 문제를 생성 중입니다..."):
                try:
                    # 💡 해결 포인트: 'models/gemini-1.5-flash' 대신 이름만 사용 시도
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    prompt = f"초등학교 {st.session_state.ai_grade} 수준 국어 받아쓰기 문제 10개를 생성해. JSON 형식으로만 답해. 형식: {{'problems': [{{'audio': '문장', 'answer': '정답'}}]}}"
                    
                    response = model.generate_content(prompt)
                    # 마크다운 제거 로직
                    clean_text = response.text.replace("```json", "").replace("```", "").strip()
                    data = json.loads(clean_text)
                    
                    st.session_state.spelling_problems = data.get('problems', [])
                    st.session_state.spelling_subpage = "ai_edit"
                    st.rerun()
                except Exception as e:
                    st.error(f"⚠️ AI 통신 오류: {e}")
                    if st.button("다시 시도"): st.rerun()
                    if st.button("메뉴로 돌아가기"): 
                        st.session_state.spelling_subpage = "menu"
                        st.rerun()

        elif st.session_state.spelling_subpage in ["ai_edit", "manual"]:
            st.subheader("📝 문제 확인 및 수정")
            if st.button("⬅️ 뒤로가기"): 
                st.session_state.spelling_subpage = "menu"
                st.rerun()
            
            for i, prob in enumerate(st.session_state.spelling_problems):
                c1, c2, c3, c4 = st.columns([1, 4, 3, 1])
                with c1: st.write(f"{i+1}번")
                with c2: st.session_state.spelling_problems[i]["audio"] = st.text_input(f"소리{i}", prob.get("audio", ""), key=f"aud_{i}", label_visibility="collapsed")
                with c3: st.session_state.spelling_problems[i]["answer"] = st.text_input(f"정답{i}", prob.get("answer", ""), key=f"ans_{i}", label_visibility="collapsed")
                with c4: 
                    if st.button("🔊", key=f"v_{i}"): play_voice_st(st.session_state.spelling_problems[i]["audio"])

            if st.button("✅ 학생들에게 배포", type="primary"):
                try:
                    u = st.session_state.user_info
                    path = f"spelling_tests/{u['school']}/{u['grade']}/{u['class']}"
                    db.reference(path).set({
                        "title": f"{u['grade']}학년 {u['class']}반 받아쓰기",
                        "problems": st.session_state.spelling_problems,
                        "created_at": str(time.time())
                    })
                    st.success("배포 완료!")
                except Exception as e: st.error(f"저장 실패: {e}")

    elif menu == "로그아웃":
        st.session_state.page = "login"; st.rerun()

# 메인 라우터
if st.session_state.page == "login": render_login_page()
elif st.session_state.page == "teacher": render_teacher_dashboard()
elif st.session_state.page == "student": st.success("학생 페이지 준비 중입니다.")
