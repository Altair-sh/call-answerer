import json

class Localisation:
    def __init__(self, language_code: str, whisper_language_code: str, ms_voice_name: str) -> None:
        """
        ``language_code`` - see in ./localisation/
        ``whisper_language_code`` - https://github.com/openai/whisper/blob/main/whisper/tokenizer.py
        ``ms_voice_name`` - name of tts model, for example 'facebook/mms-tts-kaz'
        """
        self.lang_code = language_code
        self.whisper_language_name = whisper_language_code
        self.ms_voice_name = ms_voice_name
        self.dictionary = json.load(open("localisation/"+language_code+".json"))

    def getStr(self, key: str) -> str:
        value: str | None = self.dictionary.get(key, None)
        if value is None:
            raise KeyError(f'key "{key}" not found in "{self.lang_code}" localisation ')
        return value