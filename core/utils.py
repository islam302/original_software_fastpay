from rest_framework.views import exception_handler
from rest_framework.renderers import JSONRenderer
from rest_framework.pagination import PageNumberPagination


def custom_exception_handler(exc, context):
    """Format all errors to match {'status': False, 'message': 'Failed reason'}"""
    response = exception_handler(exc, context)

    if response is not None:
        error_msg = list(response.data.values())[0] if isinstance(
            response.data, dict) else str(response.data)
        transaction = None
        if len(response.data.values()) > 1:
            transaction = list(response.data.values())[1] if isinstance(
            response.data, dict) else str(response.data)
        print(response.data)

        if transaction:
            response.data = {
                "status": False,
                "message":  type(error_msg) == list and error_msg[0] or error_msg,
                "transaction_id":  type(transaction) == list and transaction[0] or transaction
            }
        else:
            response.data = {
                "status": False,
                "message": type(error_msg) == list and error_msg[0] or error_msg
            }

    return response


class CustomJSONRenderer(JSONRenderer):
    def render(self, data, accepted_media_type=None, renderer_context=None):
        # If there's already a response structure, return as is
        response = {
            "status": True,
            "message": "Success",
            **data
        }

        if isinstance(data, dict) and "error" in data:
            response["status"] = False
            response["message"] = data.get("error", "Error")

        return super().render(response, accepted_media_type, renderer_context)
    
    
class StandardLimitOffsetPagination(PageNumberPagination):
    page_size = 25
    page_size_query_param = "page_size"
    max_page_size = 100


