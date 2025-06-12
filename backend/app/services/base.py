from abc import ABC, abstractmethod
from typing import Dict

class AIBase(ABC):
    @abstractmethod
    async def get_response(self, message: str, context: str) -> str:
        pass