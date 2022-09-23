from typing import Optional

from rowantree.contracts import BaseModel


class ApiGatewayEvent(BaseModel):
    body: Optional[str]
    headers: dict[str, str]
    path_parameters: Optional[dict[str, str]]
