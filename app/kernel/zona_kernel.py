import re
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


class ZonaKernel:
    def __init__(self) -> None:
        self.client = OpenAI()

    def obfuscate(self, text: str) -> str:
        text = re.sub(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", "[[EMAIL]]", text)
        text = re.sub(r"\b\d{10,}\b", "[[PHONE]]", text)
        return text[::-1]

    def openai_chat(self, prompt: str) -> str:
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
        )
        content = response.choices[0].message.content
        return self.obfuscate(content)
