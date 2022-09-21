import json
import logging
import traceback
from typing import Union

from starlette import status
from starlette.exceptions import HTTPException

from rowantree.auth.sdk import RegisterUserRequest, UserBase
from rowantree.auth.service.controllers.register import RegisterController
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

register_handler: RegisterController = RegisterController(auth_service=auth_service)


def handler(event, context):
    logging.info(event)
    logging.info(context)

    try:
        api_gw_event = ApiGatewayEvent.parse_obj(event)
        request: RegisterUserRequest = RegisterUserRequest.parse_obj(parse_form_data(event=api_gw_event))
        response: UserBase = register_handler.execute(request=request)
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
