import uuid
from sqlmodel import Field, Relationship, SQLModel
from typing import Optional, List, Union

# Shared properties
class Item_Base(SQLModel):
    title: str = Field(min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=255)

# Properties to receive on item creation
class Item_Create(Item_Base):
    pass

# Properties to receive on item update
class Item_Update(Item_Base):
    title: Optional[str] = Field(default=None, min_length=1, max_length=255)  # type: ignore

# Database model, database table inferred from class name
class Item(Item_Base, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    title: str = Field(max_length=255)
    owner_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    owner: Optional["User"] | None = Relationship(back_populates="items")

# Properties to return via API, id is always required
class Item_Public(Item_Base):
    id: uuid.UUID
    owner_id: uuid.UUID

class Items_Public(SQLModel):
    data: list[Item_Public]
    count: int 