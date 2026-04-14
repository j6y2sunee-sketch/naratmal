import streamlit as st
import base64

# 배경 이미지를 불러와서 화면 전체에 깔아주는 함수
def set_bg_hack(main_bg):
    # 이미지를 웹에서 읽을 수 있는 형태로 변환합니다.
    st.markdown(
        f"""
        <style>
        .stApp {{
            background: url("data:image/png;base64,{main_bg}");
            background-size: cover;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}
        /* 로그인 박스가 배경 위에서 잘 보이도록 반투명 흰색 배경 추가 */
        [data-testid="stVerticalBlock"] > div:has(div.stForm) {{
            background-color: rgba(255, 255, 255, 0.8);
            padding: 30px;
            border-radius: 20px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# GitHub에 올린 bg.png 파일을 읽어오는 로직
# (파일명이 다르면 'bg.png' 부분을 수정해 주세요)
try:
    with open("bg.png", "rb") as f:
        data = f.read()
        bin_str = base64.b64encode(data).decode()
        set_bg_hack(bin_str)
except FileNotFoundError:
    st.warning("배경 이미지 파일(bg.png)을 찾을 수 없습니다. GitHub에 파일을 올렸는지 확인해 주세요!")

# --- 이후에 로그인 화면/본문 코드 작성 ---

# 1. 화면 기본 설정
st.set_page_config(page_title="나랏말싸미", layout="wide")

# 2. 배경색 및 디자인 (집현전 느낌)
st.markdown("""
    <style>
    .stApp { background-color: #fdf5e6; }
    .main-title { color: #8b4513; text-align: center; font-size: 3rem; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# 3. 데이터 저장소 (세션 상태)
if 'page' not in st.session_state:
    st.session_state.page = "login"

# --- 화면 1: 로그인 ---
if st.session_state.page == "login":
    st.markdown("<p class='main-title'>🏯 나랏말싸미</p>", unsafe_allow_html=True)
    st.subheader("꿈틀이의 문해력 키우기")
    
    with st.container():
        name = st.text_input("이름을 입력하세요")
        pw = st.text_input("비밀번호", type="password")
        role = st.selectbox("역할", ["학생", "교사"])
        
        if st.button("집현전 입장하기"):
            if name:
                st.session_state.user_name = name
                st.session_state.role = role
                st.session_state.page = "home"
                st.rerun()

# --- 화면 2: 메인 홈 ---
elif st.session_state.page == "home":
    st.sidebar.title(f"🌳 {st.session_state.user_name}님")
    menu = st.sidebar.radio("메뉴", ["학습 현황", "맞춤법 연습", "문해력 연습", "상점", "로그아웃"])
    
    if menu == "학습 현황":
        st.header("📊 나의 학습 리포트")
        st.write("반갑습니다! 오늘 최고의 꿈틀이가 되어보세요.")
        st.info("현재 점수: 0점 | 레벨: 1단계 새싹")
        
    elif menu == "맞춤법 연습":
        st.header("✍️ 맞춤법 및 받아쓰기")
        q = st.radio("다음 중 올바른 표기는?", ["어의없다", "어이없다"])
        if st.button("채점하기"):
            if q == "어이없다":
                st.success("정답입니다! 점수가 추가되었습니다.")
            else:
                st.error("다시 한번 생각해볼까요?")

    elif menu == "로그아웃":
        st.session_state.page = "login"
        st.rerun()

