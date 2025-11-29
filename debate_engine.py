from typing import List, Callable, Optional
from agent import Agent


class DebateEngine:
    """
    Handles the back-and-forth debate between multiple agents.
    """

    def __init__(
        self,
        agents: List[Agent],
        rounds: int = 6,
        progress_callback: Optional[Callable[[str], None]] = None,
    ):
        self.agents = agents
        self.rounds = rounds
        self.progress_callback = progress_callback

    def _notify(self, message: str) -> None:
        """
        Send progress messages either to a callback (GUI) or to stdout (CLI).
        """
        if self.progress_callback is not None:
            self.progress_callback(message)
        else:
            print(message)

    def run(self, user_prompt: str) -> str:
        """
        Run the debate and return the full conversation log.
        """
        history = f"User: {user_prompt}\n\n"

        for r in range(self.rounds):
            # r starts at 0 → for 4 rounds: 4, 3, 2, 1
            rounds_remaining = self.rounds - r

            for i, agent in enumerate(self.agents):
                reply, duration = agent.reply(history)
                history += f"{agent.name}: {reply}\n\n"

                if i == 0:
                    # First agent each round (Agent A)
                    label = "round" if rounds_remaining == 1 else "rounds"
                    self._notify(
                        f"[Round {r+1}] {agent.name} replied in {duration:.2f} seconds. "
                        f"{rounds_remaining} {label} remaining."
                    )
                else:
                    self._notify(
                        f"[Round {r+1}] {agent.name} replied in {duration:.2f} seconds."
                    )

        return history
