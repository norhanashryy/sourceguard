from langchain.agents import create_agent
from langchain_ollama import ChatOllama
from retriever import search_docs
from langchain.tools import tool
import json

llm = ChatOllama(
    model="llama3.2:3b",
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
        You are a professional research assistant.

        Answer questions using only information retrieved from the
        knowledge base.

        Always use the search_knowledge_base tool before answering.

        If the retrieved information does not support an answer,
        say that the information is not supported by the documentation.

        Include the source URL when answering.
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

    answer, context = run_research(question)

    print("\n--- Researcher Answer ---")
    print(answer)

    print("\n--- Retrieved Documentation ---")
    print(context)