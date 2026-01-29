# src/graph/workflow.py
from langgraph.graph import StateGraph, END
from src.graph.state import GraphState
from src.graph.nodes import *

def build_workflow():
    workflow = StateGraph(GraphState)

    # 1. 노드 등록 (순서는 자유!)
    workflow.add_node("vision", vision_node)
    workflow.add_node("verify", verification_node) # 👈 신설!
    workflow.add_node("retriever", retriever_node)
    workflow.add_node("database", database_node)
    workflow.add_node("interpreter", interpreter_node)

    # 2. 엣지 연결 (이게 진짜 중요!)
    workflow.set_entry_point("vision") # 시작은 비전
    workflow.add_edge("vision", "verify")    # 1차 분석 후 2차 검증(조명 판독)
    workflow.add_edge("verify", "retriever") # 보정된 수치로 지식 검색
    workflow.add_edge("retriever", "database") # 지식 검색 후 제품 매칭
    workflow.add_edge("database", "interpreter") # 모든 재료 모아서 리포트 생성
    workflow.add_edge("interpreter", END)   # 끝!

    return workflow.compile()