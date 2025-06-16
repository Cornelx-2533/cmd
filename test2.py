import os
import platform
import subprocess
import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog

class ShellGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Flime Shell")
        self.root.geometry("900x600")
        self.theme = "dark"

        self.setup_ui()
        self.set_theme("dark")
        self.run_command("help")

    def setup_ui(self):
        self.root.columnconfigure(1, weight=1)
        self.root.rowconfigure(1, weight=1)

        # Sidebar for file explorer
        self.sidebar = tk.Listbox(self.root, width=30, bg="#1e1e1e", fg="#00ff00", font=("Consolas", 10))
        self.sidebar.grid(row=1, column=0, sticky='ns')
        self.sidebar.bind("<Double-Button-1>", self.open_selected_file)

        self.refresh_file_list()

        # Top frame for theme toggle and label
        top_frame = tk.Frame(self.root)
        top_frame.grid(row=0, column=0, columnspan=2, sticky="ew")
        self.theme_button = ttk.Button(top_frame, text="Toggle Theme", command=self.toggle_theme)
        self.theme_button.pack(side='right', padx=5, pady=5)

        # Output box
        self.output_text = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, font=("Consolas", 12), height=30)
        self.output_text.grid(row=1, column=1, sticky='nsew')
        self.output_text.tag_config("command", foreground="#00ffff")
        self.output_text.tag_config("output", foreground="#00ff00")
        self.output_text.config(state='disabled')

        # Input frame
        input_frame = tk.Frame(self.root)
        input_frame.grid(row=2, column=0, columnspan=2, sticky="ew")
        input_label = tk.Label(input_frame, text="CMD>", font=("Consolas", 12))
        input_label.pack(side='left')

        self.input_field = tk.Entry(input_frame, font=("Consolas", 12))
        self.input_field.pack(side='left', fill='x', expand=True, padx=5)
        self.input_field.bind("<Return>", self.on_enter)

    def set_theme(self, theme):
        self.theme = theme
        if theme == "dark":
            bg = "#1e1e1e"
            fg = "#ffffff"
            entry_bg = "#2e2e2e"
        else:
            bg = "#ffffff"
            fg = "#000000"
            entry_bg = "#eeeeee"

        self.root.configure(bg=bg)
        self.output_text.configure(bg=bg, fg=fg, insertbackground=fg)
        self.input_field.configure(bg=entry_bg, fg=fg, insertbackground=fg)
        self.sidebar.configure(bg=bg, fg=fg)

    def toggle_theme(self):
        new_theme = "light" if self.theme == "dark" else "dark"
        self.set_theme(new_theme)

    def refresh_file_list(self):
        self.sidebar.delete(0, tk.END)
        for item in os.listdir():
            self.sidebar.insert(tk.END, item)

    def open_selected_file(self, event=None):
        selection = self.sidebar.get(tk.ACTIVE)
        if os.path.exists(selection):
            self.run_command(f"open {selection}")

    def run_command(self, command):
        self.output_text.config(state='normal')
        self.output_text.insert(tk.END, f"> {command}\n", "command")

        parts = command.strip().split()
        cmd = parts[0].lower() if parts else ''
        args = parts[1:]

        try:
            if cmd == 'help':
                output = """
Available Commands:
  help           - Show this help message
  clear          - Clear the screen
  exit           - Exit the shell
  echo [text]    - Print the given text
  os             - Show OS information
  cwd            - Show current working directory
  ls             - List files in the current directory
  cd [path]      - Change directory
  mkdir [name]   - Create a new directory
  rm [file/dir]  - Delete a file or folder
  open [item]    - Open a file/folder with the default app
"""
            elif cmd == 'clear':
                self.output_text.delete('1.0', tk.END)
                self.output_text.config(state='disabled')
                return
            elif cmd == 'exit':
                self.root.destroy()
                return
            elif cmd == 'echo':
                output = ' '.join(args)
            elif cmd == 'os':
                output = f"OS: {platform.system()} {platform.release()}"
            elif cmd == 'cwd':
                output = os.getcwd()
            elif cmd == 'ls':
                output = '\n'.join(os.listdir())
            elif cmd == 'cd':
                if args:
                    os.chdir(args[0])
                    output = f"Changed to {os.getcwd()}"
                    self.refresh_file_list()
                else:
                    output = "Usage: cd [path]"
            elif cmd == 'mkdir':
                if args:
                    os.makedirs(args[0], exist_ok=True)
                    output = f"Directory '{args[0]}' created."
                    self.refresh_file_list()
                else:
                    output = "Usage: mkdir [name]"
            elif cmd == 'rm':
                if args:
                    path = args[0]
                    if os.path.isfile(path):
                        os.remove(path)
                        output = f"File '{path}' deleted."
                    elif os.path.isdir(path):
                        os.rmdir(path)
                        output = f"Directory '{path}' deleted."
                    else:
                        output = "Item not found."
                    self.refresh_file_list()
                else:
                    output = "Usage: rm [file/dir]"
            elif cmd == 'open':
                if args:
                    path = args[0]
                    if os.name == 'nt':
                        os.startfile(path)
                    elif os.name == 'posix':
                        subprocess.run(['open' if platform.system() == 'Darwin' else 'xdg-open', path])
                    output = f"Opened: {path}"
                else:
                    output = "Usage: open [file/folder]"
            else:
                output = f"Unknown command: {cmd}. Type 'help' for commands."

        except Exception as e:
            output = f"Error: {e}"

        self.output_text.insert(tk.END, output + "\n", "output")
        self.output_text.config(state='disabled')

    def on_enter(self, event=None):
        cmd = self.input_field.get()
        self.run_command(cmd)
        self.input_field.delete(0, tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = ShellGUI(root)
    root.mainloop()
