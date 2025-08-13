import base64
import json
import zlib
from dataclasses import asdict, dataclass, field

from .cryptographer import Cryptographer
from .database import Database
from .exceptions import InvalidDataError
from .message_format import MessageFormat


@dataclass
class UploadStack:
    """The UploadStack class is used to store the data that will be uploaded to the Database."""

    profile_image_stack: dict[str, str] = field(default_factory=dict)
    verify_keys_stack: dict[str, str] = field(default_factory=dict)
    public_keys_stack: dict[str, str] = field(default_factory=dict)
    message_stack: list[MessageFormat | str] = field(default_factory=list)

    @staticmethod
    def from_json(data: str) -> "UploadStack":
        """
        Deserialize a JSON string into an UploadStack object.

        Args:
            data (str): The JSON string to deserialize.

        Returns:
            UploadStack: An instance of UploadStack with the deserialized data.
        """
        json_data = json.loads(data)
        return UploadStack(
            profile_image_stack=json_data.get("profile_image_stack", {}),
            verify_keys_stack=json_data.get("verify_keys_stack", {}),
            public_keys_stack=json_data.get("public_keys_stack", {}),
            message_stack=[
                MessageFormat.from_json(message)
                for message in json_data.get("message_stack", [])
                if isinstance(message, str)
            ],
        )


class Backend:
    """
    Base class for the backend.
    This class should be inherited by all backends.
    """

    @staticmethod
    def decode(encoded_stack: str) -> UploadStack:
        """
        Decode a base64-encoded, compressed JSON string into a list of MessageFormat objects.

        Args:
            encoded_stack (str): The base64-encoded, compressed JSON string representing a stack of messages.

        Returns:
            list[MessageFormat]: A list of MessageFormat objects reconstructed from the decoded data.
        """
        if not encoded_stack:
            return UploadStack()
        compressed_stack = base64.b64decode(encoded_stack.encode("utf-8"))
        # Decompress
        string_stack = zlib.decompress(compressed_stack).decode("utf-8")
        # Convert String Stack to UploadStack object
        return UploadStack.from_json(string_stack)

    @staticmethod
    def encode(upload_stack: UploadStack) -> str:
        """
        Encode a list of MessageFormat objects into a base64-encoded, compressed JSON string.

        Args:
            upload_stack (UploadStack): The UploadStack to encode.

        Returns:
            str: A base64-encoded, compressed JSON string representing the list of messages.
        """
        # Convert each MessageFormat object to JSON
        upload_stack.message_stack = [
            message.to_json() for message in upload_stack.message_stack if isinstance(message, MessageFormat)
        ]
        # Serialize the list to JSON
        json_stack = json.dumps(asdict(upload_stack))
        # Compress the JSON string
        compressed_stack = zlib.compress(json_stack.encode("utf-8"))
        # Encode to base64 for safe transmission
        return base64.b64encode(compressed_stack).decode("utf-8")

    @staticmethod
    def send_public_text(message: MessageFormat) -> None:
        """
        Send a public test message to the Database.

        Args:
            message (MessageFormat): The message to be sent, containing senderID, event type, content, and signing key.
        """
        if not (message.sender_id and message.event_type and message.content and message.signing_key):
            raise InvalidDataError("MessageFormat is not complete")

        queried_data = Backend.decode(Database.query_data())

        # Append the verify_key to the Upload Stack if not already present
        if message.verify_key not in queried_data.verify_keys_stack:
            queried_data.verify_keys_stack[message.sender_id] = message.verify_key

        # Sign the message using the Signing Key
        signed_message = Cryptographer.sign_message(message.content, message.signing_key)
        public_message = MessageFormat(
            sender_id=message.sender_id,
            event_type=message.event_type,
            content=signed_message,
            timestamp=message.timestamp,
        )

        queried_data.message_stack.append(public_message)

        Database.upload_data(Backend.encode(queried_data))

    @staticmethod
    def read_public_text() -> list[MessageFormat]:
        """
        Read public text messages.
        This method should be overridden by the backend.
        """
        decoded_data = Backend.decode(Database.query_data())

        verified_messaged: list[MessageFormat] = []
        for message in decoded_data.message_stack:
            # Signature Verification
            if not isinstance(message, str) and message.sender_id in decoded_data.verify_keys_stack:
                verify_key = decoded_data.verify_keys_stack[message.sender_id]
                try:
                    # Verify the message content using the verify key
                    message.content = Cryptographer.verify_message(message.content, verify_key)
                    verified_messaged.append(message)
                except ValueError:
                    pass

        return verified_messaged
