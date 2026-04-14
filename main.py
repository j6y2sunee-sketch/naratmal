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
        /* 전체 배경 설정 */
        .stApp {{
            background: url("data:image/png;base64,{bin_str}");
            background-size: cover;
            background-position: center;
        }}
        
        /* 제목 영역: 박스 없이 배경 위에 직접 배치 */
        .header-container {{
            text-align: center;
            padding-top: 50px;
            padding-bottom: 30px;
        }}
        
        /* 메인 제목: 크기를 더 키우고 흰색 테두리와 그림자로 가독성 극대화 */
        .main-title {{
            color: #3E2723; /* 진한 밤색 */
            font-size: 80px !important;
            font-weight: 900;
            margin-bottom: 0px;
            text-shadow: 3px 3px 0px #FFFFFF, 5px 5px 15px rgba(0,0,0,0.3);
            line-height: 1.1;
        }}
        
        /* 부제목 */
        .sub-title {{
            color: #5D4037;
            font-size: 35px !important;
            font-weight: bold;
            margin-top: 10px;
            text-shadow: 2px 2px 0px #FFFFFF;
        }}
        
        /* 입력창 영역만 하얀색 반투명 박스로 감싸기 */
        .login-input-box {{
            background-color: rgba(255, 255, 255, 0.9);
            padding: 40px;
            border-radius: 20px;
            border: 2px solid #5D4037;
            box-shadow: 0 10px 25px rgba(0,0,0,0.2);
            margin-top: 20px;
        }}
        
        /* 라벨 및 버튼 스타일 강화 */
        .stTextInput label, .stSelectbox label, .stRadio label {{
            font-size: 20px !important;
            color: #3E2723 !important;
            font-weight: bold !important;
        }}
        
        .stButton>button {{
            width: 100%;
            background-color: #5D4037 !important;
            color: white !important;
            border-radius: 12px;
            height: 60px;
            font-size: 24px !important;
            font-weight: bold;
            border: none;
            margin-top: 20px;
        }}
        
        /* 상단 메뉴바 제거 */
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
    # 1) 제목 영역 (박스 밖 상단)
    st.markdown('<div class="header-container">', unsafe_allow_html=True)
    st.markdown('<p class="main-title">나랏말싸미</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">: 꿈틀이의 문해력 키우기</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 2) 입력 영역 (반투명 박스)
    st.markdown('<div class="login-input-box">', unsafe_allow_html=True)
    
    school = st.text_input("🏠 학교명")
    
    col1, col2 = st.columns(2)
    with col1:
        grade = st.selectbox("📅 학년", [str(i) for i in range(1, 7)])
    with col2:
        classroom = st.text_input("🏫 반")
        
    name = st.text_input("👤 이름")
    pw = st.text_input("🔒 비밀번호", type="password")
    
    role = st.radio("🏷️ 역할 선택", ["학생", "교사"], horizontal=True)
    
    if st.button("집현전 입장하기"):
        if school and name and pw:
            st.session_state.user_info = {"name": name, "role": role}
            st.session_state.page = "main"
            st.rerun()
        else:
            st.error("모든 정보를 입력해 주세요!")
            
    st.markdown('</div>', unsafe_allow_html=True)

# 4. 메인 화면
elif st.session_state.page == "main":
    st.success(f"{st.session_state.user_info['name']}님, 환영합니다!")
    if st.button("로그아웃"):
        st.session_state.page = "login"
        st.rerun()
