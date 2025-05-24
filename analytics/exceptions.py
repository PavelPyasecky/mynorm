from rest_framework import exceptions, status


class ActivityAlreadyActivatedException(exceptions.APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Activity is already activated"
