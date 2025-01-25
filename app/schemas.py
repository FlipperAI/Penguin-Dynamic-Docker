import uuid
from pydantic import BaseModel
from typing import Literal
from fastapi_users import schemas

class UserRead(schemas.BaseUser[uuid.UUID]):
    pass


class UserCreate(schemas.BaseUserCreate):
    pass


class UserUpdate(schemas.BaseUserUpdate):
    pass

class SubmissionCreate(BaseModel):
    code: str
    language: str
    #language: Literal["python", "bash"]
