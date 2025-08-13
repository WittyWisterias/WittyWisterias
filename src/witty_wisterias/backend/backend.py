import base64
import json
import zlib

from .database import Database
from .exceptions import InvalidDataError
from .message_format import MessageFormat


class Backend:
    """
    Base class for the backend.
    This class should be inherited by all backends.
    """

    @staticmethod
    def decode(stack: str) -> list[MessageFormat]:
        """
        Decode a base64-encoded, compressed JSON string into a list of MessageFormat objects.

        Args:
            stack (str): The base64-encoded, compressed JSON string representing a stack of messages.

        Returns:
            list[MessageFormat]: A list of MessageFormat objects reconstructed from the decoded data.
        """
        if not stack:
            return []
        compressed = base64.b64decode(stack.encode("utf-8"))
        # Decompress
        json_str = zlib.decompress(compressed).decode("utf-8")
        # Deserialize JSON back to list
        json_stack = json.loads(json_str)
        # Convert each JSON object back to MessageFormat
        return [MessageFormat.from_json(message) for message in json_stack]

    @staticmethod
    def encode(stack: list[MessageFormat]) -> str:
        """
        Encode a list of MessageFormat objects into a base64-encoded, compressed JSON string.

        Args:
            stack (list[MessageFormat]): A list of MessageFormat objects to be encoded.

        Returns:
            str: A base64-encoded, compressed JSON string representing the list of messages.
        """
        # Convert each MessageFormat object to JSON
        dumped_stack = [message.to_json() for message in stack]
        # Serialize the list to JSON
        json_str = json.dumps(dumped_stack)
        # Compress the JSON string
        compressed = zlib.compress(json_str.encode("utf-8"))
        # Encode to base64 for safe transmission
        return base64.b64encode(compressed).decode("utf-8")

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

        # To do: Signing Messages should be done here
        # signed_message = Cryptography.sign_message(
        #    message.content, message.signing_key
        # )
        public_message = MessageFormat(
            sender_id=message.sender_id,
            event_type=message.event_type,
            content=message.content,
            timestamp=message.timestamp,
        )

        queried_data.append(public_message)

        Database.upload_data(Backend.encode(queried_data))

    @staticmethod
    def read_public_text() -> list[MessageFormat]:
        """
        Read public text messages.
        This method should be overridden by the backend.
        """
        decoded_data = Backend.decode(Database.query_data())

        verified_messaged: list[MessageFormat] = []
        for message in decoded_data:
            # TODO: Signature verification should be done here
            # Note: We ignore copy Linting Error because we will modify the message later, when we verify it
            verified_messaged.append(message)  # noqa: PERF402

        return verified_messaged
