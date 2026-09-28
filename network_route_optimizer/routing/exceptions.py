from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework.views import exception_handler


class NoRouteFound(APIException):
    status_code = status.HTTP_404_NOT_FOUND

    def __init__(self, source: str, destination: str):
        super().__init__(f"No path exists between {source} and {destination}")


def api_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is not None:
        response.data = {"error": response.data.get("detail", response.data)}
    return response
