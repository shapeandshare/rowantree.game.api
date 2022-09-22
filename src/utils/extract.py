from starlette import status
from starlette.exceptions import HTTPException

from rowantree.auth.sdk import TokenClaims, get_claims
from src.contracts.dtos.header_type import HeaderType


def extract_claims(headers: dict) -> TokenClaims:
    if HeaderType.AUTHORIZATION in headers:
        header_value: str = headers[HeaderType.AUTHORIZATION]
        token_str = header_value.replace("Bearer ", "")
        return get_claims(token=token_str)
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing authorization header")


def demand_key(key: str, parameters: dict[str, str]) -> str:
    if key in parameters:
        return parameters[key]
    raise Exception("Missing Key")
