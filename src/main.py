import streamlit as st
import os
import sys

# 💡 [중요] 임포트 하기 전에 경로 설정을 먼저 해야 해!
# 현재 파일(main.py)의 위치를 기반으로 상위 폴더를 path에 추가
current_dir = os.path.dirname(os.path.abspath(__file__)) # src 폴더
project_root = os.path.abspath(os.path.join(current_dir, "..")) # project2 루트

if project_root not in sys.path:
    sys.path.append(project_root)

# 💡 이제 파이썬이 src 폴더를 인식할 수 있어.
from src.graph.workflow import build_workflow
# 1. 페이지 설정
st.set_page_config(page_title="SkinCare Chat", page_icon="🩺", layout="centered")

# 2. 제목
st.title("🩺 AI 피부 진단 챗봇")
st.markdown("사진을 올리고 고민을 채팅으로 말해주세요!")

# --- [삭제] 사이드바 유저 프로필 섹션 전체 삭제 ---

# 3. 세션 상태 초기화 (채팅 기록용)
if "messages" not in st.session_state:
    st.session_state.messages = []

# 4. 이미지 업로드 (채팅창 위에 배치)
uploaded_file = st.file_uploader("먼저 피부 사진을 업로드하세요", type=["jpg", "jpeg", "png"])

# 💡 [추가] 이미지 미리보기 기능 복원
if uploaded_file is not None:
    st.image(uploaded_file, caption="업로드된 피부 이미지", use_container_width=True)

# 5. 기존 채팅 내용 표시
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        # 💡 HTML 렌더링 허용 (unsafe_allow_html=True 추가)
        st.markdown(message["content"], unsafe_allow_html=True)

# 6. 채팅 입력창 (분석 실행의 트리거)
if prompt := st.chat_input("예: 리모넨은 빼고 홍조 위주로 분석해줘!"):
    # 유저 메시지 표시
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    if uploaded_file is None:
        with st.chat_message("assistant"):
            st.warning("분석을 위해 먼저 사진을 업로드해주세요!")
    else:
        # 분석 프로세스 시작
        with st.chat_message("assistant"):
            with st.status("에이전트가 분석 중입니다...", expanded=True) as status:
                image_bytes = uploaded_file.getvalue()
                app = build_workflow()
                
                # 초기 상태 설정 (채팅 메시지 포함)
                initial_state = {
                    "user_message": str(prompt),  # 💡 확실하게 문자열로 변환
                    "image_data": image_bytes,
                    "user_allergy": [],      
                    "analysis_result": {},
                    "skin_knowledge": "",
                    "recommended_products": [],
                    "final_report": ""
                }
                print(f"DEBUG: initial_state['user_message'] = '{initial_state['user_message']}'")
                
                # 그래프 실행
                final_state = app.invoke(initial_state)
                status.update(label="분석 완료!", state="complete", expanded=False)

            # 결과 리포트 출력
            report = final_state.get("final_report", "결과를 생성하지 못했습니다.")
            st.markdown(report, unsafe_allow_html=True)
            
            # 수치 정보 요약 (Metric)
            col1, col2 = st.columns(2)
            col1.metric("유분 수치", f"{final_state.get('oiliness', 0)}%")
            col2.metric("홍조 수치", f"{final_state.get('redness', 0)}%")
            
            # 채팅 기록에 저장
            st.session_state.messages.append({"role": "assistant", "content": report})