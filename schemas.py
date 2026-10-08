from pydantic import BaseModel, Field

class InfoRequestDecision(BaseModel):
    reason: str = Field(
        description="One short sentence explaining the decision, quoting the request if there is one."
    )
    is_info_request: bool = Field(
        description="True if the email asks the mailbox owner for information: an answer, data, an estimate, an opinion or a decision. Requests to perform a task do not count."
    )

class InfoRequestExtraction(BaseModel):
    items: list[str] = Field(
        description="Distinct pieces of information the mailbox owner is asked to provide. Each item must be understandable without reading the email."
    )
    deadline: str | None = Field(
        description="The deadline as written in the email, or null if there is none."
    )