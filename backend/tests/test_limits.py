import pytest
from backend.app.generation import GenerationError
from backend.app.limits import GenerationGate


def test_rolling_rate_limit_and_expiry():
    now = [0.0]
    gate = GenerationGate(2, 2, clock=lambda: now[0])
    for _ in range(2):
        gate.reserve("client")
        gate.release()
    with pytest.raises(GenerationError) as exc:
        gate.reserve("client")
    assert exc.value.status_code == 429
    now[0] = 60
    gate.reserve("client")
    assert len(gate.clients["client"]) == 1


def test_concurrency_limit_has_no_queue_or_slot_leak():
    gate = GenerationGate(6, 1)
    gate.reserve("first")
    with pytest.raises(GenerationError) as exc:
        gate.reserve("second")
    assert exc.value.status_code == 503
    assert gate.active == 1
    assert "second" not in gate.clients
    gate.release()
    gate.reserve("second")
    assert gate.active == 1


def test_memory_limit_caps_clients_and_prunes_old_clients():
    now = [0.0]
    gate = GenerationGate(6, 1, clock=lambda: now[0], max_clients=2)
    for client in ("one", "two"):
        gate.reserve(client)
        gate.release()
    with pytest.raises(GenerationError) as exc:
        gate.reserve("three")
    assert exc.value.status_code == 503
    assert len(gate.clients) == 2
    now[0] = 61
    gate.reserve("three")
    assert set(gate.clients) == {"three"}
