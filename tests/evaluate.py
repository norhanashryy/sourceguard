import json
import time
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).resolve().parent.parent))
from app.main import app


QUESTIONS_FILE = Path("tests/questions.json")
LOG_FILE = Path("logs/evaluations_logs.jsonl")


def run_evaluation():
    with open(QUESTIONS_FILE, "r", encoding="utf-8") as f:
        questions = json.load(f)

    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

    for test in questions:
        test_id = test["test_id"]
        question = test["question"]

        print(f"\nRunning test {test_id}/{len(questions)}: {question}")

        start_time = time.time()

        try:
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

            actual_refusal = (
                result["answer"]
                == "The retrieved documentation does not provide enough information to answer this question."
            )

            actual_grounded = (
                result["review"].startswith("PASS")
                and not actual_refusal
            )

            log = {
                "test_id": test_id,
                "input": question,
                "agent_1_output": result["original_answer"],
                "retrieved_chunks": result["chunks"],
                "agent_2_output": result["review"],
                "actual_grounded": actual_grounded,
                "actual_refusal": actual_refusal,
                "revision_performed": result["revised"],
                "final_answer": result["answer"],
                "latency_seconds": round(latency, 2),
                "error": None,
            }

        except Exception as e:
            latency = time.time() - start_time

            log = {
                "test_id": test_id,
                "input": question,
                "agent_1_output": None,
                "retrieved_chunks": [],
                "agent_2_output": None,
                "actual_grounded": False,
                "actual_refusal": False,
                "revision_performed": False,
                "final_answer": None,
                "latency_seconds": round(latency, 2),
                "error": str(e),
            }

        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(log, ensure_ascii=False) + "\n")

        print(
            f"  Grounded: {log['actual_grounded']} | "
            f"Refused: {log['actual_refusal']} | "
            f"Revised: {log['revision_performed']} | "
            f"Latency: {log['latency_seconds']}s"
        )


if __name__ == "__main__":
    run_evaluation()