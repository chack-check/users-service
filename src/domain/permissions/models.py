class PermissionCategory:
    _code: str
    _name: str

    def __init__(self, code: str, name: str) -> None:
        self._code = code
        self._name = name

    def get_code(self) -> str:
        return self._code

    def get_name(self) -> str:
        return self._name

    def __repr__(self) -> str:
        data = {
            "code": self._code,
            "name": self._name,
        }
        return f"{self.__class__.__name__}{data}"


class Permission:
    _code: str
    _name: str
    _category: PermissionCategory | None

    def __init__(self, code: str, name: str, category: PermissionCategory | None = None):
        self._code = code
        self._name = name
        self._category = category

    def get_code(self) -> str:
        return self._code

    def get_name(self) -> str:
        return self._name

    def get_category(self) -> PermissionCategory | None:
        return self._category

    def __repr__(self) -> str:
        data = {
            "code": self._code,
            "name": self._name,
            "category": self._category,
        }
        return f"{self.__class__.__name__}{data}"
