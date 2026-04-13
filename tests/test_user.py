from fastapi.testclient import TestClient
import pytest

from src.main import app
from src.fake_db import db

client = TestClient(app)

# Существующие пользователи
users = [
    {
        'id': 1,
        'name': 'Ivan Ivanov',
        'email': 'i.i.ivanov@mail.com',
    },
    {
        'id': 2,
        'name': 'Petr Petrov',
        'email': 'p.p.petrov@mail.com',
    }
]


@pytest.fixture(autouse=True)
def reset_db():
    db._users = [
        {
            'id': 1,
            'name': 'Ivan Ivanov',
            'email': 'i.i.ivanov@mail.com',
        },
        {
            'id': 2,
            'name': 'Petr Petrov',
            'email': 'p.p.petrov@mail.com',
        }
    ]
    db._id = len(db._users)


def test_get_existed_user():
    """Получение существующего пользователя"""
    response = client.get("/api/v1/user", params={'email': users[0]['email']})
    assert response.status_code == 200
    assert response.json() == users[0]


def test_get_unexisted_user():
    """Получение несуществующего пользователя"""
    response = client.get("/api/v1/user", params={'email': 'unknown@mail.com'})
    assert response.status_code == 404
    assert response.json() == {"detail": "User not found"}


def test_create_user_with_valid_email():
    """Создание пользователя с уникальной почтой"""
    new_user = {
        "name": "Sergey Sergeev",
        "email": "s.s.sergeev@mail.com"
    }

    response = client.post("/api/v1/user", json=new_user)
    assert response.status_code == 201
    assert response.json() == 3

    get_response = client.get("/api/v1/user", params={"email": new_user["email"]})
    assert get_response.status_code == 200
    assert get_response.json() == {
        "id": 3,
        "name": "Sergey Sergeev",
        "email": "s.s.sergeev@mail.com"
    }


def test_create_user_with_invalid_email():
    """Создание пользователя с почтой, которую использует другой пользователь"""
    existed_user = {
        "name": "Another Ivan",
        "email": users[0]["email"]
    }

    response = client.post("/api/v1/user", json=existed_user)
    assert response.status_code == 409
    assert response.json() == {
        "detail": "User with this email already exists"
    }


def test_delete_user():
    """Удаление пользователя"""
    response = client.delete("/api/v1/user", params={"email": users[1]["email"]})
    assert response.status_code == 204
    assert response.text == ""

    get_response = client.get("/api/v1/user", params={"email": users[1]["email"]})
    assert get_response.status_code == 404
    assert get_response.json() == {"detail": "User not found"}