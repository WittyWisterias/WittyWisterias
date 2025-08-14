import base64

import httpx
import regex as re
from bs4 import BeautifulSoup

from .exceptions import InvalidResponseError

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
        Converts a base64 encoded image to text using https://freeocr.ai/.

        Args:
            image_base64 (str): A base64-encoded string representing the image.

        Returns:
            str: The text extracted from the image.
        """
        # Getting some Cookies etc.
        page_resp = HTTP_SESSION.get("https://freeocr.ai/")
        # Getting All JS Scripts from the Page
        soup = BeautifulSoup(page_resp.text, "html.parser")
        js_script_links = [script.get("src") for script in soup.find_all("script") if script.get("src")]
        # Getting Page Script Content
        page_js_script: str | None = next((src for src in js_script_links if "page-" in src), None)
        if not page_js_script:
            raise InvalidResponseError("Could not find the page script in the response.")
        page_script_content = HTTP_SESSION.get("https://freeocr.ai" + page_js_script).text
        # Getting the Next-Action by searching for a 42 character long hex string
        next_action_search = re.search(r"[a-f0-9]{42}", page_script_content)
        if not next_action_search:
            raise InvalidResponseError("Could not find Next-Action in the response.")
        next_action = next_action_search.group(0)

        # Posting to the OCR service
        resp = HTTP_SESSION.post(
            "https://freeocr.ai/",
            json=["data:image/jpeg;base64," + image_base64],
            headers={
                "Next-Action": next_action,
                "Next-Router-State-Tree": "%5B%22%22%2C%7B%22children%22%3A%5B%5B%22locale%22%2C%22de%22%2"
                "C%22d%22%5D%2C%7B%22children%22%3A%5B%22__PAGE__%22%2C%7B%7D%2C"
                "%22%2Fde%22%2C%22refresh%22%5D%7D%2Cnull%2Cnull%2Ctrue%5D%7D%5D",
            },
        )
        # Removing Content Headers to extract the text
        extracted_text: str = resp.text.splitlines()[1][3:-1]
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
