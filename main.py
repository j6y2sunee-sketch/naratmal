import streamlit as st
import base64

# 1. 페이지 설정
st.set_page_config(page_title="나랏말싸미", layout="centered")

# 2. UI 디자인 설정 (박스 제거 및 폰트 강화)
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
        /* 1. 전체 배경 및 기본 박스 투명화 */
        .stApp {{
            background: url("data:image/png;base64,{bin_str}");
            background-size: cover;
            background-position: center;
        }}
        
        /* Streamlit 내부의 모든 기본 박스/배경을 투명하게 강제 고정 */
        [data-testid="stVerticalBlock"], [data-testid="stHeader"], .main {{
            background-color: transparent !important;
        }}

        /* 2. 프로그램명 디자인 (박스 없이 공중에 띄움) */
        .title-container {{
            text-align: center;
            padding: 20px;
            margin-top: -30px; /* 위쪽으로 더 바짝 붙임 */
        }}
        
        .main-title {{
            font-size: 85px !important;
            font-weight: 900;
            color: #3E2723; /* 아주 진한 고동색 */
            text-shadow: 
                -2px -2px 0 #fff,  
                 2px -2px 0 #fff,
                -2px  2px 0 #fff,
                 2px  2px 0 #fff,
                 4px 4px 15px rgba(0,0,0,0.5); /* 글자 테두리 + 그림자 */
            margin-bottom: 0px;
        }}
        
        .sub-title {{
            font-size: 32px !important;
            font-weight: bold;
            color: #5D4037;
            text-shadow: -1px -1px 0 #fff, 1px -1px 0 #fff, -1px 1px 0 #fff, 1px 1px 0 #fff;
            margin-top: 5px;
        }}

        /* 3. 입력창 영역만 세련된 반투명 흰색 박스로 감싸기 */
        .login-input-area {{
            background-color: rgba(255, 255, 255, 0.85); /* 85% 투명도 */
            padding: 35px;
            border-radius: 25px;
            border: 3px solid #8D6E63;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            margin-top: 30px;
        }}

        /* 입력창 라벨/버튼 폰트 키우기 */
        .stTextInput label, .stSelectbox label, .stRadio label {{
            font-size: 20px !important;
            color: #3E2723 !important;
            font-weight: bold !important;
        }}

        .stButton>button {{
            background-color: #5D4037 !important;
            color: white !important;
            font-size: 24px !important;
            height: 60px;
            border-radius: 15px;
            margin-top: 20px;
        }}
        
        /* 상단 메뉴바 숨기기 */
        header {{visibility: hidden;}}
        </style>
        """,
        unsafe_allow_html=True
    )

set_design()

# 3. 화면 구성 시작
if 'page' not in st.session_state:
    st.session_state.page = "login"

if st.session_state.page == "login":
    # 1) 제목 영역 (박스 없이 배경에 직접 출력)
    st.markdown('<div class="title-container">', unsafe_allow_html=True)
    st.markdown('<p class="main-title">나랏말싸미</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">꿈틀이의 문해력 키우기</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 2) 입력 영역 (반투명 카드)
    st.markdown('<div class="login-input-area">', unsafe_allow_html=True)
    
    school = st.text_input("🏠 학교명")
    col1, col2 = st.columns(2)
    with col1:
        grade = st.selectbox("📅 학년", [str(i) for i in range(1, 7)])
    with col2:
        classroom = st.text_input("🏫 반")
    
    name = st.text_input("👤 이름")
    pw = st.text_input("🔒 비밀번호", type="password")
    role = st.radio("🏷️ 역할", ["학생", "교사"], horizontal=True)
    
    if st.button("집현전 입장하기"):
        if name and pw:
            st.session_state.user_info = {"name": name, "role": role}
            st.session_state.page = "main"
            st.rerun()
            
    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.page == "main":
    st.success(f"{st.session_state.user_info['name']}님 반갑습니다!")
    if st.button("로그아웃"):
        st.session_state.page = "login"
        st.rerun()
