import requests
import json

def ask_ollama(model: str, prompt: str) -> str:
    """
    Send a simple generate request to the local Ollama server
    and return the full response text.
    """
    url = "http://localhost:11434/api/generate"
    data = {
        "model": model,
        "prompt": prompt
    }

    # stream=True lets us read chunks as they come
    response = requests.post(url, json=data, stream=True)

    full_output = ""
    for line in response.iter_lines():
        if line:
            obj = json.loads(line.decode("utf-8"))
            if "response" in obj:
                full_output += obj["response"]
    return full_output


if __name__ == "__main__":
    prompt = "Hello! Write me a short poem about futuristic trees."
    answer = ask_ollama("llama3:8b", prompt)

    print("\nPROMPT:\n")
    print(prompt)

    print("\nMODEL RESPONSE:\n")
    print(answer)
