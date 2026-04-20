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
GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=GEMINI_API_KEY)

if not firebase_admin._apps:
    try:
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

# 세션 상태(Session State) 초기화
if 'page' not in st.session_state: st.session_state.page = "login"
if 'user_info' not in st.session_state: st.session_state.user_info = {"name": "", "role": "", "school": "", "grade": "", "class": ""}

# (맞춤법 관련 세션)
if 'spelling_subpage' not in st.session_state: st.session_state.spelling_subpage = "menu"
if 'spelling_problems' not in st.session_state: st.session_state.spelling_problems = []
if 'ai_grade' not in st.session_state: st.session_state.ai_grade = "3학년"

# (문해력 관련 세션 - 새롭게 추가된 부분)
if 'lit_subpage' not in st.session_state: st.session_state.lit_subpage = "menu"
if 'lit_vocab' not in st.session_state: st.session_state.lit_vocab = [{"word": "", "mean": ""}]
if 'lit_passage' not in st.session_state: st.session_state.lit_passage = ""
if 'lit_questions' not in st.session_state: st.session_state.lit_questions = [{"q": "", "a": ""}]
if 'lit_grade' not in st.session_state: st.session_state.lit_grade = "3학년"

# 파이어베이스를 대신할 가상 데이터베이스 (테스트용)
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
    except FileNotFoundError:
        bin_str = ""

    st.markdown(
        f"""
        <style>
        .stApp {{ background: url("data:image/png;base64,{bin_str}"); background-size: cover; background-position: center; background-attachment: fixed; }}
        header, footer {{ visibility: hidden; }}
        .block-container {{ background-color: rgba(255, 255, 255, 0.95) !important; padding: 40px !important; border-radius: 20px !important; max-width: 420px !important; margin-top: 10vh !important; box-shadow: 0 4px 15px rgba(0,0,0,0.2) !important; }}
        .title-main {{ font-size: 50px !important; font-weight: bold !important; color: #5D4037 !important; text-align: center; margin-bottom: 0px; line-height: 1.2; }}
        .title-sub {{ font-size: 30px !important; font-weight: bold !important; color: #5D4037 !important; text-align: center; margin-top: 0px; margin-bottom: 20px; }}
        div.stButton {{ display: flex; justify-content: center; }}
        .stButton>button {{ width: 350px !important; height: 50px !important; background-color: #8D6E63 !important; color: white !important; border-radius: 8px !important; font-size: 18px !important; font-weight: bold !important; border: none !important; margin-top: 20px !important; }}
        </style>
        """,
        unsafe_allow_html=True
    )

    st.markdown('<p class="title-main">나랏말싸미</p><p class="title-sub">:꿈틀이의 문해력 키우기</p>', unsafe_allow_html=True)
    
    school = st.text_input("학교명")
    col1, col2 = st.columns(2)
    with col1: grade = st.selectbox("학년", ["1", "2", "3", "4", "5", "6"])
    with col2: classroom = st.text_input("반")
        
    name = st.text_input("이름")
    pw = st.text_input("비밀번호", type="password")
    role = st.radio("역할", ["학생", "교사"], horizontal=True)
    
    if st.button("입장하기"):
        if not school or not name:
            st.error("학교명과 이름을 모두 입력해주세요.")
        else:
            st.session_state.user_info = {"name": name, "role": role, "school": school, "grade": grade, "class": classroom}
            st.session_state.page = "teacher" if role == "교사" else "student"
            st.rerun()

def render_teacher_dashboard():
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
            index=1 
        )

    # -----------------------------------------------------------------
    # 홈 & 학생 관리 메뉴
    # -----------------------------------------------------------------
    if menu == "홈":
        st.markdown('<h2>나랏말싸미 <span style="color:#8D6E63;">교사 대시보드</span>입니다.</h2>', unsafe_allow_html=True)
        st.info("👈 왼쪽 메뉴를 선택하여 학생들의 학습을 관리해주세요.")

    elif menu == "학생 관리":
        st.markdown('<h2><span style="color:#5D4037;">[학생 관리]</span></h2>', unsafe_allow_html=True)
        st.divider()
        students = {uid: data for uid, data in st.session_state.mock_users.items() if data['role'] == '학생'}
        
        for uid, data in students.items():
            scores = data.get('scores', {})
            with st.container():
                c1, c2 = st.columns([1, 1])
                with c1: st.markdown(f"### 👤 {data['name']}")
                with c2: st.markdown(f"<h3 style='color:#C62828; text-align:right; margin:0;'>🏆 총점: {scores.get('total',0)}점</h3>", unsafe_allow_html=True)
                
                st.markdown(f"""
                    <div style="margin-top: 10px; margin-bottom: 20px;">
                        <span class="score-box bg-spelling">맞춤법: {scores.get('spelling', 0)}</span>
                        <span class="score-box bg-literacy">문해력: {scores.get('literacy', 0)}</span>
                        <span class="score-box bg-writing">글쓰기: {scores.get('writing', 0)}</span>
                        <span class="score-box bg-jiphyeon">집현전: {scores.get('jiphyeon', 0)}</span>
                    </div>
                """, unsafe_allow_html=True)

                st.markdown("**⭐ AI 학습 능력 분석**")
                ac1, ac2 = st.columns([1, 4])
                with ac1:
                    if st.button("🤖 AI 분석하기", key=f"ai_btn_{uid}"):
                        with st.spinner(f"{data['name']} 학생 데이터를 분석 중..."):
                            time.sleep(1.5)
                            st.session_state.mock_users[uid]['ai_report'] = f"👩‍🏫 {data['name']} 학생은 맞춤법과 집현전 독서에서 뛰어난 성취를 보이고 있어요!"
                            st.rerun()
                with ac2:
                    st.info(data.get('ai_report', "버튼을 눌러 분석해보세요."))
            st.divider()

    # -----------------------------------------------------------------
    # 맞춤법 및 받아쓰기 관리 메뉴
    # -----------------------------------------------------------------
    elif menu == "맞춤법 및 받아쓰기 관리":
        st.markdown('<h2><span style="color:#5D4037;">[맞춤법 및 받아쓰기 관리]</span></h2>', unsafe_allow_html=True)
        st.divider()

        if st.session_state.spelling_subpage == "menu":
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("<div style='text-align:center; padding:30px; background:#F5F5F5; border-radius:20px;'><h1>🤖</h1><h3>AI 자동 출제</h3></div>", unsafe_allow_html=True)
                ai_grade = st.selectbox("학년 수준", [f"{i}학년" for i in range(1, 7)], index=2, key="sp_ai_grade")
                if st.button("AI 출제 시작", use_container_width=True, key="sp_ai_btn"):
                    st.session_state.ai_grade = ai_grade
                    st.session_state.spelling_subpage = "ai_loading"
                    st.rerun()
            with c2:
                st.markdown("<div style='text-align:center; padding:30px; background:#F5F5F5; border-radius:20px;'><h1>✍️</h1><h3>교사 직접 출제</h3><br><br></div>", unsafe_allow_html=True)
                if st.button("직접 출제하기", use_container_width=True, key="sp_man_btn"):
                    st.session_state.spelling_problems = [{"audio": "", "answer": ""} for _ in range(10)]
                    st.session_state.spelling_subpage = "manual"
                    st.rerun()

        elif st.session_state.spelling_subpage == "ai_loading":
            with st.spinner(f"구글 Gemini AI가 문제를 생성 중입니다..."):
                try:
                    available_model_name = "models/gemini-pro"
                    for m in genai.list_models():
                        if 'generateContent' in m.supported_generation_methods:
                            available_model_name = m.name
                            if "flash" in m.name or "pro" in m.name: break
                    
                    model = genai.GenerativeModel(available_model_name)
                    prompt = f"초등학교 {st.session_state.ai_grade} 수준 국어 받아쓰기 문제 10개를 생성해. JSON 구조로만 답해.\n{{\"problems\": [{{\"audio\": \"문제 문장\", \"answer\": \"정답 단어 또는 문장\"}}]}}"
                    response = model.generate_content(prompt)
                    
                    content = response.text.replace("```json", "").replace("```", "").strip()
                    s_idx = content.find('{')
                    e_idx = content.rfind('}') + 1
                    if s_idx != -1 and e_idx != 0: content = content[s_idx:e_idx]
                        
                    data = json.loads(content)
                    st.session_state.spelling_problems = data.get('problems', [])
                    st.session_state.spelling_subpage = "ai_edit"
                    st.rerun()
                except Exception as e:
                    st.error("생성 오류 발생")
                    if st.button("메뉴로 돌아가기"): st.session_state.spelling_subpage = "menu"; st.rerun()

        elif st.session_state.spelling_subpage in ["ai_edit", "manual"]:
            if st.button("⬅️ 뒤로가기"): st.session_state.spelling_subpage = "menu"; st.rerun()
            st.divider()
            
            h1, h2, h3, h4, h5 = st.columns([0.6, 3.5, 3.5, 1.2, 1.2])
            with h2: st.markdown("##### 📝 문제 문장 (소리)")
            with h3: st.markdown("##### ✅ 정답 (받아쓰기 내용)")
            
            audio_to_play = None
            to_delete = None

            for i, prob in enumerate(st.session_state.spelling_problems):
                c1, c2, c3, c4, c5 = st.columns([0.6, 3.5, 3.5, 1.2, 1.2])
                with c1: st.write(f"<div style='padding-top:7px;'><b>{i+1}번</b></div>", unsafe_allow_html=True)
                with c2: 
                    audio_val = st.text_input(f"문제 문장 (소리) {i}", value=prob.get("audio", ""), key=f"audio_input_{i}", label_visibility="collapsed")
                    st.session_state.spelling_problems[i]["audio"] = audio_val
                with c3: 
                    current_ans = prob.get("answer", "")
                    if (st.session_state.spelling_subpage == "ai_edit" and "synced" not in prob) or current_ans == "":
                        current_ans = audio_val
                        prob["synced"] = True
                    answer_val = st.text_input(f"정답 {i}", value=current_ans, key=f"answer_input_{i}", label_visibility="collapsed")
                    st.session_state.spelling_problems[i]["answer"] = answer_val
                with c4: 
                    if st.button("🔊 듣기", key=f"listen_{i}", use_container_width=True): audio_to_play = st.session_state.spelling_problems[i]["audio"]
                with c5:
                    if st.button("❌ 삭제", key=f"del_{i}", use_container_width=True): to_delete = i

            if audio_to_play: play_voice_st(audio_to_play)
            if to_delete is not None:
                st.session_state.spelling_problems.pop(to_delete)
                st.rerun()
                
            if st.button("➕ 문제 추가"):
                st.session_state.spelling_problems.append({"audio": "", "answer": ""})
                st.rerun()
            st.divider()
            
            ac1, ac2, ac3 = st.columns([1, 1, 1])
            with ac1:
                if st.button("🔄 다시 생성", use_container_width=True) and st.session_state.spelling_subpage == "ai_edit":
                    st.session_state.spelling_subpage = "ai_loading"; st.rerun()
            with ac3:
                if st.button("✅ 학생들에게 배포하기", type="primary", use_container_width=True):
                    test_data = [p for p in st.session_state.spelling_problems if p["audio"] and p["answer"]]
                    if test_data:
                        try:
                            u = st.session_state.user_info
                            db.reference(f"spelling_tests/{u['school']}/{u['grade']}/{u['class']}").set({
                                "title": f"{u['grade']}학년 받아쓰기", "problems": test_data, "created_at": str(time.time())
                            })
                            st.success("✅ 문제 배포 완료!")
                        except Exception as e: st.error(f"저장 에러: {e}")

    # -----------------------------------------------------------------
    # 문해력 관리 메뉴 (NEW!)
    # -----------------------------------------------------------------
    elif menu == "문해력 관리":
        st.markdown('<h2><span style="color:#5D4037;">[문해력 관리]</span></h2>', unsafe_allow_html=True)
        st.divider()

        if st.session_state.lit_subpage == "menu":
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("<div style='text-align:center; padding:30px; background:#F5F5F5; border-radius:20px;'><h1>🤖</h1><h3>AI 통합 출제</h3></div>", unsafe_allow_html=True)
                lit_grade = st.selectbox("학년 수준", [f"{i}학년" for i in range(1, 7)], index=2, key="lit_grade_select")
                if st.button("시작하기", key="btn_lit_ai", use_container_width=True):
                    st.session_state.lit_grade = lit_grade
                    st.session_state.lit_subpage = "ai_loading"
                    st.rerun()
            
            with col2:
                st.markdown("<div style='text-align:center; padding:30px; background:#F5F5F5; border-radius:20px;'><h1>✍️</h1><h3>교사 직접 출제</h3><br><br></div>", unsafe_allow_html=True)
                if st.button("직접하기", key="btn_lit_manual", use_container_width=True):
                    # 수동 입력 전 세션 초기화
                    st.session_state.lit_vocab = [{"word": "", "mean": ""}]
                    st.session_state.lit_passage = ""
                    st.session_state.lit_questions = [{"q": "", "a": ""}]
                    st.session_state.lit_subpage = "manual"
                    st.rerun()

        # AI 문제 생성 대기 화면
        elif st.session_state.lit_subpage == "ai_loading":
            with st.spinner(f"구글 Gemini AI가 {st.session_state.lit_grade} 수준 문해력 지문과 문제를 생성 중입니다..."):
                try:
                    # 안정적인 모델 검색 로직
                    available_model_name = "models/gemini-pro"
                    for m in genai.list_models():
                        if 'generateContent' in m.supported_generation_methods:
                            available_model_name = m.name
                            if "flash" in m.name or "pro" in m.name: break
                    
                    model = genai.GenerativeModel(available_model_name)
                    
                    # 문해력 전용 프롬프트
                    prompt = f"""
                    초등학교 {st.session_state.lit_grade} 수준의 재미있는 국어 독해 지문과 관련 어휘, 이해도 확인 문제를 작성해줘. 
                    결과는 다른 설명 없이 오직 아래 JSON 구조로만 답해.
                    {{
                        "vocab": [{{"word": "단어1", "mean": "뜻1"}}, {{"word": "단어2", "mean": "뜻2"}}],
                        "passage": "지문 내용 (3~5문장 정도)",
                        "questions": [{{"q": "문제1", "a": "정답1"}}, {{"q": "문제2", "a": "정답2"}}]
                    }}
                    """
                    response = model.generate_content(prompt)
                    
                    # JSON 파싱 안전 장치
                    content = response.text.replace("```json", "").replace("```", "").strip()
                    start_idx = content.find('{')
                    end_idx = content.rfind('}') + 1
                    if start_idx != -1 and end_idx != 0:
                        content = content[start_idx:end_idx]
                    
                    data = json.loads(content)
                    
                    # 추출한 데이터를 세션에 저장
                    st.session_state.lit_vocab = data.get('vocab', [{"word":"", "mean":""}])
                    st.session_state.lit_passage = data.get('passage', "")
                    st.session_state.lit_questions = data.get('questions', [{"q":"", "a":""}])
                    
                    # 편집 화면으로 이동
                    st.session_state.lit_subpage = "manual"  
                    st.rerun()
                except Exception as e:
                    st.error(f"AI 생성 오류가 발생했습니다: {e}")
                    if st.button("뒤로가기"):
                        st.session_state.lit_subpage = "menu"
                        st.rerun()

        # 편집 및 직접 입력 화면
        elif st.session_state.lit_subpage == "manual":
            if st.button("⬅️ 뒤로가기", key="lit_back"):
                st.session_state.lit_subpage = "menu"
                st.rerun()
            st.markdown("### ✍️ 문해력 지문 및 문제 출제")
            st.divider()

            # --- 1. 어휘 등록 영역 ---
            st.markdown("#### 1. 어휘 등록")
            v_to_delete = None
            for i, v in enumerate(st.session_state.lit_vocab):
                vc1, vc2, vc3, vc4 = st.columns([0.5, 2, 4, 1])
                with vc1: st.write(f"<div style='padding-top:7px;'><b>{i+1}번</b></div>", unsafe_allow_html=True)
                with vc2: st.session_state.lit_vocab[i]["word"] = st.text_input("단어", v.get("word", ""), key=f"vw_{i}", label_visibility="collapsed", placeholder="단어")
                with vc3: st.session_state.lit_vocab[i]["mean"] = st.text_input("뜻", v.get("mean", ""), key=f"vm_{i}", label_visibility="collapsed", placeholder="뜻")
                with vc4:
                    if st.button("❌ 삭제", key=f"vdel_{i}", use_container_width=True): v_to_delete = i
            
            if v_to_delete is not None:
                st.session_state.lit_vocab.pop(v_to_delete)
                st.rerun()
            if st.button("➕ 어휘 추가"):
                st.session_state.lit_vocab.append({"word":"", "mean":""})
                st.rerun()
            
            st.divider()

            # --- 2. 지문 등록 영역 ---
            st.markdown("#### 2. 지문 등록")
            st.session_state.lit_passage = st.text_area("지문 내용", st.session_state.lit_passage, height=150, label_visibility="collapsed", placeholder="지문을 입력하세요...")

            st.divider()

            # --- 3. 문제 등록 영역 ---
            st.markdown("#### 3. 문제 등록")
            q_to_delete = None
            for i, q in enumerate(st.session_state.lit_questions):
                qc1, qc2, qc3, qc4 = st.columns([0.5, 4, 2, 1])
                with qc1: st.write(f"<div style='padding-top:7px;'><b>{i+1}번</b></div>", unsafe_allow_html=True)
                with qc2: st.session_state.lit_questions[i]["q"] = st.text_input("질문", q.get("q", ""), key=f"qq_{i}", label_visibility="collapsed", placeholder="질문")
                with qc3: st.session_state.lit_questions[i]["a"] = st.text_input("정답", q.get("a", ""), key=f"qa_{i}", label_visibility="collapsed", placeholder="정답")
                with qc4:
                    if st.button("❌ 삭제", key=f"qdel_{i}", use_container_width=True): q_to_delete = i
            
            if q_to_delete is not None:
                st.session_state.lit_questions.pop(q_to_delete)
                st.rerun()
            if st.button("➕ 문제 추가"):
                st.session_state.lit_questions.append({"q":"", "a":""})
                st.rerun()

            st.divider()

            # --- 4. 저장 및 배포 ---
            if st.button("💾 저장 및 배포", type="primary", use_container_width=True):
                # 빈칸 제외 필터링
                v_data = [v for v in st.session_state.lit_vocab if v["word"].strip()]
                q_data = [q for q in st.session_state.lit_questions if q["q"].strip()]
                
                if not st.session_state.lit_passage.strip() or not q_data:
                    st.warning("지문 내용과 문제를 최소 1개 이상 입력해주세요.")
                else:
                    try:
                        u = st.session_state.user_info
                        path = f"literacy_tests/{u['school']}/{u['grade']}/{u['class']}"
                        db.reference(path).set({
                            "vocab": v_data,
                            "passage": st.session_state.lit_passage,
                            "questions": q_data,
                            "created_at": str(time.time())
                        })
                        st.success("✅ 문제 배포가 완료되었습니다!")
                    except Exception as e:
                        st.error(f"저장 에러: {e}")

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
