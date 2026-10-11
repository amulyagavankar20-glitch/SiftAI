import os

from dotenv import load_dotenv

from agent import build_research_agent
from callbacks.research_stream import ResearchStreamHandler

load_dotenv()


def main() -> None:
    if not os.getenv("GROQ_API_KEY"):
        raise RuntimeError("GROQ_API_KEY must be set in .env or the environment.")

    query = input("Research question: ").strip()
    if not query:
        raise ValueError("A research question is required.")

    executor = build_research_agent(
        model_name=os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
    )
    result = executor.invoke(
        {"input": query, "chat_history": []},
        config={"callbacks": [ResearchStreamHandler()]},
    )
    print("\n" + result.get("output", "No output generated."))


if __name__ == "__main__":
    main()
