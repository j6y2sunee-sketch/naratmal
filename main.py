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

# --- 안전한 딕셔너리 변환 함수 ---
def safe_dict(data):
    return data if isinstance(data, dict) else {}

# --- AI 답변 정제 함수 (에러 방지용 안전장치) ---
def parse_ai_json(response_text):
    text = response_text.strip()
    # 마크다운 코드 블록(```json 등) 제거
    if text.startswith("```"):
        lines = text.split('\n')
        if len(lines) > 2:
            text = '\n'.join(lines[1:-1])
    # 중괄호 {} 사이의 순수 JSON 텍스트만 추출
    start_idx = text.find('{')
    end_idx = text.rfind('}') + 1
    if start_idx != -1 and end_idx != 0:
        text = text[start_idx:end_idx]
    return json.loads(text)


# ==========================================
# 1. 페이지 및 기본 설정
# ==========================================
st.set_page_config(page_title="나랏말싸미", layout="wide")

# 세션 상태 초기화
if 'page' not in st.session_state: st.session_state.page = "login"
if 'user_info' not in st.session_state: st.session_state.user_info = {"name": "", "role": "", "school": "", "grade": "", "class": ""}

# 맞춤법 세션
if 'spelling_subpage' not in st.session_state: st.session_state.spelling_subpage = "menu"
if 'spelling_problems' not in st.session_state: st.session_state.spelling_problems = []
if 'ai_grade' not in st.session_state: st.session_state.ai_grade = "3학년"

# 문해력 세션
if 'lit_subpage' not in st.session_state: st.session_state.lit_subpage = "menu"
if 'lit_vocab' not in st.session_state: st.session_state.lit_vocab = [{"word": "", "mean": ""}]
if 'lit_passage' not in st.session_state: st.session_state.lit_passage = ""
if 'lit_questions' not in st.session_state: st.session_state.lit_questions = [{"q": "", "a": ""}]
if 'lit_grade' not in st.session_state: st.session_state.lit_grade = "3학년"

# 문집 세션
if "board_mode" not in st.session_state: st.session_state.board_mode = "menu"
if "anthology_mode" not in st.session_state: st.session_state.anthology_mode = "menu"
if "filter_type" not in st.session_state: st.session_state.filter_type = ""
if "filter_value" not in st.session_state: st.session_state.filter_value = ""

# 💡 [집현전 세션 추가]
if "jh_mode" not in st.session_state: st.session_state.jh_mode = "list"
if "jh_book_id" not in st.session_state: st.session_state.jh_book_id = ""
if "jh_book_data" not in st.session_state: st.session_state.jh_book_data = {}
if "jh_edit_review_id" not in st.session_state: st.session_state.jh_edit_review_id = None

# 가상 데이터베이스
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
            [
                "홈", "학생 관리", "맞춤법 및 받아쓰기 관리", "문해력 관리", 
                "글쓰기 관리", "게시판 관리", "문집 관리", "집현전 관리", "상점 관리", "점수 관리", "로그아웃"
            ],
            index=1 
        )

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
            with st.spinner("구글 Gemini AI가 문제를 생성 중입니다... (API 키가 정상인지 확인합니다)"):
                try:
                    available_model_name = "gemini-1.5-flash"
                    for m in genai.list_models():
                        if 'generateContent' in m.supported_generation_methods:
                            available_model_name = m.name
                            if "flash" in m.name or "pro" in m.name: break
                    
                    model = genai.GenerativeModel(available_model_name)
                    prompt = f"초등학교 {st.session_state.ai_grade} 수준 국어 받아쓰기 문제 10개를 생성해. JSON 구조로만 답해.\n{{\"problems\": [{{\"audio\": \"문제 문장\", \"answer\": \"정답 단어 또는 문장\"}}]}}"
                    response = model.generate_content(prompt)
                    
                    data = parse_ai_json(response.text)
                    st.session_state.spelling_problems = data.get('problems', [])
                    st.session_state.spelling_subpage = "ai_edit"
                    st.rerun()
                except Exception as e:
                    # 403 에러 안내를 명확하게 표시하도록 수정했습니다.
                    if "403" in str(e) or "leaked" in str(e).lower():
                        st.error("❌ API 키 차단 오류: 구글에서 현재 사용 중인 API 키가 외부에 유출된 것으로 판단하여 사용을 차단했습니다. Google AI Studio에서 새로운 API 키를 발급받아 Secrets에 적용해주세요.")
                    else:
                        st.error(f"생성 중 오류가 발생했습니다. 다시 시도해주세요.\n(오류 내용: {e})")
                    
                    if st.button("메뉴로 돌아가기"): st.session_state.spelling_subpage = "menu"; st.rerun()
                    
        elif st.session_state.spelling_subpage in ["ai_edit", "manual"]:
            if st.button("⬅️ 뒤로가기"): st.session_state.spelling_subpage = "menu"; st.rerun()
            st.divider()
            
            h1, h2, h3, h4, h5 = st.columns([0.6, 3.5, 3.5, 1.2, 1.2])
            with h2: st.markdown("##### 📝 문제 문장 (소리)")
            with h3: st.markdown("##### ✅ 정답 (받아쓰기 내용)")
            
            audio_to_play = None
            to_delete = None
            
            if not st.session_state.spelling_problems:
                st.session_state.spelling_problems = [{"audio": "", "answer": ""}]
                
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
                    st.session_state.lit_vocab = [{"word": "", "mean": ""}]
                    st.session_state.lit_passage = ""
                    st.session_state.lit_questions = [{"q": "", "a": ""}]
                    st.session_state.lit_subpage = "manual"
                    st.rerun()
                    
        elif st.session_state.lit_subpage == "ai_loading":
            with st.spinner(f"구글 Gemini AI가 {st.session_state.lit_grade} 수준 문해력 지문과 문제를 생성 중입니다..."):
                try:
                    available_model_name = "gemini-1.5-flash"
                    for m in genai.list_models():
                        if 'generateContent' in m.supported_generation_methods:
                            available_model_name = m.name
                            if "flash" in m.name or "pro" in m.name: break
                    
                    model = genai.GenerativeModel(available_model_name)
                    
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
                    
                    data = parse_ai_json(response.text)
                    
                    st.session_state.lit_vocab = data.get('vocab', [{"word":"", "mean":""}])
                    st.session_state.lit_passage = data.get('passage', "")
                    st.session_state.lit_questions = data.get('questions', [{"q":"", "a":""}])
                    
                    st.session_state.lit_subpage = "manual"  
                    st.rerun()
                except Exception as e:
                    if "403" in str(e) or "leaked" in str(e).lower():
                        st.error("❌ API 키 차단 오류: 구글에서 현재 사용 중인 API 키가 외부에 유출된 것으로 판단하여 사용을 차단했습니다. Google AI Studio에서 새로운 API 키를 발급받아 Secrets에 적용해주세요.")
                    else:
                        st.error(f"AI 생성 중 오류가 발생했습니다. 다시 시도해주세요.\n(오류 내용: {e})")
                    if st.button("뒤로가기"):
                        st.session_state.lit_subpage = "menu"
                        st.rerun()
                        
        elif st.session_state.lit_subpage == "manual":
            if st.button("⬅️ 뒤로가기", key="lit_back"):
                st.session_state.lit_subpage = "menu"
                st.rerun()
            st.markdown("### ✍️ 문해력 지문 및 문제 출제")
            st.divider()
            
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
            st.markdown("#### 2. 지문 등록")
            st.session_state.lit_passage = st.text_area("지문 내용", st.session_state.lit_passage, height=150, label_visibility="collapsed", placeholder="지문을 입력하세요...")
            st.divider()
            
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
            
            if st.button("💾 저장 및 배포", type="primary", use_container_width=True):
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

    elif menu == "글쓰기 관리":
        st.markdown('<h2><span style="color:#5D4037;">[글쓰기 관리]</span></h2>', unsafe_allow_html=True)
        st.markdown("학생들에게 제시할 글쓰기 주제를 배포합니다.")
        st.divider()
        
        tab1, tab2 = st.tabs(["🤖 AI 주제 추천", "✍️ 직접 제시"])
        u = st.session_state.user_info
        db_path = f"writing_tasks/{u['school']}/{u['grade']}/{u['class']}"

        with tab1:
            st.subheader("AI 주제 추천")
            write_grade = st.selectbox("학년 수준", [f"{i}학년" for i in range(1, 7)], index=2, key="write_grade_select")
            
            if st.button("주제 생성 시작", type="primary"):
                with st.spinner("AI가 주제를 고민 중..."):
                    try:
                        available_model_name = "gemini-1.5-flash"
                        for m in genai.list_models():
                            if 'generateContent' in m.supported_generation_methods:
                                available_model_name = m.name
                                if "flash" in m.name or "pro" in m.name: break
                        
                        model = genai.GenerativeModel(available_model_name)
                        prompt = f"초등학교 {write_grade} 수준에 맞는 재미있고 창의적인 글쓰기 주제 1개를 생성해. JSON 구조로만 답해. 형식: {{\"topic\": \"글쓰기 주제\", \"guideline\": \"가이드라인\"}}"
                        response = model.generate_content(prompt)
                        
                        res_data = parse_ai_json(response.text)
                        
                        st.session_state.ai_topic = res_data.get('topic', '')
                        st.session_state.ai_guide = res_data.get('guideline', '')
                    except Exception as ex:
                        if "403" in str(ex) or "leaked" in str(ex).lower():
                            st.error("❌ API 키 차단 오류: 구글에서 현재 사용 중인 API 키가 외부에 유출된 것으로 판단하여 사용을 차단했습니다. Google AI Studio에서 새로운 API 키를 발급받아 Secrets에 적용해주세요.")
                        else:
                            st.error(f"생성 중 오류가 발생했습니다. 다시 시도해주세요.\n(오류 내용: {ex})")

            if "ai_topic" in st.session_state:
                st.divider()
                edited_topic = st.text_area("주제 (수정 가능)", value=st.session_state.ai_topic)
                edited_guide = st.text_area("가이드라인 (수정 가능)", value=st.session_state.ai_guide, height=100)
                
                if st.button("💾 AI 생성 문제 배포하기"):
                    db.reference(db_path).set({"topic": edited_topic, "guideline": edited_guide, "created_at": str(time.time())})
                    st.success("✅ 문제 배포가 완료되었습니다!")
                    del st.session_state.ai_topic

        with tab2:
            st.subheader("직접 제시")
            manual_topic = st.text_area("주제", placeholder="학생들에게 제시할 주제를 입력하세요.", key="man_topic")
            manual_guide = st.text_area("가이드라인", placeholder="글쓰기 가이드라인을 입력하세요.", height=100, key="man_guide")
            
            if st.button("💾 직접 배포하기"):
                if manual_topic:
                    db.reference(db_path).set({"topic": manual_topic, "guideline": manual_guide, "created_at": str(time.time())})
                    st.success("✅ 문제 배포가 완료되었습니다!")
                else:
                    st.warning("주제를 입력해주세요.")

    elif menu == "게시판 관리":
        st.markdown('<h2><span style="color:#5D4037;">[글 공유 게시판 관리]</span></h2>', unsafe_allow_html=True)
        st.divider()
        u = st.session_state.user_info
        path = f"board_posts/{u['school']}/{u['grade']}/{u['class']}"
        all_posts = safe_dict(db.reference(path).get())

        if st.session_state.board_mode == "menu":
            col1, col2 = st.columns(2)
            with col1:
                st.info("📚 **주제별 조회**\n\n그동안 제시된 주제별로 학생들의 글을 모아봅니다.")
                if st.button("주제별로 보기", use_container_width=True):
                    st.session_state.board_mode = "topics"
                    st.rerun()
            with col2:
                st.info("👤 **학생별 조회**\n\n우리 반 학생들 이름별로 작성한 글을 모아봅니다.")
                if st.button("학생별로 보기", use_container_width=True):
                    st.session_state.board_mode = "students"
                    st.rerun()

        elif st.session_state.board_mode in ["topics", "students"]:
            if st.button("⬅️ 뒤로가기"):
                st.session_state.board_mode = "menu"
                st.rerun()
                
            is_topic = st.session_state.board_mode == "topics"
            st.subheader(f"{'주제별' if is_topic else '학생별'} 목록")
            
            items = set()
            for key, data in all_posts.items():
                if isinstance(data, dict):
                    val = data.get('title' if is_topic else 'author')
                    if val: items.add(str(val))
            
            if not items:
                st.write("등록된 데이터가 없습니다.")
            else:
                for item in sorted(list(items)):
                    if st.button(item, use_container_width=True):
                        st.session_state.board_mode = "posts"
                        st.session_state.filter_type = "title" if is_topic else "author"
                        st.session_state.filter_value = item
                        st.rerun()

        elif st.session_state.board_mode == "posts":
            if st.button("⬅️ 목록으로 돌아가기"):
                st.session_state.board_mode = "topics" if st.session_state.filter_type == "title" else "students"
                st.rerun()
                
            st.subheader(f"'{st.session_state.filter_value}' 관련 글")
            st.divider()
            
            filtered_posts = {k: v for k, v in all_posts.items() if str(v.get(st.session_state.filter_type, '')) == st.session_state.filter_value}
            
            if not filtered_posts:
                st.write("해당 조건의 게시글이 없습니다.")
            else:
                for pid, pdata in filtered_posts.items():
                    with st.container(border=True):
                        st.markdown(f"#### 📝 {pdata.get('title', '')} (작성자: {pdata.get('author', '')})")
                        st.write(pdata.get('content', ''))
                        
                        if st.button("🗑️ 게시글 삭제", key=f"del_{pid}", type="primary"):
                            db.reference(f"{path}/{pid}").delete()
                            st.success("삭제 완료")
                            st.rerun()
                        
                        st.markdown("**💬 댓글**")
                        for cid, cdata in pdata.get('comments', {}).items():
                            c_col1, c_col2 = st.columns([8, 2])
                            c_col1.write(f"↳ {cdata.get('author', '익명')}: {cdata.get('text', '')}")
                            if c_col2.button("❌", key=f"cdel_{cid}"):
                                db.reference(f"{path}/{pid}/comments/{cid}").delete()
                                st.rerun()
                                
                        new_comment = st.text_input("댓글 달기", key=f"c_input_{pid}")
                        if st.button("댓글 등록", key=f"c_btn_{pid}"):
                            if new_comment:
                                db.reference(f"{path}/{pid}/comments").push({"author": st.session_state.user_info['name'], "text": new_comment})
                                st.rerun()

    elif menu == "문집 관리":
        st.markdown('<h2><span style="color:#5D4037;">[학급 문집 관리]</span></h2>', unsafe_allow_html=True)
        st.divider()
        u = st.session_state.user_info
        path = f"student_writings/{u['school']}/{u['grade']}/{u['class']}"
        all_students = safe_dict(db.reference(path).get())

        if st.session_state.anthology_mode == "menu":
            col1, col2 = st.columns(2)
            with col1:
                st.info("📚 **주제별 문집**\n\n제시된 글쓰기 주제별로 모아봅니다.")
                if st.button("주제별 문집 조회", use_container_width=True):
                    st.session_state.anthology_mode = "topics"
                    st.rerun()
            with col2:
                st.info("👤 **학생별 문집**\n\n학생 이름별로 모아봅니다.")
                if st.button("학생별 문집 조회", use_container_width=True):
                    st.session_state.anthology_mode = "students"
                    st.rerun()

        elif st.session_state.anthology_mode in ["topics", "students"]:
            if st.button("⬅️ 뒤로가기"):
                st.session_state.anthology_mode = "menu"
                st.rerun()
                
            is_topic = st.session_state.anthology_mode == "topics"
            st.subheader(f"{'주제별' if is_topic else '학생별'} 문집 목록")
            
            items = set()
            if is_topic:
                for s, w_dict in all_students.items():
                    for wid, wd in safe_dict(w_dict).items():
                        if wd.get('topic'): items.add(str(wd['topic']))
            else:
                items = set(all_students.keys())
                
            for item in sorted(list(items)):
                if st.button(item, use_container_width=True, key=f"anth_{item}"):
                    st.session_state.anthology_mode = "posts"
                    st.session_state.filter_type = "topic" if is_topic else "student"
                    st.session_state.filter_value = item
                    st.rerun()

        elif st.session_state.anthology_mode == "posts":
            if st.button("⬅️ 목록으로 돌아가기"):
                st.session_state.anthology_mode = "topics" if st.session_state.filter_type == "topic" else "students"
                st.rerun()
                
            st.subheader(f"'{st.session_state.filter_value}' 문집")
            
            data_to_download = []
            download_text = f"--- {u['grade']}학년 {u['class']}반 '{st.session_state.filter_value}' 문집 ---\n\n"
            
            for student, w_dict in all_students.items():
                for wid, wd in safe_dict(w_dict).items():
                    if (st.session_state.filter_type == "topic" and str(wd.get('topic', '')) == str(st.session_state.filter_value)) or \
                       (st.session_state.filter_type == "student" and str(student) == str(st.session_state.filter_value)):
                        
                        data_to_download.append(wd)
                        download_text += f"[{student}] 주제: {wd.get('topic', '')}\n내용: {wd.get('content', '')}\n\n"
                        
                        with st.container(border=True):
                            col1, col2 = st.columns([9, 1])
                            col1.markdown(f"**📝 {wd.get('topic', '')}** (학생: {student})")
                            if col2.button("❌", key=f"del_anth_{wid}"):
                                db.reference(f"{path}/{student}/{wid}").delete()
                                st.rerun()
                            st.write(wd.get('content', ''))

            if data_to_download:
                st.download_button(
                    label="💾 현재 목록 텍스트(.txt)로 다운로드",
                    data=download_text,
                    file_name=f"{st.session_state.filter_value}_문집.txt",
                    mime="text/plain",
                    type="primary"
                )

    elif menu == "집현전 관리":
        st.markdown('<h2><span style="color:#5D4037;">[집현전 관리]</span></h2>', unsafe_allow_html=True)
        st.divider()
        u = st.session_state.user_info
        path = f"jiphyeonjeon_books/{u['school']}/{u['grade']}/{u['class']}"

        # 1. 도서 목록 (책장) 모드
        if st.session_state.jh_mode == "list":
            head_c1, head_c2 = st.columns([1, 1])
            with head_c1:
                st.markdown("### 📚 집현전 책장")
            with head_c2:
                ai_c1, ai_c2 = st.columns([2, 1])
                jiphyeon_grade = ai_c1.selectbox("추천 학년", [f"{i}학년" for i in range(1, 7)], index=int(u['grade'])-1, label_visibility="collapsed")
                if ai_c2.button("🤖 AI 추천 추가", use_container_width=True):
                    with st.spinner("AI 선생님이 책을 고르고 있습니다..."):
                        try:
                            # Gemini 호출로 변경
                            available_model_name = "gemini-1.5-flash"
                            for m in genai.list_models():
                                if 'generateContent' in m.supported_generation_methods:
                                    available_model_name = m.name
                                    if "flash" in m.name or "pro" in m.name: break
                            model = genai.GenerativeModel(available_model_name)
                            prompt = f"초등학교 {jiphyeon_grade} 추천 도서 3권. JSON 구조로만 답해. 형식: {{ 'books': [ {{'title': '..', 'author': '..', 'desc': '..'}} ] }}"
                            response = model.generate_content(prompt)
                            
                            res_data = parse_ai_json(response.text)
                            for b in res_data.get('books', []):
                                db.reference(path).push({
                                    "title": b.get('title'), "author": b.get('author'), 
                                    "desc": b.get('desc'), "recommender": "AI 선생님"
                                })
                            st.success("AI 추천 도서가 추가되었습니다!")
                            st.rerun()
                        except Exception as ex:
                            st.error(f"생성 에러: {ex}")

            with st.expander("➕ 직접 도서 등록", expanded=False):
                with st.form("manual_book_add"):
                    man_t = st.text_input("제목")
                    man_a = st.text_input("지은이")
                    man_d = st.text_area("소개")
                    if st.form_submit_button("등록하기"):
                        if man_t.strip():
                            db.reference(path).push({"title": man_t.strip(), "author": man_a, "desc": man_d, "recommender": "교사"})
                            st.rerun()

            st.divider()
            
            books = safe_dict(db.reference(path).get())
            if not books:
                st.info("등록된 책이 없습니다. AI 추천 추가나 직접 등록을 이용해보세요.")
            else:
                book_items = []
                max_avg = 0
                for bid, bdata in books.items():
                    if not isinstance(bdata, dict): continue
                    revs = safe_dict(bdata.get('reviews', {}))
                    avg = sum(int(r.get('rating', 0)) for r in revs.values()) / len(revs) if revs else 0
                    if avg > max_avg: max_avg = avg
                    book_items.append((bid, bdata, revs, avg))

                # Streamlit의 columns를 이용한 그리드 뷰 구현 (4열 배치)
                cols = st.columns(4)
                for idx, (bid, bdata, revs, avg) in enumerate(book_items):
                    col = cols[idx % 4]
                    with col:
                        with st.container(border=True):
                            best_badge = "👑 [BEST]\n" if avg > 0 and avg == max_avg else ""
                            st.markdown(f"""
                            <div style="background-color:#8D6E63; padding:20px; border-radius:10px; text-align:center; height:180px; display:flex; flex-direction:column; justify-content:center;">
                                <div style="color:white; font-weight:bold; font-size:16px; margin-bottom:10px;">{best_badge}{bdata.get('title', '')}</div>
                                <div style="color:#E0E0E0; font-size:12px;">{bdata.get('author', '')}</div>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            st.markdown(f"<div style='text-align:center; margin-top:10px;'>⭐ {avg:.1f} ({len(revs)}명 읽음)<br><span style='font-size:12px; color:blue;'>추천인: {bdata.get('recommender', '교사')}</span></div>", unsafe_allow_html=True)
                            
                            if st.button("🔍 상세보기", key=f"v_{bid}", use_container_width=True):
                                st.session_state.jh_mode = "detail"
                                st.session_state.jh_book_id = bid
                                st.session_state.jh_book_data = bdata
                                st.rerun()
                            
                            c1, c2 = st.columns(2)
                            if c1.button("✏️ 수정", key=f"e_{bid}", use_container_width=True):
                                st.session_state.jh_mode = "edit"
                                st.session_state.jh_book_id = bid
                                st.session_state.jh_book_data = bdata
                                st.rerun()
                            if c2.button("❌ 삭제", key=f"d_{bid}", use_container_width=True):
                                db.reference(f"{path}/{bid}").delete()
                                st.rerun()

        # 2. 도서 정보 수정 모드
        elif st.session_state.jh_mode == "edit":
            if st.button("⬅️ 뒤로가기"):
                st.session_state.jh_mode = "list"
                st.rerun()
            st.markdown("### ✏️ 도서 정보 수정")
            st.divider()
            
            bdata = st.session_state.jh_book_data
            bid = st.session_state.jh_book_id
            
            with st.form("edit_book_form"):
                new_t = st.text_input("도서 제목", value=bdata.get('title', ''))
                new_a = st.text_input("지은이", value=bdata.get('author', ''))
                new_d = st.text_area("독서 포인트", value=bdata.get('desc', ''), height=150)
                
                if st.form_submit_button("💾 수정 완료"):
                    db.reference(f"{path}/{bid}").update({
                        "title": new_t, "author": new_a, "desc": new_d
                    })
                    st.success("수정되었습니다.")
                    st.session_state.jh_mode = "list"
                    time.sleep(0.5)
                    st.rerun()

        # 3. 도서 상세 보기 및 리뷰 모드
        elif st.session_state.jh_mode == "detail":
            if st.button("⬅️ 목록으로 돌아가기"):
                st.session_state.jh_mode = "list"
                st.rerun()
                
            bid = st.session_state.jh_book_id
            bdata = safe_dict(db.reference(f"{path}/{bid}").get())
            r_path = f"{path}/{bid}/reviews"
            
            st.markdown(f"## 📖 {bdata.get('title', '')}")
            st.info(f"**지은이:** {bdata.get('author', '')}\n\n**독서 포인트:** {bdata.get('desc', '')}")
            st.divider()
            
            st.markdown("### 💬 친구들의 감상평")
            revs = safe_dict(db.reference(r_path).get())
            
            if not revs:
                st.write("아직 등록된 감상평이 없습니다.")
            else:
                for rid, r in revs.items():
                    if not isinstance(r, dict): continue
                    is_mine = (str(r.get('author', '')) == "교사" or str(r.get('author', '')) == u['name'])
                    
                    with st.container(border=True):
                        col1, col2 = st.columns([8, 2])
                        col1.markdown(f"**👤 {r.get('author', '익명')}** (⭐ {r.get('rating', 5)}점)")
                        
                        # 내 글이거나 교사면 수정/삭제 가능
                        if st.session_state.jh_edit_review_id == rid:
                            # 수정 모드 뷰
                            with st.form(f"edit_rev_{rid}"):
                                edit_r_text = st.text_area("감상평 수정", value=r.get('text', ''))
                                c_save, c_cancel = st.columns(2)
                                if c_save.form_submit_button("저장"):
                                    # 리뷰 수정 저장
                                    db.reference(f"{r_path}/{rid}").update({'text': edit_r_text})
                                    # 문집 연동 수정
                                    a_path = f"student_writings/{u['school']}/{u['grade']}/{u['class']}/{r.get('author')}"
                                    a_posts = safe_dict(db.reference(a_path).get())
                                    for apid, adata in a_posts.items():
                                        if isinstance(adata, dict) and str(adata.get('topic', '')) == f"[독서록] {bdata.get('title','')}" and str(adata.get('content', '')) == r.get('text', ''):
                                            db.reference(f"{a_path}/{apid}").update({'content': edit_r_text})
                                    st.session_state.jh_edit_review_id = None
                                    st.rerun()
                                if c_cancel.form_submit_button("취소"):
                                    st.session_state.jh_edit_review_id = None
                                    st.rerun()
                        else:
                            # 일반 뷰
                            col1.write(r.get('text', ''))
                            if is_mine or u['role'] == "교사":
                                c_e, c_d = col2.columns(2)
                                if c_e.button("✏️", key=f"re_{rid}"):
                                    st.session_state.jh_edit_review_id = rid
                                    st.rerun()
                                if c_d.button("❌", key=f"rd_{rid}"):
                                    # 리뷰 삭제
                                    db.reference(f"{r_path}/{rid}").delete()
                                    # 문집 연동 삭제
                                    a_path = f"student_writings/{u['school']}/{u['grade']}/{u['class']}/{r.get('author')}"
                                    a_posts = safe_dict(db.reference(a_path).get())
                                    for apid, adata in a_posts.items():
                                        if isinstance(adata, dict) and str(adata.get('topic', '')) == f"[독서록] {bdata.get('title','')}" and str(adata.get('content', '')) == r.get('text', ''):
                                            db.reference(f"{a_path}/{apid}").delete()
                                    st.rerun()
            
            st.divider()
            st.markdown("### 📝 감상평 남기기")
            with st.form("add_review_form"):
                rating_val = st.selectbox("별점", [5, 4, 3, 2, 1], index=0)
                review_text = st.text_area("느낀 점을 적어주세요! (최소 5자 이상)", height=100)
                
                if st.form_submit_button("등록 및 점수 받기"):
                    if len(review_text.strip()) < 5:
                        st.warning("감상평을 5자 이상 작성해주세요.")
                    else:
                        author_name = u['name'] if u['name'] else "교사"
                        # 집현전 리뷰 등록
                        db.reference(r_path).push({
                            "author": author_name, "rating": rating_val, 
                            "text": review_text.strip(), "created_at": str(time.time())
                        })
                        # 문집 (student_writings) 연동 등록
                        db.reference(f"student_writings/{u['school']}/{u['grade']}/{u['class']}/{author_name}").push({
                            "topic": f"[독서록] {bdata.get('title','')}", 
                            "content": review_text.strip(), 
                            "date": str(time.time())
                        })
                        st.success("감상평이 등록되었습니다!")
                        time.sleep(0.5)
                        st.rerun()

    elif menu == "상점 관리":
        st.markdown('<h2><span style="color:#5D4037;">[상점 관리]</span></h2>', unsafe_allow_html=True)
        st.divider()
        u = st.session_state.user_info
        shop_path = f"shop_items/{u['school']}/{u['grade']}/{u['class']}"
        req_path = f"shop_requests/{u['school']}/{u['grade']}/{u['class']}"

        st.markdown("### 🛒 상점 물품 등록")
        with st.form("add_shop_item"):
            c1, c2, c3 = st.columns([2, 1, 1])
            new_item_name = c1.text_input("물품명", placeholder="예: 간식 교환권, 자리 바꾸기 권")
            new_item_price = c2.number_input("가격 (P)", min_value=0, step=10)
            submitted = c3.form_submit_button("➕ 등록")
            if submitted and new_item_name:
                db.reference(shop_path).push({"name": new_item_name.strip(), "price": int(new_item_price)})
                st.success(f"'{new_item_name}' 물품이 등록되었습니다!")
                time.sleep(0.5)
                st.rerun()

        st.divider()
        st.markdown("### 🎁 등록된 물품 목록")
        items = safe_dict(db.reference(shop_path).get())
        if items:
            for iid, idata in items.items():
                if isinstance(idata, dict):
                    col1, col2, col3 = st.columns([4, 2, 2])
                    col1.markdown(f"**🎁 {idata.get('name')}**")
                    col2.markdown(f"**💰 {idata.get('price')}P**")
                    if col3.button("❌ 삭제", key=f"del_item_{iid}"):
                        db.reference(f"{shop_path}/{iid}").delete()
                        st.rerun()
        else:
            st.info("등록된 물품이 없습니다. 상점에 물품을 등록해주세요.")

        st.divider()
        st.markdown("### 🙋‍♂️ 학생 사용 신청 내역")
        reqs = safe_dict(db.reference(req_path).get())
        pending_reqs = {k: v for k, v in reqs.items() if isinstance(v, dict) and not v.get('approved')}
        
        if pending_reqs:
            for rid, rdata in pending_reqs.items():
                with st.container(border=True):
                    rc1, rc2 = st.columns([8, 2])
                    rc1.markdown(f"🙋‍♂️ **{rdata.get('student_name')}** 학생이 **'{rdata.get('item_name')}'** 사용을 요청했습니다.")
                    if rc2.button("✅ 승인", key=f"app_{rid}"):
                        sid = rdata.get('student_id')
                        iname = rdata.get('item_name')
                        if sid and iname:
                            inv_ref = db.reference(f"users/{sid}/inventory/{iname}")
                            curr = inv_ref.get() or 0
                            if int(curr) > 0:
                                inv_ref.set(int(curr) - 1)
                        db.reference(f"{req_path}/{rid}").update({"approved": True})
                        st.success("승인 완료!")
                        time.sleep(0.5)
                        st.rerun()
        else:
            st.write("대기 중인 사용 요청이 없습니다.")

    # 💡 [새로 추가된 점수 관리 코드]
    elif menu == "점수 관리":
        st.markdown('<h2><span style="color:#5D4037;">[점수 관리]</span></h2>', unsafe_allow_html=True)
        st.divider()
        u = st.session_state.user_info
        settings_path = f"score_settings/{u['school']}/{u['grade']}/{u['class']}"

        # 파이어베이스 배열/딕셔너리 안전 변환 로직
        def safe_to_dict_local(data):
            if isinstance(data, list):
                return {str(i): v for i, v in enumerate(data) if v is not None}
            return data if isinstance(data, dict) else {}

        raw_data = db.reference(settings_path).get()
        data = safe_to_dict_local(raw_data)
        
        existing_scores = safe_to_dict_local(data.get("scores"))
        existing_levels = safe_to_dict_local(data.get("levels"))

        default_scores = {"spelling": 10, "spelling_bonus": 50, "literacy": 20, "literacy_bonus": 100, "writing": 50, "share": 5, "comment": 2, "jiphyeon": 100}
        default_levels = {"2": 100, "3": 300, "4": 600, "5": 1000, "6": 1500, "7": 2100}

        # 상태 초기화
        sc_state = {k: existing_scores.get(k, default_scores[k]) for k in default_scores}
        lv_state = {str(k): existing_levels.get(str(k), default_levels[str(k)]) for k in default_levels}

        with st.form("score_settings_form"):
            st.markdown("### 🎯 활동별 획득 점수 설정")
            sc1, sc2, sc3, sc4 = st.columns(4)
            sc_state["spelling"] = sc1.number_input("맞춤법 (기본)", value=int(sc_state["spelling"]), step=1)
            sc_state["spelling_bonus"] = sc2.number_input("맞춤법 (전체정답 보너스)", value=int(sc_state["spelling_bonus"]), step=1)
            sc_state["literacy"] = sc3.number_input("문해력 (기본)", value=int(sc_state["literacy"]), step=1)
            sc_state["literacy_bonus"] = sc4.number_input("문해력 (전체정답 보너스)", value=int(sc_state["literacy_bonus"]), step=1)
            
            sc5, sc6, sc7, sc8 = st.columns(4)
            sc_state["writing"] = sc5.number_input("글쓰기", value=int(sc_state["writing"]), step=1)
            sc_state["share"] = sc6.number_input("공유", value=int(sc_state["share"]), step=1)
            sc_state["comment"] = sc7.number_input("댓글", value=int(sc_state["comment"]), step=1)
            sc_state["jiphyeon"] = sc8.number_input("집현전", value=int(sc_state["jiphyeon"]), step=1)
            
            st.divider()
            st.markdown("### 📈 레벨업 요구 점수 설정")
            lc1, lc2, lc3 = st.columns(3)
            lv_state["2"] = lc1.number_input("Lv.2 요구 점수", value=int(lv_state["2"]), step=10)
            lv_state["3"] = lc2.number_input("Lv.3 요구 점수", value=int(lv_state["3"]), step=10)
            lv_state["4"] = lc3.number_input("Lv.4 요구 점수", value=int(lv_state["4"]), step=10)
            
            lc4, lc5, lc6 = st.columns(3)
            lv_state["5"] = lc4.number_input("Lv.5 요구 점수", value=int(lv_state["5"]), step=10)
            lv_state["6"] = lc5.number_input("Lv.6 요구 점수", value=int(lv_state["6"]), step=10)
            lv_state["7"] = lc6.number_input("Lv.7 요구 점수", value=int(lv_state["7"]), step=10)

            st.write("")
            if st.form_submit_button("💾 설정 저장하기", type="primary"):
                try:
                    db.reference(settings_path).set({
                        "scores": sc_state,
                        "levels": lv_state
                    })
                    st.success("설정이 성공적으로 저장되었습니다!")
                except Exception as ex:
                    st.error(f"저장 실패: {str(ex)}")

    elif menu == "로그아웃":


def render_student_dashboard():
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
