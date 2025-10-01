from rest_framework import exceptions


class BaseAPIException(exceptions.APIException):
    default_detail = NotImplementedError
    default_code = NotImplementedError

    def __init__(self, detail=None, code=None):
        if detail is None:
            detail = self.default_detail
        if code is None:
            code = self.default_code

        self.detail = {
            'detail': detail,
            'code': code
        }