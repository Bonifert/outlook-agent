import httpx
from state import Email, Meeting, Person, Attendee, EmailStatus


def _create_person(email_address: dict) -> Person:
    return Person(
        name=email_address["emailAddress"]["name"],
        email=email_address["emailAddress"]["address"]
    )

def _create_attendee(attendee: dict) -> Attendee:
    return Attendee(
        name=attendee["emailAddress"]["name"],
        email=attendee["emailAddress"]["address"],
        type=attendee["type"]
    )

def _convert(email: dict, status: EmailStatus) -> Email:
    meeting = None
    if email.get("meetingMessageType") and email["meetingMessageType"] == "meetingRequest":
        meeting_info = email["meetingInfo"]
        meeting = Meeting(
            start=meeting_info["start"]["dateTime"],
            end=meeting_info["end"]["dateTime"],
            location=meeting_info["location"]["displayName"],
            organizer=_create_person(meeting_info["organizer"]),
            attendees=[_create_attendee(a) for a in meeting_info["attendees"]]
        )
    converted = Email(
        id=email["id"],
        subject=email["subject"],
        body=email["body"]["content"],
        sender=_create_person(email["from"]),
        received=email["receivedDateTime"],
        meeting=meeting,
        categories=[],
        status=status,
        conversation_id=email["conversationId"],
        to=[_create_person(p) for p in email["toRecipients"]],
        cc=[_create_person(p) for p in email["ccRecipients"]]
    )
    return converted


class OutlookClient:
    """This is a wrapper around the mocked outlook API"""

    def __init__(self, base_url: str = "http://127.0.0.1:8000"):
        self.http = httpx.AsyncClient(
            base_url=base_url,
            headers={"Prefer": 'outlook.body-content-type="text"'}
        )
        self.INBOX_NAME = "inbox"

    async def get_last_emails_from_inbox(self, top: int) -> list[Email]:
        response = await self.http.get(f"/v1.0/me/mailFolders/{self.INBOX_NAME}/messages",params={
            "$top": top,
            "$orderby": "receivedDateTime desc",
            "$select": "subject,body,from,receivedDateTime,toRecipients,ccRecipients,meetingMessageType,meetingInfo,conversationId"
        })
        response.raise_for_status()
        data = response.json()["value"]
        return [_convert(e, "Inbox") for e in data]

    async def get_me(self) -> Person:
        response = await self.http.get(f"/v1.0/me")
        response.raise_for_status()
        data = response.json()
        return Person(name=data["displayName"], email=data["mail"])


    async def reset_mock_db(self) -> None:
        response = await self.http.post("/mock/reset")
        response.raise_for_status()

    async def get_folders(self) -> dict[EmailStatus, str]:
        response = await self.http.get("/v1.0/me/mailFolders")
        response.raise_for_status()
        data = response.json()["value"]
        return {folder["displayName"]: folder["id"] for folder in data}

    async def move_email_to_folder(self, email_id: str, destination_id: str) -> str:
        response = await self.http.post(f"/v1.0/me/messages/{email_id}/move", json={"destinationId": destination_id})
        response.raise_for_status()
        data = response.json()
        return data["id"]

    async def close(self):
        await self.http.aclose()
