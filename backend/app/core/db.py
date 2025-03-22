from sqlmodel import Session, SQLModel, create_engine

from app import crud
from app.core.config import settings
# Import all models explicitly to ensure they are registered
from app.models import (
    User,
    User_Create,
    Account,
    Item
)

# PostgreSQL 연결 엔진 생성
engine = create_engine(
    str(settings.SQLALCHEMY_DATABASE_URI),
    echo=False,  # SQL 쿼리 로깅 비활성화
    pool_pre_ping=True,  # 연결 확인
)

# 세션 생성 함수
def get_session() -> Session:
    with Session(engine) as session:
        yield session

# Make sure all SQLModel models are imported before initializing the metadata
def init_db(session: Session) -> None:
    # Ensure all models are registered with SQLModel
    from app.models import User, Account, Item
    SQLModel.metadata.create_all(engine)

    user = session.query(User).filter(User.email == settings.FIRST_SUPERUSER).first()
    if not user:
        user_in = User_Create(
            email=settings.FIRST_SUPERUSER,
            password=settings.FIRST_SUPERUSER_PASSWORD,
            is_superuser=True,
        )
        user = crud.create_user(session=session, user_create=user_in)
