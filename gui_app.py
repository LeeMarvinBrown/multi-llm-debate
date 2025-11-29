import tkinter as tk
from tkinter import scrolledtext, messagebox
import time
import threading

from ollama_client import OllamaClient
from agent import Agent
from debate_engine import DebateEngine
from summarizer import Summarizer
import config
from main import save_run_to_file  # reuse existing logging


class DebateApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Multi-LLM Debate Engine")

        # ===== Prompt input =====
        prompt_frame = tk.Frame(root)
        prompt_frame.pack(fill="x", padx=10, pady=5)

        tk.Label(prompt_frame, text="Enter your question or topic:").pack(anchor="w")

        self.prompt_entry = scrolledtext.ScrolledText(
            prompt_frame, height=4, wrap=tk.WORD
        )
        self.prompt_entry.pack(fill="x", pady=5)

        # ===== Settings (rounds + options) =====
        options_frame = tk.Frame(root)
        options_frame.pack(fill="x", padx=10, pady=5)

        # Rounds control
        tk.Label(options_frame, text="Rounds:").pack(side="left")
        self.rounds_var = tk.StringVar(value=str(config.ROUNDS))
        tk.Entry(options_frame, textvariable=self.rounds_var, width=5).pack(
            side="left", padx=(5, 15)
        )

        # Show full log checkbox
        self.show_full_log_var = tk.BooleanVar(value=False)
        tk.Checkbutton(
            options_frame,
            text="Show full debate log in output",
            variable=self.show_full_log_var,
        ).pack(side="left")

        # ===== Agent roles (dynamic from config) =====
        roles_frame = tk.Frame(root)
        roles_frame.pack(fill="x", padx=10, pady=5)

        tk.Label(roles_frame, text="Agent roles (edit per run):").pack(anchor="w")

        self.agent_role_entries = []
        for agent_cfg in config.AGENTS:
            row = tk.Frame(roles_frame)
            row.pack(fill="x", pady=2)

            tk.Label(row, text=f"{agent_cfg['name']} role:").pack(side="left")

            entry = tk.Entry(row)
            entry.pack(side="left", fill="x", expand=True)
            entry.insert(0, agent_cfg["role"])
            self.agent_role_entries.append(entry)

        # ===== Run button =====
        run_frame = tk.Frame(root)
        run_frame.pack(fill="x", padx=10, pady=5)

        self.run_button = tk.Button(
            run_frame,
            text="Run Debate",
            command=self.run_debate_clicked,
        )
        self.run_button.pack()

        # ===== Output area =====
        output_frame = tk.Frame(root)
        output_frame.pack(fill="both", expand=True, padx=10, pady=5)

        tk.Label(output_frame, text="Output:").pack(anchor="w")

        self.output_text = scrolledtext.ScrolledText(
            output_frame, height=20, wrap=tk.WORD
        )
        self.output_text.pack(fill="both", expand=True)

    def append_output(self, text: str):
        self.output_text.insert(tk.END, text + "\n")
        self.output_text.see(tk.END)

    # Called on main/UI thread when button is clicked
    def run_debate_clicked(self):
        prompt = self.prompt_entry.get("1.0", tk.END).strip()
        if not prompt:
            messagebox.showwarning("No prompt", "Please enter a question or topic.")
            return

        # Rounds: snapshot + validate
        try:
            rounds = int(self.rounds_var.get().strip())
            if rounds <= 0:
                raise ValueError
        except ValueError:
            rounds = config.ROUNDS  # fallback to default

        # Roles: snapshot current values, fallback to config defaults if empty
        roles_for_run = []
        for i, entry in enumerate(self.agent_role_entries):
            role_text = entry.get().strip()
            if not role_text:
                role_text = config.AGENTS[i]["role"]
            roles_for_run.append(role_text)

        # Disable button while running
        self.run_button.config(state=tk.DISABLED)
        self.output_text.delete("1.0", tk.END)
        self.append_output("Running debate... this may take a bit.\n")

        # Run the heavy work in a background thread
        thread = threading.Thread(
            target=self._run_debate_worker,
            args=(prompt, rounds, roles_for_run),
        )
        thread.daemon = True
        thread.start()

    # Background thread: does the heavy work
    def _run_debate_worker(self, prompt: str, rounds: int, roles_for_run):
        try:
            client = OllamaClient()

            # Build agents from config + user-edited roles
            agents = []
            for idx, agent_cfg in enumerate(config.AGENTS):
                role = roles_for_run[idx] if idx < len(roles_for_run) else agent_cfg["role"]
                agent = Agent(
                    name=agent_cfg["name"],
                    role=role,
                    model=config.MODEL_NAME,
                    client=client,
                )
                agents.append(agent)

            # Debate engine with progress callback
            engine = DebateEngine(
                agents=agents,
                rounds=rounds,
                progress_callback=self._progress_from_engine,
            )

            # Run debate
            debate_start = time.time()
            debate_log = engine.run(prompt)
            debate_end = time.time()
            debate_seconds = debate_end - debate_start

            # Summarize
            summarizer = Summarizer(client=client, model=config.MODEL_NAME)

            summary_start = time.time()
            summary = summarizer.summarize(prompt, debate_log)
            summary_end = time.time()
            summary_seconds = summary_end - summary_start

            # Save to file in background thread (I/O is fine here)
            save_run_to_file(
                user_prompt=prompt,
                debate_log=debate_log,
                summary=summary,
                debate_seconds=debate_seconds,
                summary_seconds=summary_seconds,
            )

            # Push final results to UI
            self.root.after(
                0,
                lambda: self._finish_run(
                    debate_seconds, summary_seconds, summary, debate_log
                ),
            )

        except Exception as e:
            self.root.after(
                0, lambda: messagebox.showerror("Error", f"An error occurred:\n{e}")
            )
        finally:
            # Re-enable button on main thread
            self.root.after(0, lambda: self.run_button.config(state=tk.NORMAL))

    # Called by DebateEngine (from background thread) to show progress
    def _progress_from_engine(self, message: str):
        self.root.after(0, lambda: self.append_output(message))

    # Runs on main thread to add final results
    def _finish_run(
        self,
        debate_seconds: float,
        summary_seconds: float,
        summary: str,
        debate_log: str,
    ):
        self.append_output(
            f"\nDebate completed in {debate_seconds:.2f} seconds.\n"
            f"Summary generated in {summary_seconds:.2f} seconds.\n"
        )

        self.append_output("\n=== SUMMARY OF DEBATE ===\n")
        self.append_output(summary)

        if self.show_full_log_var.get():
            self.append_output("\n=== FULL DEBATE LOG ===\n")
            self.append_output(debate_log)


def main():
    root = tk.Tk()
    app = DebateApp(root)
    root.geometry("900x600")
    root.mainloop()


if __name__ == "__main__":
    main()
