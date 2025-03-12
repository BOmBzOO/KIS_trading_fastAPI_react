import uuid

from fastapi.testclient import TestClient
from sqlmodel import Session

from app.core.config import settings
from app.tests.utils.account import create_random_account


def test_create_account(
    client: TestClient, normal_user_token_headers: dict[str, str]
) -> None:
    data = {
        "app_key": "test_app_key",
        "app_secret": "test_app_secret",
        "cano": "50071234",
        "acnt_prdt_cd": "01",
        "acnt_type": "real",
        "hts_id": "test_user",
        "is_active": True
    }
    response = client.post(
        f"{settings.API_V1_STR}/accounts/",
        headers=normal_user_token_headers,
        json=data,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["app_key"] == data["app_key"]
    assert content["app_secret"] == data["app_secret"]
    assert content["cano"] == data["cano"]
    assert content["acnt_prdt_cd"] == data["acnt_prdt_cd"]
    assert content["acnt_type"] == data["acnt_type"]
    assert content["hts_id"] == data["hts_id"]
    assert content["is_active"] == data["is_active"]
    assert "id" in content
    assert "owner_id" in content


def test_read_account(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    account = create_random_account(db)
    response = client.get(
        f"{settings.API_V1_STR}/accounts/{account.id}",
        headers=normal_user_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["app_key"] == account.app_key
    assert content["app_secret"] == account.app_secret
    assert content["cano"] == account.cano
    assert content["acnt_prdt_cd"] == account.acnt_prdt_cd
    assert content["acnt_type"] == account.acnt_type
    assert content["hts_id"] == account.hts_id
    assert content["is_active"] == account.is_active
    assert content["id"] == str(account.id)
    assert content["owner_id"] == str(account.owner_id)


def test_read_account_not_found(
    client: TestClient, normal_user_token_headers: dict[str, str]
) -> None:
    response = client.get(
        f"{settings.API_V1_STR}/accounts/{uuid.uuid4()}",
        headers=normal_user_token_headers,
    )
    assert response.status_code == 404
    content = response.json()
    assert content["detail"] == "Item not found"


def test_read_account_not_enough_permissions(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    account = create_random_account(db)  # This creates an account owned by a different user
    response = client.get(
        f"{settings.API_V1_STR}/accounts/{account.id}",
        headers=normal_user_token_headers,
    )
    assert response.status_code == 400
    content = response.json()
    assert content["detail"] == "Not enough permissions"


def test_read_accounts(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    account1 = create_random_account(db)
    account2 = create_random_account(db)
    response = client.get(
        f"{settings.API_V1_STR}/accounts/",
        headers=normal_user_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert len(content["data"]) >= 2
    assert content["count"] >= 2


def test_update_account(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    account = create_random_account(db)
    data = {
        "app_key": "updated_app_key",
        "app_secret": "updated_app_secret",
        "cano": "50075678",
        "acnt_prdt_cd": "02",
        "acnt_type": "virtual",
        "hts_id": "updated_user",
        "is_active": False
    }
    response = client.put(
        f"{settings.API_V1_STR}/accounts/{account.id}",
        headers=normal_user_token_headers,
        json=data,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["app_key"] == data["app_key"]
    assert content["app_secret"] == data["app_secret"]
    assert content["cano"] == data["cano"]
    assert content["acnt_prdt_cd"] == data["acnt_prdt_cd"]
    assert content["acnt_type"] == data["acnt_type"]
    assert content["hts_id"] == data["hts_id"]
    assert content["is_active"] == data["is_active"]
    assert content["id"] == str(account.id)
    assert content["owner_id"] == str(account.owner_id)


def test_update_account_not_found(
    client: TestClient, normal_user_token_headers: dict[str, str]
) -> None:
    data = {"app_key": "updated_app_key", "app_secret": "updated_app_secret"}
    response = client.put(
        f"{settings.API_V1_STR}/accounts/{uuid.uuid4()}",
        headers=normal_user_token_headers,
        json=data,
    )
    assert response.status_code == 404
    content = response.json()
    assert content["detail"] == "Item not found"


def test_update_account_not_enough_permissions(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    account = create_random_account(db)
    data = {"app_key": "updated_app_key", "app_secret": "updated_app_secret"}
    response = client.put(
        f"{settings.API_V1_STR}/accounts/{account.id}",
        headers=normal_user_token_headers,
        json=data,
    )
    assert response.status_code == 400
    content = response.json()
    assert content["detail"] == "Not enough permissions"


def test_delete_account(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    account = create_random_account(db)
    response = client.delete(
        f"{settings.API_V1_STR}/accounts/{account.id}",
        headers=normal_user_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["message"] == "Account deleted successfully"


def test_delete_account_not_found(
    client: TestClient, normal_user_token_headers: dict[str, str]
) -> None:
    response = client.delete(
        f"{settings.API_V1_STR}/accounts/{uuid.uuid4()}",
        headers=normal_user_token_headers,
    )
    assert response.status_code == 404
    content = response.json()
    assert content["detail"] == "Item not found"


def test_delete_account_not_enough_permissions(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    account = create_random_account(db)
    response = client.delete(
        f"{settings.API_V1_STR}/accounts/{account.id}",
        headers=normal_user_token_headers,
    )
    assert response.status_code == 400
    content = response.json()
    assert content["detail"] == "Not enough permissions" 