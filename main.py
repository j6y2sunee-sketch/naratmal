import streamlit as st
import base64

# 1. 페이지 기본 설정 (가운데 정렬)
st.set_page_config(page_title="나랏말싸미", layout="centered")

# 2. UI 디자인 (사진과 똑같은 화이트 카드 디자인)
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
        /* 1. 전체 화면 배경에 이미지 깔기 */
        .stApp {{
            background: url("data:image/png;base64,{bin_str}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}
        
        /* 상단 메뉴바 숨기기 */
        header {{ visibility: hidden; }}
        footer {{ visibility: hidden; }}

        /* 2. 핵심! Streamlit 메인 화면 자체를 '하얀색 카드'로 만들기 */
        .block-container {{
            background-color: rgba(255, 255, 255, 0.95) !important; /* 95% 불투명한 흰색 */
            padding: 3rem 4rem 4rem 4rem !important; /* 안쪽 여백 넉넉히 */
            border-radius: 25px !important; /* 둥근 모서리 */
            box-shadow: 0 10px 30px rgba(0,0,0,0.15) !important; /* 부드러운 그림자 */
            max-width: 650px !important; /* 카드 가로 길이 고정 */
            margin-top: 8vh !important; /* 화면 위에서 살짝 띄우기 */
            border: 2px solid #EFEBE9 !important; /* 연한 테두리 */
        }}

        /* 3. 제목 가운데 정렬 및 세련된 폰트 */
        h1 {{
            color: #4E342E !important; /* 짙은 갈색 */
            text-align: center !important;
            font-size: 3.5rem !important;
            font-weight: 900 !important;
            margin-bottom: 0px !important;
            padding-bottom: 0px !important;
        }}
        h3 {{
            color: #6D4C41 !important; /* 조금 연한 갈색 */
            text-align: center !important;
            font-size: 1.5rem !important;
            font-weight: bold !important;
            margin-top: 5px !important;
            margin-bottom: 30px !important;
        }}

        /* 4. 입력창 라벨(학교명, 학년 등) 스타일 */
        .stTextInput label p, .stSelectbox label p, .stRadio label p {{
            font-size: 1.5rem !important;
            color: #4E342E !important;
            font-weight: bold !important;
        }}

        /* 5. 입력창(글씨 쓰는 곳) 디자인 */
        .stTextInput input, .stSelectbox div[data-baseweb="select"] {{
            border-radius: 10px !important;
            border: 1.5px solid #D7CCC8 !important;
            font-size: 1.5rem !important;
            height: 3rem !important; /* 적당한 높이 */
            background-color: #FAFAFA !important;
        }}

        /* 6. 입장하기 버튼 세련되게! */
        .stButton>button {{
            width: 100% !important;
            background-color: #6D4C41 !important; /* 갈색 버튼 */
            color: white !important;
            font-size: 1.4rem !important;
            font-weight: bold !important;
            border-radius: 12px !important;
            height: 3.5rem !important;
            border: none !important;
            margin-top: 15px !important;
            transition: 0.2s;
        }}
        .stButton>button:hover {{
            background-color: #4E342E !important; /* 마우스 올리면 더 진해짐 */
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

set_design()

# 3. 화면 구성 시작 (Streamlit의 기본 방식만 사용)
if 'page' not in st.session_state:
    st.session_state.page = "login"

if st.session_state.page == "login":
    # 제목 넣기
    st.markdown("<h1>나랏말싸미</h1>", unsafe_allow_html=True)
    st.markdown("<h3>: 꿈틀이의 문해력 키우기</h3>", unsafe_allow_html=True)

    # 입력창 넣기
    school = st.text_input("학교명")
    
    col1, col2 = st.columns(2)
    with col1:
        grade = st.selectbox("학년", [str(i) for i in range(1, 7)])
    with col2:
        classroom = st.text_input("반")
        
    name = st.text_input("이름")
    pw = st.text_input("비밀번호", type="password")
    
    role = st.radio("역할 선택", ["학생", "교사"], horizontal=True)

    # 버튼
    if st.button("입장하기"):
        if school and name and pw:
            st.session_state.user_info = {"name": name, "role": role}
            st.session_state.page = "main"
            st.rerun()
        else:
            st.error("정보를 모두 입력해 주세요!")

# 4. 로그인 성공 후 임시 메인 화면
elif st.session_state.page == "main":
    st.success(f"{st.session_state.user_info['name']}님, 환영합니다!")
    if st.button("로그아웃"):
        st.session_state.page = "login"
        st.rerun()
