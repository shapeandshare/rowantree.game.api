import json
import logging
import traceback
from typing import Union

from starlette import status
from starlette.exceptions import HTTPException

from rowantree.contracts import UserFeatureState
from rowantree.game.service.controllers.user_transport import UserTransportController
from rowantree.game.service.sdk import UserTransportRequest
from rowantree.game.service.services.db.dao import DBDAO
from rowantree.game.service.services.db.utils import WrappedConnectionPool
from src.contracts.dtos.lambda_response import LambdaResponse
from src.utils.extract import demand_is_enabled, demand_is_subject_or_admin, demand_key, marshall_body, preprocess

# https://docs.aws.amazon.com/lambda/latest/dg/python-logging.html
logging.getLogger().setLevel(logging.INFO)

# Creating database connection pool, and DAO
wrapped_cnxpool: WrappedConnectionPool = WrappedConnectionPool()
dao: DBDAO = DBDAO(cnxpool=wrapped_cnxpool.cnxpool)

user_transport_controller = UserTransportController(dao=dao)


def handler(event, context) -> dict:
    logging.info(event)
    logging.info(context)

    try:
        # Get AWS event and request claims
        api_gw_event, token_claims = preprocess(event=event)

        # Get the request from the body
        request: UserTransportRequest = marshall_body(body=api_gw_event.body, return_type=UserTransportRequest)

        # Extract the guid from the request url
        user_guid: str = demand_key(key="user_guid", parameters=api_gw_event.path_parameters)

        # Authorize the request
        demand_is_enabled(token_claims=token_claims)
        demand_is_subject_or_admin(user_guid=user_guid, token_claims=token_claims)

        # Execute the request
        response: UserFeatureState = user_transport_controller.execute(user_guid=user_guid, request=request)

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
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            body=json.dumps({"detail": "Internal Server Error"}),
        ).dict(by_alias=True)
