import logging

from requests_toolbelt.multipart import decoder
from starlette import status
from starlette.exceptions import HTTPException

from src.contracts.dtos.api_gateway_event import ApiGatewayEvent
from src.contracts.dtos.form_response import FormResponse
from src.contracts.dtos.header_type import HeaderType


def parse_form_data(event: ApiGatewayEvent) -> dict[str, str]:
    try:
        encoding: str = "utf-8"
        multipart_data = decoder.MultipartDecoder.from_response(
            FormResponse(
                content=bytes(event.body, encoding), headers={"content-type": event.headers[HeaderType.CONTENT_TYPE]}
            )
        )

        form_values: dict[str, str] = {}
        for part in multipart_data.parts:
            entry_name: str = (
                part.headers[b"Content-Disposition"].decode(encoding).split(";")[1].split("=")[1].replace('"', "")
            )
            entry_value: str = part.content.decode(encoding)
            form_values[entry_name] = entry_value

        return form_values
    except Exception as error:
        logging.error(str(error))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unable to parse form data") from error
