from outlook_client import OutlookClient
from state import AgentState, Email, EmailStatus
from nodes.common import client
import asyncio

async def get_outlook_data_node(_state: AgentState) -> dict:
    """This function fetches the Outlook folders and the last 15 email from the Inbox"""
    folders, emails, user = await asyncio.gather(client.get_folders(), client.get_last_emails_from_inbox(15), client.get_me())
    return {"folders": folders, "emails": emails, "me": user}

async def move_emails_to_processing_node(state: AgentState) -> dict:
    """This function moves the emails from the Inbox folder to the Processing folder in Outlook"""
    return await _move_emails(client, state["emails"], state["folders"]["Processing"], "Processing")

async def move_emails_to_done_node(state: AgentState) -> dict:
    """This function moves the emails from the Processing folder to the Done folder in Outlook"""
    return await _move_emails(client, state["emails"], state["folders"]["Done"], "Done")

async def _move_emails(email_client: OutlookClient, emails: list[Email], new_folder_id: str, status: EmailStatus) -> dict:
    new_ids = await asyncio.gather(*(email_client.move_email_to_folder(email["id"], new_folder_id) for email in emails))
    moved = []
    for email, new_id in zip(emails, new_ids):
        moved.append({
            **email,
            "id": new_id,
            "status": status
        })
    return {"emails": moved}