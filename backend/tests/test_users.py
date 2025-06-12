from typing import Dict

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.services import user_service


def test_create_user(client: TestClient, db: Session) -> None:
    """
    测试创建用户
    """
    data = {
        "email": "test@example.com",
        "username": "test",
        "password": "password",
    }
    response = client.post("/api/v1/users/", json=data)
    assert response.status_code == 200
    user = response.json()
    assert user["email"] == data["email"]
    assert user["username"] == data["username"]
    assert "password" not in user
    
    # 清理
    # db_user = user_service.get_user_by_email(db, email=data["email"])
    # if db_user:
    #     db.delete(db_user)
    #     db.commit()


def test_read_users(client: TestClient, superuser: Dict[str, str]) -> None:
    """
    测试获取所有用户
    """
    response = client.get("/api/v1/users/")
    assert response.status_code == 200
    users = response.json()
    assert isinstance(users, list)
    assert len(users) > 0


def test_read_user(client: TestClient, superuser: Dict[str, str], db: Session) -> None:
    """
    测试获取用户详情
    """
    # 获取超级用户
    db_user = user_service.get_user_by_email(db, email=superuser["email"])
    
    response = client.get(f"/api/v1/users/{db_user.id}")
    assert response.status_code == 200
    user = response.json()
    assert user["email"] == superuser["email"]
    assert user["username"] == "admin"
    assert user["is_superuser"] is True 


