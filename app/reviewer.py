from langchain.agents import create_agent
from langchain_ollama import ChatOllama
from researcher import run_research

llm = ChatOllama(
    model="llama3.2:3b",
    temperature=0,
)

reviewer = create_agent(
    model=llm,
    tools=[],
    system_prompt="""
        You are a strict documentation fact checker.

        Your only job is to determine whether the researcher's claims are
        explicitly supported by the provided documentation.

        Do NOT use your own knowledge.

        Do NOT infer or assume information.

        A claim is supported ONLY if the documentation directly states it
        or clearly states the same fact.

        For example, if the documentation says "graph API", that does NOT
        support the claim "knowledge graph".

        If every claim is explicitly supported, return PASS.

        If even one claim is not explicitly supported, return FAIL and
        identify the unsupported claim.

        Be strict rather than generous.
        Do not use outside knowledge when reviewing.
        """
)


def review_answer(answer, context):
    prompt = f"""
    Review the researcher's answer against the provided documentation.

    Documentation:
    {context}

    Researcher's answer:
    {answer}

    Check every factual claim in the answer.

    Return PASS if every claim is supported by the documentation.

    If any claim is unsupported, return FAIL and briefly explain
    which claim is not supported.

    Do not use outside knowledge.
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

    return result["messages"][-1].content

if __name__ == "__main__":
    question = input("Ask a question: ")

    answer, context = run_research(question)

    review = review_answer(answer, context)

    print("\n--- Researcher Answer ---")
    print(answer)

    print("\n--- Reviewer ---")
    print(review)