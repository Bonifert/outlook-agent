from langchain_core.messages import SystemMessage, HumanMessage
from nodes.common import base_llm, format_email
from prompts import SUMMARIZE_EMAIL_SYSTEM_PROMPT
from state import AgentState, Email, Person, EmailSummary
import asyncio

async def summary_node(state: AgentState) -> dict:
    summaries = await asyncio.gather(*(_summarize_email(base_llm, e, state["me"]) for e in state["emails"] if "other" in e["categories"]))
    return {"summaries": summaries}

async def _summarize_email(llm, email: Email, me: Person) -> EmailSummary:
    messages = [
        SystemMessage(SUMMARIZE_EMAIL_SYSTEM_PROMPT.format(owner_name=me["name"], owner_email=me["email"])),
        HumanMessage(format_email(email))
    ]
    llm_response = await llm.ainvoke(messages)
    return EmailSummary(summary=llm_response.text, sender=email["sender"], subject=email["subject"])

