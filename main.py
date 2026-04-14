import streamlit as st
import base64

# 1. 페이지 설정
st.set_page_config(page_title="나랏말싸미", layout="centered")

# 2. UI 디자인 설정 (CSS)
def set_design():
    try:
        with open("bg.png", "rb") as f:
            data = f.read()
            bin_str = base64.b64encode(data).decode()
    except FileNotFoundError:
        bin_str = ""

    st.markdown(
        f"""
        <style>
        /* 전체 배경 */
        .stApp {{
            background: url("data:image/png;base64,{bin_str}");
            background-size: cover;
            background-position: center;
        }}
        
        /* 로그인 박스 설정: 제목이 이 안에 포함됩니다 */
        .login-container {{
            background-color: rgba(255, 255, 255, 0.95);
            padding: 50px;
            border-radius: 30px;
            border: 4px solid #5D4037;
            box-shadow: 0 15px 35px rgba(0,0,0,0.3);
            text-align: center;
            margin-top: 20px;
        }}
        
        /* 메인 제목: 크기를 키우고 진한 색상 적용 */
        .main-title {{
            color: #4E342E;
            font-size: 60px !important;
            font-weight: 900;
            margin-bottom: 0px;
            line-height: 1.2;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
        }}
        
        /* 부제목 */
        .sub-title {{
            color: #5D4037;
            font-size: 28px !important;
            font-weight: bold;
            margin-bottom: 30px;
        }}
        
        /* 입력창 라벨 (학교, 이름 등) 글자 크기 및 색상 */
        .stTextInput label, .stSelectbox label, .stRadio label {{
            font-size: 22px !important;
            color: #3E2723 !important;
            font-weight: bold !important;
        }}
        
        /* 입력창 내부 글자 크기 */
        input {{
            font-size: 20px !important;
        }}
        
        /* 버튼: 더 크고 눈에 띄게 */
        .stButton>button {{
            width: 100%;
            background-color: #5D4037 !important;
            color: #FFFFFF !important;
            border-radius: 15px;
            height: 65px;
            font-size: 26px !important;
            font-weight: bold;
            margin-top: 20px;
            border: none;
            transition: 0.3s;
        }}
        .stButton>button:hover {{
            background-color: #3E2723 !important;
            transform: scale(1.02);
        }}

        /* 하단 여백 제거 */
        #MainMenu, footer {{visibility: hidden;}}
        </style>
        """,
        unsafe_allow_html=True
    )

set_design()

# 3. 화면 구성
if 'page' not in st.session_state:
    st.session_state.page = "login"

if st.session_state.page == "login":
    # 화면 중앙 정렬을 위한 여백
    st.write("<br>", unsafe_allow_html=True)
    
    # 로그인 박스 시작
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    
    # 박스 내부에 제목을 직접 배치하여 흰 박스 밖으로 나가지 않게 함
    st.markdown('<p class="main-title">나랏말싸미</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">: 꿈틀이의 문해력 키우기</p>', unsafe_allow_html=True)
    
    # 입력 필드
    school = st.text_input("🏠 학교명")
    
    col1, col2 = st.columns(2)
    with col1:
        grade = st.selectbox("📅 학년", [str(i) for i in range(1, 7)])
    with col2:
        classroom = st.text_input("🏫 반")
        
    name = st.text_input("👤 이름")
    pw = st.text_input("🔒 비밀번호", type="password")
    
    role = st.radio("🏷️ 역할 선택", ["학생", "교사"], horizontal=True)
    
    # 입장 버튼
    if st.button("입장하기"):
        if school and name and pw:
            st.session_state.user_info = {"name": name, "role": role}
            st.session_state.page = "main"
            st.rerun()
        else:
            st.error("모든 정보를 입력해 주세요!")
            
    st.markdown('</div>', unsafe_allow_html=True)

# 4. 메인 화면 (임시)
elif st.session_state.page == "main":
    st.success(f"{st.session_state.user_info['name']}님, 환영합니다!")
    if st.button("로그아웃"):
        st.session_state.page = "login"
        st.rerun()
