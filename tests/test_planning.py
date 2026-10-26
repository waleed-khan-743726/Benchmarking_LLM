import pytest

from backend.planning import AStarPlanner, GridMap, validate_route


def test_direct_path_is_shortest_and_valid() -> None:
    result = AStarPlanner().plan(GridMap(5, 5), (0, 0), (4, 0))
    assert result.status == "success"
    assert result.path_length == 4
    assert result.validation.valid


def test_obstacle_detour() -> None:
    grid = GridMap(5, 5, {(1, 0), (2, 0), (3, 0)})
    result = AStarPlanner().plan(grid, (0, 0), (4, 0))
    assert result.status == "success"
    assert result.path_length == 6
    assert not set(result.path) & grid.obstacles


def test_unreachable_goal() -> None:
    grid = GridMap(3, 3, {(1, 2), (2, 1)})
    result = AStarPlanner().plan(grid, (0, 0), (2, 2))
    assert result.status == "no_path"
    assert not result.validation.valid


@pytest.mark.parametrize("blocked", [{(0, 0)}, {(2, 2)}])
def test_blocked_start_or_goal(blocked: set[tuple[int, int]]) -> None:
    result = AStarPlanner().plan(GridMap(3, 3, blocked), (0, 0), (2, 2))
    assert result.status == "invalid"


@pytest.mark.parametrize("start,goal", [((-1, 0), (1, 1)), ((0, 0), (3, 0))])
def test_invalid_coordinates(start: tuple[int, int], goal: tuple[int, int]) -> None:
    assert AStarPlanner().plan(GridMap(3, 3), start, goal).status == "invalid"


def test_route_validator_rejects_illegal_transition() -> None:
    validation = validate_route(GridMap(4, 4), [(0, 0), (2, 0), (3, 0)], (0, 0), (3, 0))
    assert not validation.valid
    assert validation.invalid_index == 1


def test_grid_rejects_bad_boundaries() -> None:
    with pytest.raises(ValueError):
        GridMap(1, 5)
    with pytest.raises(ValueError):
        GridMap(5, 5, {(7, 1)})

