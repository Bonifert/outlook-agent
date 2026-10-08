from typing import TypedDict, Optional, Literal

class Person(TypedDict):
    name: str
    email: str

class Attendee(Person):
    type: Literal["required", "optional"]

class Meeting(TypedDict):
    start: str
    end: str
    location: str
    organizer: Person
    attendees: list[Attendee]

class InfoRequest(TypedDict):
    requester: Person
    subject: str
    items: list[str]
    deadline: str | None


Category = Literal["meeting", "info_request", "other"]
EmailStatus = Literal["Inbox", "Processing", "Done"]

class Email(TypedDict):
    id: str
    subject: str
    body: str
    sender: Person
    received: str
    meeting: Optional[Meeting]
    categories: list[Category]
    status: EmailStatus
    conversation_id: str
    to: list[Person]
    cc: list[Person]

class EmailSummary(TypedDict):
    sender: Person
    subject: str
    summary: str

class AgentState(TypedDict):
    me: Person
    folders: dict[str, str]
    emails: list[Email]
    agendas: list[str]
    info_requests: list[InfoRequest]
    summaries: list[EmailSummary]
    report: str

