import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
import os
import threading
import openai
from fpdf import FPDF

# === Your OpenAI API key ===
openai.api_key = "sk-...xCEA"  # <--- Your key here

# =======================
# Constants & Themes Setup
# =======================
LIGHT_THEME = {
    "bg": "#ffffff",
    "fg": "#000000",
    "button_bg": "#0078d7",
    "button_fg": "#ffffff",
    "entry_bg": "#f0f0f0",
    "entry_fg": "#000000",
    "tab_bg": "#e6f2ff",
    "text_bg": "#ffffff",
    "text_fg": "#000000"
}

DARK_THEME = {
    "bg": "#2e2e2e",
    "fg": "#ffffff",
    "button_bg": "#0a84ff",
    "button_fg": "#ffffff",
    "entry_bg": "#444444",
    "entry_fg": "#ffffff",
    "tab_bg": "#3a3a3a",
    "text_bg": "#1e1e1e",
    "text_fg": "#ffffff"
}

# =======================
# DATABASE SETUP
# =======================
conn = sqlite3.connect('users.db')
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS users
                  (username TEXT PRIMARY KEY, password TEXT)''')
conn.commit()

# =======================
# MAIN APP CLASS
# =======================
class ComplexTkinterApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Complex Tkinter AI App")
        self.geometry("1000x700")
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.resizable(True, True)
        self.theme = LIGHT_THEME
        self.current_user = None

        self.create_splash_screen()

    def create_splash_screen(self):
        splash = tk.Toplevel(self)
        splash.overrideredirect(True)
        splash.geometry("400x200+{}+{}".format(
            int(self.winfo_screenwidth()/2 - 200),
            int(self.winfo_screenheight()/2 - 100)
        ))
        splash.configure(bg="#0078d7")

        label = tk.Label(splash, text="Welcome to Complex AI Tkinter App", 
                         font=("Segoe UI", 16, "bold"), fg="white", bg="#0078d7")
        label.pack(expand=True)

        self.after(2000, lambda: [splash.destroy(), self.create_login_screen()])

    def create_login_screen(self):
        self.login_frame = tk.Frame(self, bg=self.theme["bg"])
        self.login_frame.pack(fill="both", expand=True)

        tk.Label(self.login_frame, text="Login", font=("Segoe UI", 20, "bold"),
                 bg=self.theme["bg"], fg=self.theme["fg"]).pack(pady=20)

        self.username_var = tk.StringVar()
        self.password_var = tk.StringVar()

        username_entry = tk.Entry(self.login_frame, textvariable=self.username_var,
                                  font=("Segoe UI", 14), bg=self.theme["entry_bg"], fg=self.theme["entry_fg"])
        username_entry.pack(pady=10, ipady=5, ipadx=10)
        username_entry.insert(0, "Username")

        password_entry = tk.Entry(self.login_frame, textvariable=self.password_var,
                                  font=("Segoe UI", 14), bg=self.theme["entry_bg"], fg=self.theme["entry_fg"], show="*")
        password_entry.pack(pady=10, ipady=5, ipadx=10)
        password_entry.insert(0, "password")

        login_btn = tk.Button(self.login_frame, text="Login", font=("Segoe UI", 14, "bold"),
                              bg=self.theme["button_bg"], fg=self.theme["button_fg"], command=self.handle_login)
        login_btn.pack(pady=10, ipadx=10, ipady=5)

        register_btn = tk.Button(self.login_frame, text="Register", font=("Segoe UI", 14, "bold"),
                                 bg=self.theme["button_bg"], fg=self.theme["button_fg"], command=self.handle_register)
        register_btn.pack(pady=10, ipadx=10, ipady=5)

    def handle_login(self):
        username = self.username_var.get()
        password = self.password_var.get()

        cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        result = cursor.fetchone()
        if result:
            self.current_user = username
            self.login_frame.destroy()
            self.create_main_ui()
        else:
            messagebox.showerror("Error", "Invalid username or password")

    def handle_register(self):
        username = self.username_var.get()
        password = self.password_var.get()
        if not username or not password or username == "Username" or password == "password":
            messagebox.showerror("Error", "Please enter a valid username and password")
            return
        try:
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
            messagebox.showinfo("Success", "User registered successfully")
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Username already exists")

    def create_main_ui(self):
        self.configure(bg=self.theme["bg"])

        # Menu Bar
        menubar = tk.Menu(self)
        self.config(menu=menubar)
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Export Text", command=self.export_text)
        file_menu.add_separator()
        file_menu.add_command(label="Logout", command=self.logout)
        file_menu.add_command(label="Exit", command=self.on_closing)

        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Toggle Theme", command=self.toggle_theme)

        # Main Notebook Tabs
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True)

        # File Explorer Tab
        self.file_explorer_tab = tk.Frame(self.notebook, bg=self.theme["bg"])
        self.notebook.add(self.file_explorer_tab, text="File Explorer")
        self.create_file_explorer_ui()

        # Python Shell Tab
        self.shell_tab = tk.Frame(self.notebook, bg=self.theme["bg"])
        self.notebook.add(self.shell_tab, text="Python Shell")
        self.create_shell_ui()

        # AI Assistant Tab
        self.assistant_tab = tk.Frame(self.notebook, bg=self.theme["bg"])
        self.notebook.add(self.assistant_tab, text="AI Assistant")
        self.create_ai_assistant_ui()

    def create_file_explorer_ui(self):
        # Left Frame: Directory Tree and Search
        left_frame = tk.Frame(self.file_explorer_tab, bg=self.theme["bg"], width=250)
        left_frame.pack(side="left", fill="y", padx=5, pady=5)

        search_label = tk.Label(left_frame, text="Search Files:", bg=self.theme["bg"], fg=self.theme["fg"])
        search_label.pack(anchor="nw", padx=5)
        self.search_var = tk.StringVar()
        search_entry = tk.Entry(left_frame, textvariable=self.search_var, bg=self.theme["entry_bg"], fg=self.theme["entry_fg"])
        search_entry.pack(fill="x", padx=5, pady=5)
        self.search_var.trace_add("write", self.update_file_list)

        self.file_listbox = tk.Listbox(left_frame, bg=self.theme["entry_bg"], fg=self.theme["entry_fg"])
        self.file_listbox.pack(fill="both", expand=True, padx=5, pady=5)
        self.file_listbox.bind("<<ListboxSelect>>", self.load_selected_file)

        # Right Frame: File Content Editor
        right_frame = tk.Frame(self.file_explorer_tab, bg=self.theme["bg"])
        right_frame.pack(side="right", fill="both", expand=True, padx=5, pady=5)

        self.file_content_text = tk.Text(right_frame, bg=self.theme["text_bg"], fg=self.theme["text_fg"])
        self.file_content_text.pack(fill="both", expand=True)

        # Buttons
        btn_frame = tk.Frame(right_frame, bg=self.theme["bg"])
        btn_frame.pack(fill="x", pady=5)

        save_btn = tk.Button(btn_frame, text="Save File", bg=self.theme["button_bg"], fg=self.theme["button_fg"],
                             command=self.save_file)
        save_btn.pack(side="left", padx=5, ipadx=5, ipady=3)

        open_btn = tk.Button(btn_frame, text="Open File", bg=self.theme["button_bg"], fg=self.theme["button_fg"],
                             command=self.open_file_dialog)
        open_btn.pack(side="left", padx=5, ipadx=5, ipady=3)

        # Initialize file list
        self.current_directory = os.getcwd()
        self.all_files = []
        self.update_file_list()

    def update_file_list(self, *args):
        search_text = self.search_var.get().lower()
        self.file_listbox.delete(0, tk.END)
        self.all_files = []
        for root, dirs, files in os.walk(self.current_directory):
            for file in files:
                if search_text in file.lower():
                    filepath = os.path.join(root, file)
                    self.all_files.append(filepath)
                    display_name = os.path.relpath(filepath, self.current_directory)
                    self.file_listbox.insert(tk.END, display_name)
        if self.file_listbox.size() > 0:
            self.file_listbox.select_set(0)
            self.load_selected_file()

    def load_selected_file(self, event=None):
        try:
            index = self.file_listbox.curselection()
            if not index:
                return
            filepath = self.all_files[index[0]]
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            self.file_content_text.delete(1.0, tk.END)
            self.file_content_text.insert(tk.END, content)
            self.current_open_file = filepath
        except Exception as e:
            print("Error loading file:", e)

    def save_file(self):
        try:
            if hasattr(self, 'current_open_file') and self.current_open_file:
                content = self.file_content_text.get(1.0, tk.END)
                with open(self.current_open_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                messagebox.showinfo("Saved", f"File saved: {self.current_open_file}")
            else:
                self.open_file_dialog()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save file: {e}")

    def open_file_dialog(self):
        file_path = filedialog.askopenfilename(initialdir=self.current_directory)
        if file_path:
            self.current_open_file = file_path
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            self.file_content_text.delete(1.0, tk.END)
            self.file_content_text.insert(tk.END, content)

    def create_shell_ui(self):
        shell_frame = tk.Frame(self.shell_tab, bg=self.theme["bg"])
        shell_frame.pack(fill="both", expand=True, padx=5, pady=5)

        self.shell_output = tk.Text(shell_frame, bg=self.theme["text_bg"], fg=self.theme["text_fg"])
        self.shell_output.pack(fill="both", expand=True)

        self.shell_input_var = tk.StringVar()
        shell_input_entry = tk.Entry(shell_frame, textvariable=self.shell_input_var,
                                     bg=self.theme["entry_bg"], fg=self.theme["entry_fg"])
        shell_input_entry.pack(fill="x", pady=5)
        shell_input_entry.bind("<Return>", self.execute_shell_command)

        shell_btn_frame = tk.Frame(shell_frame, bg=self.theme["bg"])
        shell_btn_frame.pack(fill="x")

        run_btn = tk.Button(shell_btn_frame, text="Run", bg=self.theme["button_bg"], fg=self.theme["button_fg"],
                            command=self.execute_shell_command)
        run_btn.pack(side="left", padx=5, ipadx=5, ipady=3)

        clear_btn = tk.Button(shell_btn_frame, text="Clear", bg=self.theme["button_bg"], fg=self.theme["button_fg"],
                              command=lambda: self.shell_output.delete(1.0, tk.END))
        clear_btn.pack(side="left", padx=5, ipadx=5, ipady=3)

    def execute_shell_command(self, event=None):
        cmd = self.shell_input_var.get()
        if not cmd.strip():
            return
        self.shell_output.insert(tk.END, f">>> {cmd}\n")
        self.shell_input_var.set("")

        # Simple Python eval exec sandbox
        try:
            result = eval(cmd, {}, {})
            if result is not None:
                self.shell_output.insert(tk.END, str(result) + "\n")
        except Exception as e_eval:
            try:
                exec(cmd, {}, {})
            except Exception as e_exec:
                self.shell_output.insert(tk.END, f"Error: {e_exec}\n")

        self.shell_output.see(tk.END)

    def create_ai_assistant_ui(self):
        top_frame = tk.Frame(self.assistant_tab, bg=self.theme["bg"])
        top_frame.pack(fill="x", padx=5, pady=5)

        prompt_label = tk.Label(top_frame, text="Ask AI Assistant:", bg=self.theme["bg"], fg=self.theme["fg"])
        prompt_label.pack(side="left")

        self.ai_prompt_var = tk.StringVar()
        ai_prompt_entry = tk.Entry(top_frame, textvariable=self.ai_prompt_var, bg=self.theme["entry_bg"], fg=self.theme["entry_fg"])
        ai_prompt_entry.pack(side="left", fill="x", expand=True, padx=5)
        ai_prompt_entry.bind("<Return>", self.ask_ai)

        ask_btn = tk.Button(top_frame, text="Ask", bg=self.theme["button_bg"], fg=self.theme["button_fg"], command=self.ask_ai)
        ask_btn.pack(side="left", padx=5)

        clear_btn = tk.Button(top_frame, text="Clear", bg=self.theme["button_bg"], fg=self.theme["button_fg"], command=self.clear_ai_output)
        clear_btn.pack(side="left", padx=5)

        self.ai_output_text = tk.Text(self.assistant_tab, bg=self.theme["text_bg"], fg=self.theme["text_fg"])
        self.ai_output_text.pack(fill="both", expand=True, padx=5, pady=5)

    def ask_ai(self, event=None):
        prompt = self.ai_prompt_var.get().strip()
        if not prompt:
            return

        self.ai_output_text.insert(tk.END, f">>> You: {prompt}\n")
        self.ai_prompt_var.set("")
        self.ai_output_text.see(tk.END)

        def thread_ask():
            try:
                response = openai.Completion.create(
                    engine="text-davinci-003",
                    prompt=prompt,
                    max_tokens=200,
                    n=1,
                    stop=None,
                    temperature=0.7,
                )
                answer = response.choices[0].text.strip()
                self.ai_output_text.insert(tk.END, f"🤖 AI: {answer}\n\n")
            except Exception as e:
                self.ai_output_text.insert(tk.END, f"Error communicating with AI: {e}\n\n")
            self.ai_output_text.see(tk.END)

        threading.Thread(target=thread_ask).start()

    def clear_ai_output(self):
        self.ai_output_text.delete(1.0, tk.END)

    def toggle_theme(self):
        if self.theme == LIGHT_THEME:
            self.theme = DARK_THEME
        else:
            self.theme = LIGHT_THEME
        self.apply_theme()

    def apply_theme(self):
        # Apply theme colors to all widgets
        self.configure(bg=self.theme["bg"])
        for widget in self.winfo_children():
            self.recursive_theme_apply(widget)

    def recursive_theme_apply(self, widget):
        cls = widget.__class__.__name__
        if cls in ["Frame", "LabelFrame"]:
            widget.configure(bg=self.theme["bg"])
        elif cls == "Label":
            widget.configure(bg=self.theme["bg"], fg=self.theme["fg"])
        elif cls == "Button":
            widget.configure(bg=self.theme["button_bg"], fg=self.theme["button_fg"], activebackground=self.theme["button_bg"])
        elif cls == "Entry":
            widget.configure(bg=self.theme["entry_bg"], fg=self.theme["entry_fg"], insertbackground=self.theme["fg"])
        elif cls == "Text":
            widget.configure(bg=self.theme["text_bg"], fg=self.theme["text_fg"], insertbackground=self.theme["fg"])
        elif cls == "Listbox":
            widget.configure(bg=self.theme["entry_bg"], fg=self.theme["entry_fg"])
        for child in widget.winfo_children():
            self.recursive_theme_apply(child)

    def export_text(self):
        # Export content from current tab text widgets to file
        current_tab = self.notebook.index(self.notebook.select())
        text_content = ""
        if current_tab == 0:  # File Explorer
            text_content = self.file_content_text.get(1.0, tk.END)
        elif current_tab == 1:  # Python Shell
            text_content = self.shell_output.get(1.0, tk.END)
        elif current_tab == 2:  # AI Assistant
            text_content = self.ai_output_text.get(1.0, tk.END)
        else:
            messagebox.showinfo("Export", "No exportable content in this tab.")
            return

        if not text_content.strip():
            messagebox.showinfo("Export", "There is no content to export.")
            return

        filetypes = [("Text Files", "*.txt"), ("Markdown Files", "*.md"), ("PDF Files", "*.pdf")]
        filename = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=filetypes)

        if not filename:
            return

        try:
            if filename.endswith(".pdf"):
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", size=12)
                for line in text_content.splitlines():
                    pdf.cell(0, 10, txt=line, ln=True)
                pdf.output(filename)
            else:
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(text_content)
            messagebox.showinfo("Export", f"Content exported successfully to:\n{filename}")
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export content:\n{e}")

    def logout(self):
        answer = messagebox.askyesno("Logout", "Are you sure you want to logout?")
        if answer:
            self.current_user = None
            self.notebook.destroy()
            self.create_login_screen()

    def on_closing(self):
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            conn.close()
            self.destroy()

if __name__ == "__main__":
    app = ComplexTkinterApp()
    app.mainloop()
