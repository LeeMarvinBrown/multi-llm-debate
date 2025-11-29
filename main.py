import time
from ollama_client import OllamaClient
from agent import Agent
from debate_engine import DebateEngine

def main():
    client = OllamaClient()

    # Define two agents
    agent_a = Agent(
        name="Agent A",
        role="optimistic creative problem-solver",
        model="llama3:8b",
        client=client
    )

    agent_b = Agent(
        name="Agent B",
        role="skeptical logical analyst who critiques Agent A",
        model="llama3:8b",
        client=client
    )

    # Ask user for a prompt
    user_prompt = input("Enter your question or topic: ")

    # Set up debate
    engine = DebateEngine(
        agents=[agent_a, agent_b],
        rounds=4  # you can tweak this later
    )

    # Run debate with timing
    debate_start = time.time()
    debate_log = engine.run(user_prompt)
    debate_end = time.time()

    print(f"\nDebate completed in {debate_end - debate_start:.2f} seconds.")

    print("\n=== FULL DEBATE LOG ===\n")
    print(debate_log)


if __name__ == "__main__":
    main()
