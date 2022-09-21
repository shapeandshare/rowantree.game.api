from rowantree.contracts import BaseModel


class FormResponse(BaseModel):
    content: bytes
    headers: dict[str, str]
