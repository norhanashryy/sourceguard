from langchain.agents import create_agent
from langchain_ollama import ChatOllama
from app.retriever import search_docs
from langchain.tools import tool
import json

llm = ChatOllama(
    model="qwen2.5:7b",
    temperature=0,
)

@tool
def search_knowledge_base(question):
    """Search the knowledge base for information relevant to the question"""
    documents = search_docs(question, top_k=5)

    chunks = [
        {
            "source": doc.payload.get("source"),
            "text": doc.payload.get("text"),
        }
        for doc in documents
    ]

    return json.dumps(chunks)


researcher = create_agent(
    model=llm,
    tools=[search_knowledge_base],
    system_prompt="""
        You are a documentation research agent.

        Your job is to answer the user's question using ONLY the text returned
        by the search_knowledge_base tool.

        You MUST call search_knowledge_base before answering.

        GROUNDING RULES:
        1. Every factual statement in your answer must be directly supported by
        the retrieved documentation.
        2. Do not use your pretrained knowledge.
        3. Do not infer relationships that are not explicitly stated.
        4. Do not reverse relationships. For example, if the documentation says
        "LangChain agents are built on top of LangGraph", do not conclude that
        "LangGraph is built on top of LangChain".
        5. Prefer exact statements from the documentation over general explanations.
        6. If the documentation only provides partial information, answer only
        what is explicitly supported.
        7. If the documentation does not provide enough information, say:
        "The retrieved documentation does not provide enough information to answer this question."
        8. Keep answers concise.
        9. Include the source URL for the supporting information.

        Do not add information from outside the retrieved documentation.
        """
)

def run_research(question):
    result = researcher.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": question,
                }
            ]
        }
    )

    answer = result["messages"][-1].content

    chunks = []
    for message in result["messages"]:
        if type(message).__name__ == "ToolMessage":
            chunks = json.loads(message.content)

    context = "\n\n".join(
        f"Source: {chunk['source']}\n"
        f"Content: {chunk['text']}"
        for chunk in chunks
    )

    return answer, context, chunks


def revise_answer(question, answer, review, context):
    prompt = f"""
You are a strict factual editor.

Your job is to fix the researcher's answer using ONLY the retrieved documentation.

USER QUESTION:
{question}

RETRIEVED DOCUMENTATION:
{context}

ORIGINAL ANSWER:
{answer}

REVIEWER FEEDBACK:
{review}

The reviewer found an unsupported claim.

Rewrite the answer from scratch.

STRICT RULES:
1. Use ONLY facts explicitly stated in the retrieved documentation.
2. Remove the unsupported claim identified by the reviewer.
3. Do not add replacement facts from your own knowledge.
4. Do not infer facts.
5. Do not explain why a claim is unsupported.
6. If the documentation does not contain enough information to answer the question, say:
   "The retrieved documentation does not provide enough information to answer this question."
7. Keep the answer concise.
8. Return ONLY the final answer.
"""

    response = llm.invoke(prompt)

    return response.content

if __name__ == "__main__":
    question = input("Ask a question: ")

    answer, context, chunks = run_research(question)

    print("\n--- Researcher Answer ---")
    print(answer)

    print("\n--- Retrieved Documentation ---")
    print(context)