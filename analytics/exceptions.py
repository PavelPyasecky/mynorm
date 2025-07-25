from rest_framework import exceptions, status


class ActivityAlreadyActivatedException(exceptions.APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Activity is already activated"


class FailureIsNotStartedException(exceptions.APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Failure is not started"


class ActivityFailureException(exceptions.APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "All activities finished"
