from typing import Optional, Union

from rowantree.contracts import BaseModel
from src.contracts.dtos.header_type import HeaderType


class ApiGatewayEvent(BaseModel):
    body: Optional[str]
    headers: dict[Union[HeaderType, str], str]
    path_parameters: dict[str, str]
