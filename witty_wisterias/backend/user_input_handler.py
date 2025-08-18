import base64
import json

import httpx
from websockets.sync.client import connect

# Global HTTP Session for the User Input Handler
HTTP_SESSION = httpx.Client(timeout=30)


class UserInputHandler:
    """
    UserInputHandler class to convert images to text and text to images, to help the Theme "Wrong tool for the job".
    Which also gets Implemented in the Frontend User Input and converted here.
    """

    @staticmethod
    def image_to_text(image_base64: str) -> str:
        """
        Converts a base64 encoded image to text using https://olmocr.allenai.org.

        Args:
            image_base64 (str): A base64-encoded string representing the image.

        Returns:
            str: The text extracted from the image.
        """
        # Connecting to the WebSocket OCR server
        with connect("wss://olmocr.allenai.org/api/ws", max_size=10 * 1024 * 1024) as websocket:
            # Removing the "data:image/jpeg;base64," prefix if it exists
            image_base64 = image_base64.removeprefix("data:image/jpeg;base64,")
            # Sending the base64 image to the WebSocket server
            websocket.send(json.dumps({"fileChunk": image_base64}))
            websocket.send(json.dumps({"endOfFile": True}))

            # Receiving the response from the server
            while True:
                response_str = websocket.recv()
                response_json = json.loads(response_str)

                # Check if the response contains the final processed data
                if response_json.get("type") == "page_complete":
                    # Getting the Response data
                    page_data = response_json.get("data", {}).get("response", {})
                    # Returning the extracted Text
                    extracted_text: str = page_data.get("natural_text", "No text found.")
                    return extracted_text

    @staticmethod
    def text_to_image(text: str) -> str:
        """
        Converts text to an image link using https://pollinations.ai/

        Args:
            text (str): The text to convert to an image.

        Returns:
            str: The base64 encoded generated image.
        """
        # Lowest Quality for best Speed (and low Database Usage)
        generation_url = f"https://image.pollinations.ai/prompt/{text}?width=256&height=256&quality=low"
        # Getting the Generated Image Content
        generated_image = HTTP_SESSION.get(generation_url).content
        # Encode the image content to base64
        return base64.b64encode(generated_image).decode("utf-8")
