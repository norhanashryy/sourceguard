from langchain.agents import create_agent
from langchain_ollama import ChatOllama
from retriever import search_docs
from langchain.tools import tool

llm = ChatOllama(
    model="llama3.2:3b",
    temperature=0,
)

@tool
def search_knowledge_base(question):
    """Search the knowledge base for information relevant to the question"""
    documents = search_docs(question, top_k=5)

    context = "\n\n".join(
        f"Source: {doc.payload.get('source')}\n"
        f"Content: {doc.payload.get('text')}"
        for doc in documents
    )
    return context


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

if __name__ == "__main__":
    question = input("Ask a question: ")

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

    for message in result["messages"]:
        print("\n---")
        print(type(message).__name__)
        print(message.content)