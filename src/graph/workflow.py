import sys
import os

# 💡 여기서 자기 자신을 import 하는 문장이 있다면 반드시 삭제해!
# (예: from src.graph.workflow import build_workflow <- 이 줄 삭제)

from langgraph.graph import StateGraph, END
from .nodes import (
    intent_analysis_node, 
    vision_node, 
    verification_node, 
    retriever_node, 
    database_node,     # 💡 추가했던 노드
    interpreter_node
)
from src.graph.state import GraphState

def build_workflow():
    workflow = StateGraph(GraphState)

    # 노드 등록
    workflow.add_node("intent", intent_analysis_node)
    workflow.add_node("vision", vision_node)
    workflow.add_node("verify", verification_node)
    workflow.add_node("retriever", retriever_node)
    workflow.add_node("database", database_node)
    workflow.add_node("interpreter", interpreter_node)

    # 엣지 연결
    workflow.set_entry_point("intent")
    workflow.add_edge("intent", "vision")
    workflow.add_edge("vision", "verify")
    workflow.add_edge("verify", "retriever")
    workflow.add_edge("retriever", "database")
    workflow.add_edge("database", "interpreter")
    workflow.add_edge("interpreter", END)

    return workflow.compile()