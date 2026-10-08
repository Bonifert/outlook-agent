from langchain_core.messages import SystemMessage, HumanMessage
from nodes.common import format_email, classifier_llm
from prompts import CLASSIFY_INFO_REQUEST_SYSTEM_PROMPT
from schemas import InfoRequestDecision
from state import AgentState, Email, Person
import asyncio

def classify_meetings_node(state: AgentState) -> dict:
    """This function classifies the meeting invite related emails"""
    meeting_conversation_ids: set[str] = {e["conversation_id"] for e in state["emails"] if e["meeting"] is not None}
    updated = []
    for email in state["emails"]:
        if email["conversation_id"] in meeting_conversation_ids:
            updated.append({
                **email,
                "categories": [*email["categories"], "meeting"]
            })
        else:
            updated.append(email)
    return {"emails": updated}

async def classify_with_llm_node(state: AgentState) -> dict:
    """This function classifies the info_request and other type related emails"""
    info_requests_results = await asyncio.gather(*(_classify_info_request_from_email(classifier_llm, e, state["me"]) for e in state["emails"]))
    updated = []
    for email, info_request_result in zip(state["emails"], info_requests_results):
        print(f"For email {email["id"]}(email id) info_request flag is: {info_request_result.is_info_request} because: {info_request_result.reason}")
        if info_request_result.is_info_request:
            updated.append({
                **email,
                "categories": [*email["categories"], "info_request"]
            })
        else:
            if len(email["categories"]) == 0:
                updated.append({
                    **email,
                    "categories": ["other"]
                })
            else:
                updated.append(email)
    return {"emails": updated}


async def _classify_info_request_from_email(llm, email: Email, me: Person) -> InfoRequestDecision:
    messages = [
        SystemMessage(CLASSIFY_INFO_REQUEST_SYSTEM_PROMPT.format(owner_name=me["name"], owner_email=me["email"])),
        HumanMessage(format_email(email))
    ]
    return await llm.ainvoke(messages)
