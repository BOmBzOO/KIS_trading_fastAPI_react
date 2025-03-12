from sqlmodel import Session, SQLModel, create_engine

from app import crud
from app.core.config import settings
from app.models import User, UserCreate, Account, AccountAPIConfig

engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))

# Make sure all SQLModel models are imported before initializing the metadata
SQLModel.metadata.create_all(engine)

def init_db(session: Session) -> None:
    # Tables should be created with Alembic migrations
    # But if you don't want to use migrations, create
    # the tables un-commenting the next lines
    # from sqlmodel import SQLModel

    # This works because the models are already imported and registered from app.models
    # SQLModel.metadata.create_all(engine)

    user = session.query(User).filter(User.email == settings.FIRST_SUPERUSER).first()
    if not user:
        user_in = UserCreate(
            email=settings.FIRST_SUPERUSER,
            password=settings.FIRST_SUPERUSER_PASSWORD,
            is_superuser=True,
        )
        user = crud.create_user(session=session, user_create=user_in)
