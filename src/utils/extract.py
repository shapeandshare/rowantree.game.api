import json
import logging
import traceback
from json import JSONDecodeError
from typing import Any, Tuple, Type, TypeVar, Union

from pydantic import ValidationError
from starlette import status
from starlette.exceptions import HTTPException

from rowantree.auth.sdk import TokenClaims, get_claims
from src.contracts.dtos.api_gateway_event import ApiGatewayEvent


def extract_claims(headers: dict) -> TokenClaims:
    for key in headers.keys():
        if key.lower() == "authorization":
            header_value: str = headers[key]
            token_str = header_value.replace("Bearer ", "")
            return get_claims(token=token_str)
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing authorization header")


def demand_key(key: str, parameters: dict[str, str]) -> str:
    if parameters and key in parameters:
        return parameters[key]
    raise Exception("Missing Key")


def preprocess(event: Any) -> Tuple[ApiGatewayEvent, TokenClaims]:
    try:
        # Marshall the raw inbound event into a known structure
        api_gw_event: ApiGatewayEvent = ApiGatewayEvent.parse_obj(event)

        # Extract the claims of the request (this fails nicely with 401 where expected)
        token_claims: TokenClaims = extract_claims(api_gw_event.headers)
        return api_gw_event, token_claims
    except HTTPException as error:
        raise error from error
    except (ValidationError, JSONDecodeError) as error:
        message_dict: dict[str, Union[dict, str]] = {
            "statusCode": status.HTTP_400_BAD_REQUEST,
            "traceback": traceback.format_exc(),
            "error": str(error),
        }
        message: str = json.dumps(message_dict)
        logging.error(message)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Malformed request")


def demand_is_enabled(token_claims: TokenClaims) -> None:
    if token_claims.disabled:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account not enabled",
        )


def demand_is_admin(token_claims: TokenClaims) -> None:
    # Authorize the request
    demand_is_enabled(token_claims=token_claims)
    if not token_claims.admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Permission denied",
        )


def demand_is_subject_or_admin(user_guid: str, token_claims: TokenClaims) -> None:
    if token_claims.admin:
        return

    if user_guid == token_claims.sub:
        return

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Permission denied",
    )


TBodyType = TypeVar("TBodyType")


def marshall_body(body: str, return_type: Type[TBodyType]) -> TBodyType:
    try:
        # Get the request from the body
        return return_type.parse_raw(body)
    except (ValidationError, JSONDecodeError) as error:
        message_dict: dict[str, Union[dict, str]] = {
            "statusCode": status.HTTP_400_BAD_REQUEST,
            "traceback": traceback.format_exc(),
            "error": str(error),
        }
        message: str = json.dumps(message_dict)
        logging.error(message)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Malformed request")
