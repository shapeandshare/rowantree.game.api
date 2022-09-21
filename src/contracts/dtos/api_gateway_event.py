from typing import Union

from rowantree.contracts import BaseModel
from src.contracts.dtos.header_type import HeaderType


class ApiGatewayEvent(BaseModel):
    body: str
    headers: dict[Union[HeaderType, str], str]
