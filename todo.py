import json
import os
from dataclasses import dataclass
from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, TypeAdapter

from config import settings


app = FastAPI()

DATA_FILE = settings.data_file


class MessageIn(BaseModel):
    author: str
    text: str


class MessagePatch(BaseModel):
    author: str | None = None
    text: str | None = None


@dataclass
class Message:
    id: int
    author: str
    text: str
    created_at: datetime | None = None


MESSAGE_LIST_ADAPTER = TypeAdapter(list[Message])


def load() -> list[Message]:
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, encoding="utf-8") as f:
        return MESSAGE_LIST_ADAPTER.validate_python(json.load(f))


def save(messages: list[Message]) -> None:
    tmp = DATA_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(
            MESSAGE_LIST_ADAPTER.dump_python(messages, mode="json"),
            f,
            ensure_ascii=False,
            indent=2,
        )
    os.replace(tmp, DATA_FILE)


MESSAGES: list[Message] = load()
next_id: int = max((m.id for m in MESSAGES), default=0) + 1


def find(message_id: int) -> Message:
    for message in MESSAGES:
        if message.id == message_id:
            return message

    raise HTTPException(status_code=404, detail="Message not found")


@app.get("/messages", response_model=list[Message])
def list_messages() -> list[Message]:
    return MESSAGES


@app.post("/messages", response_model=Message, status_code=201)
def create_message(payload: MessageIn) -> Message:
    global next_id


    if len(MESSAGES) >= settings.max_messages:
        raise HTTPException(status_code=409, detail="Chat is full")

    message = Message(
        id=next_id,
        author=payload.author,
        text=payload.text,
        created_at=datetime.now(timezone.utc),
    )

    MESSAGES.append(message)
    next_id += 1
    save(MESSAGES)

    return message


@app.get("/messages/{message_id}", response_model=Message)
def get_message(message_id: int) -> Message:
    return find(message_id)


@app.put("/messages/{message_id}", response_model=Message)
def put_message(message_id: int, payload: MessageIn) -> Message:
    message = find(message_id)

    message.author = payload.author
    message.text = payload.text
    save(MESSAGES)

    return message


@app.patch("/messages/{message_id}", response_model=Message)
def patch_message(message_id: int, payload: MessagePatch) -> Message:
    message = find(message_id)

    sent = payload.model_dump(exclude_unset=True)

    for field, value in sent.items():
        setattr(message, field, value)
    save(MESSAGES)

    return message


@app.delete("/messages/{message_id}", status_code=204)
def delete_message(message_id: int) -> None:
    MESSAGES.remove(find(message_id))
    save(MESSAGES)