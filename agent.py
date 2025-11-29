import time
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

    def reply(self, conversation_history: str):
        """
        Generate a reply based on the full conversation history.
        Also return how long it took to generate.
        """

        system_prompt = (
            f"You are {self.name}. Your persona: {self.role}.\n"
            "You are participating in a structured debate with other agents.\n"
            "Your goals:\n"
            "- Think clearly and logically.\n"
            "- Express your position precisely.\n"
            "- Avoid filler phrases and enthusiasm.\n"
            "- Do NOT talk about this being a debate or conversation.\n"
            "- Do NOT describe yourself as an agent or say things like "
            "  'Here's my response', 'As Agent A', or 'I will now respond'. "
            "Just answer directly.\n"
            "- Do NOT praise the other agent or the conversation.\n"
            "- Do NOT repeat long portions of what has already been said.\n"
            "- Focus on new reasoning, refinements, or counterpoints.\n"
            "- Aim for ~150–250 tokens (2–4 short paragraphs).\n"
            "- Write in a calm, neutral, professional tone.\n"
            "\n"
            "Real-world references:\n"
            "- When it genuinely strengthens your argument, you MAY briefly refer to real-world "
            "  examples, experiments, or well-known studies (e.g. 'some pilots in Finland', "
            "  'a well-known study on basic income').\n"
            "- Use these references sparingly.\n"
            "- Do NOT invent highly specific details like exact paper titles, author lists, or years "
            "  unless you are very sure. If uncertain, keep it general ('some research suggests...').\n"
        )

        full_prompt = system_prompt + "\n\n" + conversation_history

        start = time.time()
        output = self.client.generate(self.model, full_prompt)
        end = time.time()

        duration = end - start
        return output, duration
