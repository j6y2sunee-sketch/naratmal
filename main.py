import streamlit as st
import base64

# 1. 페이지 설정
st.set_page_config(page_title="나랏말싸미", layout="centered")

# 2. 배경 이미지 및 UI 스타일 설정 (이미지 기반 CSS)
def set_design():
    # 배경 이미지를 읽어옵니다. (파일명이 다르면 bg.png 부분을 수정하세요)
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
        
        /* 메인 컨테이너 (로그인 박스) 디자인 */
        .login-box {{
            background-color: rgba(255, 255, 255, 0.92); /* 하얀 상자 투명도 */
            padding: 40px;
            border-radius: 25px;
            box-shadow: 0 10px 25px rgba(0,0,0,0.2);
            text-align: center;
            border: 2px solid #8D6E63;
        }}
        
        /* 제목 스타일 */
        .main-title {{
            color: #5D4037;
            font-size: 45px;
            font-weight: bold;
            margin-bottom: 5px;
        }}
        .sub-title {{
            color: #5D4037;
            font-size: 22px;
            margin-bottom: 30px;
        }}
        
        /* 버튼 디자인 */
        .stButton>button {{
            width: 100%;
            background-color: #8D6E63 !important;
            color: white !important;
            border-radius: 10px;
            height: 50px;
            font-size: 18px;
            font-weight: bold;
            border: none;
        }}
        
        /* 입력창 레이블 색상 고정 */
        label {{
            color: #5D4037 !important;
            font-weight: bold !important;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

set_design()

# 3. 로그인 로직 및 화면 구성
if 'page' not in st.session_state:
    st.session_state.page = "login"

if st.session_state.page == "login":
    # 화면 중앙 정렬을 위한 컬럼 배치
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # 상단 공백
        st.write("<br><br>", unsafe_allow_html=True)
        
        # 실제 로그인 상자 시작
        st.markdown('<div class="login-box">', unsafe_allow_html=True)
        st.markdown('<p class="main-title">나랏말싸미</p>', unsafe_allow_html=True)
        st.markdown('<p class="sub-title">:꿈틀이의 문해력 키우기</p>', unsafe_allow_html=True)
        
        # 입력 필드들 (이미지 속 필드 구성 재현)
        school = st.text_input("학교")
        
        c1, c2 = st.columns(2)
        with c1:
            grade = st.selectbox("학년", [str(i) for i in range(1, 7)])
        with c2:
            classroom = st.text_input("반")
            
        name = st.text_input("이름")
        pw = st.text_input("비밀번호", type="password")
        
        role = st.radio("역할 선택", ["학생", "교사"], horizontal=True)
        
        st.write("<br>", unsafe_allow_html=True)
        if st.button("입장하기"):
            if school and name and pw:
                st.session_state.user_info = {"name": name, "role": role, "school": school}
                st.session_state.page = "main"
                st.success(f"{name}님, 환영합니다!")
                st.rerun()
            else:
                st.warning("모든 정보를 입력해주세요.")
        
        st.markdown('</div>', unsafe_allow_html=True)

# 4. 메인 화면 (로그인 성공 후)
elif st.session_state.page == "main":
    st.sidebar.title(f"🏯 {st.session_state.user_info['name']} {st.session_state.user_info['role']}")
    
    if st.sidebar.button("로그아웃"):
        st.session_state.page = "login"
        st.rerun()
        
    st.header("🏠 메뉴를 선택해주세요")
    st.write("이제 이곳에 내용을 하나씩 채워갈 것입니다.")
