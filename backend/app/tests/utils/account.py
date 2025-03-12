import random
import string
import uuid

from sqlmodel import Session

from app.models import Account
from app.tests.utils.user import create_random_user


def random_lower_string(length: int = 32) -> str:
    return "".join(random.choices(string.ascii_lowercase, k=length))


def create_random_account(db: Session) -> Account:
    user = create_random_user(db)
    account = Account(
        app_key=random_lower_string(),
        app_secret=random_lower_string(),
        cano=str(random.randint(50070000, 50079999)),
        acnt_prdt_cd=str(random.randint(1, 99)).zfill(2),
        acnt_type=random.choice(["real", "virtual"]),
        hts_id=random_lower_string(8),
        is_active=True,
        owner_id=user.id,
    )
    db.add(account)
    db.commit()
    db.refresh(account)
    return account 