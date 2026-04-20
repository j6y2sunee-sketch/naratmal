import streamlit as st
import requests
import json
import time
from firebase_admin import db

# ==========================================
# ⚙️ 0. 기본 환경 설정 및 세션 상태 초기화
# ==========================================
# (참고: 실제 환경에 맞게 키와 학교 정보를 설정하세요)
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", "여기에_키_입력")
TARGET_URL = "https://api.groq.com/openai/v1/chat/completions"

# 테스트용 기본 정보 (실제 구현 시 로그인 정보 등과 연동)
if "school" not in st.session_state: st.session_state.school = "테스트초"
if "grade" not in st.session_state: st.session_state.grade = "3학년"
if "class_num" not in st.session_state: st.session_state.class_num = "1반"
if "teacher_name" not in st.session_state: st.session_state.teacher_name = "교사"

def safe_dict(data):
    return data if isinstance(data, dict) else {}

# 서브 메뉴 이동을 위한 상태 관리
if "board_mode" not in st.session_state: st.session_state.board_mode = "menu"
if "anthology_mode" not in st.session_state: st.session_state.anthology_mode = "menu"
if "filter_type" not in st.session_state: st.session_state.filter_type = ""
if "filter_value" not in st.session_state: st.session_state.filter_value = ""


# ==========================================
# 🧑‍🎓 1. 학생 관리 (기존)
# ==========================================
def get_student_management_view():
    st.header("🧑‍🎓 학생 관리")
    st.markdown("우리 반 학생들의 목록을 확인하고 기본 정보를 관리합니다.")
    st.info("이곳에 학생 목록 조회 및 추가/수정/삭제 기능을 구현하시면 됩니다.")
    # TODO: 기존 학생 관리 세부 로직 추가


# ==========================================
# ✏️ 2. 맞춤법 및 받아쓰기 관리 (기존)
# ==========================================
def get_spelling_management_view():
    st.header("✏️ 맞춤법 및 받아쓰기 관리")
    st.markdown("학생들의 받아쓰기 성적과 자주 틀리는 맞춤법 데이터를 관리합니다.")
    st.info("이곳에 맞춤법/받아쓰기 데이터 관리 및 문제 배포 기능을 구현하시면 됩니다.")
    # TODO: 기존 맞춤법/받아쓰기 세부 로직 추가


# ==========================================
# 📖 3. 문해력 관리 (기존)
# ==========================================
def get_literacy_management_view():
    st.header("📖 문해력 관리")
    st.markdown("학생들의 읽기 수준과 문해력 향상 추이를 확인합니다.")
    st.info("이곳에 문해력 진단 평가 결과 및 지문 배포 기능을 구현하시면 됩니다.")
    # TODO: 기존 문해력 관리 세부 로직 추가


# ==========================================
# ✍️ 4. 글쓰기 관리 (새로 추가)
# ==========================================
def get_writing_management_view():
    st.header("📝 글쓰기 관리")
    st.markdown("학생들에게 제시할 글쓰기 주제를 AI로 생성하거나 직접 작성하여 배포합니다.")
    
    tab1, tab2 = st.tabs(["🤖 AI 주제 추천", "✍️ 직접 제시"])
    db_path = f"writing_tasks/{st.session_state.school}/{st.session_state.grade}/{st.session_state.class_num}"

    with tab1:
        st.subheader("AI 주제 추천")
        write_grade = st.selectbox("학년 수준", [f"{i}학년" for i in range(1, 7)], index=2)
        
        if st.button("주제 생성 시작", type="primary"):
            with st.spinner("AI가 주제를 고민 중..."):
                try:
                    prompt = f"초등학교 {write_grade} 수준에 맞는 재미있고 창의적인 글쓰기 주제 1개를 JSON으로 생성해줘. 형식: {{ 'topic': '글쓰기 주제', 'guideline': '가이드라인' }}"
                    payload = {"model": "llama-3.3-70b-versatile", "temperature": 0.2, "messages": [{"role": "system", "content": "You are a creative writing teacher. Output ONLY JSON. 반드시 자연스럽고 완벽한 한국어(표준어)로만 작성하세요."}, {"role": "user", "content": prompt}], "response_format": {"type": "json_object"}}
                    response = requests.post(TARGET_URL, json=payload, headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"})
                    res_data = json.loads(response.json()['choices'][0]['message']['content'])
                    
                    st.session_state.ai_topic = res_data.get('topic', '')
                    st.session_state.ai_guide = res_data.get('guideline', '')
                except Exception as ex:
                    st.error(f"생성 오류가 발생했습니다: {ex}")

        if "ai_topic" in st.session_state:
            st.divider()
            edited_topic = st.text_area("주제 (수정 가능)", value=st.session_state.ai_topic)
            edited_guide = st.text_area("가이드라인 (수정 가능)", value=st.session_state.ai_guide, height=100)
            
            if st.button("💾 AI 생성 문제 배포하기"):
                db.reference(db_path).set({"topic": edited_topic, "guideline": edited_guide, "created_at": str(time.time())})
                st.success("✅ 문제 배포가 완료되었습니다!")
                del st.session_state.ai_topic

    with tab2:
        st.subheader("직접 제시")
        manual_topic = st.text_area("주제", placeholder="학생들에게 제시할 주제를 입력하세요.")
        manual_guide = st.text_area("가이드라인", placeholder="글쓰기 가이드라인을 입력하세요.", height=100)
        
        if st.button("💾 직접 배포하기"):
            if manual_topic:
                db.reference(db_path).set({"topic": manual_topic, "guideline": manual_guide, "created_at": str(time.time())})
                st.success("✅ 문제 배포가 완료되었습니다!")
            else:
                st.warning("주제를 입력해주세요.")


# ==========================================
# 📋 5. 게시판 관리 (새로 추가)
# ==========================================
def get_board_management_view():
    st.header("📋 글 공유 게시판 관리")
    path = f"board_posts/{st.session_state.school}/{st.session_state.grade}/{st.session_state.class_num}"
    all_posts = safe_dict(db.reference(path).get())

    if st.session_state.board_mode == "menu":
        col1, col2 = st.columns(2)
        with col1:
            st.info("📚 **주제별 조회**\n\n그동안 제시된 주제별로 학생들의 글을 모아봅니다.")
            if st.button("주제별로 보기", use_container_width=True):
                st.session_state.board_mode = "topics"
                st.rerun()
        with col2:
            st.info("👤 **학생별 조회**\n\n우리 반 학생들 이름별로 작성한 글을 모아봅니다.")
            if st.button("학생별로 보기", use_container_width=True):
                st.session_state.board_mode = "students"
                st.rerun()

    elif st.session_state.board_mode in ["topics", "students"]:
        if st.button("⬅️ 뒤로가기"):
            st.session_state.board_mode = "menu"
            st.rerun()
            
        is_topic = st.session_state.board_mode == "topics"
        st.subheader(f"{'주제별' if is_topic else '학생별'} 목록")
        
        items = set()
        for key, data in all_posts.items():
            if isinstance(data, dict):
                val = data.get('title' if is_topic else 'author')
                if val: items.add(str(val))
        
        if not items:
            st.write("등록된 데이터가 없습니다.")
        else:
            for item in sorted(list(items)):
                if st.button(item, use_container_width=True):
                    st.session_state.board_mode = "posts"
                    st.session_state.filter_type = "title" if is_topic else "author"
                    st.session_state.filter_value = item
                    st.rerun()

    elif st.session_state.board_mode == "posts":
        if st.button("⬅️ 목록으로 돌아가기"):
            st.session_state.board_mode = "topics" if st.session_state.filter_type == "title" else "students"
            st.rerun()
            
        st.subheader(f"'{st.session_state.filter_value}' 관련 글")
        st.divider()
        
        filtered_posts = {k: v for k, v in all_posts.items() if str(v.get(st.session_state.filter_type, '')) == st.session_state.filter_value}
        
        if not filtered_posts:
            st.write("해당 조건의 게시글이 없습니다.")
        else:
            for pid, pdata in filtered_posts.items():
                with st.container(border=True):
                    st.markdown(f"#### 📝 {pdata.get('title', '')} (작성자: {pdata.get('author', '')})")
                    st.write(pdata.get('content', ''))
                    
                    if st.button("🗑️ 게시글 삭제", key=f"del_{pid}", type="primary"):
                        db.reference(f"{path}/{pid}").delete()
                        st.success("삭제 완료")
                        st.rerun()
                    
                    st.markdown("**💬 댓글**")
                    for cid, cdata in pdata.get('comments', {}).items():
                        c_col1, c_col2 = st.columns([8, 2])
                        c_col1.write(f"↳ {cdata.get('author', '익명')}: {cdata.get('text', '')}")
                        if c_col2.button("❌", key=f"cdel_{cid}"):
                            db.reference(f"{path}/{pid}/comments/{cid}").delete()
                            st.rerun()
                            
                    new_comment = st.text_input("댓글 달기", key=f"c_input_{pid}")
                    if st.button("댓글 등록", key=f"c_btn_{pid}"):
                        if new_comment:
                            db.reference(f"{path}/{pid}/comments").push({"author": "교사", "text": new_comment})
                            st.rerun()


# ==========================================
# 🏛️ 6. 집현전(도서관) 관리 (새로 추가)
# ==========================================
def get_jiphyeonjeon_management_view():
    st.header("🏛️ 집현전(도서관) 관리")
    path = f"jiphyeonjeon_books/{st.session_state.school}/{st.session_state.grade}/{st.session_state.class_num}"
    books = safe_dict(db.reference(path).get())
    
    if not books:
        st.info("등록된 도서가 없습니다.")
        return

    for bid, bdata in books.items():
        with st.expander(f"📖 {bdata.get('title', '제목 없음')} - {bdata.get('author', '작자 미상')}"):
            with st.form(key=f"book_form_{bid}"):
                new_title = st.text_input("도서 제목", value=bdata.get('title', ''))
                new_author = st.text_input("지은이", value=bdata.get('author', ''))
                new_desc = st.text_area("독서 포인트", value=bdata.get('desc', ''))
                
                if st.form_submit_button("💾 정보 수정 완료"):
                    db.reference(f"{path}/{bid}").update({"title": new_title, "author": new_author, "desc": new_desc})
                    st.success("수정되었습니다.")
                    st.rerun()


# ==========================================
# 📘 7. 문집 관리 (새로 추가)
# ==========================================
def get_anthology_management_view():
    st.header("📘 학급 문집 관리")
    path = f"student_writings/{st.session_state.school}/{st.session_state.grade}/{st.session_state.class_num}"
    all_students = safe_dict(db.reference(path).get())

    if st.session_state.anthology_mode == "menu":
        col1, col2 = st.columns(2)
        with col1:
            st.info("📚 **주제별 문집**\n\n제시된 글쓰기 주제별로 모아봅니다.")
            if st.button("주제별 문집 조회", use_container_width=True):
                st.session_state.anthology_mode = "topics"
                st.rerun()
        with col2:
            st.info("👤 **학생별 문집**\n\n학생 이름별로 모아봅니다.")
            if st.button("학생별 문집 조회", use_container_width=True):
                st.session_state.anthology_mode = "students"
                st.rerun()

    elif st.session_state.anthology_mode in ["topics", "students"]:
        if st.button("⬅️ 뒤로가기"):
            st.session_state.anthology_mode = "menu"
            st.rerun()
            
        is_topic = st.session_state.anthology_mode == "topics"
        st.subheader(f"{'주제별' if is_topic else '학생별'} 문집 목록")
        
        items = set()
        if is_topic:
            for s, w_dict in all_students.items():
                for wid, wd in safe_dict(w_dict).items():
                    if wd.get('topic'): items.add(str(wd['topic']))
        else:
            items = set(all_students.keys())
            
        for item in sorted(list(items)):
            if st.button(item, use_container_width=True, key=f"anth_{item}"):
                st.session_state.anthology_mode = "posts"
                st.session_state.filter_type = "topic" if is_topic else "student"
                st.session_state.filter_value = item
                st.rerun()

    elif st.session_state.anthology_mode == "posts":
        if st.button("⬅️ 목록으로 돌아가기"):
            st.session_state.anthology_mode = "topics" if st.session_state.filter_type == "topic" else "students"
            st.rerun()
            
        st.subheader(f"'{st.session_state.filter_value}' 문집")
        
        data_to_download = []
        download_text = f"--- {st.session_state.grade} {st.session_state.class_num} '{st.session_state.filter_value}' 문집 ---\n\n"
        
        for student, w_dict in all_students.items():
            for wid, wd in safe_dict(w_dict).items():
                if (st.session_state.filter_type == "topic" and str(wd.get('topic', '')) == str(st.session_state.filter_value)) or \
                   (st.session_state.filter_type == "student" and str(student) == str(st.session_state.filter_value)):
                    
                    data_to_download.append(wd)
                    download_text += f"[{student}] 주제: {wd.get('topic', '')}\n내용: {wd.get('content', '')}\n\n"
                    
                    with st.container(border=True):
                        col1, col2 = st.columns([9, 1])
                        col1.markdown(f"**📝 {wd.get('topic', '')}** (학생: {student})")
                        if col2.button("❌", key=f"del_anth_{wid}"):
                            db.reference(f"{path}/{student}/{wid}").delete()
                            st.rerun()
                        st.write(wd.get('content', ''))

        if data_to_download:
            st.download_button(
                label="💾 현재 목록 텍스트(.txt)로 다운로드",
                data=download_text,
                file_name=f"{st.session_state.filter_value}_문집.txt",
                mime="text/plain",
                type="primary"
            )


# ==========================================
# 💎 8. 상점 관리
# ==========================================
def get_shop_management_view():
    st.header("💎 상점(리워드) 관리")
    st.markdown("학생들이 획득한 포인트로 구매할 수 있는 상점 아이템을 관리합니다.")
    st.info("이곳에 상점 아이템 추가/삭제/수정 기능을 구현할 수 있습니다.")


# ==========================================
# 📈 9. 점수 관리
# ==========================================
def get_score_management_view():
    st.header("📈 학생 점수/포인트 관리")
    st.markdown("학생들의 활동 내역과 누적 포인트를 한눈에 확인하고 조정합니다.")
    st.info("이곳에 학생별 데이터 조회 및 포인트 수정 기능을 구현할 수 있습니다.")


# ==========================================
# 🚀 메인 애플리케이션 (사이드바 메뉴 통합)
# ==========================================
def main():
    st.set_page_config(page_title="나랏말싸미 교사용 관리자", page_icon="👩‍🏫", layout="wide")
    
    with st.sidebar:
        st.title("👩‍🏫 교사 대시보드")
        menu = st.radio(
            "관리 메뉴 선택",
            [
                "학생 관리", 
                "맞춤법 및 받아쓰기 관리", 
                "문해력 관리", 
                "글쓰기 관리", 
                "게시판 관리", 
                "집현전 관리", 
                "문집 관리", 
                "상점 관리", 
                "점수 관리"
            ]
        )
        
        st.divider()
        st.caption(f"현재 접속: {st.session_state.school} {st.session_state.grade} {st.session_state.class_num}")

    # 선택된 메뉴 렌더링
    if menu == "학생 관리":
        get_student_management_view()
    elif menu == "맞춤법 및 받아쓰기 관리":
        get_spelling_management_view()
    elif menu == "문해력 관리":
        get_literacy_management_view()
    elif menu == "글쓰기 관리":
        get_writing_management_view()
    elif menu == "게시판 관리":
        get_board_management_view()
    elif menu == "집현전 관리":
        get_jiphyeonjeon_management_view()
    elif menu == "문집 관리":
        get_anthology_management_view()
    elif menu == "상점 관리":
        get_shop_management_view()
    elif menu == "점수 관리":
        get_score_management_view()

if __name__ == "__main__":
    main()
