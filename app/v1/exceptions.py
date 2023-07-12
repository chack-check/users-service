class IncorrectEmail(Exception):
    ...


class PasswordsNotMatch(Exception):
    ...


class UserWithThisEmailAlreadyExists(Exception):
    ...


class UserWithThisUsernameAlreadyExists(Exception):
    ...


class UserWithThisPhoneAlreadyExists(Exception):
    ...
