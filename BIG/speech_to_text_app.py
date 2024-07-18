import speech_recognition as sr
import tkinter as tk
from tkinter import scrolledtext
import threading
import pyperclip

class SpeechToTextApp:
    def __init__(self, master):
        self.master = master
        master.title("Speech to Text Converter")
        master.geometry("600x400")

        self.create_widgets()

        self.is_listening = False
        self.recognizer = sr.Recognizer()

    def create_widgets(self):
        # Control frame
        control_frame = tk.Frame(self.master)
        control_frame.pack(pady=10)

        self.listen_button = tk.Button(control_frame, text="Start Listening", command=self.toggle_listening)
        self.listen_button.pack(side=tk.LEFT, padx=5)

        self.copy_button = tk.Button(control_frame, text="Copy All", command=self.copy_text)
        self.copy_button.pack(side=tk.LEFT, padx=5)

        self.clear_button = tk.Button(control_frame, text="Clear All", command=self.clear_text)
        self.clear_button.pack(side=tk.LEFT, padx=5)

        # Scrolled text widget
        self.text_output = scrolledtext.ScrolledText(self.master, wrap=tk.WORD, width=70, height=20)
        self.text_output.pack(padx=10, pady=10, expand=True, fill=tk.BOTH)

        # Right-click menu
        self.create_right_click_menu()

    def create_right_click_menu(self):
        self.right_click_menu = tk.Menu(self.master, tearoff=0)
        self.right_click_menu.add_command(label="Copy", command=self.copy_selected)
        self.right_click_menu.add_command(label="Paste", command=self.paste_text)
        self.right_click_menu.add_separator()
        self.right_click_menu.add_command(label="Cut", command=self.cut_selected)
        self.text_output.bind("<Button-3>", self.show_right_click_menu)

    def show_right_click_menu(self, event):
        self.right_click_menu.tk_popup(event.x_root, event.y_root)

    def toggle_listening(self):
        if not self.is_listening:
            self.start_listening()
        else:
            self.stop_listening()

    def start_listening(self):
        self.is_listening = True
        self.listen_button.config(text="Stop Listening")
        self.append_text("Listening... Speak now!\n")
        threading.Thread(target=self.speech_to_text, daemon=True).start()

    def stop_listening(self):
        self.is_listening = False
        self.listen_button.config(text="Start Listening")

    def speech_to_text(self):
        with sr.Microphone() as source:
            self.recognizer.adjust_for_ambient_noise(source)
            while self.is_listening:
                try:
                    audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=5)
                    text = self.recognizer.recognize_google(audio)
                    self.master.after(0, self.append_text, f"You said: {text}\n")
                except sr.WaitTimeoutError:
                    continue
                except sr.UnknownValueError:
                    self.master.after(0, self.append_text, "Sorry, I couldn't understand what you said.\n")
                except sr.RequestError as e:
                    self.master.after(0, self.append_text, f"Could not request results; {e}\n")

    def append_text(self, message):
        self.text_output.insert(tk.END, message)
        self.text_output.see(tk.END)

    def copy_text(self):
        text = self.text_output.get("1.0", tk.END).strip()
        pyperclip.copy(text)

    def clear_text(self):
        self.text_output.delete("1.0", tk.END)

    def copy_selected(self):
        try:
            selected_text = self.text_output.get(tk.SEL_FIRST, tk.SEL_LAST)
            pyperclip.copy(selected_text)
        except tk.TclError:
            pass  # No text selected

    def paste_text(self):
        try:
            self.text_output.insert(tk.INSERT, pyperclip.paste())
        except:
            pass

    def cut_selected(self):
        try:
            selected_text = self.text_output.get(tk.SEL_FIRST, tk.SEL_LAST)
            pyperclip.copy(selected_text)
            self.text_output.delete(tk.SEL_FIRST, tk.SEL_LAST)
        except tk.TclError:
            pass  # No text selected

root = tk.Tk()
app = SpeechToTextApp(root)
root.mainloop()