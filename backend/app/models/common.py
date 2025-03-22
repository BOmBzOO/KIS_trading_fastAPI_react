from sqlmodel import SQLModel
from typing import Optional
from pydantic import Field

# Generic message
class Message(SQLModel):
    message: str

# JSON payload containing access token
class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"

# Contents of JWT token
class Token_Payload(SQLModel):
    sub: Optional[str] = None

class New_Password(SQLModel):
    token: str
    new_password: str = Field(min_length=8, max_length=40) 