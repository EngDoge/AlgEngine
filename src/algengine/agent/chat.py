from openai import OpenAI

class ChatAgent:
    def __init__(self, base_url, model, api_key='', system_prompt=None):
        self._client = OpenAI(api_key=api_key, base_url=base_url)
        self._model = model
        self._base_url = base_url
        self._system_prompt = system_prompt or "You are a helpful assistant."
        
    def set_system_prompt(self, prompt: str):
        self._system_prompt = prompt
        
    def query(self, prompt: str):
        response = self._client.chat.completions.create(
            model=self._model,
            messages=[
                {"role": "system", "content": self._system_prompt},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                    ],
                },
            ],
        )
        return response.choices[0].message.content
    
    def query_image(self, image: str, prompt: str):
        response = self._client.chat.completions.create(
            model=self._model,
            messages=[
                {"role": "system", "content": self._system_prompt},
                {
                    "role": "user",
                    "content": [
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image}"}},
                        {"type": "text", "text": prompt},
                    ],
                },
            ],
        )
        return response.choices[0].message.content