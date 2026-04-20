import streamlit as st
import time
import base64
import requests
import json
import io
import firebase_admin
from firebase_admin import credentials, db
from gtts import gTTS
import google.generativeai as genai  # 구글 제미나이 공식 도구

# --- 1. API 키 및 파이어베이스 설정 ---
GEMINI_API_KEY = "AIzaSyCCAWQdULdgUlbaFpvGZ9tFC_jPvPY1JjI".strip()
genai.configure(api_key=GEMINI_API_KEY)

# Firebase 초기화 (중복 방지)
if not firebase_admin._apps:
    try:
        cred = credentials.Certificate("naratmal.json") # JSON 파일이 같은 폴더에 있어야 합니다!
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
        # Streamlit에서 오디오 플레이어 띄우기 (자동 재생)
        st.audio(fp, format="audio/mp3", autoplay=True)
    except Exception as e:
        st.error(f"음성 재생 오류: {e}")

# ==========================================
# 1. 페이지 및 기본 설정
# ==========================================
st.set_page_config(page_title="나랏말싸미", layout="wide")

# 세션 상태(Session State) 초기화
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

# 파이어베이스를 대신할 가상 데이터베이스 (테스트용)
if 'mock_users' not in st.session_state:
    st.session_state.mock_users = {
        "uid_001": {
            "role": "학생", "school": "테스트초", "grade": "3", "class": "1", "name": "김꿈틀",
            "scores": {"total": 420, "spelling": 100, "literacy": 90, "writing": 80, "jiphyeon": 150},
            "ai_report": "버튼을 눌러 현재 학습 데이터를 분석해보세요."
        },
        "uid_002": {
            "role": "학생", "school": "테스트초", "grade": "3", "class": "1", "name": "이새싹",
            "scores": {"total": 350, "spelling": 80, "literacy": 85, "writing": 75, "jiphyeon": 110},
            "ai_report": "버튼을 눌러 현재 학습 데이터를 분석해보세요."
        },
        "uid_003": {
            "role": "학생", "school": "테스트초", "grade": "3", "class": "1", "name": "박나무",
            "scores": {"total": 390, "spelling": 90, "literacy": 80, "writing": 100, "jiphyeon": 120},
            "ai_report": "버튼을 눌러 현재 학습 데이터를 분석해보세요."
        }
    }

# ==========================================
# 2. 화면 구성 함수들
# ==========================================

def render_login_page():
    """로그인 화면 UI"""
    try:
        with open("bg.png", "rb") as f:
            data = f.read()
            bin_str = base64.b64encode(data).decode()
    except FileNotFoundError:
        bin_str = ""

    st.markdown(
        f"""
        <style>
        .stApp {{
            background: url("data:image/png;base64,{bin_str}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}
        header, footer {{ visibility: hidden; }}
        
        .block-container {{
            background-color: rgba(255, 255, 255, 0.95) !important;
            padding: 40px !important;
            border-radius: 20px !important;
            max-width: 420px !important;
            margin-top: 10vh !important;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2) !important;
        }}
        .title-main {{ font-size: 50px !important; font-weight: bold !important; color: #5D4037 !important; text-align: center; margin-bottom: 0px; line-height: 1.2; }}
        .title-sub {{ font-size: 30px !important; font-weight: bold !important; color: #5D4037 !important; text-align: center; margin-top: 0px; margin-bottom: 20px; }}
        
        div.stButton {{ display: flex; justify-content: center; }}
        .stButton>button {{ width: 350px !important; height: 50px !important; background-color: #8D6E63 !important; color: white !important; border-radius: 8px !important; font-size: 18px !important; font-weight: bold !important; border: none !important; margin-top: 20px !important; }}
        .stButton>button:hover {{ background-color: #5D4037 !important; }}
        </style>
        """,
        unsafe_allow_html=True
    )

    st.markdown('<p class="title-main">나랏말싸미</p>', unsafe_allow_html=True)
    st.markdown('<p class="title-sub">:꿈틀이의 문해력 키우기</p>', unsafe_allow_html=True)
    
    school = st.text_input("학교명")
    col1, col2 = st.columns(2)
    with col1:
        grade = st.selectbox("학년", ["1", "2", "3", "4", "5", "6"])
    with col2:
        classroom = st.text_input("반")
        
    name = st.text_input("이름")
    pw = st.text_input("비밀번호", type="password")
    role = st.radio("역할", ["학생", "교사"], horizontal=True)
    
    if st.button("입장하기"):
        if not school or not name:
            st.error("학교명과 이름을 모두 입력해주세요.")
        else:
            st.session_state.user_info = {
                "name": name, "role": role, "school": school, "grade": grade, "class": classroom
            }
            st.session_state.page = "teacher" if role == "교사" else "student"
            st.rerun()

def render_teacher_dashboard():
    """교사 대시보드 화면 UI"""
    st.markdown("""
        <style>
        .stApp { background: #F8F9FA !important; }
        .block-container { max-width: 1000px !important; background-color: transparent !important; padding: 3rem 2rem !important; box-shadow: none !important; margin-top: 0 !important; }
        .score-box { display: inline-block; padding: 6px 14px; border-radius: 15px; margin-right: 10px; margin-bottom: 8px; font-weight: bold; font-size: 14px; color: #333; }
        .bg-spelling { background-color: #FDEEF4; }
        .bg-literacy { background-color: #EBF4FA; }
        .bg-writing { background-color: #F0F9ED; }
        .bg-jiphyeon { background-color: #FFF9E5; }
        </style>
    """, unsafe_allow_html=True)

    with st.sidebar:
        st.markdown(f"### 👨‍🏫 {st.session_state.user_info['name']} 선생님")
        st.caption(f"{st.session_state.user_info['school']} {st.session_state.user_info['grade']}학년 {st.session_state.user_info['class']}반")
        st.divider()
        menu = st.radio(
            "이동할 메뉴를 선택하세요",
            ["홈", "학생 관리", "맞춤법 및 받아쓰기 관리", "문해력 관리", "글쓰기 관리", "로그아웃"],
            index=1 # 기본으로 학생 관리가 보이게 설정
        )

    if menu == "홈":
        st.markdown('<h2>나랏말싸미 <span style="color:#8D6E63;">교사 대시보드</span>입니다.</h2>', unsafe_allow_html=True)
        st.info("👈 왼쪽 메뉴를 선택하여 학생들의 학습을 관리해주세요.")
        st.success("오늘도 아이들의 문해력을 위해 힘써주셔서 감사합니다!")

    elif menu == "학생 관리":
        st.markdown('<h2><span style="color:#5D4037;">[학생 관리]</span></h2>', unsafe_allow_html=True)
        st.divider()

        students = {uid: data for uid, data in st.session_state.mock_users.items() if data['role'] == '학생'}
        
        for uid, data in students.items():
            scores = data.get('scores', {})
            total = scores.get('total', 0)
            
            with st.container():
                col1, col2 = st.columns([1, 1])
                with col1:
                    st.markdown(f"### 👤 {data['name']}")
                with col2:
                    st.markdown(f"<h3 style='color:#C62828; text-align:right; margin:0;'>🏆 총점: {total}점</h3>", unsafe_allow_html=True)
                
                st.markdown(f"""
                    <div style="margin-top: 10px; margin-bottom: 20px;">
                        <span class="score-box bg-spelling">맞춤법: {scores.get('spelling', 0)}</span>
                        <span class="score-box bg-literacy">문해력: {scores.get('literacy', 0)}</span>
                        <span class="score-box bg-writing">글쓰기: {scores.get('writing', 0)}</span>
                        <span class="score-box bg-jiphyeon">집현전: {scores.get('jiphyeon', 0)}</span>
                    </div>
                """, unsafe_allow_html=True)

                st.markdown("**⭐ AI 학습 능력 분석**")
                
                ai_col1, ai_col2 = st.columns([1, 4])
                with ai_col1:
                    if st.button("🤖 AI 분석하기", key=f"ai_btn_{uid}"):
                        with st.spinner(f"{data['name']} 학생 데이터를 분석 중입니다..."):
                            time.sleep(1.5)
                            dummy_ai_result = f"👩‍🏫 {data['name']} 학생은 맞춤법과 집현전 독서에서 뛰어난 성취를 보이고 있어요! 훌륭하게 성장 중입니다."
                            st.session_state.mock_users[uid]['ai_report'] = dummy_ai_result
                            st.rerun()

                with ai_col2:
                    report_text = data.get('ai_report', "버튼을 눌러 현재 학습 데이터를 분석해보세요.")
                    if report_text == "버튼을 눌러 현재 학습 데이터를 분석해보세요.":
                        st.write(report_text)
                    else:
                        st.info(report_text)
            
            st.divider()

    # -----------------------------------------------------------------
    # 맞춤법 및 받아쓰기 관리 메뉴 (에러 원천 차단: 자동 모델 검색기 적용!)
    # -----------------------------------------------------------------
    elif menu == "맞춤법 및 받아쓰기 관리":
        st.markdown('<h2><span style="color:#5D4037;">[맞춤법 및 받아쓰기 관리]</span></h2>', unsafe_allow_html=True)
        st.divider()

        # 1. 최초 선택 화면
        if st.session_state.spelling_subpage == "menu":
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("<div style='text-align:center; padding:30px; background:#F5F5F5; border-radius:20px;'>", unsafe_allow_html=True)
                st.markdown("<h1 style='font-size:50px;'>🤖</h1>", unsafe_allow_html=True)
                st.markdown("<h3>AI 자동 출제</h3>", unsafe_allow_html=True)
                ai_grade = st.selectbox("학년 수준", [f"{i}학년" for i in range(1, 7)], index=2, key="ai_grade_select")
                if st.button("AI 출제 시작", use_container_width=True):
                    st.session_state.ai_grade = ai_grade
                    st.session_state.spelling_subpage = "ai_loading"
                    st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)
            
            with col2:
                st.markdown("<div style='text-align:center; padding:30px; background:#F5F5F5; border-radius:20px;'>", unsafe_allow_html=True)
                st.markdown("<h1 style='font-size:50px;'>✍️</h1>", unsafe_allow_html=True)
                st.markdown("<h3>교사 직접 출제</h3>", unsafe_allow_html=True)
                st.write("<br><br>", unsafe_allow_html=True)
                if st.button("직접 출제하기", use_container_width=True):
                    st.session_state.spelling_problems = [{"audio": "", "answer": ""} for _ in range(10)]
                    st.session_state.spelling_subpage = "manual"
                    st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)

        # 2. AI 문제 생성 로딩 (404 에러를 막기 위한 완벽한 자동 검색 로직)
        elif st.session_state.spelling_subpage == "ai_loading":
            with st.spinner(f"구글 Gemini AI가 사용 가능한 서버를 찾아 문제를 생성 중입니다... (최대 10초 소요)"):
                try:
                    # 💡 [핵심 해결 로직] 구글 서버에 직접 "지금 사용 가능한 텍스트 모델 이름이 뭐야?"라고 물어보고 잡아옵니다.
                    available_model_name = "models/gemini-pro" # 최후의 수단 기본값
                    for m in genai.list_models():
                        if 'generateContent' in m.supported_generation_methods:
                            available_model_name = m.name
                            # 최신/최고 성능 모델을 우선적으로 선택
                            if "flash" in m.name or "pro" in m.name:
                                break
                    
                    st.toast(f"자동 감지된 AI 모델: {available_model_name}") # 잘 연결되었는지 우측 하단에 잠깐 띄워줌
                    
                    # 자동 감지된 이름으로 모델 실행!
                    model = genai.GenerativeModel(available_model_name)
                    
                    prompt = f"초등학교 {st.session_state.ai_grade} 수준 국어 받아쓰기 문제 10개를 생성해. 반드시 자연스러운 한국어(표준어)로 작성해. 결과는 다른 말은 절대 하지 말고 오직 아래 JSON 구조로만 답해.\n{{\"problems\": [{{\"audio\": \"문제 문장\", \"answer\": \"정답 단어 또는 문장\"}}]}}"
                    
                    response = model.generate_content(prompt)
                    
                    # AI가 불필요한 마크다운을 붙였을 경우 순수 JSON만 안전하게 추출
                    content = response.text.replace("```json", "").replace("```", "").strip()
                    start_idx = content.find('{')
                    end_idx = content.rfind('}') + 1
                    if start_idx != -1 and end_idx != 0:
                        content = content[start_idx:end_idx]
                        
                    data = json.loads(content)
                    st.session_state.spelling_problems = data.get('problems', [])
                    st.session_state.spelling_subpage = "ai_edit"
                    st.rerun()
                            
                except json.JSONDecodeError:
                    st.error("AI가 올바른 데이터를 보내주지 않았습니다. 다시 생성해주세요.")
                    if st.button("메뉴로 돌아가기", key="err_btn_1"): 
                        st.session_state.spelling_subpage = "menu"
                        st.rerun()
                except Exception as e:
                    st.error(f"알 수 없는 오류 발생 (오류 상세: {e})")
                    if st.button("메뉴로 돌아가기", key="err_btn_2"): 
                        st.session_state.spelling_subpage = "menu"
                        st.rerun()

        # 3. 문제 확인 및 편집 화면
        elif st.session_state.spelling_subpage in ["ai_edit", "manual"]:
            st.markdown(f"### {'📝 AI 생성 문제 확인 및 수정' if st.session_state.spelling_subpage == 'ai_edit' else '✍️ [교사 직접 출제]'}")
            if st.button("⬅️ 뒤로가기", key="btn_back_edit"):
                st.session_state.spelling_subpage = "menu"
                st.rerun()
            
            st.divider()
            
            audio_to_play = None
            to_delete = None

            for i, prob in enumerate(st.session_state.spelling_problems):
                c1, c2, c3, c4, c5 = st.columns([1, 4, 3, 1, 1])
                with c1: 
                    st.write(f"**{i+1}번**")
                with c2: 
                    audio_val = st.text_input(f"문제 문장 (소리) {i}", value=prob.get("audio", ""), key=f"audio_input_{i}", label_visibility="collapsed")
                    st.session_state.spelling_problems[i]["audio"] = audio_val
                with c3: 
                    answer_val = st.text_input(f"정답 {i}", value=prob.get("answer", ""), key=f"answer_input_{i}", label_visibility="collapsed")
                    st.session_state.spelling_problems[i]["answer"] = answer_val
                with c4: 
                    if st.button("🔊 듣기", key=f"listen_{i}"):
                        audio_to_play = st.session_state.spelling_problems[i]["audio"]
                with c5:
                    if st.button("❌ 삭제", key=f"del_{i}"):
                        to_delete = i

            if audio_to_play:
                st.info("👇 아래 재생 버튼을 누르면 소리가 나옵니다.")
                play_voice_st(audio_to_play)

            if to_delete is not None:
                st.session_state.spelling_problems.pop(to_delete)
                st.rerun()
                
            if st.button("➕ 문제 추가", key="btn_add_prob"):
                st.session_state.spelling_problems.append({"audio": "", "answer": ""})
                st.rerun()
                
            st.divider()
            
            action_col1, action_col2, action_col3 = st.columns([1, 1, 1])
            with action_col1:
                if st.session_state.spelling_subpage == "ai_edit":
                    if st.button("🔄 다시 생성", use_container_width=True, key="btn_regen"):
                        st.session_state.spelling_subpage = "ai_loading"
                        st.rerun()
            with action_col2:
                txt_content = "\n".join([f"{i+1}. 문장: {p['audio']} / 정답: {p['answer']}" for i, p in enumerate(st.session_state.spelling_problems)])
                st.download_button(label="💾 PC에 저장(TXT)", data=txt_content, file_name="dictation_result.txt", mime="text/plain", use_container_width=True, key="btn_download")
            with action_col3:
                if st.button("✅ 학생들에게 배포하기", type="primary", use_container_width=True, key="btn_deploy"):
                    test_data = [p for p in st.session_state.spelling_problems if p["audio"] and p["answer"]]
                    if test_data:
                        try:
                            u_info = st.session_state.user_info
                            path = f"spelling_tests/{u_info['school']}/{u_info['grade']}/{u_info['class']}"
                            
                            t_prefix = st.session_state.ai_grade if st.session_state.spelling_subpage == "ai_edit" else u_info['grade']
                            t_suffix = "(AI)" if st.session_state.spelling_subpage == "ai_edit" else ""
                            
                            db.reference(path).set({
                                "title": f"{t_prefix} {u_info['class']} 받아쓰기 {t_suffix}".strip(),
                                "problems": test_data,
                                "created_at": str(time.time())
                            })
                            st.success("✅ Firebase에 문제 배포가 완료되었습니다!")
                        except Exception as e:
                            st.error(f"저장 에러: {e}")
                    else:
                        st.warning("저장할 문제가 없습니다. 빈칸을 채워주세요.")
                        
    elif menu == "로그아웃":
        st.session_state.page = "login"
        st.rerun()

    else:
        st.warning(f"'{menu}' 메뉴는 현재 Streamlit으로 마이그레이션 중입니다! 🚧")

def render_student_dashboard():
    """학생 대시보드 임시 화면"""
    st.success(f"👦 {st.session_state.user_info['name']} 학생 환영합니다!")
    if st.button("로그아웃", key="btn_logout_student"):
        st.session_state.page = "login"
        st.rerun()

# ==========================================
# 3. 메인 라우터 (페이지 전환 제어)
# ==========================================
if st.session_state.page == "login":
    render_login_page()
elif st.session_state.page == "teacher":
    render_teacher_dashboard()
elif st.session_state.page == "student":
    render_student_dashboard()
