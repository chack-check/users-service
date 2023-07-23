class IncorrectEmail(Exception):
    ...


class PasswordsNotMatch(Exception):

    def __init__(self,
                 message: str = 'Passwords do not match'):
        super().__init__(message)


class IncorrectPassword(Exception):

    def __init__(self,
                 message: str = 'Password is incorrect'):
        super().__init__(message)


class UserWithThisEmailAlreadyExists(Exception):

    def __init__(self,
                 message: str = 'User with this email already exists'):
        super().__init__(message)


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
                 message: str = 'You need to specify email or phone'):
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
