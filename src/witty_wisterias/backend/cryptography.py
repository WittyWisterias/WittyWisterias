import base64
import random

from nacl.public import Box, PrivateKey, PublicKey
from nacl.signing import SigningKey, VerifyKey


class Cryptography:
    """
    A class to handle cryptographic operations of our chat App.
    Handles Public-Key Encryption and Digital Signatures of messages.
    """

    @staticmethod
    def generate_random_user_id() -> str:
        """
        Generates a random UserID which will be 48bit (fits exactly 2 RGB pixels).
        Note: The chance that two users having the same UserID is 1 in 281,474,976,710,656.
              So for this CodeJam, we can safely assume that this will never happen and don't check for Duplicates.

        Returns:
            str: A random 48-bit UserID encoded in base64.
        """
        # Generate random 48-bit integer (0 to 2^48 - 1)
        user_id_bits = random.getrandbits(48)
        # Convert to bytes (6 bytes for 48 bits)
        user_id_bytes = user_id_bits.to_bytes(6, byteorder="big")
        # Encode to base64
        return base64.b64encode(user_id_bytes).decode("utf-8")

    @staticmethod
    def generate_signing_key_pair() -> tuple[str, str]:
        """
        Generates a new base64-encoded signing-verify key pair for signing messages.

        Returns:
            str: The base64-encoded signing key.
            str: The base64-encoded verify key.
        """
        # Generate a new signing key
        nacl_signing_key = SigningKey.generate()
        nacl_verify_key = nacl_signing_key.verify_key
        # Encode the keys in base64
        encoded_signing_key = base64.b64encode(nacl_signing_key.encode()).decode("utf-8")
        encoded_verify_key = base64.b64encode(nacl_verify_key.encode()).decode("utf-8")
        # Return the signing key and its verify key in base64 encoding
        return encoded_signing_key, encoded_verify_key

    @staticmethod
    def generate_encryption_key_pair() -> tuple[str, str]:
        """
        Generates a new base64-encoded private-public key pair.

        Returns:
            str: The base64-encoded private key.
            str: The base64-encoded public key.
        """
        # Generate a new private key
        nacl_private_key = PrivateKey.generate()
        nacl_public_key = nacl_private_key.public_key
        # Encode the keys in base64
        encoded_private_key = base64.b64encode(nacl_private_key.encode()).decode("utf-8")
        encoded_public_key = base64.b64encode(nacl_public_key.encode()).decode("utf-8")
        # Return the private key and its public key in base64 encoding
        return encoded_private_key, encoded_public_key

    @staticmethod
    def sign_message(message: str, signing_key: str) -> str:
        """
        Signs a message using the provided signing key.

        Args:
            message (str): The message to sign.
            signing_key (str): The base64-encoded signing key.

        Returns:
            str: The signed, base64-encoded message.
        """
        # Decode the signing key from base64
        signing_key_bytes = base64.b64decode(signing_key)
        # Create a SigningKey object
        nacl_signing_key = SigningKey(signing_key_bytes)
        # Sign the message
        signed_message = nacl_signing_key.sign(message.encode("utf-8"))
        return base64.b64encode(signed_message).decode("utf-8")

    @staticmethod
    def verify_message(signed_message: str, verify_key: str) -> str:
        """
        Verifies a signed message using the provided verify key.

        Args:
            signed_message (str): The signed, base64-encoded message.
            verify_key (str): The base64-encoded verify key.

        Returns:
            str: The original message if verification is successful.

        Raises:
            ValueError: If the verification fails.
        """
        # Decode the signed message and verify key from base64
        signed_message_bytes = base64.b64decode(signed_message)
        verify_key_bytes = base64.b64decode(verify_key)
        # Create a VerifyKey object
        nacl_verify_key = VerifyKey(verify_key_bytes)
        # Verify the signed message
        try:
            verified_message: bytes = nacl_verify_key.verify(signed_message_bytes)
            return verified_message.decode("utf-8")
        except Exception as e:
            raise ValueError("Verification failed") from e

    @staticmethod
    def encrypt_message(message: str, sender_private_key: str, recipient_public_key: str) -> str:
        """
        Encrypts a message using the recipient's public key and the sender's private key.

        Args:
            message (str): The message to encrypt.
            sender_private_key (str): The sender's private key in base64 encoding.
            recipient_public_key (str): The recipient's public key in base64 encoding.

        Returns:
            str: The encrypted, base64-encoded message.
        """
        # Decode the keys from base64
        sender_private_key_bytes = base64.b64decode(sender_private_key)
        recipient_public_key_bytes = base64.b64decode(recipient_public_key)
        # Create the Box for encryption
        nacl_box = Box(PrivateKey(sender_private_key_bytes), PublicKey(recipient_public_key_bytes))
        # Encrypt the message
        encrypted_message = nacl_box.encrypt(message.encode("utf-8"))
        return base64.b64encode(encrypted_message).decode("utf-8")

    @staticmethod
    def decrypt_message(encrypted_message: str, recipient_private_key: str, sender_public_key: str) -> str:
        """
        Decrypts a message using the recipient's private key and the sender's public key.

        Args:
            encrypted_message (str): The encrypted, base64-encoded message.
            recipient_private_key (str): The recipient's private key in base64 encoding.
            sender_public_key (str): The sender's public key in base64 encoding.

        Returns:
            str: The decrypted message.
        """
        # Decode the keys from base64
        recipient_private_key_bytes = base64.b64decode(recipient_private_key)
        sender_public_key_bytes = base64.b64decode(sender_public_key)
        # Create the Box for decryption
        nacl_box = Box(PrivateKey(recipient_private_key_bytes), PublicKey(sender_public_key_bytes))
        # Decode the encrypted message from base64
        encrypted_message_bytes = base64.b64decode(encrypted_message)
        # Decrypt the message
        decrypted_message: bytes = nacl_box.decrypt(encrypted_message_bytes)
        return decrypted_message.decode("utf-8")
