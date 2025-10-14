from rest_framework import status

from core.exceptions import BaseAPIException


class ActivityAlreadyActivatedException(BaseAPIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Activity is already activated"
    default_code = "activity_is_already_activated"


class FailureIsNotStartedException(BaseAPIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Failure is not started"
    default_code = "failure_is_not_started"


class ActivityFailureException(BaseAPIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "All activities finished"
    default_code = "all_activities_finished"


class AnalyticsDoesNotExistException(BaseAPIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Analytics does not exist"
    default_code = "analytics_does_not_exist"


class SupervisionIsNotFinishedException(BaseAPIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Last supervision is not finished"
    default_code = "last_supervision_is_not_finished"
