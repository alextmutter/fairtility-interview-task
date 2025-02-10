import subprocess
import platform
import shutil
import os


def find_terminal():
        for term in ["gnome-terminal", "konsole", "xfce4-terminal", "lxterminal", "alacritty", "kitty", "hyper", "xterm", "x-terminal-emulator"]:
            if shutil.which(term):
                print(term)
                return term
        return None

def run_all_scripts():
    scripts = ["naive-pipeline.py", "optimised-pipeline.py", "image-generator.py"]
    script_dir = os.path.dirname(os.path.abspath(__file__))
    terminal = find_terminal()

    for script in scripts:
        script_path = os.path.join(script_dir, script)  # Get absolute path of the script

        if platform.system() == "Windows":
            subprocess.Popen(["start", "cmd", "/k", f"python {script}"], shell=True)
        
        elif platform.system() == "Darwin":  # macOS
            subprocess.Popen([
                "osascript", "-e",
                f'tell application "Terminal" to do script "python3 {script_path}"'
            ])
        
        elif terminal:
            subprocess.Popen([terminal, "-e", f"python3 {script}"])
        
        else:
            print(f"No terminal found. Running {script} in background.")
            subprocess.Popen(["python3", script])

if __name__ == "__main__":
    run_all_scripts()
