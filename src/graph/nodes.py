import base64
import numpy as np
import cv2
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from src.graph.state import GraphState
from src.engine.vision_model import SkinAnalyzer
from src.database.sqlite_db import get_recommended_products
from src.agents.interpreter import interpreter_node
from src.agents.interpreter import generate_skin_report, generate_final_report
from src.agents.retriever import get_relevant_knowledge
from src.agents.interpreter import summarize_knowledge
# 1. 객체 초기화
analyzer = SkinAnalyzer()
# 비전 분석을 위한 LLM 모델 (API 키는 환경변수에 설정되어 있어야 함)
# llm_vision = ChatOpenAI(model="gpt-4o") # 환경에 따라 설정
# src/graph/nodes.py

# ... (기존 임포트들)

# 수정 전: llm_vision = ChatOpenAI(model="gpt-4o")
# 수정 후:
llm_vision = None # 일단 비워둬

def get_llm_vision():
    """필요할 때만 LLM을 부르는 안전한 방식"""
    global llm_vision
    if llm_vision is None:
        from langchain_openai import ChatOpenAI
        llm_vision = ChatOpenAI(model="gpt-4o")
    return llm_vision

def encode_image(image_bytes):
    """이미지 바이트를 base64 문자열로 변환"""
    return base64.b64encode(image_bytes).decode('utf-8')

# src/graph/nodes.py의 vision_node 부분 수정

def vision_node(state: GraphState):
    print("--- [Node] 비전 분석 시작 ---")
    image_bytes = state.get("image_data")
    if not image_bytes: return {"redness": 0.0, "oiliness": 0.0}
    
    result = analyzer.analyze_process(image_bytes)
    if result["status"] == "success":
        m = result["metrics"]
        return {"redness": m['redness_level'], "oiliness": m['oiliness_level']}
    
    # src/graph/nodes.py 내부 vision_node의 OpenCV 백업 부분

    # [Step 2] 얼굴 감지 실패 시 OpenCV 픽셀 분석 모드 (백업)
    print(f"⚠️ MediaPipe 실패. OpenCV로 강제 분석을 시작합니다...")
    
    try:
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        h, w, _ = img.shape
        
        # --- [여기가 핵심: ROI 정의] ---
        # 이미지의 중앙 50% 영역만 추출해서 'roi'라는 이름의 변수에 저장해!
        roi = img[h//4:3*h//4, w//4:3*w//4]
        
        # 1. 홍조 분석 (Lab a채널)
        lab = cv2.cvtColor(roi, cv2.COLOR_BGR2Lab)
        avg_a = np.mean(lab[:, :, 1])
        
        # [수정] 기준점을 128 -> 123으로 낮춤 (더 민감하게 반응)
        # 배수도 5 -> 3으로 조절해서 수치가 너무 팍 튀지 않게 밸런스를 잡았어.
        raw_redness = (avg_a - 123) * 3 
        
        # 0~100 사이 고정
        redness = round(min(max(raw_redness, 0), 100), 1)
        
        # 2. 유분 분석 (HSV V채널)
        hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV) # 여기서도 roi 사용
        v_channel = hsv[:, :, 2]
        glare_ratio = np.mean(v_channel > 200)
        oiliness = round(min(glare_ratio * 100, 100), 1)
        
        print(f"✅ OpenCV 백업 성공: 홍조 {redness}, 유분 {oiliness}")
        return {"redness": redness, "oiliness": oiliness}
        
    except Exception as e:
        print(f"❌ OpenCV 백업 분석 실패: {e}") # 여기서 아까 그 에러가 찍혔던 거야
        return {"redness": 0.0, "oiliness": 0.0}

def analyzer_node(state: GraphState):
    print("--- [Node] 지수님 LLM 1차 진단 중 ---")
    # 현재는 더미 데이터, 추후 지수님 진짜 함수로 연결
    return {"analysis_result": {"skin_summary": "민감성 건성", "care_priorities": ["진정", "장벽 강화"]}}

def retriever_node(state: GraphState):
    print("--- [Node] 지식 리트리빙(RAG) 시작 ---")
    
    # 1. 피부 타입이나 현재 수치를 바탕으로 검색어 생성
    # 홍조가 높으면 '홍조 진정 케어', 유분이 적으면 '건성 피부 보습' 등
    red = state.get("redness", 0)
    oil = state.get("oiliness", 0)
    
    # 간단한 쿼리 생성 로직 (LLM을 써서 쿼리를 짜도 되지만 일단은 직관적으로!)
    search_query = ""
    if red > 50: search_query += "홍조 민감성 피부 진정 관리법 "
    if oil < 40: search_query += "건성 피부 수분 장벽 강화 성분"
    else: search_query += "지성 피부 피지 조절 성분"

    # 2. Vector DB에서 지식 추출
    knowledge = get_relevant_knowledge(search_query)
    
    # 3. State 업데이트
    return {"skin_knowledge": knowledge}

def database_node(state: GraphState):
    print("--- [Node] DB 검색 시작 ---")
    oil = state.get("oiliness", 0)
    red = state.get("redness", 0)
    
    recommended = get_recommended_products(oil, red)
    return {"recommended_products": recommended}

def interpreter_node(state: GraphState):
    print("--- [Node] 지수님 로직 가동: 분석 및 리포트 생성 ---")
    red = state.get("redness", 0)
    oil = state.get("oiliness", 0)
    products = state.get("recommended_products", [])
    knowledge = state.get("skin_knowledge", "")
    analysis_json = generate_skin_report(red, oil)
    summarized_knowledge = summarize_knowledge(knowledge)

    # 지수님이 만든 최종 리포트 생성 함수 호출
    final_report = generate_final_report(red, oil, analysis_json, products, summarized_knowledge)

    return {
        "analysis_result": analysis_json, 
        "final_report": final_report
    }

# def generator_node(state: GraphState):
#     print("--- [Node] 최종 지능형 리포트 생성 시작 ---")
    
#     llm = ChatOpenAI(model="gpt-4o", temperature=0.7) # 약간의 창의성을 위해 temp 조절
    
#     # 1. 재료 준비
#     red = state.get("redness", 0)
#     oil = state.get("oiliness", 0)
#     knowledge = state.get("skin_knowledge", "기본적인 보습이 중요합니다.")
#     products = state.get("recommended_products", [])
#     user_allergy = state.get("user_allergy", [])

#     # 2. 지능형 프롬프트 설계
#     prompt = ChatPromptTemplate.from_template("""
#     당신은 피부과 전문의이자 뷰티 큐레이터입니다. 
#     아래 정보를 바탕으로 사용자에게 최적의 피부 리포트를 작성하세요.

#     [분석 데이터]
#     - 홍조 수치: {redness}/100
#     - 유분 수치: {oiliness}/100
#     - 전문 지식(RAG): {knowledge}
#     - 사용자의 알레르기 성분: {user_allergy}

#     [제품 추천 규칙]
#     1. 만약 아래 'DB 제품 리스트'에 데이터가 있다면, 반드시 해당 제품의 이름과 링크를 우선적으로 안내하세요.
#     2. 만약 'DB 제품 리스트'가 비어있다면, 당신이 알고 있는 지식을 활용해 해당 피부 타입에 가장 적합한 대중적인 제품 2~3개를 추천하고 특징을 설명하세요.
#     3. 추천 시 사용자의 알레르기 성분이 포함되어 있는지 주의 깊게 살피고 경고하세요.

#     [DB 제품 리스트]
#     {products_json}

#     마크다운 형식을 사용하여 전문적이고 친절하게 작성하세요.
#     """)

#     # 3. 체인 실행
#     chain = prompt | llm
#     response = chain.invoke({
#         "redness": red,
#         "oiliness": oil,
#         "knowledge": knowledge,
#         "user_allergy": user_allergy,
#         "products_json": products if products else "현재 매칭되는 DB 제품이 없습니다. AI 지식으로 추천해주세요."
#     })

#     return {"final_report": response.content}