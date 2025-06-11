import os
import sys
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox
from datetime import datetime

# Library dependency Check
def ensure_package(package_name, import_name=None):
    import_name = import_name or package_name
    try:
        __import__(import_name)
    except ImportError:
        print(f"[INFO] Installing missing package: {package_name}")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
        except subprocess.CalledProcessError as e:
            print(f"[ERROR] Failed to install {package_name}: {e}")
            return False
    return True

# Ensure required packages
ensure_package("python-can")
if sys.platform == "win32":
    ensure_package("pywin32")

# Imports after ensuring
import can

if sys.platform == "win32":
    try:
        import ctypes
        from ctypes import windll
    except ImportError:
        print("[WARNING] Drag-and-drop support may not work on this system.")

# TRC to ASC Conversion
def convert_trc_to_asc(trc_path, asc_path):
    try:
        with open(trc_path, 'r') as trc_file:
            lines = trc_file.readlines()

        asc_lines = []
        asc_lines.append("// ASCII Logfile Version 1.10")
        asc_lines.append(f"// Date: {datetime.now().strftime('%Y-%m-%d')}\n")

        for line in lines:
            line = line.strip()
            if not line or line.startswith(";"):
                continue

            try:
                parts = line.split()
                time_offset = float(parts[1])
                can_id = parts[3].replace('h', '')
                can_id = f"0x{can_id.zfill(5)}"
                dlc = int(parts[4])
                data_bytes = " ".join(parts[5:5 + dlc])
                asc_line = f"{time_offset:.6f} 1 {can_id} Rx d {dlc} {data_bytes}"
                asc_lines.append(asc_line)
            except Exception as e:
                print(f"[WARNING] Skipping line: {line} -> {e}")
                continue

        with open(asc_path, 'w') as asc_file:
            asc_file.write("\n".join(asc_lines))

        return True, f"ASC file created:\n{asc_path}"

    except Exception as e:
        return False, str(e)

# ASC to BLF Conversion
def convert_asc_to_blf(asc_path, blf_path):
    try:
        reader = can.ASCReader(asc_path)
        writer = can.BLFWriter(blf_path)

        for msg in reader:
            writer.on_message_received(msg)

        writer.stop()
        return True, f"Arquivo BLF criado:\n{blf_path}"

    except Exception as e:
        return False, str(e)

# GUI App
class TRCConverterGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Conversor TRC para BLF")
        self.geometry("500x250")
        self.configure(bg="#f0f0f0")

        self.label = tk.Label(
            self,
            text="Clique para selecionar um arquivo .trc e converter para .blf",
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
        if sys.platform == "win32":
            try:
                self.drop_target_register = self.register_drop_target()
            except Exception as e:
                print(f"[WARNING] Arrastar pode não funcionar: {e}")

    def register_drop_target(self):
        try:
            from ctypes import windll
            windll.shell32.DragAcceptFiles(self.winfo_id(), True)
            self.bind("<Drop>", self.drop_file)
        except Exception as e:
            print(f"[ERROR] Arrastar falhou: {e}")

    def browse_file(self, _=None):
        file_path = filedialog.askopenfilename(filetypes=[("PCAN-View Trace Files", "*.trc")])
        if file_path:
            self.convert_file(file_path)

    def drop_file(self, event):
        try:
            file_path = event.data
            if file_path.startswith("{") and file_path.endswith("}"):
                file_path = file_path[1:-1]
            if os.path.isfile(file_path) and file_path.lower().endswith(".trc"):
                self.convert_file(file_path)
        except Exception as e:
            self.status.config(text=f"Error: {e}", fg="red")

    def convert_file(self, trc_path):
        asc_path = os.path.splitext(trc_path)[0] + ".asc"
        blf_path = os.path.splitext(trc_path)[0] + ".blf"

        self.status.config(text="Convertendo para ASC...", fg="blue")
        self.update_idletasks()

        success, message = convert_trc_to_asc(trc_path, asc_path)
        if not success:
            self.status.config(text=f"Error: {message}", fg="red")
            return

        self.status.config(text="Convertendo para BLF...", fg="blue")
        self.update_idletasks()

        success, message = convert_asc_to_blf(asc_path, blf_path)
        if success:
            self.status.config(text=message, fg="green")
        else:
            self.status.config(text=f"ASC ok, porém erro no BLF: {message}", fg="orange")

# Entry Point
if __name__ == "__main__":
    app = TRCConverterGUI()
    app.mainloop()