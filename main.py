import streamlit as st
import time
import requests

# (주의) 기존 로그인 코드가 있는 파일이라면 아래 페이지 설정 부분은 제외하거나 적절히 합쳐주세요!
# st.set_page_config(page_title="나랏말싸미", layout="wide") # 교사 화면은 넓게 쓰는 것이 좋습니다.

def show_teacher_dashboard():
    # --- 가상 데이터 (Firebase db.reference('users').get() 대체용) ---
    if 'mock_users' not in st.session_state:
        st.session_state.mock_users = {
            "uid_001": {
                "role": "학생", "school": "테스트초", "grade": "3", "class": "1", "name": "김꿈틀",
                "scores": {"total": 420, "spelling": 100, "literacy": 90, "writing": 80, "jiphyeon": 150},
                "ai_report": "버튼을 눌러 현재 학습 데이터를 분석해보세요."
            },
            "uid_002": {
                "role": "학생", "school": "테스트초", "grade": "3", "class": "1", "name": "이새싹",
                "scores": {"total": 350, "spelling": 80, "literacy": 85, "writing": 75, "jiphyeon": 110},
                "ai_report": "버튼을 눌러 현재 학습 데이터를 분석해보세요."
            }
        }

    # --- CSS 스타일 적용 (Flet의 아기자기한 컨테이너 색상 완벽 구현) ---
    st.markdown("""
        <style>
        .student-card { background-color: #F5F5F5; border-radius: 15px; padding: 20px; margin-bottom: 20px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); }
        .score-box { display: inline-block; padding: 8px 12px; border-radius: 10px; margin-right: 10px; font-weight: bold; font-size: 14px; color: #333; }
        .bg-spelling { background-color: #FDEEF4; }
        .bg-literacy { background-color: #EBF4FA; }
        .bg-writing { background-color: #F0F9ED; }
        .bg-jiphyeon { background-color: #FFF9E5; }
        .ai-box { margin-top: 15px; padding: 15px; background-color: white; border-radius: 10px; border-left: 5px solid #8D6E63; }
        </style>
    """, unsafe_allow_html=True)

    # --- 사이드바 메뉴 구성 ---
    with st.sidebar:
        st.markdown("### 👨‍🏫 교사 메뉴")
        menu = st.radio(
            "이동할 메뉴를 선택하세요",
            ["홈", "학생 관리", "맞춤법 및 받아쓰기 관리", "문해력 관리", "글쓰기 관리", "로그아웃"]
        )

    # --- 1. 홈 (첫 화면) ---
    if menu == "홈":
        st.markdown('<h2>나랏말싸미 <span style="color:#8D6E63;">교사 대시보드</span>입니다.</h2>', unsafe_allow_html=True)
        st.info("👈 왼쪽 메뉴를 선택하여 학생들의 학습을 관리해주세요.")
        
        # 교사 정보 요약 (선택 사항)
        st.success("오늘도 아이들의 문해력을 위해 힘써주셔서 감사합니다!")

    # --- 2. 학생 관리 화면 ---
    elif menu == "학생 관리":
        st.markdown('<h2><span style="color:#5D4037;">[학생 관리]</span></h2>', unsafe_allow_html=True)
        st.divider()

        # 검색된 학생 수에 따라 반복해서 카드 생성
        for uid, data in st.session_state.mock_users.items():
            if data['role'] == '학생':
                scores = data.get('scores', {})
                total = scores.get('total', 0)
                sp = scores.get('spelling', 0)
                li = scores.get('literacy', 0)
                wr = scores.get('writing', 0)
                zi = scores.get('jiphyeon', 0)
                ai_report = data.get('ai_report', "")

                # 카드 컨테이너 시작
                with st.container():
                    st.markdown('<div class="student-card">', unsafe_allow_html=True)
                    
                    # 이름 및 총점
                    col1, col2 = st.columns([1, 4])
                    with col1:
                        st.markdown(f"### 👤 {data['name']}")
                    with col2:
                        st.markdown(f"<h3 style='color:#C62828; margin:0;'>🏆 총점: {total}점</h3>", unsafe_allow_html=True)
                    
                    # 세부 점수 뱃지 (HTML/CSS)
                    st.markdown(f"""
                        <div style="margin-top: 10px;">
                            <div class="score-box bg-spelling">맞춤법: {sp}</div>
                            <div class="score-box bg-literacy">문해력: {li}</div>
                            <div class="score-box bg-writing">글쓰기: {wr}</div>
                            <div class="score-box bg-jiphyeon">집현전: {zi}</div>
                        </div>
                    """, unsafe_allow_html=True)

                    # AI 분석 영역
                    st.markdown('<div class="ai-box">', unsafe_allow_html=True)
                    
                    ai_col1, ai_col2 = st.columns([1, 4])
                    with ai_col1:
                        st.markdown("**⭐ AI 학습 능력 분석**")
                        # Streamlit에서는 버튼의 고유 key가 필수입니다
                        if st.button("🤖 AI 분석하기", key=f"ai_btn_{uid}"):
                            with st.spinner(f"{data['name']} 학생의 데이터를 분석 중입니다..."):
                                # 실제로는 여기에 Groq API 호출 코드가 들어갑니다.
                                # 현재는 시뮬레이션을 위해 2초 대기 후 결과 텍스트를 업데이트합니다.
                                time.sleep(2) 
                                
                                # (원래 코드의 Groq API 로직이 들어갈 자리)
                                dummy_ai_result = f"👩‍🏫 {data['name']} 학생은 맞춤법({sp}점)과 집현전 독서({zi}점)에서 아주 뛰어난 성취를 보이고 있어요! 다만 글쓰기({wr}점) 점수를 보완하기 위해 짧은 일기 쓰기부터 차근차근 지도해 주시면 더욱 완벽해질 거예요. 훌륭하게 성장 중입니다!"
                                
                                # 세션 스테이트(가상 DB) 업데이트
                                st.session_state.mock_users[uid]['ai_report'] = dummy_ai_result
                                st.rerun() # 화면 새로고침

                    with ai_col2:
                        st.write(ai_report)
                    
                    st.markdown('</div>', unsafe_allow_html=True) # ai-box 끝
                    st.markdown('</div>', unsafe_allow_html=True) # student-card 끝

    # --- 3. 로그아웃 처리 ---
    elif menu == "로그아웃":
        st.session_state.page = "login"
        st.rerun()

    # --- 나머지 메뉴들 (임시) ---
    else:
        st.warning(f"'{menu}' 화면은 현재 공사 중입니다! 🚧")


# 단독 실행 테스트용 로직
if __name__ == "__main__":
    if 'page' not in st.session_state:
        st.session_state.page = "teacher"
    
    if st.session_state.page == "teacher":
        show_teacher_dashboard()
