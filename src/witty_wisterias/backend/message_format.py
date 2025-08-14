import json
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import TypedDict


# TODO: We should probably move types to a separate file for better organization (and exceptions.py too), doesnt belong
# in /modules/...
class EventType(Enum):
    """Enumeration for different task types."""

    PUBLIC_TEXT = auto()
    PUBLIC_IMAGE = auto()
    PRIVATE_TEXT = auto()
    PRIVATE_IMAGE = auto()
    SET_USERNAME = auto()
    SET_PROFILEPICTURE = auto()


class MessageJson(TypedDict):
    """
    Defines the structure of the JSON representation of a message.
    This is used for serialization and deserialization of messages.
    """

    header: dict[str, str | float | None]
    body: dict[str, str | dict[str, str | None]]


@dataclass
class ExtraEventInfo:
    """Storage for extra information related to an event."""

    user_name: str | None = field(default=None)
    user_image: str | None = field(default=None)

    def to_dict(self) -> dict[str, str | None]:
        """Convert the extra event info to a dictionary."""
        return {
            "user_name": self.user_name,
            "user_image": self.user_image,
        }

    @staticmethod
    def from_json(data: dict[str, str | None]) -> "ExtraEventInfo":
        """Deserialize a JSON string into an ExtraEventInfo object."""
        return ExtraEventInfo(user_name=data.get("user_name", ""), user_image=data.get("user_image", ""))


@dataclass
class MessageFormat:
    """
    Defines the standard structure for messages in the system.
    Supports serialization/deserialization for storage in images.
    """

    sender_id: str
    event_type: EventType
    content: str
    timestamp: float
    receiver_id: str = field(default="None")
    signing_key: str = field(default="")
    verify_key: str = field(default="")
    private_key: str = field(default="")
    public_key: str = field(default="")
    extra_event_info: ExtraEventInfo = field(default_factory=ExtraEventInfo)

    def to_dict(self) -> MessageJson:
        """Convert the message into a Python dictionary."""
        return {
            "header": {
                "sender_id": self.sender_id,
                "receiver_id": self.receiver_id,
                "event_type": self.event_type.name,
                "signing_key": self.signing_key,
                "verify_key": self.verify_key,
                "public_key": self.public_key,
                "private_key": self.private_key,
                "timestamp": self.timestamp,
            },
            "body": {"content": self.content, "extra_event_info": self.extra_event_info.to_dict()},
        }

    def to_json(self) -> str:
        """Serialize the message into a JSON string."""
        return json.dumps(self.to_dict(), ensure_ascii=False)

    @staticmethod
    def from_json(data: str) -> "MessageFormat":
        """Deserialize a JSON string into a MessageFormat object."""
        obj = json.loads(data)
        return MessageFormat(
            sender_id=obj["header"]["sender_id"],
            receiver_id=obj["header"].get("receiver_id"),
            event_type=EventType[obj["header"]["event_type"]],
            signing_key=obj["header"].get("signing_key"),
            verify_key=obj["header"].get("verify_key"),
            public_key=obj["header"].get("public_key"),
            private_key=obj["header"].get("private_key"),
            timestamp=obj["header"]["timestamp"],
            content=obj["body"]["content"],
            extra_event_info=ExtraEventInfo.from_json(obj["body"].get("extra_event_info", {})),
        )
