from abc import ABC, abstractmethod

from domain.users.models import User

from .models import SavedFile, UploadingFile


class FilesPort(ABC):

    @abstractmethod
    async def save(self, file: SavedFile) -> SavedFile: ...

    @abstractmethod
    def validate_uploading(self, file: UploadingFile) -> None: ...

    @abstractmethod
    def get_default(self, user: User) -> SavedFile: ...
