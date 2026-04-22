from __future__ import annotations

from abc import ABC, abstractmethod

from ..schemas import FederatedUpdatePacket


class FederatedCoordinator(ABC):
    @abstractmethod
    def submit(self, packet: FederatedUpdatePacket) -> dict:
        raise NotImplementedError
