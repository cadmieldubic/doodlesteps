"""Small in-memory request and concurrency controls for the private prototype."""

from collections import deque
from collections.abc import Callable
from time import monotonic

from .generation import GenerationError


class GenerationGate:
    """Single-event-loop gate; no await occurs while counters are modified."""

    def __init__(
        self,
        requests_per_minute: int,
        max_concurrent: int,
        clock: Callable[[], float] = monotonic,
        max_clients: int = 1000,
    ):
        self.requests_per_minute = requests_per_minute
        self.max_concurrent = max_concurrent
        self.clock = clock
        self.max_clients = max_clients
        self.clients: dict[str, deque[float]] = {}
        self.active = 0

    def reserve(self, client: str) -> None:
        now = self.clock()
        # Prune every expired client rather than retaining arbitrary remote addresses.
        for key, attempts in list(self.clients.items()):
            while attempts and attempts[0] <= now - 60:
                attempts.popleft()
            if not attempts:
                del self.clients[key]
        attempts = self.clients.get(client)
        if attempts is not None and len(attempts) >= self.requests_per_minute:
            raise GenerationError(
                "Please wait a minute before requesting another photo lesson.", 429
            )
        if self.active >= self.max_concurrent:
            raise GenerationError("The drawing teacher is busy. Please try again shortly.", 503)
        if attempts is None:
            if len(self.clients) >= self.max_clients:
                raise GenerationError("The drawing teacher is busy. Please try again shortly.", 503)
            attempts = self.clients[client] = deque()
        attempts.append(now)
        self.active += 1

    def release(self) -> None:
        self.active = max(0, self.active - 1)
