Name: Sobar Danil 
Group: PO 25-Z 
Date: 25.09.26

from __future__ import annotations

from typing import Optional

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field, field_validator

app = FastAPI(title="Tighten your own API")


_users_db: dict[int, dict] = {}
_messages_db: dict[int, dict] = {}
_next_user_id = 1
_next_message_id = 1



class UserIn(BaseModel):

    author: str = Field(..., min_length=2, max_length=32)
    password: str = Field(..., min_length=8, max_length=128)

    @field_validator("author")
    @classmethod
    def author_must_not_be_blank(cls, v: str) -> str:
        trimmed = v.strip()
        if not trimmed:
            raise ValueError("author must not be blank")
        return trimmed


class UserOut(BaseModel):

    id: int
    author: str


class MessageIn(BaseModel):

    author: str = Field(..., min_length=2, max_length=32)
    text: str = Field(..., min_length=1, max_length=500)
    room_id: int = Field(..., ge=1)

    @field_validator("text")
    @classmethod
    def text_must_not_be_blank_and_is_trimmed(cls, v: str) -> str:
        trimmed = v.strip()
        if not trimmed:
            # "a text of only spaces returns 422"
            raise ValueError("text must not be blank")
        # "text is stored trimmed"
        return trimmed

    @field_validator("author")
    @classmethod
    def author_is_trimmed(cls, v: str) -> str:
        trimmed = v.strip()
        if not trimmed:
            raise ValueError("author must not be blank")
        return trimmed


class MessageOut(BaseModel):
    id: int
    author: str
    text: str
    room_id: int



@app.post("/users", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user(user: UserIn) -> UserOut:
    global _next_user_id
    user_id = _next_user_id
    _next_user_id += 1
    _users_db[user_id] = {"id": user_id, "author": user.author, "password": user.password}
    return UserOut(id=user_id, author=user.author)


@app.get("/users", response_model=list[UserOut])
def list_users() -> list[UserOut]:
    return [UserOut(id=u["id"], author=u["author"]) for u in _users_db.values()]


@app.get("/users/{user_id}", response_model=UserOut)
def get_user(user_id: int) -> UserOut:
    user = _users_db.get(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return UserOut(id=user["id"], author=user["author"])


@app.post("/messages", response_model=MessageOut, status_code=status.HTTP_201_CREATED)
def create_message(message: MessageIn) -> MessageOut:
    global _next_message_id
    message_id = _next_message_id
    _next_message_id += 1
    record = {
        "id": message_id,
        "author": message.author,
        "text": message.text,
        "room_id": message.room_id,
    }
    _messages_db[message_id] = record
    return MessageOut(**record)


@app.get("/messages", response_model=list[MessageOut])
def list_messages(room_id: Optional[int] = None) -> list[MessageOut]:
    values = _messages_db.values()
    if room_id is not None:
        values = [m for m in values if m["room_id"] == room_id]
    return [MessageOut(**m) for m in values]
