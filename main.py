import time
import os
import sys
import threading
import shutil
import llama_index.llms.openai
import llama_index.core
import logging
import openai
import keyboard
from speech import *
from localisation import *
from database import *
from question_answering import *

DEBUG: bool

if __name__ == "__main__":
    DEBUG = "--debug" in sys.argv or "debug" in sys.argv

    try:
        os.makedirs("logs", exist_ok=True)
        log_file_path = time.strftime("logs/%Y.%m.%d_%H-%M-%S.log", time.localtime())
        logging.basicConfig(stream=sys.stdout, 
                level= logging.DEBUG if DEBUG else logging.INFO)
        log = logging.getLogger()
        log_file_handler = logging.StreamHandler(open(log_file_path, "w"))
        log.addHandler(log_file_handler)

        if not os.path.exists("config.json"):
            shutil.copy("default_config.json", "config.json")
            print("error: no config")
            print("edit config.json")
            os._exit(1)
        config_file = open("config.json", "r")
        config = json.load(config_file)
        config_file.close()
        
        shutil.rmtree("records", ignore_errors=True)
        os.mkdir("records")

        os.environ["OPENAI_API_KEY"] = config["openai_api_key"]
        openai.api_key = config["openai_api_key"]
        llama_index.core.Settings.llm = llama_index.llms.openai.OpenAI(model="gpt-3.5-turbo")

        log.info("reading localisation files...")
        locales = {
            'ru': Localisation("ru", "russian", "ru-RU-SvetlanaNeural"),
            # 'kz': Localisation("kz", "kazakh", "kk-KZ-AigulNeural")
        }

        log.info("connecting to database...")
        db = Database(f'mysql+mysqlconnector://{config["db_login"]}:{config["db_password"]}@localhost/pharmacy')
        log.info("generating database indices...")
        db.generateIndices(list(locales.values()))

        whisper_model_name = config["whisper_model_name"]
        log.info(f"loading OpenAI Whisper model ({whisper_model_name})...")
        whisper_model = whisper.load_model(whisper_model_name, download_root="./models/")
        
        qa = dict[str, QAEngine]()
        rec = dict[str, SpeechRecognizer]()
        tts = dict[str, TextToSpeech]()
        for lang_code, locale in locales.items():
            log.info(f"creating Question Answering Engine ({lang_code})...")
            qa[lang_code] = QAEngine(db.getIndex(lang_code), locale, config["send_k_most_likely_variants"])

            log.info(f"creating Speech Recognizer ({lang_code})...")
            rec[lang_code] = SpeechRecognizer(locale, whisper_model_name, whisper_model)

            log.info(f"loading Text To Speech model ({lang_code})...")
            tts[lang_code] = TextToSpeech(locale.ms_voice_name)

        log.info("initialization completed!")

        while True:
            print("select language [ru/kz]: ")
            l = sys.stdin.readline().strip('\n').strip('\r')
            log.info(f"selecting '{l}' locale")
            locale = locales[l]
            log.info("playing greeting message")
            tts[l].generateAndPlayAudio(locale.getStr("greeting_message"))

            def loop(kill: threading.Event):
                while not kill.is_set():
                    try:
                        log.info("listening to microphone input")
                        question = rec[l].transcribeMicrophoneInput()
                        log.info(f'Q: "{question}"')
                        if kill.is_set():
                            break
                        
                        answer = qa[l].ask(question)
                        log.info(f'A: "{answer}"')
                        if kill.is_set():
                            break
                        
                        log.info(f'generating answer audio...')
                        tts[l].generateAndPlayAudio(answer)
                        time.sleep(1)
                    except Exception as e:
                        log.error(e)
                        log.info("playing error message")
                        tts[l].generateAndPlayAudio(locale.getStr("query_error_message"))

            loop_kill_event = threading.Event()
            loop_thread = threading.Thread(target=loop, args=(loop_kill_event,))
            loop_thread.start()

            while not keyboard.is_pressed("s"):
                time.sleep(0.05)
            loop_kill_event.set()
            if loop_thread.is_alive():
                loop_thread.join()

    except KeyboardInterrupt:
        log.info("Ctrl+C pressed!")
        os._exit(0)

