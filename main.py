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

        /* ft.ElevatedButton(..., color="white", bgcolor="#8D6E63", height=50) 대응 */
        .stButton>button {{
            width: 100% !important; /* 부모 너비에 맞춤 */
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
