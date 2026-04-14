import streamlit as st
import base64

# 1. 페이지 설정 (최대한 넓게 사용)
st.set_page_config(page_title="나랏말싸미", layout="centered")

# 2. UI 디자인 고도화 (선생님 원본 이미지 스타일 반영)
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
        /* 배경화면 설정 */
        .stApp {{
            background: url("data:image/png;base64,{bin_str}");
            background-size: cover;
            background-position: center;
        }}
        
        /* 로그인 박스 - 폭을 넓히고 가독성 확보 */
        .login-container {{
            background-color: rgba(255, 255, 255, 0.95);
            padding: 50px 60px;
            border-radius: 30px;
            box-shadow: 0 15px 35px rgba(0,0,0,0.3);
            text-align: center;
            border: 3px solid #5D4037;
            max-width: 500px;
            margin: auto;
        }}
        
        /* 프로그램명 - 칸에 쏙 들어가게 크기 조절 및 진한 색상 */
        .main-title {{
            color: #5D4037;
            font-size: 55px; /* 크기를 더 키움 */
            font-weight: 900;
            margin-bottom: 0px;
            letter-spacing: -2px;
            line-height: 1.2;
        }}
        
        .sub-title {{
            color: #795548;
            font-size: 26px; /* 부제 크기 키움 */
            font-weight: bold;
            margin-bottom: 40px;
        }}
        
        /* 입력창 라벨 - 배경색과 겹치지 않게 아주 진한 갈색으로 */
        label {{
            color: #3E2723 !important;
            font-size: 18px !important;
            font-weight: bold !important;
        }}
        
        /* 버튼 - 원본의 묵직한 느낌 재현 */
        .stButton>button {{
            width: 100%;
            background-color: #8D6E63 !important;
            color: white !important;
            border-radius: 12px;
            height: 60px;
            font-size: 22px;
            font-weight: bold;
            border: none;
            margin-top: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.2);
        }}
        
        /* 라디오 버튼(역할 선택) 글자 크기 */
        .stRadio div[role='radiogroup'] label {{
            font-size: 18px !important;
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
    # 화면 중앙 배치를 위한 공백 처리
    st.write("<br><br>", unsafe_allow_html=True)
    
    # 로그인 컨테이너 시작 (HTML 태그 사용)
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    
    st.markdown('<p class="main-title">나랏말싸미</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">:꿈틀이의 문해력 키우기</p>', unsafe_allow_html=True)
    
    # 학교 입력
    school = st.text_input("학교", placeholder="학교명을 입력하세요")
    
    # 학년/반 가로 배치
    c1, c2 = st.columns(2)
    with c1:
        grade = st.selectbox("학년", [str(i) for i in range(1, 7)])
    with c2:
        classroom = st.text_input("반")
        
    # 이름/비번
    name = st.text_input("이름", placeholder="이름을 입력하세요")
    pw = st.text_input("비밀번호", type="password", placeholder="비밀번호를 입력하세요")
    
    # 역할 선택
    role = st.radio("역할 선택", ["학생", "교사"], horizontal=True)
    
    # 버튼
    if st.button("입장하기"):
        if school and name and pw:
            st.session_state.user_info = {"name": name, "role": role}
            st.session_state.page = "main"
            st.rerun()
        else:
            st.error("모든 정보를 정확히 입력해주세요.")
            
    st.markdown('</div>', unsafe_allow_html=True)

# 4. 메인 화면
elif st.session_state.page == "main":
    st.sidebar.title(f"🏯 {st.session_state.user_info['name']} {st.session_state.user_info['role']}")
    if st.sidebar.button("로그아웃"):
        st.session_state.page = "login"
        st.rerun()
    st.header("🏠 메뉴를 선택해주세요")
