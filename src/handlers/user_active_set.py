import json
import logging
import traceback
from typing import Union

from starlette import status
from starlette.exceptions import HTTPException

from rowantree.game.service.controllers.user_active_set import UserActiveSetController
from rowantree.game.service.sdk import UserActiveGetStatus
from rowantree.game.service.services.db.dao import DBDAO
from rowantree.game.service.services.db.utils import WrappedConnectionPool
from src.contracts.dtos.api_gateway_event import ApiGatewayEvent
from src.contracts.dtos.lambda_response import LambdaResponse

logging.basicConfig(level=logging.INFO)

# Creating database connection pool, and DAO
wrapped_cnxpool: WrappedConnectionPool = WrappedConnectionPool()
dao: DBDAO = DBDAO(cnxpool=wrapped_cnxpool.cnxpool)

user_active_set_controller = UserActiveSetController(dao=dao)


def handler(event, context):
    logging.info(event)
    logging.info(context)

    # TODO: Check auth...
    try:
        api_gw_event = ApiGatewayEvent.parse_obj(event)
        request: UserActiveGetStatus = UserActiveGetStatus.parse_raw(api_gw_event.body)
        # if user_guid != token_claims.sub and not token_claims.admin:
        #     raise HTTPException(
        #         status_code=status.HTTP_401_UNAUTHORIZED,
        #         detail="Could not validate credentials",
        #     )

        # user_active_set_controller.execute(user_guid=user_guid, request=request)

        return LambdaResponse(status_code=status.HTTP_200_OK).dict(by_alias=True)
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
