from enum import Enum


class SavedFile:
    _id: int
    _original_url: str
    _original_filename: str
    _converted_url: str | None
    _converted_filename: str | None

    def __init__(
        self,
        id_: int,
        original_url: str,
        original_filename: str,
        converted_url: str | None = None,
        converted_filename: str | None = None,
    ) -> None:
        self._id = id_
        self._original_url = original_url
        self._original_filename = original_filename
        self._converted_url = converted_url
        self._converted_filename = converted_filename

    def get_id(self) -> int:
        return self._id

    def get_original_url(self) -> str:
        return self._original_url

    def get_original_filename(self) -> str:
        return self._original_filename

    def get_converted_url(self) -> str | None:
        return self._converted_url

    def get_converted_filename(self) -> str | None:
        return self._converted_filename

    def __repr__(self) -> str:
        data = {
            "id": self._id,
            "original_url": self._original_url,
            "original_filename": self._original_filename,
            "converted_url": self._converted_url,
            "converted_url": self._converted_url,
        }
        return f"{self.__class__.__name__}{data}"


class SystemFiletypes(Enum):
    avatar = "avatar"
    file_in_chat = "file_in_chat"


class UploadingFileMeta:
    _url: str
    _signature: str
    _filename: str
    _system_filetype: SystemFiletypes

    def __init__(self, url: str, signature: str, filename: str, system_filetype: SystemFiletypes):
        self._url = url
        self._signature = signature
        self._filename = filename
        self._system_filetype = system_filetype

    def get_url(self) -> str:
        return self._url

    def get_signature(self) -> str:
        return self._signature

    def get_filename(self) -> str:
        return self._filename

    def get_system_filetype(self) -> SystemFiletypes:
        return self._system_filetype

    def __repr__(self) -> str:
        data = {
            "url": self._url,
            "signature": self._signature,
            "filename": self._filename,
            "system_filetype": self._system_filetype,
        }
        return f"{self.__class__.__name__}{data}"


class UploadingFile:
    _original: UploadingFileMeta
    _converted: UploadingFileMeta | None

    def __init__(self, original: UploadingFileMeta, converted: UploadingFileMeta | None = None):
        self._original = original
        self._converted = converted

    def get_original(self) -> UploadingFileMeta:
        return self._original

    def get_converted(self) -> UploadingFileMeta | None:
        return self._converted

    def __repr__(self) -> str:
        data = {
            "original": self._original,
            "converted": self._converted,
        }
        return f"{self.__class__.__name__}{data}"
