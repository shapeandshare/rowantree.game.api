import json
import logging
import traceback
from typing import Union

from starlette import status
from starlette.exceptions import HTTPException

from rowantree.game.service.controllers.world_get import WorldStatusGetController
from rowantree.game.service.sdk import WorldStatus
from rowantree.game.service.services.db.dao import DBDAO
from rowantree.game.service.services.db.utils import WrappedConnectionPool
from src.contracts.dtos.lambda_response import LambdaResponse
from src.utils.extract import demand_is_admin, demand_is_enabled, preprocess

logging.basicConfig(level=logging.INFO)

# Creating database connection pool, and DAO
wrapped_cnxpool: WrappedConnectionPool = WrappedConnectionPool()
dao: DBDAO = DBDAO(cnxpool=wrapped_cnxpool.cnxpool)

world_status_get_controller = WorldStatusGetController(dao=dao)


def handler(event, context) -> dict:
    logging.error(event)
    logging.error(context)

    try:
        # Get AWS event and request claims
        api_gw_event, token_claims = preprocess(event=event)

        # Authorize the request
        demand_is_enabled(token_claims=token_claims)
        demand_is_admin(token_claims=token_claims)

        # Execute the request
        response: WorldStatus = world_status_get_controller.execute()

        # Response
        return LambdaResponse(status_code=status.HTTP_201_CREATED, body=response.json(by_alias=True)).dict(
            by_alias=True
        )
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
