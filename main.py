import streamlit as st
import base64

# 1. 페이지 설정
st.set_page_config(page_title="나랏말싸미", layout="centered")

# 2. UI 디자인 (버튼 중앙 정렬 추가)
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
        /* 전체 화면 배경 */
        .stApp {{
            background: url("data:image/png;base64,{bin_str}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}
        
        header {{ visibility: hidden; }}
        footer {{ visibility: hidden; }}

        /* 하얀색 카드 컨테이너 (Flet width=420 대응) */
        .block-container {{
            background-color: rgba(255, 255, 255, 0.95) !important;
            padding: 40px !important;
            border-radius: 20px !important;
            max-width: 420px !important;
            margin-top: 10vh !important;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2) !important;
        }}

        /* 제목 스타일 */
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

        /* 핵심! 버튼을 가운데로 보내는 설정 */
        div.stButton {{
            display: flex;
            justify-content: center; /* 가로 방향 중앙 정렬 */
            margin-top: 20px;
        }}

        /* 입장하기 버튼 스타일 (Flet width=300 대응) */
        .stButton>button {{
            width: 300px !important; /* 선생님 코드의 width=300 적용 */
            height: 55px !important;
            background-color: #8D6E63 !important;
            color: white !important;
            border-radius: 12px !important;
            font-size: 20px !important;
            font-weight: bold !important;
            border: none !important;
            transition: 0.3s;
        }}
        .stButton>button:hover {{
            background-color: #5D4037 !important;
            transform: scale(1.02);
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

set_flet_design()

# 3. 화면 구성
if 'page' not in st.session_state:
    st.session_state.page = "login"

if st.session_state.page == "login":
    st.markdown('<p class="title-main">나랏말싸미</p>', unsafe_allow_html=True)
    st.markdown('<p class="title-sub">:꿈틀이의 문해력 키우기</p>', unsafe_allow_html=True)
    
    school = st.text_input("🏠 학교명")
    
    col1, col2 = st.columns(2)
    with col1:
        grade = st.selectbox("📅 학년", ["1", "2", "3", "4", "5", "6"])
    with col2:
        classroom = st.text_input("🏫 반")
        
    name = st.text_input("👤 이름")
    pw = st.text_input("🔒 비밀번호", type="password")
    role = st.radio("🏷️ 역할", ["학생", "교사"], horizontal=True)
    
    # 버튼 출력 (CSS 설정 덕분에 자동으로 가운데 정렬됩니다)
    if st.button("입장하기"):
        if not school or not name:
            st.error("학교명과 이름을 모두 입력해주세요.")
        else:
            st.session_state.user_info = {"name": name, "role": role}
            st.session_state.page = "teacher" if role == "교사" else "student"
            st.rerun()

# --- 화면 전환 테스트용 ---
elif st.session_state.page in ["teacher", "student"]:
    st.success(f"🏯 {st.session_state.user_info['name']} {st.session_state.user_info['role']}님 환영합니다!")
    if st.button("처음으로"):
        st.session_state.page = "login"
        st.rerun()
