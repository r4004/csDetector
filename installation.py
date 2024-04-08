import tkinter as tk
from tkinter import filedialog, ttk
import os
import subprocess

class DirectorySelectorApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Installazione csDetector")
        self.master.geometry("500x300")

        default_path = os.getcwd()
        self.project_directory = ""

        main_frame = ttk.Frame(self.master, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Frame label and button
        left_frame = ttk.Frame(main_frame, padding="10")
        left_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        right_frame = ttk.Frame(main_frame, padding="10")
        right_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Labels and Button
        labels = ["Seleziona la directory del tuo progetto", "Clona repo", "Avvia ambiente virtuale", "Avvia web services"]
        buttons_text = ["Scegli Directory", "Clone Repo", "Start", "Web"]
        commands = [lambda: self.select_directory(default_path, self.label1),
                    lambda: self.cloneRepo(self.label1),
                    lambda: self.activateEnv(),
                    lambda: self.startWebServices()]

        for i, label_text in enumerate(labels):
            label = ttk.Label(left_frame, text=label_text, font=("Helvetica", 14))
            label.grid(row=i, column=0, sticky=tk.W, pady=5)

            button_text = buttons_text[i]
            button_command = commands[i]
            button = ttk.Button(right_frame, text=button_text, command=button_command)
            button.grid(row=i, column=0, sticky=tk.W, pady=5)

        # Label selected path
        self.label1 = tk.Label(self.master, text=f"{default_path}", font=("Helvetica", 12))
        self.label1.grid(row=1, column=0, columnspan=2, pady=10)
    
    def openTerminal(self, commands):
        subprocess.run(" && ".join(commands), shell=True, check=True)

    def cloneRepo(self, label_select):
        self.project_directory = label_select.cget("text")
        text = self.project_directory
        commands = [f"cd {text}",
                    "git clone https://github.com/PaoloCarmine1201/csDetector.git"
                    ]
        
        # Open terminal
        try:
            self.openTerminal(commands)
            #time.sleep(5)
        except Exception as e:
            print("terminal opening error", e)
        self.createFolder()

    def select_directory(self, initial_dir, label_scelta):
        selected_directory = filedialog.askdirectory(initialdir=initial_dir)
        if selected_directory:
            label_scelta.config(text=f"{selected_directory}")

    def createFolder(self):
        self.project_directory = self.project_directory+"/csDetector"
        
        sentiPath = os.path.join(self.project_directory, "sentiStrenght")
        outPath = os.path.join(self.project_directory, "out")

        if not os.path.exists(sentiPath) or not os.path.exists(outPath) :
            os.makedirs(sentiPath)
            os.makedirs(outPath)
        else:
            raise Exception("At least one of the two folders already exists")
        
        self.createEnv()

    def createEnv(self):
        comandi = [f"cd {self.project_directory}",
                    "python3.8 -m venv .venv"
                    ]
        # Apri il terminale
        try:
            self.openTerminal(comandi)
            print("Env activated successfully")
            #time.sleep(5)
        except Exception as e:
            print("terminal opening error", e)
    
    def activateEnv(self):
        commands = [f"cd {self.project_directory}",
                    "source .venv/bin/activate",
                    "pip install -r requirements.txt",
                    "python3 -m spacy download en_core_web_sm"
                    ]
        
        try:
            self.openTerminal(commands)
            #time.sleep(5)
        except Exception as e:
            print("terminal opening error", e)
    
    def startWebServices(self):
        if self.project_directory == "":
            self.project_directory = self.label1.cget("text")

        
        self.activateEnv()
        commands = [f"cd {self.project_directory}",
                    "source .venv/bin/activate",
                    "python csDetectorWebService.py"
                    ]
        
        try:
            self.openTerminal(commands)
            #time.sleep(5)
        except Exception as e:
            print("terminal opening error", e)

if __name__ == "__main__":
    root = tk.Tk()
    app = DirectorySelectorApp(root)
    root.mainloop()