import json
import logging
import traceback
from typing import Union

from fastapi.security import OAuth2PasswordRequestForm
from starlette import status
from starlette.exceptions import HTTPException

from rowantree.auth.sdk import AuthenticateUserRequest, Token
from rowantree.auth.service.controllers.token import TokenController
from rowantree.auth.service.services.auth import AuthService
from rowantree.auth.service.services.db.dao import DBDAO
from rowantree.auth.service.services.db.utils import WrappedConnectionPool
from src.contracts.dtos.api_gateway_event import ApiGatewayEvent
from src.contracts.dtos.lambda_response import LambdaResponse
from src.utils.form import parse_form_data

logging.basicConfig(level=logging.INFO)

# Creating database connection pool, and DAO
wrapped_cnxpool: WrappedConnectionPool = WrappedConnectionPool()
dao: DBDAO = DBDAO(cnxpool=wrapped_cnxpool.cnxpool)
auth_service: AuthService = AuthService(dao=dao)

token_controller: TokenController = TokenController(auth_service=auth_service)


def handler(event, context):
    logging.info(event)
    logging.info(context)

    try:
        api_gw_event = ApiGatewayEvent.parse_obj(event)
        auth_request: AuthenticateUserRequest = AuthenticateUserRequest.parse_obj(parse_form_data(event=api_gw_event))
        request: OAuth2PasswordRequestForm = OAuth2PasswordRequestForm(
            username=auth_request.username, password=auth_request.password, scope="", grant_type="password"
        )
        response: Token = token_controller.execute(request=request)
        return LambdaResponse(status_code=status.HTTP_200_OK, body=response.json(by_alias=True)).dict(by_alias=True)
    except HTTPException as error:
        message_dict: dict[str, Union[dict, str]] = {
            "statusCode": error.status_code,
            "traceback": traceback.format_exc(),
            "error": str(error),
            "detail": error.detail,
        }
        message: str = json.dumps(message_dict)
        logging.error(message)
        return LambdaResponse(status_code=error.status_code, body=json.dumps({"detail": error.detail})).dict(
            by_alias=True
        )
    except Exception as error:
        message_dict: dict[str, Union[dict, str]] = {
            "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR,
            "traceback": traceback.format_exc(),
            "error": str(error),
        }
        message: str = json.dumps(message_dict)
        logging.error(message)
        return LambdaResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, body=json.dumps({"detail": "Internal Server Error"})
        ).dict(by_alias=True)
