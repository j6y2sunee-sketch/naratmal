import streamlit as st
import time
import base64

# 1. 페이지 설정 (기본적으로 넓게 설정)
st.set_page_config(page_title="나랏말싸미", layout="wide")

# Session State 초기화
if 'page' not in st.session_state:
    st.session_state.page = "login"

if 'user_info' not in st.session_state:
    st.session_state.user_info = {"name": "", "role": ""}

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

# ---------------------------------------------------------
# 화면 1: 로그인 화면 
# ---------------------------------------------------------
def render_login_page():
    # 배경 이미지 변환
    try:
        with open("bg.png", "rb") as f:
            data = f.read()
            bin_str = base64.b64encode(data).decode()
    except FileNotFoundError:
        bin_str = ""

    # 로그인 전용 CSS
    st.markdown(
        f"""
        <style>
        .stApp {{
            background: url("data:image/png;base64,{bin_str}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}
        header {{ visibility: hidden; }}
        footer {{ visibility: hidden; }}
        
        .block-container {{
            background-color: rgba(255, 255, 255, 0.95) !important;
            padding: 40px !important;
            border-radius: 20px !important;
            max-width: 420px !important;
            margin-top: 10vh !important;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2) !important;
        }}
        .title-main {{
            font-size: 50px !important;
            font-weight: bold !important;
            color: #5D4037 !important;
            text-align: center;
            margin-bottom: 0px;
            line-height: 1.2;
        }}
        .title-sub {{
            font-size: 30px !important;
            font-weight: bold !important;
            color: #5D4037 !important;
            text-align: center;
            margin-top: 0px;
            margin-bottom: 20px;
        }}
        div.stButton {{
            display: flex;
            justify-content: center;
        }}
        .stButton>button {{
            width: 350px !important;
            height: 50px !important;
            background-color: #8D6E63 !important;
            color: white !important;
            border-radius: 8px !important;
            font-size: 18px !important;
            font-weight: bold !important;
            border: none !important;
            margin-top: 20px !important;
        }}
        .stButton>button:hover {{
            background-color: #5D4037 !important;
        }}
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
            st.session_state.user_info = {"name": name, "role": role}
            if role == "교사":
                st.session_state.page = "teacher"
            else:
                st.session_state.page = "student"
            st.rerun()

# ---------------------------------------------------------
# 화면 2: 교사 대시보드 화면
# ---------------------------------------------------------
def render_teacher_dashboard():
    # 대시보드 전용 CSS (2단 구성에 맞게 카드 및 글꼴 크기 조정)
    st.markdown("""
        <style>
        .stApp {
            background: #F8F9FA !important;
        }
        .block-container {
            max-width: 1200px !important; /* 조금 더 넓게 */
            background-color: transparent !important;
            padding: 3rem 2rem !important;
            box-shadow: none !important;
            margin-top: 0 !important;
        }
        .student-card {
            background-color: #FFFFFF;
            border-radius: 15px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.05);
            border: 1px solid #EFEFEF;
            height: 100%;
        }
        .card-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 2px solid #F5F5F5;
            padding-bottom: 10px;
            margin-bottom: 15px;
        }
        .score-box {
            display: inline-block;
            padding: 6px 12px;
            border-radius: 15px;
            margin-right: 8px;
            margin-bottom: 8px;
            font-weight: bold;
            font-size: 13px;
            color: #333;
        }
        .bg-spelling { background-color: #FDEEF4; }
        .bg-literacy { background-color: #EBF4FA; }
        .bg-writing { background-color: #F0F9ED; }
        .bg-jiphyeon { background-color: #FFF9E5; }
        .ai-box {
            margin-top: 15px;
            padding: 15px;
            background-color: #FAFAFA;
            border-radius: 12px;
            border-left: 5px solid #8D6E63;
            font-size: 14px;
        }
        </style>
    """, unsafe_allow_html=True)

    with st.sidebar:
        st.markdown("### 👨‍🏫 교사 메뉴")
        menu = st.radio(
            "이동할 메뉴를 선택하세요",
            ["홈", "학생 관리", "맞춤법 및 받아쓰기 관리", "문해력 관리", "글쓰기 관리", "로그아웃"],
            index=1 
        )

    if menu == "홈":
        st.markdown('<h2>나랏말싸미 <span style="color:#8D6E63;">교사 대시보드</span>입니다.</h2>', unsafe_allow_html=True)
        st.info("👈 왼쪽 메뉴를 선택하여 학생들의 학습을 관리해주세요.")
        st.success("오늘도 아이들의 문해력을 위해 힘써주셔서 감사합니다!")

    # --- 수정한 부분: 학생 관리 2단(그리드) 레이아웃 적용 ---
    elif menu == "학생 관리":
        st.markdown('<h2><span style="color:#5D4037;">[학생 관리]</span></h2>', unsafe_allow_html=True)
        st.divider()

        # 학생 데이터만 필터링
        students = {uid: data for uid, data in st.session_state.mock_users.items() if data['role'] == '학생'}
        
        # 2열 컬럼 생성
        cols = st.columns(2)
        
        # enumerate를 통해 인덱스와 함께 반복
        for index, (uid, data) in enumerate(students.items()):
            # 짝수 인덱스는 왼쪽(col[0]), 홀수 인덱스는 오른쪽(col[1])에 배치
            col = cols[index % 2]
            
            with col:
                scores = data.get('scores', {})
                total = scores.get('total', 0)
                sp = scores.get('spelling', 0)
                li = scores.get('literacy', 0)
                wr = scores.get('writing', 0)
                zi = scores.get('jiphyeon', 0)
                ai_report = data.get('ai_report', "")

                with st.container():
                    st.markdown('<div class="student-card">', unsafe_allow_html=True)
                    
                    # 이름 및 총점
                    st.markdown(f"""
                        <div class="card-header">
                            <h4 style="margin: 0;">👤 {data['name']}</h4>
                            <h4 style="margin: 0; color: #C62828;">🏆 총점: {total}점</h4>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    # 세부 점수 뱃지 (스팬 태그 사용)
                    st.markdown(f"""
                        <div style="margin-bottom: 15px;">
                            <span class="score-box bg-spelling">맞춤법: {sp}</span>
                            <span class="score-box bg-literacy">문해력: {li}</span>
                            <span class="score-box bg-writing">글쓰기: {wr}</span>
                            <span class="score-box bg-jiphyeon">집현전: {zi}</span>
                        </div>
                    """, unsafe_allow_html=True)

                    # AI 분석 영역 (세로로 깔끔하게 배치)
                    st.markdown('<div class="ai-box">', unsafe_allow_html=True)
                    st.markdown("**⭐ AI 학습 능력 분석**")
                    
                    if st.button("🤖 AI 분석하기", key=f"ai_btn_{uid}"):
                        with st.spinner(f"{data['name']} 학생의 데이터를 분석 중입니다..."):
                            time.sleep(1.5) 
                            dummy_ai_result = f"👩‍🏫 {data['name']} 학생은 맞춤법({sp}점)과 집현전 독서({zi}점)에서 아주 뛰어난 성취를 보이고 있어요! 다만 글쓰기({wr}점) 점수를 보완하기 위해 짧은 일기 쓰기부터 차근차근 지도해 주시면 더욱 완벽해질 거예요. 훌륭하게 성장 중입니다!"
                            st.session_state.mock_users[uid]['ai_report'] = dummy_ai_result
                            st.rerun()

                    # 분석 결과 텍스트 출력
                    st.write(ai_report)
                    
                    st.markdown('</div>', unsafe_allow_html=True) # ai-box 닫기
                    st.markdown('</div>', unsafe_allow_html=True) # student-card 닫기

    elif menu == "로그아웃":
        st.session_state.page = "login"
        st.rerun()

    else:
        st.warning(f"'{menu}' 화면은 현재 공사 중입니다! 🚧")

# ---------------------------------------------------------
# 화면 3: 학생 대시보드 화면
# ---------------------------------------------------------
def render_student_dashboard():
    st.success(f"👦 {st.session_state.user_info['name']} 학생 대시보드 화면입니다.")
    if st.button("처음으로 돌아가기"):
        st.session_state.page = "login"
        st.rerun()

# ---------------------------------------------------------
# 메인 라우터
# ---------------------------------------------------------
if st.session_state.page == "login":
    render_login_page()
elif st.session_state.page == "teacher":
    render_teacher_dashboard()
elif st.session_state.page == "student":
    render_student_dashboard()
