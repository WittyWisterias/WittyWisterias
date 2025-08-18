import base64
import json
from dataclasses import dataclass, field
from enum import Enum, auto
from io import BytesIO
from typing import TypedDict

from PIL import Image


class EventType(Enum):
    """Enumeration for different task types."""

    PUBLIC_TEXT = auto()
    PUBLIC_IMAGE = auto()
    PRIVATE_TEXT = auto()
    PRIVATE_IMAGE = auto()


class MessageFormatJson(TypedDict):
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
        """
        Convert the extra event info to a dictionary.

        Returns:
            dict[str, str | None]: The Extra Event Info in a dict format.
        """
        return {
            "user_name": self.user_name,
            "user_image": self.user_image,
        }

    @staticmethod
    def from_json(data: dict[str, str | None]) -> "ExtraEventInfo":
        """
        Deserialize a JSON string into an ExtraEventInfo object.

        Args:
            data (dict[str, str | None]): The Extra Event Info in a dict format.

        Returns:
            ExtraEventInfo: : The Extra Event Info in a ExtraEventInfo object.
        """
        return ExtraEventInfo(user_name=data.get("user_name", ""), user_image=data.get("user_image", ""))


@dataclass
class MessageFormat:
    """
    Defines the standard structure for messages in the backend.
    Supports serialization/deserialization for storage in images.
    """

    sender_id: str
    event_type: EventType
    content: str
    timestamp: float
    sender_username: str = field(default="")
    sender_profile_image: str = field(default="")
    receiver_id: str = field(default="None")
    signing_key: str = field(default="")
    verify_key: str = field(default="")
    own_public_key: str = field(default="")
    receiver_public_key: str = field(default="")
    private_key: str = field(default="")
    extra_event_info: ExtraEventInfo = field(default_factory=ExtraEventInfo)

    def to_dict(self) -> MessageFormatJson:
        """
        Convert the message into a Python dictionary.

        Returns:
            MessageFormatJson: The MessageFormat encoded in a dict.
        """
        return {
            "header": {
                "sender_id": self.sender_id,
                "receiver_id": self.receiver_id,
                "event_type": self.event_type.name,
                "timestamp": self.timestamp,
                "signing_key": self.signing_key,
                "verify_key": self.verify_key,
                "own_public_key": self.own_public_key,
                "private_key": self.private_key,
                "receiver_public_key": self.receiver_public_key,
            },
            "body": {"content": self.content, "extra_event_info": self.extra_event_info.to_dict()},
        }

    def to_json(self) -> str:
        """
        Serialize the message into a JSON string.

        Returns:
            str: The MessageFormat encoded in a JSON String.
        """
        return json.dumps(self.to_dict(), ensure_ascii=False)

    @staticmethod
    def from_json(data: str) -> "MessageFormat":
        """
        Deserialize a JSON string into a MessageFormat object.

        Args:
            data (str): The MessageFormat encoded in a JSON String.

        Returns:
            MessageFormat: The Message Info in a  MessageFormat object.
        """
        obj = json.loads(data)
        return MessageFormat(
            sender_id=obj["header"]["sender_id"],
            receiver_id=obj["header"].get("receiver_id"),
            event_type=EventType[obj["header"]["event_type"]],
            signing_key=obj["header"].get("signing_key"),
            verify_key=obj["header"].get("verify_key"),
            own_public_key=obj["header"].get("own_public_key"),
            receiver_public_key=obj["header"].get("receiver_public_key"),
            private_key=obj["header"].get("private_key"),
            timestamp=obj["header"]["timestamp"],
            content=obj["body"]["content"],
            extra_event_info=ExtraEventInfo.from_json(obj["body"].get("extra_event_info", {})),
        )


class MessageStateJson(TypedDict):
    """
    Defines the structure of the JSON representation of a message.
    This is used for serialization and deserialization of messages.
    """

    message: str
    user_id: str
    receiver_id: str | None
    user_name: str
    user_profile_image: str | None
    own_message: bool
    is_image_message: bool
    timestamp: float


@dataclass
class MessageState:
    """A message in the chat application state (Frontend)."""

    message: str | Image.Image
    user_id: str
    receiver_id: str | None
    user_name: str
    user_profile_image: str | None
    own_message: bool
    is_image_message: bool
    timestamp: float

    @staticmethod
    def from_message_format(message_format: MessageFormat, user_id: str) -> "MessageState":
        """
        Convert a MessageFormat object to a Message object.

        Args:
            message_format (MessageFormat): The MessageFormat object to convert.
            user_id (str): The ChatState.user_id as str.

        Returns:
            Message: A Message object created from the MessageFormat.
        """
        return MessageState(
            message=message_format.content,
            user_id=message_format.sender_id,
            receiver_id=message_format.receiver_id if message_format.receiver_id != "None" else None,
            user_name=message_format.extra_event_info.user_name or message_format.sender_id,
            user_profile_image=message_format.extra_event_info.user_image,
            own_message=user_id == message_format.sender_id,
            is_image_message=message_format.event_type in (EventType.PUBLIC_IMAGE, EventType.PRIVATE_IMAGE),
            timestamp=message_format.timestamp,
        )

    @staticmethod
    def from_dict(data: MessageStateJson) -> "MessageState":
        """
        Convert a dictionary to a Message object.

        Args:
            data (dict[str, str]): The dictionary containing message data.

        Returns:
            Message: A Message object created from the dictionary.
        """
        # Convert the base64 message content to a Pillow Image if it is an image message
        if data.get("is_image_message", False):
            # Decode the base64 image data to an Image object
            image_data = base64.b64decode(data["message"])
            message_content = Image.open(BytesIO(image_data))
            message_content = message_content.convert("RGB")
        else:
            message_content = data["message"]
        return MessageState(
            message=message_content,
            user_id=data["user_id"],
            receiver_id=data.get("receiver_id"),
            user_name=data["user_name"],
            user_profile_image=data.get("user_profile_image"),
            own_message=data.get("own_message", False),
            is_image_message=data.get("is_image_message", False),
            timestamp=float(data["timestamp"]),
        )

    def to_dict(self) -> MessageStateJson:
        """
        Convert the message into a Python dictionary.

        Returns:
            MessageJson: A dictionary representation of the message.
        """
        # Convert the Image to Base64 if it is an Image Message
        if isinstance(self.message, Image.Image):
            # Convert the image to bytes and encode it in base64 (JPEG to save limited LocalStorage space)
            buffered = BytesIO()
            self.message.save(buffered, format="JPEG")
            message_data = base64.b64encode(buffered.getvalue()).decode("utf-8")
        else:
            message_data = self.message

        return {
            "message": message_data,
            "user_id": self.user_id,
            "receiver_id": self.receiver_id,
            "user_name": self.user_name,
            "user_profile_image": self.user_profile_image,
            "own_message": self.own_message,
            "is_image_message": self.is_image_message,
            "timestamp": self.timestamp,
        }
