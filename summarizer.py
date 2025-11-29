from ollama_client import OllamaClient

class Summarizer:
    """
    Uses the LLM to read the full debate log and produce a concise,
    structured summary for the user.
    """

    def __init__(self, client: OllamaClient, model: str = "llama3:8b"):
        self.client = client
        self.model = model

    def summarize(self, user_prompt: str, debate_log: str) -> str:
        """
        Summarize the debate with a focus on:
        - final answer / conclusion
        - key points from both sides
        - notable disagreements or alternatives
        """
        instruction = (
            "You are a neutral judge summarizing a debate between two AI agents.\n"
            "Write in a clear, concise, professional tone.\n"
            "Avoid filler phrases and emotional reactions (no 'interesting conversation', "
            "'fantastic debate', etc.).\n"
            "Your job is to:\n"
            "1. Give the best final answer to the user's question.\n"
            "2. Briefly list key points that were raised by the agents.\n"
            "3. Mention any major disagreements or alternative viewpoints.\n"
            "4. Keep it relatively concise (no more than ~400–500 words).\n"
        )

        prompt = (
            f"{instruction}\n\n"
            f"User's original question:\n{user_prompt}\n\n"
            f"Full debate log:\n{debate_log}\n\n"
            "Now respond in this exact structure:\n"
            "FINAL ANSWER:\n"
            "<your best consolidated answer here>\n\n"
            "KEY POINTS:\n"
            "- point 1\n- point 2\n- ...\n\n"
            "DISAGREEMENTS OR ALTERNATIVES:\n"
            "- item 1\n- item 2\n"
        )

        return self.client.generate(self.model, prompt)
