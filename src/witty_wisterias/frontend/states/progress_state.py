import asyncio
from collections.abc import AsyncGenerator

import reflex as rx


class ProgressState(rx.State):
    """The Placebo Progress State"""

    # Own User Data
    progress: str = ""

    @rx.event(background=True)
    async def public_message_progress(self) -> AsyncGenerator[None, None]:
        """Simulates the progress of sending a public message with a placebo progress bar."""
        public_message_states = [
            "Pulling Message Stack...",
            "Signing Message...",
            "Pushing Signed Message...",
            "Uploading new Message Stack...",
            "",
        ]

        for message in public_message_states:
            async with self:
                # A small text fade-in animation
                self.progress = ""
                for char in message:
                    self.progress += char
                    await asyncio.sleep(0.005)
                    yield

            # Simulate some processing time (different for each state)
            match message:
                case "Pulling Message Stack...":
                    await asyncio.sleep(0.5)
                case "Signing Message...":
                    await asyncio.sleep(0.3)
                case "Pushing Signed Message...":
                    await asyncio.sleep(0.3)
                case "Uploading new Message Stack...":
                    await asyncio.sleep(1)
                case "":
                    pass

    @rx.event(background=True)
    async def private_message_progress(self) -> AsyncGenerator[None, None]:
        """Simulates the progress of sending a private message with a placebo progress bar."""
        public_message_states = [
            "Pulling Message Stack...",
            "Encrypting Message...",
            "Pushing Encrypted Message...",
            "Uploading new Message Stack...",
            "",
        ]

        for message in public_message_states:
            async with self:
                # A small text fade-in animation
                self.progress = ""
                for char in message:
                    self.progress += char
                    await asyncio.sleep(0.005)
                    yield

            # Simulate some processing time (different for each state)
            match message:
                case "Pulling Message Stack...":
                    await asyncio.sleep(0.5)
                case "Encrypting Message...":
                    await asyncio.sleep(0.3)
                case "Pushing Encrypted Message...":
                    await asyncio.sleep(0.3)
                case "Uploading new Message Stack...":
                    await asyncio.sleep(1)
                case "":
                    pass
