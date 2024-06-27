import speech_recognition
import whisper
import tempfile
import edge_tts
import asyncio
import time
from pygame import mixer 
from localisation import Localisation

class SpeechRecognizer:
    def __init__(self, lang: Localisation, whisper_model_name: str, whisper_model: whisper.Whisper) -> None:
        self.locale = lang
        self.whisper_model_name = whisper_model_name
        self.whisper_model = whisper_model

    def transcribeMicrophoneInput(self) -> str:
        rec = speech_recognition.Recognizer()
        setattr(rec, "whisper_model", dict[str, whisper.Whisper]())
        rec.whisper_model[self.whisper_model_name] = self.whisper_model
        mic = speech_recognition.Microphone()
        with mic as source:
            rec.adjust_for_ambient_noise(source)
            audio = rec.listen(source)
        speech_text = rec.recognize_whisper(audio, 
            language=self.locale.whisper_language_name,
            model=self.whisper_model_name
        )
        return speech_text


class TextToSpeech:
    def __init__(self, ms_voice_name: str) -> None:
        """
        ``ms_voice_name`` - name of Microsoft TTS voice, for example 'kk-KZ-AigulNeural'.
        See https://huggingface.co/spaces/thunder-lord/tts/blob/main/app.py for more
        """
        self.ms_voice_name = ms_voice_name

    def text_to_speech_edge(self, text) -> str:
        voice = self.ms_voice_name
        communicate = edge_tts.Communicate(text, voice)
        with tempfile.NamedTemporaryFile(delete=False, dir="records", suffix=".mp3") as tmp_file:
            tmp_path = tmp_file.name
            asyncio.run(communicate.save(tmp_path))
        return tmp_path


    def generateAndPlayAudio(self, text: str) -> None:
        tmp_mp3_path = self.text_to_speech_edge(text)
        mixer.init()
        mixer.music.load(tmp_mp3_path)
        mixer.music.play()
        while mixer.music.get_busy(): # wait for file to finish playing
            time.sleep(0.1)
        