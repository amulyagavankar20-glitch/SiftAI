from langchain_classic.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_groq import ChatGroq

from tools.evaluation import evaluate_answer, finalize_report
from tools.extraction import check_contradictions, extract_claims
from tools.retrieval import fetch_page, parse_pdf
from tools.search import web_search

DEFAULT_GROQ_MODEL = "openai/gpt-oss-120b"

SYSTEM_RESEARCH_PROMPT = """You are an autonomous, evidence-first research agent.
Decompose the question into sub-questions, search iteratively, and inspect sources
before making empirical claims. Record every claim with extract_claims, including
an exact quote, URL, date, methodology, dataset, limitations, and confidence.
Check contradictions and call evaluate_answer before finalizing. If it says revise,
perform targeted follow-up searches. Use finalize_report only after evaluation passes.
Never invent metrics, citations, or source text. Keep tool requests concise: use
at most five search results and summarize only the evidence needed for the report.
For normal requests, use no more than three searches and fetch only the most
relevant sources. Prefer a concise, useful answer over exhaustive coverage.
Do not repeat searches unless evaluation identifies a specific missing requirement.
Stop after the configured iteration limit."""


def build_research_agent(
    model_name: str = DEFAULT_GROQ_MODEL,
    temperature: float = 0.0,
    max_iterations: int = 8,
    max_execution_time: int = 180,
) -> AgentExecutor:
    tools = [
        web_search,
        fetch_page,
        parse_pdf,
        extract_claims,
        check_contradictions,
        evaluate_answer,
        finalize_report,
    ]
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", SYSTEM_RESEARCH_PROMPT),
            MessagesPlaceholder("chat_history", optional=True),
            ("human", "{input}"),
            MessagesPlaceholder("agent_scratchpad"),
        ]
    )
    llm = ChatGroq(model=model_name, temperature=temperature)
    agent = create_tool_calling_agent(llm, tools, prompt)
    return AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        max_iterations=max_iterations,
        max_execution_time=max_execution_time,
        handle_parsing_errors=True,
        return_intermediate_steps=True,
    )
