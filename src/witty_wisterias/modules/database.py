import base64
import math
import random
import re
from datetime import UTC, datetime
from io import BytesIO

# Using httpx instead of requests as it is more modern and has built-in typing support
import httpx
import xxhash
from bs4 import BeautifulSoup
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
    def extract_timestamp(url: str) -> float:
        """
        Extracts the timestamp from the Filename of a given URL in our format.

        Args:
            url (str): The URL from which to extract the timestamp.

        Returns:
            float: The extracted timestamp as a float.
        """
        # Use regex to find the timestamp in the URL
        match = re.search(r"(\d+\.\d+)", url)
        if match:
            return float(match.group(1))
        return 0.0

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
            InvalidResponseError: If the configuration data cannot be fetched or the auth token is not found.
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
            InvalidResponseError: If the upload fails or the response is not as expected.
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

    def query_data(self) -> str:
        """
        Queries the latest data from the database.

        Returns:
            str: The latest data.

        Raises:
            InvalidResponseError: If the query fails or the response is not as expected.
        """
        # Query all images with the search term "WittyWisterias" from the image hosting service
        response = self.session.get("https://freeimghost.net/search/images/?q=WittyWisterias")
        # Check if the response is successful
        if response.status_code != 200:
            raise InvalidResponseError("Failed to query latest image from the image hosting service.")

        # Extracting the latest image URL from the response using beautifulsoup
        soup = BeautifulSoup(response.text, "html.parser")
        # Find all image elements which are hosted on the image hosting service
        image_links = [img.get("src") for img in soup.find_all("img") if "https://freeimghost.net/" in img.get("src")]

        # Sort the image elements by the timestamp in the filename (in the link) (newest first)
        sorted_image_links = sorted(image_links, key=self.extract_timestamp, reverse=True)

        # Find the first image link that contains our validation header and return its pixel byte data
        for image_link in sorted_image_links:
            # Fetch the image content
            image_content = self.session.get(image_link).content

            # Get the byte content of the image without the PNG Image File Header
            image_stream = BytesIO(image_content)
            pil_image = Image.open(image_stream).convert("RGB")
            pixel_byte_data = pil_image.tobytes()

            # Validate the image content starts with our validation header
            if pixel_byte_data.startswith(b"WittyWisterias"):
                # Remove the validation header and noise bytes from the first valid image
                no_header_data = pixel_byte_data[len(b"WittyWisterias") + 8 :]
                # Remove any padding bytes (if any) to get the original data
                no_padding_data = no_header_data.rstrip(b"\x00")
                # Decode bytes into string and return it
                decoded_data: str = no_padding_data.decode("utf-8", errors="ignore")
                return decoded_data

        # If no valid image is found, raise an error
        raise InvalidResponseError("No valid image found in the response.")

    def upload_data(self, base64_data: str) -> None:
        """
        Uploads base64 encoded data as an image to the database hosted on the Image Hosting Service.

        Args:
            base64_data (str): The base64 encoded data to upload.

        Raises:
            InvalidResponseError: If the upload fails or the response is not as expected.
        """
        image_bytes = self.base64_to_image(base64_data)
        self.upload_image(image_bytes)


if __name__ == "__main__":
    # Example/Testing usage
    db = Database()
    # Base64 for "Hello, World!"
    base64_string = base64.b64encode(b"Hello, World! Witty Wisterias.").decode("utf-8")
    db.upload_data(base64_string)
    print(db.query_data())
