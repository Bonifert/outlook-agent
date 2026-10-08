# TODO: I should move these into a LangGraph runtime context (DI)
from langchain_openai import ChatOpenAI

from outlook_client import OutlookClient
from schemas import InfoRequestDecision, InfoRequestExtraction
from state import Person, Email

client = OutlookClient()
base_llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
classifier_llm = base_llm.with_structured_output(InfoRequestDecision)
info_request_extractor_llm = base_llm.with_structured_output(InfoRequestExtraction)

def _format_person(person: Person) -> str:
    return f"{person['name']} <{person['email']}>"


def _format_people(people: list[Person]) -> str:
    return ", ".join(_format_person(p) for p in people) or "-"


def format_email(email: Email) -> str:
    lines = [
        f"From: {_format_person(email['sender'])}",
        f"To: {_format_people(email['to'])}",
        f"Cc: {_format_people(email['cc'])}",
        f"Received: {email['received']}",
        f"Subject: {email['subject']}",
    ]

    meeting = email["meeting"]
    if meeting is None:
        lines.append("Meeting invitation: no")
    else:
        attendees = ", ".join(
            f"{_format_person(a)} ({a['type']})" for a in meeting["attendees"]
        )
        lines += [
            "Meeting invitation: yes",
            f"Meeting time: {meeting['start']} - {meeting['end']} (UTC)",
            f"Location: {meeting['location']}",
            f"Organizer: {_format_person(meeting['organizer'])}",
            f"Attendees: {attendees}",
        ]

    lines += ["", email["body"]]
    return "\n".join(lines)