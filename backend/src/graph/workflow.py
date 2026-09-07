'''
This file defines the DAG: Directed Acyclic Graph that orchestrates the vidoe compliance ausdit process.
It connects the nodes from the stategrapf from langgraph

START -> index_video_node -> audit_content_node -> END
'''


from langgraph.graph import StateGraph, END
from backend.src.graph.state import VideoAuditState
from backend.src.graph.nodes import index_video_node, audit_content_node


def create_graph():
    '''
    Constructs and compiles the langgraph workflow
    Returns:
    Compiled Graph : runnable graph object for execution
    '''

    # Initializing the state graph
    workflow = StateGraph(VideoAuditState)

    # Adding the nodes to the graph
    workflow.add_node("indexer", index_video_node)
    workflow.add_node("auditor", audit_content_node)

    # Defining the entry pointer : indexer
    workflow.set_entry_point("indexer")

    # Defining the edges
    workflow.add_edge("indexer", "auditor")
    workflow.add_edge("auditor", END)

    # Compiling the graph
    app = workflow.compile()
    return app