import base64
import json
import zlib
from dataclasses import asdict, dataclass, field

from .cryptographer import Cryptographer
from .database import Database
from .exceptions import InvalidDataError
from .message_format import EventType, ExtraEventInfo, MessageFormat


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
    """Base class for the backend, which is used by the Frontend to handle Messages."""

    @staticmethod
    def decode(encoded_stack: str) -> UploadStack:
        """
        Decode a base64-encoded, compressed JSON string into a list of MessageFormat objects.

        Args:
            encoded_stack (str): The base64-encoded, compressed JSON string representing a stack of messages.

        Returns:
            list[MessageFormat]: A list of MessageFormat objects reconstructed from the decoded data.
        """
        # Check if the Message Stack is completely empty
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
    def push_public_keys(user_id: str, verify_key: str, public_key: str) -> None:
        """
        Push public keys to the Upload Stack.

        Args:
            user_id (str): The ID of the user.
            verify_key (str): The verify key of the user.
            public_key (str): The public key of the user.
        """
        # Query the latest Data from the Database
        queried_data = Backend.decode(Database.query_data())

        # Append the verify_key to the Upload Stack if not already present
        if user_id not in queried_data.verify_keys_stack:
            queried_data.verify_keys_stack[user_id] = verify_key

        # Append the public_key to the Upload Stack if not already present
        if user_id not in queried_data.public_keys_stack:
            queried_data.public_keys_stack[user_id] = public_key

        # Upload the new Data to save it in the Database
        Database.upload_data(Backend.encode(queried_data))

    @staticmethod
    def read_public_keys() -> tuple[dict[str, str], dict[str, str]]:
        """
        Read verify and public keys from the Upload Stack.

        Returns:
            dict[str, str]: A dictionary containing user IDs as keys and their verify keys as values.
            dict[str, str]: A dictionary containing user IDs as keys and their public keys as values.
        """
        # Query the latest Data from the Database
        queried_data = Backend.decode(Database.query_data())
        return queried_data.verify_keys_stack, queried_data.public_keys_stack

    @staticmethod
    def send_public_message(message: MessageFormat) -> None:
        """
        Send a public test message to the Database.

        Args:
            message (MessageFormat): The message to be sent, containing senderID, event type, content, and signing key.
        """
        if not (message.sender_id and message.event_type and message.content and message.signing_key):
            raise InvalidDataError("MessageFormat is not complete")

        # Query the latest Data from the Backend
        queried_data = Backend.decode(Database.query_data())

        # Append the verify_key to the Upload Stack if not already present
        if message.sender_id not in queried_data.verify_keys_stack:
            queried_data.verify_keys_stack[message.sender_id] = message.verify_key

        # Sign the message using the Signing Key
        signed_message = Cryptographer.sign_message(message.content, message.signing_key)
        # Create the Public Message to push
        public_message = MessageFormat(
            sender_id=message.sender_id,
            event_type=message.event_type,
            content=signed_message,
            timestamp=message.timestamp,
            extra_event_info=ExtraEventInfo(
                user_name=message.sender_username,
                user_image=message.sender_profile_image,
            ),
        )

        # Push the new Public Message to the Message Stack
        queried_data.message_stack.append(public_message)

        # Upload the new Data to save it in the Database
        Database.upload_data(Backend.encode(queried_data))

    @staticmethod
    def send_private_message(message: MessageFormat) -> None:
        """
        Send a private message to the Database.

        Args:
            message (MessageFormat): The message to be sent, containing senderID, event type, content, and signing key.
        """
        if not (
            message.sender_id
            and message.receiver_id
            and message.event_type
            and message.content
            and message.timestamp
            and message.own_public_key
            and message.receiver_public_key
            and message.private_key
        ):
            raise InvalidDataError("MessageFormat is not complete")

        # Query the latest Data from the Database
        queried_data = Backend.decode(Database.query_data())

        # Append own Public Key to the Upload Stack if not already present
        if message.sender_id not in queried_data.public_keys_stack:
            queried_data.public_keys_stack[message.sender_id] = message.own_public_key

        # Encrypt the message content using the receiver's public key
        encrypted_message = Cryptographer.encrypt_message(
            message.content, message.private_key, message.receiver_public_key
        )
        # Create the Private Message to push
        private_message = MessageFormat(
            sender_id=message.sender_id,
            receiver_id=message.receiver_id,
            event_type=message.event_type,
            content=encrypted_message,
            timestamp=message.timestamp,
            extra_event_info=ExtraEventInfo(
                user_name=message.sender_username,
                user_image=message.sender_profile_image,
            ),
        )

        # Push the new Public Message to the Message Stack
        queried_data.message_stack.append(private_message)

        # Upload the new Data to save it in the Database
        Database.upload_data(Backend.encode(queried_data))

    @staticmethod
    def read_public_messages() -> list[MessageFormat]:
        """
        Read public text messages.

        Returns:
            list[MessageFormat]: A list of verified public messages.
        """
        # Query the latest Data from the Database
        queried_data = Backend.decode(Database.query_data())

        # Only verifiable Messages should be displayed
        verified_messaged: list[MessageFormat] = []
        for message in queried_data.message_stack:
            if isinstance(message, str):
                continue
            # Checking if the message is a public message
            if message.event_type not in (EventType.PUBLIC_TEXT, EventType.PUBLIC_IMAGE):
                continue
            # Signature Verification
            if message.sender_id in queried_data.verify_keys_stack:
                verify_key = queried_data.verify_keys_stack[message.sender_id]
                try:
                    # Verify the message content using the verify key
                    message.content = Cryptographer.verify_message(message.content, verify_key)
                    verified_messaged.append(message)
                except ValueError:
                    pass

        return verified_messaged

    @staticmethod
    def read_private_messages(user_id: str, private_key: str) -> list[MessageFormat]:
        """
        Read private messages for a specific receiver.

        Args:
            user_id (str): The ID of own user which tries to read private messages.
            private_key (str): The private key of the receiver used for decrypting messages.

        Returns:
            list[MessageFormat]: A list of decrypted private messages for the specified receiver.
        """
        # Query the latest Data from the Database
        queried_data = Backend.decode(Database.query_data())

        # Only decryptable Messages should be displayed
        decrypted_messages: list[MessageFormat] = []
        for message in queried_data.message_stack:
            if isinstance(message, str):
                continue
            # Checking if the message is a private message
            if message.event_type not in (EventType.PRIVATE_TEXT, EventType.PRIVATE_IMAGE):
                continue
            # Message Decryption check
            if message.receiver_id == user_id and message.sender_id in queried_data.public_keys_stack:
                try:
                    sender_public_key = queried_data.public_keys_stack[message.sender_id]
                    # Decrypt the message content using the receiver's private key and the sender's public key
                    decrypted_content = Cryptographer.decrypt_message(message.content, private_key, sender_public_key)
                    message.content = decrypted_content
                    decrypted_messages.append(message)
                except ValueError:
                    pass

        return decrypted_messages
