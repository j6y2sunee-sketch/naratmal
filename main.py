import streamlit as st
import base64

# 1. 페이지 설정
st.set_page_config(page_title="나랏말싸미", layout="wide")

# 2. UI 디자인 설정 (CSS 최적화)
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
        @import url('https://fonts.googleapis.com/css2?family=Nanum+Myeongjo:wght@700;800&family=Nanum+Gothic:wght@400;700&display=swap');

        /* 전체 배경 */
        .stApp {{
            background: url("data:image/png;base64,{bin_str}");
            background-size: cover;
            background-position: center;
        }}

        /* Streamlit 기본 요소 투명화 및 여백 제거 */
        [data-testid="stHeader"], [data-testid="stVerticalBlock"] {{
            background: transparent !important;
        }}
        
        /* 중앙 정렬 컨테이너 */
        .main-wrapper {{
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            width: 100%;
            font-family: 'Nanum Gothic', sans-serif;
        }}

        /* 제목 섹션 */
        .title-section {{
            text-align: center;
            margin-top: 30px;
            margin-bottom: 20px;
        }}
        .main-title {{
            font-family: 'Nanum Myeongjo', serif;
            font-size: 100px !important;
            font-weight: 800;
            color: #3E2723;
            text-shadow: 4px 4px 0px #FFFFFF, 8px 8px 20px rgba(0,0,0,0.3);
            margin-bottom: 0px;
        }}
        .sub-title {{
            font-size: 38px !important;
            color: #5D4037;
            font-weight: 700;
            margin-top: 0px;
            text-shadow: 2px 2px 0px #FFFFFF;
        }}

        /* 입력 카드 영역 */
        .input-card {{
            background: rgba(255, 255, 255, 0.9);
            padding: 50px;
            border-radius: 40px;
            border: 5px solid #8D6E63;
            box-shadow: 0 20px 50px rgba(0,0,0,0.4);
            width: 750px;
            margin-top: 20px;
        }}

        /* 입력 항목 라벨 */
        .stTextInput label, .stSelectbox label, .stRadio label p {{
            font-size: 28px !important;
            color: #3E2723 !important;
            font-weight: 800 !important;
            margin-bottom: 12px !important;
        }}

        /* 입력창 스타일 */
        .stTextInput input, .stSelectbox div[data-baseweb="select"] {{
            height: 75px !important;
            font-size: 26px !important;
            border-radius: 15px !important;
            border: 2px solid #A1887F !important;
            background-color: white !important;
        }}
        
        /* 라디오 버튼 텍스트 크기 */
        div[data-testid="stMarkdownContainer"] p {{
            font-size: 26px !important;
            font-weight: 600;
        }}

        /* 입장하기 버튼 */
        .stButton>button {{
            width: 100%;
            background: linear-gradient(135deg, #8D6E63 0%, #5D4037 100%) !important;
            color: white !important;
            font-size: 38px !important;
            font-weight: 800;
            height: 100px !important;
            border-radius: 20px;
            border: 3px solid #FFFFFF;
            box-shadow: 0 8px 15px rgba(0,0,0,0.3);
            margin-top: 30px;
            transition: 0.3s;
        }}
        .stButton>button:hover {{
            transform: translateY(-5px);
            box-shadow: 0 12px 20px rgba(0,0,0,0.4);
        }}

        /* 상단 툴바 숨기기 */
        header {{visibility: hidden;}}
        </style>
        """,
        unsafe_allow_html=True
    )

set_design()

# 3. 화면 구성 (HTML 구조로 강제 가운데 정렬)
if 'page' not in st.session_state:
    st.session_state.page = "login"

if st.session_state.page == "login":
    # 제목 영역
    st.markdown('<div class="main-wrapper">', unsafe_allow_html=True)
    st.markdown('<div class="title-section">', unsafe_allow_html=True)
    st.markdown('<p class="main-title">나랏말싸미</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">: 꿈틀이의 문해력 키우기</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 입력 카드 시작
    st.markdown('<div class="input-card">', unsafe_allow_html=True)
    
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
            
    st.markdown('</div>', unsafe_allow_html=True) # input-card 끝
    st.markdown('</div>', unsafe_allow_html=True) # main-wrapper 끝

elif st.session_state.page == "main":
    st.success(f"{st.session_state.user_info['name']}님, 환영합니다!")
    if st.button("로그아웃"):
        st.session_state.page = "login"
        st.rerun()
