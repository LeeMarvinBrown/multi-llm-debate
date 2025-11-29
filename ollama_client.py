import requests
import json
from typing import List, Dict

class OllamaClient:
    """
    A clean wrapper around the local Ollama API.
    Handles streaming, parsing, and returning full responses.
    """

    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url

    def generate(self, model: str, prompt: str) -> str:
        """
        Send a text generation request to Ollama and return full output.
        """
        url = f"{self.base_url}/api/generate"
        data = {
            "model": model,
            "prompt": prompt
        }

        response = requests.post(url, json=data, stream=True)

        full_output = ""
        for line in response.iter_lines():
            if line:
                obj = json.loads(line.decode("utf-8"))
                if "response" in obj:
                    full_output += obj["response"]

        return full_output
