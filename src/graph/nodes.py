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
import json
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
import base64
import re
def call_gpt4o_vision(image_base64, prompt):
    llm = ChatOpenAI(model="gpt-4o", temperature=0) # 변동성 없애기 위해 0 설정

    # 시스템 메시지로 "넌 이미지 분석기야"라고 세뇌하기
    system_msg = SystemMessage(content="You are a technical image analysis assistant. Your task is to adjust sensor data based on visual pixel analysis. Do not provide medical advice.")
    
    # ... (이미지 헤더 처리 로직)
    
    message = HumanMessage(
        content=[
            {"type": "text", "text": prompt},
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}}
        ]
    )

    response = llm.invoke([system_msg, message])
    content = response.content.strip()

    # 💡 [핵심] JSON 블록만 추출하는 정규표현식 로직
    try:
        # ```json { ... } ``` 형식을 찾거나, 그냥 { ... } 형식을 찾음
        json_match = re.search(r"\{.*\}", content, re.DOTALL)
        if json_match:
            json_str = json_match.group()
            return json.loads(json_str)
        else:
            raise ValueError("No JSON object found in response")
            
    except Exception as e:
        print(f"❌ JSON 파싱 에러 상세: {e}")
        print(f"⚠️ GPT 원본 응답: {content}") # 디버깅용으로 원본 출력
        return None # 실패 시 None 반환
# 1. 객체 초기화
analyzer = SkinAnalyzer()
llm_vision = None 

# nodes.py 내 수정
def intent_analysis_node(state: GraphState):
    print("--- [Node] 유저 의도 분석 시작 ---")
    user_msg = state.get("user_message", "")
    print(f"💬 유저 입력 메시지: {user_msg}") # 전달된 메시지 확인용

    prompt = f"""
    당신은 화장품 성분 분석 전문가입니다. 유저의 메시지에서 '피해야 할 성분명'을 리스트로 추출하세요.
    
    [규칙]
    1. '리모넨 성분'이라고 하면 '리모넨'만 추출합니다.
    2. '알러지', '제외', '빼줘', '안 맞아'와 연결된 성분은 무조건 리스트에 넣습니다.
    3. 결과는 반드시 아래 JSON 형식으로만 응답하세요.
    
    메시지: "{user_msg}"
    
    응답 예시: {{"allergy_ingredients": ["리모넨"], "user_concerns": "홍조"}}
    """
    
    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    response = llm.invoke(prompt)
    
    try:
        # JSON만 깔끔하게 추출하기 위해 정규식 사용
        import re
        content = response.content.strip()
        json_match = re.search(r"\{.*\}", content, re.DOTALL)
        if json_match:
            extracted = json.loads(json_match.group())
        else:
            extracted = {"allergy_ingredients": [], "user_concerns": ""}
    except Exception as e:
        print(f"⚠️ JSON 파싱 에러: {e}")
        extracted = {"allergy_ingredients": [], "user_concerns": ""}

    # 💡 터미널 로그를 통해 추출된 결과를 확실히 확인
    print(f"🚫 최종 추출된 차단 성분: {extracted.get('allergy_ingredients', [])}")
    
    return {
        "user_allergy": extracted.get('allergy_ingredients', []),
        "user_concerns": extracted.get('user_concerns', "")
    }

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

def vision_node(state: GraphState):
    print("--- [Node] 비전 분석 시작 ---")
    image_bytes = state.get("image_data")
    if not image_bytes: return {"redness": 0.0, "oiliness": 0.0}
    
    result = analyzer.analyze_process(image_bytes)
    if result["status"] == "success":
        m = result["metrics"]
        return {"redness": m['redness_level'], "oiliness": m['oiliness_level']}

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

def verification_node(state: GraphState):
    print("--- [Node] 데이터 기반 논리 보정 시작 ---")
    
    # 1. 이전 노드에서 측정된 원시 수치 가져오기
    raw_red = state.get("redness", 0)
    raw_oil = state.get("oiliness", 0)
    
    # 2. GPT에게 보낼 텍스트 프롬프트 구성 (사진 제외!)
    # 유분 점수가 40점 근처(건성 경계)일 때 지성으로 보정할 논리적 근거를 심어줌
    prompt = f"""
    당신은 피부 데이터 분석 전문가입니다. 
    시각 센서가 측정해온 원시 수치(Raw Data)를 검토하여 최종 수치를 보정하십시오.

    [측정 데이터]
    - 유분 반사광 수치: {raw_oil}
    - 헤모글로빈(홍조) 수치: {raw_red}

    [보정 가이드라인]
    1. 유분 수치가 35~45 사이(건성/복합성 경계)라면, 조명 오차를 고려하여 이를 '지성(70점 이상)'으로 보정하는 것을 적극 검토하십시오.
    2. 특히 사진이 밝은 환경에서 촬영되었다면 반사광이 실제보다 적게 측정될 수 있음을 반영하십시오.
    3. 결과는 반드시 아래 JSON 형식으로만 응답하고, 부연 설명은 하지 마십시오.

    {{
        "corrected_redness": {raw_red}를 바탕으로 보정한 값,
        "corrected_oiliness": {raw_oil}를 바탕으로 보정한 값,
        "reason": "데이터 기반 보정 근거"
    }}
    """
    
    try:
        llm = ChatOpenAI(model="gpt-4o", temperature=0)
        response = llm.invoke(prompt)
        
        import re
        content = response.content.strip()
        json_match = re.search(r"\{.*\}", content, re.DOTALL)
        
        if json_match:
            verified_result = json.loads(json_match.group())
        else:
            verified_result = None

    except Exception as e:
        print(f"⚠️ GPT 보정 중 에러 발생: {e}")
        verified_result = None

    # 3. 안전한 리턴 및 가중 평균 로직
    if verified_result is None:
        return {"redness": raw_red, "oiliness": raw_oil, "verification_log": "보정 실패"}

    # 💡 [신규] GPT가 제안한 보정값 가져오기
    gpt_red = float(verified_result.get("corrected_redness", raw_red))
    gpt_oil = float(verified_result.get("corrected_oiliness", raw_oil))

    # 💡 [신규] 가중 평균 계산 (기계 0.3 : GPT 0.7)
    # 기계의 분석력과 GPT의 직관을 섞어서 수치를 부드럽게 만듦
    final_red = (raw_red * 0.3) + (gpt_red * 0.7)
    final_oil = (raw_oil * 0.3) + (gpt_oil * 0.7)

    print(f"⚖️ 가중 평균 보정 완료: 유분({raw_oil} -> {round(final_oil, 1)}), 홍조({raw_red} -> {round(final_red, 1)})")

    return {
        "redness": round(final_red, 1),
        "oiliness": round(final_oil, 1),
        "verification_log": verified_result.get("reason", "Success")
    }

def retriever_node(state: GraphState):
    print("--- [Node] 지식 리트리빙(RAG) 시작 ---")
    
    # 💡 state.get("key", 0)에서 뒤의 0은 "값이 없으면 0으로 써라"는 뜻이야.
    # 하지만 더 안전하게 한번 더 체크하자.
    red = state.get("redness")
    oil = state.get("oiliness")

    # 만약 앞 노드에서 실수로 None을 보냈다면 0으로 강제 치환
    if red is None: red = 0
    if oil is None: oil = 0
    
    search_queries = []
    
    # 이제 red가 무조건 숫자니까 '>' 비교에서 에러가 안 나!
    if red > 40:
        search_queries.append("민감성 홍조 피부 진정 성분 판테놀 병풀")
    
    # 유분 점수에 따른 타입별 쿼리
    # nodes.py 내 retriever_node 부분
    if oil < 40:
        search_queries.append("건성 피부 보습 에센스 세럼 추천 성분")
    elif oil > 70:
        search_queries.append("지성 피부 산뜻한 에센스 수분 세럼 관리")
    else:
        search_queries.append("복합성 피부 유수분 밸런스 조절법") # 복합성 쿼리 추가!

    # 쿼리 합치기
    search_query = " ".join(search_queries)
    
    # 2. Vector DB에서 지식 추출
    knowledge = get_relevant_knowledge(search_query)
    
    return {"skin_knowledge": knowledge}

def database_node(state: GraphState):
    # 제품 DB 검색만 수행
    print("--- [Node] 가성비 및 알러지 필터링 제품 검색 ---")
    red = state.get("redness", 0)
    oil = state.get("oiliness", 0)
    allergy = state.get("user_allergy", [])
    
    # 아까 수정한 sqlite_db의 함수 호출
    products = get_recommended_products(oil, red, allergy)
    return {"recommended_products": products}

def interpreter_node(state: GraphState):
    print("--- [Node] 지수님 로직 가동: 분석 및 리포트 생성 ---")
    
    red = state.get("redness", 0)
    oil = state.get("oiliness", 0)
    products = state.get("recommended_products", [])
    knowledge = state.get("skin_knowledge", "")
    
    # 1. 브랜드명 제거를 위한 클리닝 함수 정의
    def get_clean_name(brand, full_name):
        if not brand or brand == "Unknown":
            return full_name
        # 브랜드명 글자 사이에 공백이 있을 수 있음을 고려한 패턴 (브\s*리\s*오\s*쉬\s*번)
        brand_pattern = r"\s*".join(map(re.escape, brand))
        # 패턴 제거 및 앞뒤 찌꺼기(특수문자 등) 정리
        clean_name = re.sub(brand_pattern, "", full_name, flags=re.IGNORECASE).strip()
        clean_name = re.sub(r"^[\[\(\-\s\.]+", "", clean_name)
        return clean_name if clean_name else full_name

    # 2. 지수님 리포트 함수에 넣기 전에 제품명만 클리닝한 새로운 리스트 생성
    # 원본 products 데이터는 유지하면서 display용 이름만 바꿔주는 거야
    cleaned_products = []
    for p in products:
        new_p = p.copy()  # 원본 복사
        brand = p.get('brand', '')
        raw_name = p.get('name', '')
        new_p['name'] = get_clean_name(brand, raw_name)  # 이름만 클리닝된 버전으로 교체
        cleaned_products.append(new_p)

    # 3. 기존 로직 그대로 실행하되, 제품 리스트만 cleaned_products로 교체
    analysis_json = generate_skin_report(red, oil)
    summarized_knowledge = summarize_knowledge(knowledge)

    # 지수님 함수 호출 (청소된 제품 리스트를 전달!)
    final_report = generate_final_report(red, oil, analysis_json, cleaned_products, summarized_knowledge)

    return {
        "analysis_result": analysis_json, 
        "final_report": final_report
    }