# Global configuration for the multi-LLM debate system.

# Which Ollama model to use by default
MODEL_NAME = "llama3:8b"

# How many rounds the debate should run
ROUNDS = 4

# Define the agents participating in the debate.
# You can edit this list to change names or roles.
AGENTS = [
    {
        "name": "Agent A",
        "role": "optimistic creative problem-solver",
    },
    {
        "name": "Agent B",
        "role": "skeptical logical analyst who critiques Agent A",
    },
]
