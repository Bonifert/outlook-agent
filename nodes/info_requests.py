from langchain_core.messages import SystemMessage, HumanMessage
from nodes.common import format_email, info_request_extractor_llm
from prompts import EXTRACT_INFO_REQUESTS_SYSTEM_PROMPT
from state import AgentState, Email, Person, InfoRequest
import asyncio

# TODO: we can lose emails here, if the classify node classifies an email as info_request, but here the llm thinks it doesn't contain info_request.
async def info_request_node(state: AgentState) -> dict:
    info_requests_summaries = await asyncio.gather(*(_get_info_requests_from_email(info_request_extractor_llm, e, state["me"]) for e in state["emails"] if "info_request" in e["categories"]))
    info_requests_summaries = [e for e in info_requests_summaries if e["items"]]
    return {"info_requests": info_requests_summaries}

async def _get_info_requests_from_email(llm, email: Email, me: Person) -> InfoRequest:
    messages = [
        SystemMessage(EXTRACT_INFO_REQUESTS_SYSTEM_PROMPT.format(owner_name=me["name"], owner_email=me["email"])),
        HumanMessage(format_email(email))
    ]
    llm_response = await llm.ainvoke(messages)
    return InfoRequest(requester=email["sender"], subject=email["subject"], items=llm_response.items, deadline=llm_response.deadline or None)