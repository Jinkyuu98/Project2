# src/graph/workflow.py
from langgraph.graph import StateGraph, END
from src.graph.state import GraphState
from src.graph.nodes import *

def build_workflow():
    workflow = StateGraph(GraphState)

    workflow.add_node("vision", vision_node)
    workflow.add_node("db_search", database_node)
    workflow.add_node("retriever", retriever_node) # 💡 RAG 노드 추가
    workflow.add_node("interpreter", interpreter_node)

    workflow.set_entry_point("vision")
    workflow.add_edge("vision", "db_search")
    workflow.add_edge("db_search", "retriever")    # 💡 DB 검색 후 지식 검색
    workflow.add_edge("retriever", "interpreter")  # 💡 지식 가지고 해석 노드로!
    workflow.add_edge("interpreter", END)

    return workflow.compile()