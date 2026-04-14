import streamlit as st
import time
import requests
import streamlit as st
import base64

# 1. 페이지 설정
st.set_page_config(page_title="나랏말싸미", layout="centered")

# 2. Flet 코드를 그대로 번역한 UI 디자인
def set_flet_design():
    try:
        with open("bg.png", "rb") as f:
            data = f.read()
            bin_str = base64.b64encode(data).decode()
    except FileNotFoundError:
        bin_str = ""

    st.markdown(
        f"""
        <style>
        /* bg_img = ft.Image(src="bg.png", fit="cover" ...) 완벽 대응 */
        .stApp {{
            background: url("data:image/png;base64,{bin_str}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}
        
        /* 상하단 기본 여백 지우기 */
        header {{ visibility: hidden; }}
        footer {{ visibility: hidden; }}

        /* login_box = ft.Container(...) 완벽 대응 */
        .block-container {{
            background-color: rgba(255, 255, 255, 0.95) !important; /* bgcolor="#F2FFFFFF" */
            padding: 40px !important;                               /* padding=40 */
            border-radius: 20px !important;                         /* border_radius=20 */
            max-width: 420px !important;                            /* width=420 */
            margin-top: 10vh !important;                            /* 화면 중앙 정렬 */
            box-shadow: 0 4px 15px rgba(0,0,0,0.2) !important;
        }}

        /* ft.Text("나랏말싸미", size=50, weight="bold", color="#5D4037") 대응 */
        .title-main {{
            font-size: 50px !important;
            font-weight: bold !important;
            color: #5D4037 !important;
            text-align: center;
            margin-bottom: 0px;
            line-height: 1.2;
        }}
        
        /* ft.Text(":꿈틀이의 문해력 키우기", size=30...) 대응 */
        .title-sub {{
            font-size: 30px !important;
            font-weight: bold !important;
            color: #5D4037 !important;
            text-align: center;
            margin-top: 0px;
            margin-bottom: 20px;
        }}

        /* --- 수정한 부분: 버튼을 가운데로 정렬 --- */
        div.stButton {{
            display: flex;
            justify-content: center;
        }}

        /* ft.ElevatedButton(..., color="white", bgcolor="#8D6E63", height=50) 대응 */
        .stButton>button {{
            width: 350px !important; /* 너비를 좀 더 넓게 수정 (기존 100% -> 350px) */
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

set_flet_design()

# 3. 로그인 화면 및 화면 전환 로직 (Flet과 동일한 흐름)
if 'page' not in st.session_state:
    st.session_state.page = "login"

if st.session_state.page == "login":
    # 텍스트 출력
    st.markdown('<p class="title-main">나랏말싸미</p>', unsafe_allow_html=True)
    st.markdown('<p class="title-sub">:꿈틀이의 문해력 키우기</p>', unsafe_allow_html=True)
    
    # 입력 필드 (school_field, name_field 등)
    school = st.text_input("학교명")
    
    # ft.Row([grade_field, class_field]) 대응
    col1, col2 = st.columns(2)
    with col1:
        grade = st.selectbox("학년", ["1", "2", "3", "4", "5", "6"])
    with col2:
        classroom = st.text_input("반")
        
    name = st.text_input("이름")
    pw = st.text_input("비밀번호", type="password")
    role = st.radio("역할", ["학생", "교사"], horizontal=True)
    
    # 입장하기 버튼 (enter_app 함수 대응)
    if st.button("입장하기"):
        if not school or not name:
            # page.snack_bar 대응
            st.error("학교명과 이름을 모두 입력해주세요.")
        else:
            st.session_state.user_info = {"name": name, "role": role}
            if role == "교사":
                st.session_state.page = "teacher"
            else:
                st.session_state.page = "student"
            st.rerun()

# --- 화면 전환: 교사 대시보드 (show_teacher_dashboard 대응) ---
elif st.session_state.page == "teacher":
    st.success("👨‍🏫 교사 대시보드 화면입니다.")
    if st.button("처음으로 돌아가기"):
        st.session_state.page = "login"
        st.rerun()

# --- 화면 전환: 학생 대시보드 (show_student_dashboard 대응) ---
elif st.session_state.page == "student":
    st.success(f"👦 {st.session_state.user_info['name']} 학생 대시보드 화면입니다.")
    if st.button("처음으로 돌아가기"):
        st.session_state.page = "login"
        st.rerun()

def show_teacher_dashboard():
    # --- 가상 데이터 (Firebase db.reference('users').get() 대체용) ---
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
            }
        }

    # --- CSS 스타일 적용 (Flet의 아기자기한 컨테이너 색상 완벽 구현) ---
    st.markdown("""
        <style>
        .student-card { background-color: #F5F5F5; border-radius: 15px; padding: 20px; margin-bottom: 20px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); }
        .score-box { display: inline-block; padding: 8px 12px; border-radius: 10px; margin-right: 10px; font-weight: bold; font-size: 14px; color: #333; }
        .bg-spelling { background-color: #FDEEF4; }
        .bg-literacy { background-color: #EBF4FA; }
        .bg-writing { background-color: #F0F9ED; }
        .bg-jiphyeon { background-color: #FFF9E5; }
        .ai-box { margin-top: 15px; padding: 15px; background-color: white; border-radius: 10px; border-left: 5px solid #8D6E63; }
        </style>
    """, unsafe_allow_html=True)

    # --- 사이드바 메뉴 구성 ---
    with st.sidebar:
        st.markdown("### 👨‍🏫 교사 메뉴")
        menu = st.radio(
            "이동할 메뉴를 선택하세요",
            ["홈", "학생 관리", "맞춤법 및 받아쓰기 관리", "문해력 관리", "글쓰기 관리", "로그아웃"]
        )

    # --- 1. 홈 (첫 화면) ---
    if menu == "홈":
        st.markdown('<h2>나랏말싸미 <span style="color:#8D6E63;">교사 대시보드</span>입니다.</h2>', unsafe_allow_html=True)
        st.info("👈 왼쪽 메뉴를 선택하여 학생들의 학습을 관리해주세요.")
        
        # 교사 정보 요약 (선택 사항)
        st.success("오늘도 아이들의 문해력을 위해 힘써주셔서 감사합니다!")

    # --- 2. 학생 관리 화면 ---
    elif menu == "학생 관리":
        st.markdown('<h2><span style="color:#5D4037;">[학생 관리]</span></h2>', unsafe_allow_html=True)
        st.divider()

        # 검색된 학생 수에 따라 반복해서 카드 생성
        for uid, data in st.session_state.mock_users.items():
            if data['role'] == '학생':
                scores = data.get('scores', {})
                total = scores.get('total', 0)
                sp = scores.get('spelling', 0)
                li = scores.get('literacy', 0)
                wr = scores.get('writing', 0)
                zi = scores.get('jiphyeon', 0)
                ai_report = data.get('ai_report', "")

                # 카드 컨테이너 시작
                with st.container():
                    st.markdown('<div class="student-card">', unsafe_allow_html=True)
                    
                    # 이름 및 총점
                    col1, col2 = st.columns([1, 4])
                    with col1:
                        st.markdown(f"### 👤 {data['name']}")
                    with col2:
                        st.markdown(f"<h3 style='color:#C62828; margin:0;'>🏆 총점: {total}점</h3>", unsafe_allow_html=True)
                    
                    # 세부 점수 뱃지 (HTML/CSS)
                    st.markdown(f"""
                        <div style="margin-top: 10px;">
                            <div class="score-box bg-spelling">맞춤법: {sp}</div>
                            <div class="score-box bg-literacy">문해력: {li}</div>
                            <div class="score-box bg-writing">글쓰기: {wr}</div>
                            <div class="score-box bg-jiphyeon">집현전: {zi}</div>
                        </div>
                    """, unsafe_allow_html=True)

                    # AI 분석 영역
                    st.markdown('<div class="ai-box">', unsafe_allow_html=True)
                    
                    ai_col1, ai_col2 = st.columns([1, 4])
                    with ai_col1:
                        st.markdown("**⭐ AI 학습 능력 분석**")
                        # Streamlit에서는 버튼의 고유 key가 필수입니다
                        if st.button("🤖 AI 분석하기", key=f"ai_btn_{uid}"):
                            with st.spinner(f"{data['name']} 학생의 데이터를 분석 중입니다..."):
                                # 실제로는 여기에 Groq API 호출 코드가 들어갑니다.
                                # 현재는 시뮬레이션을 위해 2초 대기 후 결과 텍스트를 업데이트합니다.
                                time.sleep(2) 
                                
                                # (원래 코드의 Groq API 로직이 들어갈 자리)
                                dummy_ai_result = f"👩‍🏫 {data['name']} 학생은 맞춤법({sp}점)과 집현전 독서({zi}점)에서 아주 뛰어난 성취를 보이고 있어요! 다만 글쓰기({wr}점) 점수를 보완하기 위해 짧은 일기 쓰기부터 차근차근 지도해 주시면 더욱 완벽해질 거예요. 훌륭하게 성장 중입니다!"
                                
                                # 세션 스테이트(가상 DB) 업데이트
                                st.session_state.mock_users[uid]['ai_report'] = dummy_ai_result
                                st.rerun() # 화면 새로고침

                    with ai_col2:
                        st.write(ai_report)
                    
                    st.markdown('</div>', unsafe_allow_html=True) # ai-box 끝
                    st.markdown('</div>', unsafe_allow_html=True) # student-card 끝

    # --- 3. 로그아웃 처리 ---
    elif menu == "로그아웃":
        st.session_state.page = "login"
        st.rerun()

    # --- 나머지 메뉴들 (임시) ---
    else:
        st.warning(f"'{menu}' 화면은 현재 공사 중입니다! 🚧")


# 단독 실행 테스트용 로직
if __name__ == "__main__":
    if 'page' not in st.session_state:
        st.session_state.page = "teacher"
    
    if st.session_state.page == "teacher":
        show_teacher_dashboard()
