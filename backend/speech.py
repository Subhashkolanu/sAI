"""
=========================================================
sAI V1 - Speech Engine
=========================================================
Speech Recognition + Text-to-Speech
Supports:
- SpeechRecognition
- Edge TTS
- pyttsx3 (offline fallback)
=========================================================
"""

from __future__ import annotations

import asyncio
import os
import tempfile

import speech_recognition as sr
import pyttsx3
import edge_tts

from config import (
    VOICE_RATE,
    VOICE_VOLUME,
    MIC_TIMEOUT,
    MIC_PHRASE_LIMIT,
)


class SpeechEngine:
    def __init__(self):

        self.recognizer = sr.Recognizer()

        self.tts = pyttsx3.init()

        self.tts.setProperty("rate", VOICE_RATE)
        self.tts.setProperty("volume", VOICE_VOLUME)

    # -------------------------------------------------

    def listen(self):

        with sr.Microphone() as source:

            self.recognizer.adjust_for_ambient_noise(source, duration=1)

            print("Listening...")

            audio = self.recognizer.listen(
                source,
                timeout=MIC_TIMEOUT,
                phrase_time_limit=MIC_PHRASE_LIMIT,
            )

        try:

            text = self.recognizer.recognize_google(audio)

            return text

        except sr.UnknownValueError:

            return ""

        except Exception:

            return ""

    # -------------------------------------------------

    def speak(self, text: str):

        if not text:
            return

        self.tts.say(text)
        self.tts.runAndWait()

    # -------------------------------------------------

    async def edge_speak(self, text: str):

        if not text:
            return

        with tempfile.NamedTemporaryFile(
            suffix=".mp3",
            delete=False,
        ) as tmp:

            filename = tmp.name

        communicate = edge_tts.Communicate(
            text=text,
            voice="en-US-AriaNeural",
        )

        await communicate.save(filename)

        os.system(f'"{filename}"')

    # -------------------------------------------------

    def speak_hd(self, text: str):

        try:

            asyncio.run(self.edge_speak(text))

        except Exception:

            self.speak(text)

    # -------------------------------------------------

    def test(self):

        self.speak("Speech engine is working.")