"""
My first application
"""
import speech_recognition as sr
import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW


class HelloWorld(toga.App):
    def speech_to_text():
        # Create a recognizer object
        recognizer = sr.Recognizer()

        # Use the default microphone as the audio source
        with sr.Microphone() as source:
            print("Listening... Speak now!")

            # Adjust for ambient noise
            recognizer.adjust_for_ambient_noise(source)

            # Listen for audio input
            audio = recognizer.listen(source)

        try:
            # Use Google Speech Recognition to convert audio to text
            text = recognizer.recognize_google(audio)
            print("You said:", text)
            return text
        except sr.UnknownValueError:
            print("Sorry, I couldn't understand what you said.")
        except sr.RequestError as e:
            print("Could not request results from the speech recognition service; {0}".format(e))

    # Run the speech-to-text function
    speech_to_text()

    def main():
        return None

