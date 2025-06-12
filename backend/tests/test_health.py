from fastapi.testclient import TestClient


def test_health_check(client: TestClient) -> None:
    """
    测试健康检查端点
    """
    response = client.get("/api/v1/health/")
    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "message": "服务正常运行"
    } 