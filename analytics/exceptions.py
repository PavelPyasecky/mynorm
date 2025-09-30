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


class AnalyticsDoesNotExistException(exceptions.APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Analytics does not exist"


class SupervisionIsNotFinishedException(exceptions.APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Last supervision is not finished"
