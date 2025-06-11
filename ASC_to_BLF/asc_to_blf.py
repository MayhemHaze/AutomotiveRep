import os
import tkinter as tk
from tkinter import filedialog, messagebox
import can

class ASCtoBLFConverterApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Conversor ASC para BLF")
        self.geometry("500x250")
        self.configure(bg="#f0f0f0")

        self.label = tk.Label(
            self,
            text="Clique aqui para selecionar o arquivo .asc",
            bg="#e0e0e0",
            fg="#333",
            font=("Arial", 14),
            width=50,
            height=5,
            relief="groove",
            bd=2
        )
        self.label.pack(pady=40)
        self.label.bind("<Button-1>", self.browse_file)

        self.status = tk.Label(self, text="", bg="#f0f0f0", fg="green", font=("Arial", 10))
        self.status.pack(pady=10)

        self.try_enable_dragdrop()

    def try_enable_dragdrop(self):
        if os.name == "nt":
            try:
                from ctypes import windll
                windll.shell32.DragAcceptFiles(self.winfo_id(), True)
                self.bind("<Drop>", self.drop_file)
            except Exception as e:
                print(f"[WARNING] Arrastar e Clicar pode não funcionar: {e}")

    def browse_file(self, _=None):
        file_path = filedialog.askopenfilename(filetypes=[("ASC CAN Log Files", "*.asc")])
        if file_path:
            self.convert_file(file_path)

    def drop_file(self, event):
        try:
            file_path = event.data
            if file_path.startswith("{") and file_path.endswith("}"):
                file_path = file_path[1:-1]
            if os.path.isfile(file_path) and file_path.lower().endswith(".asc"):
                self.convert_file(file_path)
        except Exception as e:
            self.status.config(text=f"Error: {e}", fg="red")

    def convert_file(self, asc_path):
        blf_path = os.path.splitext(asc_path)[0] + ".blf"
        self.status.config(text="Convertendo", fg="blue")
        self.update_idletasks()

        try:
            with open(asc_path, 'r') as asc_file:
                reader = can.ASCReader(asc_file)
                messages = list(reader)

            with can.BLFWriter(blf_path) as writer:
                for msg in messages:
                    writer.write(msg)

            self.status.config(text=f"Conversão completa:\n{blf_path}", fg="green")
        except Exception as e:
            self.status.config(text=f"Error: {e}", fg="red")

if __name__ == "__main__":
    app = ASCtoBLFConverterApp()
    app.mainloop()
