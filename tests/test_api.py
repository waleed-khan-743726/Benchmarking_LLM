from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)


def basic_payload() -> dict:
    return {
        "name": "API test",
        "grid": {"width": 5, "depth": 4, "obstacles": [{"x": 2, "z": 1}]},
        "start": {"x": 0, "z": 1},
        "goal": {"x": 4, "z": 1},
    }


def test_health_reports_d_drive_paths() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["project_root"].startswith("D:\\Robot_Navigation_FYP")
    assert body["free_space_gb"] > 20


def test_plan_endpoint_returns_valid_detour() -> None:
    response = client.post("/api/v1/plan", json=basic_payload())
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "success"
    assert body["validation"]["valid"] is True
    assert {"x": 2, "z": 1} not in body["path"]


def test_plan_endpoint_rejects_duplicate_obstacle() -> None:
    payload = basic_payload()
    payload["grid"]["obstacles"] *= 2
    response = client.post("/api/v1/plan", json=payload)
    assert response.status_code == 422


def test_simulation_lifecycle_and_missing_id() -> None:
    created = client.post("/api/v1/simulations", json=basic_payload())
    assert created.status_code == 201
    simulation_id = created.json()["id"]

    played = client.post(
        f"/api/v1/simulations/{simulation_id}/actions", json={"action": "play"}
    )
    assert played.json()["status"] == "running"

    stepped = client.post(
        f"/api/v1/simulations/{simulation_id}/actions", json={"action": "step"}
    )
    assert stepped.json()["position"] != {"x": 0, "z": 1}

    missing = client.get("/api/v1/simulations/not-real")
    assert missing.status_code == 404


def test_simulation_rejects_obstacle_on_robot() -> None:
    created = client.post("/api/v1/simulations", json=basic_payload()).json()
    response = client.post(
        f"/api/v1/simulations/{created['id']}/obstacles",
        json={"operation": "add", "cell": {"x": 0, "z": 1}},
    )
    assert response.status_code == 422

