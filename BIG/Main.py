import os
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import threading
import subprocess


class FileIndexerApp:
    def __init__(self, master):
        self.master = master
        self.master.title("File Indexer")
        self.master.geometry("800x600")

        self.file_index = {}
        self.current_image = None

        # Load the background image
        bg_image = Image.open("mushroom_forest.jpeg")
        bg_image = bg_image.resize((1020, 1000))
        self.bg_photo = ImageTk.PhotoImage(bg_image)

        # Create a canvas and put the image on it
        self.canvas = tk.Canvas(self.master, width=1024, height=800)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.create_image(0, 0, image=self.bg_photo, anchor="nw")

        # Create a frame for other widgets
        self.frame = tk.Frame(self.canvas, bg='white', bd=5)
        self.canvas.create_window(400, 300, window=self.frame, anchor="center")

        self.create_widgets()

    def create_widgets(self):
        # Header
        self.header_label = tk.Label(self.frame, text="File Indexer - made by Sacha Brassel",
                                     font=("Arial", 16, "bold"))
        self.header_label.pack(pady=10)

        # Index button
        self.index_button = tk.Button(self.frame, text="Index Files", command=self.start_indexing)
        self.index_button.pack(pady=10)

        # Search entry
        self.search_var = tk.StringVar()
        self.search_entry = tk.Entry(self.frame, textvariable=self.search_var, width=50)
        self.search_entry.pack(pady=10)
        self.search_entry.bind('<Return>', lambda event: self.search_files())

        # Search button
        self.search_button = tk.Button(self.frame, text="Search", command=self.search_files)
        self.search_button.pack(pady=5)

        # Results listbox
        self.results_listbox = tk.Listbox(self.frame, width=80, height=20)
        self.results_listbox.pack(pady=10)
        self.results_listbox.bind('<<ListboxSelect>>', self.show_selected_file)
        self.results_listbox.bind('<Double-1>', self.open_file_in_browser)

        # Image display
        self.image_label = tk.Label(self.frame)
        self.image_label.pack(pady=10)

    def start_indexing(self):
        threading.Thread(target=self.index_files, daemon=True).start()

    def index_files(self):
        self.file_index.clear()
        for drive in self.get_drives():
            for root, _, files in os.walk(drive):
                for file in files:
                    if file.lower().endswith(
                            ('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.pdf', '.doc', '.docx', '.html')):
                        full_path = os.path.join(root, file)
                        self.file_index[full_path.lower()] = full_path
        messagebox.showinfo("Indexing Complete", f"Indexed {len(self.file_index)} files.")

    def get_drives(self):
        if os.name == 'nt':  # Windows
            return [f"{d}:\\" for d in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ' if os.path.exists(f"{d}:")]
        else:  # Unix-based systems
            return ['/']

    def search_files(self):
        query = self.search_var.get().lower()
        results = [path for path in self.file_index.values() if query in os.path.basename(path).lower()]
        self.display_results(results)

    def display_results(self, results):
        self.results_listbox.delete(0, tk.END)
        for result in results:
            self.results_listbox.insert(tk.END, result)

    def show_selected_file(self, event):
        selection = self.results_listbox.curselection()
        if selection:
            file_path = self.results_listbox.get(selection[0])
            if file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                self.display_image(file_path)
            else:
                self.image_label.config(image='')
                self.image_label.image = None

    def display_image(self, image_path):
        try:
            image = Image.open(image_path)
            image.thumbnail((300, 300))
            photo = ImageTk.PhotoImage(image)
            self.image_label.config(image=photo)
            self.image_label.image = photo
        except Exception as e:
            messagebox.showerror("Error", f"Unable to display image: {str(e)}")

    def open_file_in_browser(self, event):
        selection = self.results_listbox.curselection()
        if selection:
            file_path = self.results_listbox.get(selection[0])
            try:
                if os.name == 'nt':  # Windows
                    os.startfile(file_path)
                elif os.name == 'posix':  # macOS and Linux
                    subprocess.call(('xdg-open', file_path))
            except Exception as e:
                messagebox.showerror("Error", f"Unable to open file: {str(e)}")


if __name__ == "__main__":
    root = tk.Tk()
    app = FileIndexerApp(root)
    root.mainloop()
