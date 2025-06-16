import os
import platform
import subprocess
from colorama import init, Fore, Style

init(autoreset=True)

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def show_help():
    print(Fore.CYAN + """
Available Commands:
  help           - Show this help message
  clear          - Clear the screen
  exit           - Close/Exit the shell
  echo [text]    - Print the given text
  os             - Show OS information
  cwd            - Show current working directory
  ls             - List files in the current directory
  cd [path]      - Change directory
  mkdir [name]   - Create a new directory
  rm [file/dir]  - Delete a file or folder
  open [item]    - Open a file/folder with the default app
""")

def list_files():
    for f in os.listdir():
        print(Fore.YELLOW + f)

def change_directory(path):
    try:
        os.chdir(path)
        print(Fore.GREEN + f"Changed directory to {os.getcwd()}")
    except FileNotFoundError:
        print(Fore.RED + "Directory not found.")
    except Exception as e:
        print(Fore.RED + f"Error: {e}")

def make_directory(name):
    try:
        os.makedirs(name)
        print(Fore.GREEN + f"Directory '{name}' created.")
    except FileExistsError:
        print(Fore.YELLOW + "Directory already exists.")
    except Exception as e:
        print(Fore.RED + f"Error: {e}")

def delete_item(path):
    try:
        if os.path.isfile(path):
            os.remove(path)
            print(Fore.GREEN + f"File '{path}' deleted.")
        elif os.path.isdir(path):
            os.rmdir(path)
            print(Fore.GREEN + f"Directory '{path}' deleted.")
        else:
            print(Fore.RED + "Item not found.")
    except Exception as e:
        print(Fore.RED + f"Error: {e}")

def open_item(path):
    try:
        if os.name == 'nt':  # Windows
            os.startfile(path)
        elif os.name == 'posix':
            subprocess.run(['xdg-open', path])
        else:
            print(Fore.RED + "Unsupported OS for open command.")
    except Exception as e:
        print(Fore.RED + f"Error opening item: {e}")

def main():
    clear_screen()
    print(Fore.MAGENTA + "🔧 Custom Python Shell - Type 'help' for a list of commands.")

    while True:
        try:
            command = input(Fore.BLUE + "CMD> ").strip()
            if not command:
                continue

            parts = command.split()
            cmd = parts[0].lower()
            args = parts[1:]

            if cmd == 'help':
                show_help()
            elif cmd == 'clear':
                clear_screen()
            elif cmd == 'exit':
                print(Fore.CYAN + "Exiting shell.")
                break
            elif cmd == 'echo':
                print(' '.join(args))
            elif cmd == 'os':
                print(f"OS: {platform.system()} {platform.release()}")
            elif cmd == 'cwd':
                print(f"Current Directory: {os.getcwd()}")
            elif cmd == 'ls':
                list_files()
            elif cmd == 'cd':
                if args:
                    change_directory(args[0])
                else:
                    print(Fore.YELLOW + "Usage: cd [path]")
            elif cmd == 'mkdir':
                if args:
                    make_directory(args[0])
                else:
                    print(Fore.YELLOW + "Usage: mkdir [directory_name]")
            elif cmd == 'rm':
                if args:
                    delete_item(args[0])
                else:
                    print(Fore.YELLOW + "Usage: rm [file_or_folder_name]")
            elif cmd == 'open':
                if args:
                    open_item(args[0])
                else:
                    print(Fore.YELLOW + "Usage: open [file_or_folder]")
            else:
                print(Fore.RED + f"Unknown command: {cmd}. Type 'help' to see available commands.")

        except KeyboardInterrupt:
            print(Fore.YELLOW + "\nUse 'exit' to quit.")
        except Exception as e:
            print(Fore.RED + f"An error occurred: {e}")

if __name__ == "__main__":
    main()
