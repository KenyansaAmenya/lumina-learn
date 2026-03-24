from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Optional, List

T = TypeVar('T')

class BaseRepository(ABC, Generic[T]):
    @abstractmethod
    async def get_by_id(self, id: int) -> Optional[T]:
        pass