import os
import tkinter as tk
from tkinter import filedialog
import can

class ASCtoBLFConverterApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Conversor ASC para BLF")
        self.geometry("500x250")
        self.configure(bg="#f0f0f0")

        self.label = tk.Label(
            self,
            text="Clique para selecionar o arquivo .asc",
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

    def browse_file(self, _=None):
        file_path = filedialog.askopenfilename(filetypes=[("ASC CAN Log Files", "*.asc")])
        if file_path:
            self.convert_file(file_path)

    def convert_file(self, asc_path):
        blf_path = os.path.splitext(asc_path)[0] + ".blf"
        self.status.config(text="Convertendo...", fg="blue")
        self.update_idletasks()

        try:
            with open(asc_path, 'r') as asc_file:
                reader = can.ASCReader(asc_file)
                messages = list(reader)

            writer = can.BLFWriter(blf_path)
            for msg in messages:
                if isinstance(msg, can.Message):
                    writer.on_message_received(msg)
            writer.stop() 

            self.status.config(text=f"Conversão completa:\n{blf_path}", fg="green")
        except Exception as e:
            self.status.config(text=f"Error: {e}", fg="red")

if __name__ == "__main__":
    app = ASCtoBLFConverterApp()
    app.mainloop()
