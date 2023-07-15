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
