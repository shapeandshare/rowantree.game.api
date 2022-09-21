from rowantree.contracts import BaseModel


class LambdaResponse(BaseModel):
    status_code: int
    body: str
