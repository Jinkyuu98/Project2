import sys
import os
from dotenv import load_dotenv

load_dotenv() # .env 파일의 환경 변수를 불러옵니다.

# 현재 파일(main.py)의 위치를 기준으로 프로젝트 루트(Project2)를 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
from src.graph.workflow import build_workflow

# 1. 페이지 설정
st.set_page_config(page_title="SkinCare Agent", page_icon="🩺", layout="centered")

# 2. 제목 및 소개
st.title("🩺 퍼스널 피부 헬스케어 에이전트")
st.markdown("---")

# 3. 사이드바 - 유저 정보 입력
with st.sidebar:
    st.header("👤 유저 프로필")
    user_allergy = st.multiselect(
        "본인이 예민한 성분을 선택하세요",
        ["아밀신남알", "벤질알코올", "신나밀알코올", "시트랄", 
        "유제놀", "하이드록시시트로넬알","아이소유제놀","아밀신나밀알코올",
        "벤질살리실레이트","신남알","쿠마린",
        "제라니올","아니스알코올","벤질신나메이트",
        "파네솔","부틸페닐메틸프로피오날","리날룰","벤질벤조에이트",
        "시트로넬올","헥실신남알","리모넨","메틸 2-옥티노에이트",
        "알파-아이소메틸아이오논","참나무이끼추출물","나무이끼추출물"]
    )

# 4. 메인 화면 - 이미지 업로드
st.subheader("📸 피부 사진 분석")
uploaded_file = st.file_uploader("피부 사진을 업로드하세요", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    st.image(uploaded_file, caption="업로드된 사진", width='content')
    if st.button("에이전트에게 분석 요청하기"):
        with st.status("에이전트가 분석 중입니다...", expanded=True) as status:
            
            # 1. 업로드된 이미지 파일을 바이트 데이터로 추출
            # (이 데이터가 vision_node의 SkinAnalyzer로 전달됨)
            image_bytes = uploaded_file.getvalue()
            
            # 2. LangGraph 워크플로우 빌드
            st.write("🧠 AI 에이전트 워크플로우 가동 중...")
            app = build_workflow()
            
            # 3. 초기 상태(initial_state) 설정
            # 이제 고정 수치 대신 'image_data'를 직접 전달함
            initial_state = {
                "image_data": image_bytes,  # 실제 이미지 데이터 투입
                "user_allergy": user_allergy,
                "analysis_result": {},
                "skin_knowledge": "",
                "recommended_products": [],
                "final_report": ""
            }
            
            # 4. 그래프 실행 (비전 분석 -> LLM 진단 -> 제품 매칭)
            # 이제 vision_node가 image_data를 분석해 redness, oiliness를 업데이트함
            final_state = app.invoke(initial_state)
            
            status.update(label="분석 완료!", state="complete", expanded=False)

        # 5. 최종 결과 출력 (실제 분석된 수치와 리포트 표시)
        st.success("✅ 분석이 완료되었습니다!")
        st.divider()
        
        col1, col2 = st.columns(2)
        with col1:
            # final_state에 저장된 실제 유분 수치 출력
            st.metric(label="유분 수치", value=f"{final_state.get('oiliness', 0)}%")
        with col2:
            # final_state에 저장된 실제 홍조 수치 출력
            st.metric(label="홍조 수치", value=f"{final_state.get('redness', 0)}%")
            
        st.markdown(final_state["final_report"], unsafe_allow_html=True)

else:
    st.info("왼쪽 사이드바에서 정보를 입력하고 피부 사진을 업로드해주세요.")