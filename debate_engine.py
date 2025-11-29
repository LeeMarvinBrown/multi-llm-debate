from typing import List
from agent import Agent

class DebateEngine:
    """
    Handles the back-and-forth debate between multiple agents.
    """

    def __init__(self, agents: List[Agent], rounds: int = 6):
        self.agents = agents
        self.rounds = rounds

    def run(self, user_prompt: str) -> str:
        """
        Run the debate and return the full conversation log.
        """
        history = f"User: {user_prompt}\n\n"

        for r in range(self.rounds):
            for agent in self.agents:
                reply, duration = agent.reply(history)
                history += f"{agent.name}: {reply}\n\n"
                print(f"[Round {r+1}] {agent.name} replied in {duration:.2f} seconds.")

        return history
