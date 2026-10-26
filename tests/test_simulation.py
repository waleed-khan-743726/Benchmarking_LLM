from backend.planning import GridMap
from backend.simulation import SimulationEngine


def test_obstacle_on_route_triggers_safe_replan() -> None:
    engine = SimulationEngine(GridMap(5, 3), (0, 1), (4, 1))
    initial = engine.plan()
    blocked_next = initial.path[1]
    engine.play()
    engine.add_dynamic_obstacle(blocked_next)
    snapshot = engine.step()
    assert snapshot.position == (0, 1)
    assert snapshot.replans == 1
    assert blocked_next not in snapshot.route
    assert snapshot.status == "running"


def test_obstacle_away_from_route_does_not_replan() -> None:
    engine = SimulationEngine(GridMap(5, 3), (0, 1), (4, 1))
    engine.plan()
    engine.play()
    engine.add_dynamic_obstacle((4, 2))
    snapshot = engine.step()
    assert snapshot.position == (1, 1)
    assert snapshot.replans == 0


def test_no_alternative_route_stops_safely() -> None:
    engine = SimulationEngine(GridMap(3, 2, {(0, 0), (1, 0), (2, 0)}), (0, 1), (2, 1))
    engine.plan()
    engine.play()
    engine.add_dynamic_obstacle((1, 1))
    snapshot = engine.step()
    assert snapshot.position == (0, 1)
    assert snapshot.status == "no_path"


def test_reset_restores_start() -> None:
    engine = SimulationEngine(GridMap(4, 4), (0, 0), (3, 0))
    engine.plan()
    engine.step()
    assert engine.reset().position == (0, 0)
    assert engine.status == "idle"

