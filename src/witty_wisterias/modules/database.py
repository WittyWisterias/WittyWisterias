import base64
import math
from io import BytesIO

from PIL import Image


class Database:
    """
    Our Database, responsible for storing and retrieving data.
    We are encoding any data into .PNG Images (lossless compression).
    Then we will store them here: https://freeimghost.net, which is a free image hosting service.
    We will later be able to query for the latest messages via https://freeimghost.net/search/images/?q={SearchTerm}
    """

    def __init__(self) -> None:
        pass

    @staticmethod
    def base64_to_image(base64_string: str) -> bytes:
        """
        Converts arbitrary base64 encoded data to image bytes.

        Args:
            base64_string (str): The base64 encoded arbitrary data.

        Returns:
            bytes: The encoded data as image bytes.
        """
        # Decode the base64 string
        data = base64.b64decode(base64_string)
        # Prepend Custom Message Header for later Image Validation
        header = b"WittyWisterias"
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


if __name__ == "__main__":
    # Example/Testing usage
    db = Database()
    # Base64 for "Hello, World!"
    base64_string = "SGVsbG8sIFdvcmxkIQ=="
    image_bytes = db.base64_to_image(base64_string)
    # Save the image bytes to a file for validation/verification
    with open("output_image.png", "wb") as f:
        f.write(image_bytes)
    print("Image created successfully.")
