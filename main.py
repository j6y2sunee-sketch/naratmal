import streamlit as st
import base64

# 1. 페이지 설정
st.set_page_config(page_title="나랏말싸미", layout="centered")

# 2. UI 디자인 설정 (박스 제거, 폰트 확대, 입력칸 높이 조절)
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
        /* 1. 배경 설정 및 불필요한 기본 박스 완전 제거 */
        .stApp {{
            background: url("data:image/png;base64,{bin_str}");
            background-size: cover;
            background-position: center;
        }}
        
        /* Streamlit 기본 박스(상자)를 완전히 투명하게 만듦 */
        [data-testid="stVerticalBlock"] {{
            background-color: transparent !important;
        }}
        [data-testid="stHeader"] {{
            background: rgba(0,0,0,0);
        }}

        /* 2. 프로그램명: 가운데 정렬 및 가독성 강화 */
        .title-area {{
            text-align: center;
            width: 100%;
            margin-top: 20px;
            margin-bottom: 40px;
        }}
        .main-title {{
            font-size: 90px !important; /* 글자 훨씬 크게 */
            font-weight: 900;
            color: #3E2723;
            text-shadow: -3px -3px 0 #fff, 3px -3px 0 #fff, -3px 3px 0 #fff, 3px 3px 0 #fff, 5px 5px 15px rgba(0,0,0,0.4);
            margin-bottom: 0px;
        }}
        .sub-title {{
            font-size: 40px !important;
            font-weight: bold;
            color: #5D4037;
            text-shadow: -2px -2px 0 #fff, 2px -2px 0 #fff, -2px 2px 0 #fff, 2px 2px 0 #fff;
            margin-top: 10px;
        }}

        /* 3. 입력창(Input) 영역 커스터마이징 */
        /* 라벨(학교명, 이름 등) 크기 2배 확대 */
        .stTextInput label, .stSelectbox label, .stRadio label p {{
            font-size: 30px !important; /* 기존보다 2배 이상 */
            color: #3E2723 !important;
            font-weight: bold !important;
            margin-bottom: 10px !important;
            text-shadow: 1px 1px 0px #fff;
        }}

        /* 입력창 높이(높이) 및 내부 글자 크기 대폭 확대 */
        .stTextInput input, .stSelectbox div[data-baseweb="select"] {{
            height: 70px !important; /* 높이 대폭 상향 */
            font-size: 28px !important;
            border-radius: 15px !important;
            border: 3px solid #5D4037 !important;
        }}
        
        /* 라디오 버튼(역할 선택) 글자 크기 */
        div[data-testid="stMarkdownContainer"] p {{
            font-size: 28px !important;
        }}

        /* 4. 입장하기 버튼: 초대형화 */
        .stButton>button {{
            width: 100%;
            background-color: #5D4037 !important;
            color: white !important;
            font-size: 40px !important; /* 버튼 글자 대폭 확대 */
            height: 90px !important; /* 버튼 높이 대폭 확대 */
            border-radius: 20px;
            margin-top: 40px;
            border: 4px solid #fff;
            box-shadow: 0 5px 15px rgba(0,0,0,0.3);
        }}
        
        /* 화면 중앙에 정렬되도록 여백 조정 */
        .main-container {{
            max-width: 800px;
            margin: 0 auto;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

set_design()

# 3. 화면 구성
if 'page' not in st.session_state:
    st.session_state.page = "login"

if st.session_state.page == "login":
    # 1) 프로그램명 (완벽 가운데 정렬)
    st.markdown('<div class="title-area">', unsafe_allow_html=True)
    st.markdown('<p class="main-title">나랏말싸미</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">: 꿈틀이의 문해력 키우기</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 2) 입력 영역 (박스 제거 후 내용만 배치)
    st.write("<div class='main-container'>", unsafe_allow_html=True)
    
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
        if name and pw:
            st.session_state.user_info = {"name": name, "role": role}
            st.session_state.page = "main"
            st.rerun()
            
    st.write("</div>", unsafe_allow_html=True)

elif st.session_state.page == "main":
    st.success(f"{st.session_state.user_info['name']}님, 환영합니다!")
    if st.button("로그아웃"):
        st.session_state.page = "login"
        st.rerun()
