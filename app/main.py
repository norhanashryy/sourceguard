from typing import TypedDict
from langgraph.graph import StateGraph, END
from researcher import run_research, revise_answer
from reviewer import reviewer
import json
import time

class ResearchState(TypedDict):
    question: str
    answer: str
    original_answer: str
    documentation: str
    chunks:list
    review: str
    revised: bool
    


def research(state: ResearchState):
    answer, documentation, chunks = run_research(state["question"])

    return {
        "answer": answer,
        "original_answer": answer,
        "documentation": documentation,
        "chunks": chunks,
    }


def review(state: ResearchState):
    prompt = f"""
    Question:
    {state["question"]}

    Documentation:
    {state["documentation"]}

    Researcher's answer:
    {state["answer"]}

    Review the answer against the documentation.

    Return PASS if every claim is supported.

    If any claim is unsupported, return FAIL and briefly explain
    which claim is unsupported.
    """

    result = reviewer.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": prompt,
                }
            ]
        }
    )

    return {
        "review": result["messages"][-1].content
    }


def revise(state: ResearchState):
    answer = revise_answer(
        state["question"],
        state["answer"],
        state["review"],
        state["documentation"],
    )

    return {
        "answer": answer,
        "revised": True,
    }

def route_after_review(state: ResearchState):
    if state["review"].startswith("PASS"):
        return "final"

    if state["revised"]:
        return "final"

    return "revise"


graph = StateGraph(ResearchState)

graph.add_node("research", research)
graph.add_node("review", review)
graph.add_node("revise", revise)

graph.set_entry_point("research")

graph.add_edge("research", "review")

graph.add_conditional_edges(
    "review",
    route_after_review,
    {
        "final": END,
        "revise": "revise",
    },
)

graph.add_edge("revise", "review")
app = graph.compile()


if __name__ == "__main__":
    question = input("Ask a question: ")
    start_time = time.time()
    result = app.invoke(
        {
            "question": question,
            "answer": "",
            "original_answer": "",
            "documentation": "",
            "chunks": [],
            "review": "",
            "revised": False,
        }
    )

    latency = time.time() - start_time

    print("\n--- Researcher Answer ---")
    print(result["answer"])

    print("\n--- Retrieved Documentation ---")
    print(result["documentation"])

    print("\n--- Reviewer Verdict ---")
    print(result["review"])

    if result["revised"]:
        print("\n--- Revised / Final Answer ---")
        print(result["answer"])

    log = {
        "test_id": 1,
        "input": question,
        "agent_1_output": result["original_answer"],
        "retrieved_chunks": [result["documentation"]],
        "agent_2_output": result["review"],
        "expected_grounded": True,
        "actual_grounded": result["review"].startswith("PASS"),
        "expected_refusal": False,
        "actual_refusal": "not supported" in result["answer"].lower(),
        "latency_seconds": round(latency, 2),
        "error": None
    }

    print("\n--- Evaluation Log ---")
    print(json.dumps(log, indent=2))
