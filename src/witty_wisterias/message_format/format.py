import json
from typing import Any, Dict, Optional


class MessageFormat:
    """
    Defines the standard structure for messages in the system.
    Supports serialization/deserialization for storage in images.
    """

    def __init__(
        self,
        sender_id: str,
        content: Any,
        event_type: str,
        receiver_id: Optional[str] = None,
        public_key: Optional[str] = None,
        extra_event_info: Optional[Dict] = None,
        previous_messages: Optional[list] = None,
        stop_signal: bool = False
    ):
        self.sender_id = sender_id
        self.receiver_id = receiver_id
        self.event_type = event_type
        self.public_key = public_key
        self.content = content
        self.extra_event_info = extra_event_info or {}
        self.previous_messages = previous_messages or []
        self.stop_signal = stop_signal

    def to_dict(self) -> Dict:
        """Convert the message into a Python dictionary."""
        return {
            "header": {
                "sender_id": self.sender_id,
                "receiver_id": self.receiver_id,
                "event_type": self.event_type,
                "public_key": self.public_key
            },
            "body": {
                "content": self.content,
                "extra_event_info": self.extra_event_info
            },
            "previous_messages": self.previous_messages,
            "stop_signal": self.stop_signal
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
            event_type=obj["header"]["event_type"],
            public_key=obj["header"].get("public_key"),
            content=obj["body"]["content"],
            extra_event_info=obj["body"].get("extra_event_info", {}),
            previous_messages=obj.get("previous_messages", []),
            stop_signal=obj.get("stop_signal", False)
        )