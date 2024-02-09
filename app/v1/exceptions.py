import json
from typing import TypedDict


class ErrorMessages(TypedDict):
    general: str | None
    errors: dict[str, list[str]]


class BaseGraphqlApiException(Exception):

    def __init__(self, errors: ErrorMessages):
        message = json.dumps(errors)
        super().__init__(message)


INCORRECT_EMAIL_ERRORS: ErrorMessages = {
    "general": None,
    "errors": {
        "email": ["Incorrect email"]
    }
}

PASSWORDS_NOT_MATCH_ERRORS: ErrorMessages = {
    "general": None,
    "errors": {
        "password_repeat": ["Passwords do not match"],
    }
}

INCORRECT_PASSWORD_ERRORS: ErrorMessages = {
    "general": None,
    "errors": {
        "password": ["Incorrect password"]
    }
}

USER_WITH_THIS_EMAIL_ALREADY_EXISTS_ERRORS: ErrorMessages = {
    "general": None,
    "errors": {
        "email": ["User with this email already exists"]
    }
}

USER_WITH_THIS_USERNAME_ALREADY_EXISTS_ERRORS: ErrorMessages = {
    "general": None,
    "errors": {
        "username": ["User with this username already exists"]
    }
}


class IncorrectEmail(BaseGraphqlApiException):

    def __init__(self, errors: ErrorMessages = INCORRECT_EMAIL_ERRORS):
        super().__init__(errors)


class PasswordsNotMatch(BaseGraphqlApiException):

    def __init__(self, errors: ErrorMessages = PASSWORDS_NOT_MATCH_ERRORS):
        super().__init__(errors)


class IncorrectPassword(BaseGraphqlApiException):

    def __init__(self, errors: ErrorMessages = INCORRECT_PASSWORD_ERRORS):
        super().__init__(errors)


class UserWithThisEmailAlreadyExists(Exception):

    def __init__(self, errors: ErrorMessages = USER_WITH_THIS_EMAIL_ALREADY_EXISTS_ERRORS):
        super().__init__(errors)


class UserWithThisUsernameAlreadyExists(Exception):

    def __init__(self,
                 message: str = 'User with this username already exists'):
        super().__init__(message)


class UserWithThisPhoneAlreadyExists(Exception):

    def __init__(self,
                 message: str = 'User with this phone already exists'):
        super().__init__(message)


class UserDoesNotExist(Exception):

    def __init__(self,
                 message: str = ('User with this phone or '
                                 'username does not exist')):
        super().__init__(message)


class IncorrectToken(Exception):

    def __init__(self,
                 message: str = 'Incorrect token'):
        super().__init__(message)


class AuthRequired(Exception):

    def __init__(self,
                 message: str = 'Authentication required'):
        super().__init__(message)


class IncorrectVerificationSource(Exception):

    def __init__(self,
                 message: str = ('You need to specify only email'
                                 ' or only phone')):
        super().__init__(message)


class IncorrectVerificationCode(Exception):

    def __init__(self,
                 message: str = 'Incorrect verification code'):
        super().__init__(message)


class VerificationAttemptsExpired(Exception):

    def __init__(self,
                 message: str = ('Verification attempts expired.'
                                 ' Try to resend code')):
        super().__init__(message)


class IncorrectSignature(Exception):

    def __init__(self,
                 message: str = ('Incorrect signature')):
        super().__init__(message)


class AuthenticationEmailOrPhoneRequired(Exception):

    def __init__(self,
                 message: str = ('You need to specify'
                                 ' email or phone')):
        super().__init__(message)


class IncorrectAuthenticationSession(Exception):

    def __init__(self,
                 message: str = ('Incorrect session')):
        super().__init__(message)
