import base64
import math
import random
import re
from datetime import UTC, datetime
from io import BytesIO

# Using httpx instead of requests as it is more modern and has built-in typing support
import httpx
import xxhash
from PIL import Image

from .exceptions import InvalidResponseError


class Database:
    """
    Our Database, responsible for storing and retrieving data.
    We are encoding any data into .PNG Images (lossless compression).
    Then we will store them here: https://freeimghost.net, which is a free image hosting service.
    We will later be able to query for the latest messages via https://freeimghost.net/search/images/?q={SearchTerm}
    """

    def __init__(self) -> None:
        self.session = httpx.Client()

    @staticmethod
    def base64_to_image(base64_data: str) -> bytes:
        """
        Converts arbitrary base64 encoded data to image bytes.

        Args:
            base64_data (str): The base64 encoded arbitrary data.

        Returns:
            bytes: The encoded data as image bytes.
        """
        # Decode the base64 string
        data = base64.b64decode(base64_data)
        # Prepend Custom Message Header for later Image Validation
        # We also add a random noise header to avoid duplicates
        header = b"WittyWisterias" + random.randbytes(8)
        validation_data = header + data

        # Check how many total pixels we need
        total_pixels = math.ceil(len(validation_data) / 3)
        # Calculate the size of the image (assuming square for simplicity)
        # TODO: Use a more complex, space-efficient shape to save more data if needed
        size = math.ceil(math.sqrt(total_pixels))
        # Pad the data to fit the image size
        padded_data = validation_data.ljust(size * size * 3, b"\x00")

        # Create the image bytes from the padded data
        pil_image = Image.frombytes(mode="RGB", size=(size, size), data=padded_data)
        # Save as PNG (lossless) in memory
        buffer = BytesIO()
        pil_image.save(buffer, format="PNG")
        return buffer.getvalue()

    def get_configuration_data(self) -> str:
        """
        Fetches the necessary configuration data for uploading images to the database.

        Returns:
            str: The auth token required for uploading images.

        Raises:
            AssertionError: If the configuration data cannot be fetched or the auth token is not found.
        """
        # Getting necessary configuration data for upload
        config_response = self.session.get("https://freeimghost.net/upload")
        # Check if the response is successful
        if config_response.status_code != 200:
            raise InvalidResponseError("Failed to fetch configuration data from the image hosting service.")

        # Getting auth token from config response
        auth_token_pattern = r'PF\.obj\.config\.auth_token\s*=\s*"([a-fA-F0-9]{40})";'
        match = re.search(auth_token_pattern, config_response.text)
        if not match:
            raise InvalidResponseError("Auth token not found in the configuration response.")
        # Extracting auth token
        return match.group(1)

    def upload_image(self, image_bytes: bytes) -> None:
        """
        Uploads the image bytes to the database and returns the URL.

        Args:
            image_bytes (bytes): The image bytes to upload.

        Raises:
            AssertionError: If the upload fails or the response is not as expected.
        """
        # Get current UTC time
        utc_time = datetime.now(UTC)
        # Convert to UTC Timestamp
        utc_timestamp = utc_time.timestamp()

        auth_token = self.get_configuration_data()
        # Hash the image bytes to create a checksum using xxHash64 (Specified by Image Hosting Service)
        checksum = xxhash.xxh64(image_bytes).hexdigest()

        # Post Image to Image Hosting Service
        response = self.session.post(
            url="https://freeimghost.net/json",
            files={
                "source": (f"WittyWisterias_{utc_timestamp}.png", image_bytes, "image/png"),
            },
            data={
                "type": "file",
                "action": "upload",
                "timestamp": str(int(utc_timestamp)),
                "auth_token": auth_token,
                "nsfw": "0",
                "mimetype": "image/png",
                "checksum": checksum,
            },
        )
        # Check if the response is successful
        if response.status_code != 200:
            raise InvalidResponseError("Failed to upload image to the image hosting service.")

    def upload_data(self, base64_data: str) -> None:
        """
        Uploads base64 encoded data as an image to the database hosted on the Image Hosting Service.

        Args:
            base64_data (str): The base64 encoded data to upload.

        Raises:
            AssertionError: If the upload fails or the response is not as expected.
        """
        image_bytes = self.base64_to_image(base64_data)
        self.upload_image(image_bytes)


if __name__ == "__main__":
    # Example/Testing usage
    db = Database()
    # Base64 for "Hello, World!"
    base64_string = "SGVsbG8sIFdvcmxkIQ=="
    db.upload_data(base64_string)
