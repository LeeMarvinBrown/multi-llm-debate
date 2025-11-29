from ollama_client import OllamaClient

class Agent:
    """
    Represents one debating agent with a role/personality.
    """

    def __init__(self, name: str, role: str, model: str, client: OllamaClient):
        self.name = name
        self.role = role
        self.model = model
        self.client = client

    def reply(self, conversation_history: str) -> str:
        """
        Generate a reply based on the full conversation history.
        """
        system_prompt = (
            f"You are {self.name}. Your persona: {self.role}.\n"
            f"Respond thoughtfully and concisely. Stay in character."
        )

        full_prompt = system_prompt + "\n\n" + conversation_history

        return self.client.generate(self.model, full_prompt)
