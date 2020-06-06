from django.http import JsonResponse

ERROR_RESOURCE_NOT_FOUND = JsonResponse({"status": "ERROR_RESOURCE_NOT_FOUND", "message": "Could not find the requested resource"}, status="404")
ERROR_INVALID_AUTH = JsonResponse({"status": "ERROR_INVALID_AUTH", "message": "Your authentication credentials are invalid"}, status="401")
ERROR_NOT_AUTHORIZED = JsonResponse({"status": "ERROR_NOT_AUTHORIZED", "message": "You are not authorized to access this resource"}, status="403")
ERROR_MISSING_SECRET = JsonResponse({"status": "ERROR_MISSING_SECRET", "message": "Request must include your secret key"}, status="401")
ERROR_INVALID_SUPERUSER_AUTH = JsonResponse({"status": "ERROR_INVALID_SUPERUSER_AUTH", "message": "Invalid superuser username or password"}, status="401")
ERROR_BAD_SUPERUSER_LOGIN_REQUEST = JsonResponse({"status": "ERROR_BAD_SUPERUSER_LOGIN_REQUEST", "message": "Request must include username and password fields"}, status="400")
ERROR_INVALID_HOST_AUTH = JsonResponse({"status": "ERROR_INVALID_HOST_AUTH", "message": "Invalid host username or password"}, status="401")
ERROR_BAD_HOST_LOGIN_REQUEST = JsonResponse({"status": "ERROR_BAD_HOST_LOGIN_REQUEST", "message": "Request must include username and password fields"}, status="400")

def ERROR_BAD_PUT_DATA(errors={}):
    return JsonResponse({"status": "ERROR_BAD_PUT_DATA", "message": "Invalid PUT input data", "errors": errors}, status="400")
def ERROR_BAD_POST_DATA(errors={}):
    return JsonResponse({"status": "ERROR_BAD_POST_DATA", "message": "Invalid POST input data", "errors": errors}, status="400")
def ERROR_BAD_DELETE_DATA(errors={}):
    return JsonResponse({"status": "ERROR_BAD_DELETE_DATA", "message": "Invalid DELETE input data", "errors": errors}, status="400")