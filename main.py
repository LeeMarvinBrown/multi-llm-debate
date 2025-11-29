import time
import os
from datetime import datetime

from ollama_client import OllamaClient
from agent import Agent
from debate_engine import DebateEngine
from summarizer import Summarizer
import config


def save_run_to_file(
    user_prompt: str,
    debate_log: str,
    summary: str,
    debate_seconds: float,
    summary_seconds: float,
) -> None:
    """
    Save the results of a debate run to a timestamped log file.
    """
    os.makedirs("logs", exist_ok=True)

    now = datetime.now()

    # Human-readable timestamp for inside the file
    readable_timestamp = now.strftime("%m/%d/%Y - %I:%M:%S %p")

    # Filename-friendly timestamp (no slashes or colons)
    filename_timestamp = now.strftime("%Y%m%d_%H%M%S")

    filename = os.path.join("logs", f"debate_{filename_timestamp}.txt")

    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"TIMESTAMP: {readable_timestamp}\n")
        f.write(f"PROMPT:\n{user_prompt}\n\n")
        f.write(f"DEBATE TIME: {debate_seconds:.2f} seconds\n")
        f.write(f"SUMMARY TIME: {summary_seconds:.2f} seconds\n\n")

        f.write("=== SUMMARY ===\n\n")
        f.write(summary)
        f.write("\n\n=== FULL DEBATE LOG ===\n\n")
        f.write(debate_log)

    print(f"\nSaved debate and summary to: {filename}")


def main():
    client = OllamaClient()

    # Build agents from config.AGENTS
    agents = []
    for agent_cfg in config.AGENTS:
        agent = Agent(
            name=agent_cfg["name"],
            role=agent_cfg["role"],
            model=config.MODEL_NAME,
            client=client,
        )
        agents.append(agent)

    # Ask user for a prompt
    user_prompt = input("Enter your question or topic: ")

    # Set up debate
    engine = DebateEngine(
        agents=agents,
        rounds=config.ROUNDS,
    )

    # Run debate with timing
    debate_start = time.time()
    debate_log = engine.run(user_prompt)
    debate_end = time.time()
    debate_seconds = debate_end - debate_start
    print(f"\nDebate completed in {debate_seconds:.2f} seconds.")

    # Summarize result
    summarizer = Summarizer(client=client, model=config.MODEL_NAME)

    summary_start = time.time()
    summary = summarizer.summarize(user_prompt, debate_log)
    summary_end = time.time()
    summary_seconds = summary_end - summary_start
    print(f"Summary generated in {summary_seconds:.2f} seconds.")

    print("\n=== SUMMARY OF DEBATE ===\n")
    print(summary)

    # Save to log file
    save_run_to_file(
        user_prompt=user_prompt,
        debate_log=debate_log,
        summary=summary,
        debate_seconds=debate_seconds,
        summary_seconds=summary_seconds,
    )

    # Optional: show full log in console
    show_log = input("\nShow full debate log here as well? (y/n): ").strip().lower()
    if show_log.startswith("y"):
        print("\n=== FULL DEBATE LOG ===\n")
        print(debate_log)


if __name__ == "__main__":
    main()
