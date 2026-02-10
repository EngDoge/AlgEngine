from PIL import Image
from io import BytesIO

from google import genai

class NanoBananaGenerator:
    def __init__(self, api_key: str, model: str):
        self.client = genai.Client(
            api_key=api_key
        )
        self.model = model
        
    def generate(self, prompt: str, images: list[Image.Image] | Image.Image | None = None):
        response = self.client.models.generate_content(
            model=self.model,
            contents=[prompt, *images] if isinstance(images, list) else [prompt, images],
        )
        
        results = []
        for part in response.candidates[0].content.parts:
            text = part.text if part.text is not None else None
            image = Image.open(BytesIO(part.inline_data.data)) if part.inline_data is not None else None
            results.append((text, image))
        
        return results