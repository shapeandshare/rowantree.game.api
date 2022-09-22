from typing import Optional

from rowantree.contracts import BaseModel


class LambdaResponse(BaseModel):
    status_code: int
    body: Optional[str]
    headers: dict[str, str]
