import os
import socket
import threading
import time
import re
from datetime import datetime
from dotenv import load_dotenv
import azure.cognitiveservices.speech as speechsdk
from collections import Counter
from Azure_Voice_List import AzureVoiceList
from obs_websockets import OBSWebsocketsManager


def get_user(line):
    separate = line.split("!", 1)
    user = separate[0].split(":")[1]
    return user


def create_ssml_emotions(voice_region, voice_name, style, text):
    return (f'<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xmlns:mstts="http://www.w3.org'
            f'/2001/mstts" xml:lang="{voice_region}"><voice name="{voice_name}"><mstts:express-as '
            f'style="{style}">{text}'
            f'</mstts:express-as></voice></speak>')


def write_response_to_file(response):
    file_path = 'ChatLogs/Question_For_Beta'
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(response)


def create_small_ssml(voice_region, voice_name, text):
    return (
        f'<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="{voice_region}"><voice name="'
        f'{voice_name}">{text}</voice></speak>')


def allowed_repeated_characters(word, allowed_repeats):
    if any(char in allowed_repeats for char in word) and all(
            char in allowed_repeats for char in word.strip("".join(allowed_repeats))
    ):
        return True
    for char in set(word):
        if word.count(char) >= 6 and char not in allowed_repeats:
            return False
        if char not in allowed_repeats and word.count(char * 4) > 0:
            return False
    return True


def is_spam_message(msgs, allowed_words, allowed_repeats, max_word_length):
    words = msgs.lower().split()
    word_counts = Counter(words)

    for word, count in word_counts.items():
        if word in allowed_words:
            continue
        if count > 3:
            return True
        if len(word) > max_word_length:
            return True
        if not allowed_repeated_characters(word, allowed_repeats):
            return True
    return False


def load_user_voice_mappings(filename="user_voices_2.txt"):
    user_voices = {}
    try:
        with open(filename, "r", encoding="utf-8") as file:
            for line in file:
                parts = line.strip().split(",")
                user = parts[0]
                voice_details = (parts[1], parts[2], parts[3] if parts[3] != 'None' else None, parts[4])
                user_voices[user] = (voice_details, True)
    except FileNotFoundError:
        pass
    return user_voices


def extract_preference_from_message(message):
    normalized_message = message.strip().lower()
    if "m " in normalized_message or normalized_message.startswith("m"):
        return "M"
    elif "f " in normalized_message or normalized_message.startswith("f"):
        return "F"
    elif "random" in normalized_message:
        return "Random"
    return None


def synthesize_emotion_with_ssml(text, ssml):
    speech_config = speechsdk.SpeechConfig(
        subscription=os.getenv("AZURE_TTS_KEY"), region=os.getenv("AZURE_TTS_REGION")
    )
    speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config)
    result = speech_synthesizer.speak_ssml_async(ssml).get()
    if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        print(f"Speech synthesized for text [{text}]")
    elif result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = result.cancellation_details
        print(f"Speech synthesis canceled: {cancellation_details.reason}")


def save_user_voice_mappings(filename="user_voices_2.txt", user_voices=None):
    if user_voices is None:
        user_voices = {}

    with open(filename, "w", encoding="utf-8") as file:
        for user, (voice_details, _) in user_voices.items():
            voice_details_serialized = ','.join(
                [str(detail if detail is not None else 'None') for detail in voice_details])
            file.write(f"{user},{voice_details_serialized}\n")


def get_or_assign_voice_id(user, user_voices, user_pref):
    if user in user_voices:
        voice_details, first_message = user_voices[user]
        return voice_details, first_message
    else:
        user_pref = user_pref.get(user, {"gender": "RANDOM", "region": None})
        preferred_gender = user_pref.get("gender", "RANDOM")
        preferred_region = user_pref.get("region")
        new_voice_details = AzureVoiceList.get_voice_by_preference(preferred_gender, preferred_region)
        if not new_voice_details:
            raise ValueError("No available voices left for the specified preferences")
        user_voices[user] = (new_voice_details, True)
        return new_voice_details, True


def synthesize_message(user, message, user_voices, user_picked):
    if user not in user_voices:
        voice_details, first_message = get_or_assign_voice_id(user, user_voices, user_picked)
        user_voices[user] = (voice_details, True)
    else:
        voice_details, first_message = user_voices[user]
    text = f"{user} says {message}" if first_message else message
    user_voices[user] = (voice_details, False)
    voice_region, voice_name, emotion, _ = voice_details
    ssml_template = create_ssml_emotions(voice_region, voice_name, emotion,
                                         text) if emotion else create_small_ssml(
        voice_region, voice_name, text)
    synthesize_emotion_with_ssml(message, ssml_template)


def sanitize_username(user):
    return re.sub(r"\W+", "_", user)


def get_file_path(user):
    sanitized_username = sanitize_username(user)
    return os.path.join("ChatLogs", f"{sanitized_username}_chat_messages.txt")


def ensure_directory_exists():
    if not os.path.exists("ChatLogs"):
        os.makedirs("ChatLogs")


def write_initial_message_to_file(file_path, user):
    if not os.path.exists(file_path):
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(f"This is all of the chat messages produced by {user}\n")
        print(f"{user} has a new txt document.")


def write_date_to_file(file_path):
    current_date = datetime.now().strftime("%Y-%m-%d")
    with open(file_path, "r+", encoding="utf-8") as file:
        content = file.read()
        last_date_line = f"{current_date} _____________________\n"
        if last_date_line not in content:
            file.seek(0, os.SEEK_END)
            file.write(last_date_line)
            print(f"Date line added for {current_date} in {file_path}.")


def append_message_to_file(file_path, user, message):
    write_date_to_file(file_path)
    with open(file_path, "a", encoding="utf-8") as file:
        file.write(f"{message}\n")
    print(f"{user} said '{message}' and it was recorded in the txt document.")


def save_user_txt_files(user, message):
    ensure_directory_exists()
    file_path = get_file_path(user)
    write_initial_message_to_file(file_path, user)
    append_message_to_file(file_path, user, message)


class AzureBotTwitchManager:
    def __init__(self):
        self.env_path = os.path.join(os.path.dirname(__file__), 'EnvKeys', '.env')
        load_dotenv(self.env_path)

        self.server = os.getenv("TWITCH_SERVER")
        self.port = int(os.getenv("TWITCH_PORT"))
        self.bot_oath_code = os.getenv("BOT_OATH_CODE")
        self.bot_name = os.getenv("TWITCH_BOT_NAME")
        self.channel_monitoring = os.getenv("LOWERCASE_CHANNEL_NAME")
        self.irc = socket.socket()
        self.assigned_voice_ids = set()
        self.user_preferences = {}

    def connect_to_twitch(self):
        self.irc.connect((self.server, self.port))
        self.irc.send(f"PASS {self.bot_oath_code}\n".encode("utf-8"))
        self.irc.send(f"NICK {self.bot_name}\n".encode("utf-8"))
        self.irc.send(f"JOIN #{self.channel_monitoring}\n".encode("utf-8"))

    def join_channel(self):
        loading = True
        while loading:
            readbuffer_join = self.irc.recv(1024).decode()
            for line in readbuffer_join.split("\n")[0:-1]:
                if "End of /NAMES list" in line:
                    print(f"{self.bot_name} has joined {self.channel_monitoring}'s Channel.")
                    self.send_message("T0MKETCHUM 's text to speech bot is now active!")
                    loading = False

    def send_message(self, message):
        message_temp = f"PRIVMSG #{self.channel_monitoring} :{message}\r\n"
        self.irc.send(message_temp.encode("utf-8"))

    def get_message(self, line):
        try:
            message = line.split("PRIVMSG #" + self.channel_monitoring + " :")[1]
        except IndexError:
            message = ""
        return message

    synthesis_lock = threading.Lock()

    def check_file(self):
        obswebsockets_manager = OBSWebsocketsManager()
        last_mod_time = 0.0  # Initialize as 0.0 to handle initial case
        file_path = 'ChatLogs/CHATGPT_RESPONSE_1'
        while True:
            time.sleep(0.5)
            if os.path.exists(file_path):
                current_mod_time = os.path.getmtime(file_path)
                obswebsockets_manager.set_source_visibility("In Game", "Pajama Sam", True)
                if current_mod_time > last_mod_time:  # Explicitly use last_mod_time in the comparison
                    with open(file_path, 'r', encoding='utf-8') as file:
                        text = file.read().strip()
                        if text:
                            print(f"Reading from file: {text}")
                            voice_region = 'en-US'
                            voice_name = 'en-US-AriaNeural'
                            style = 'narration-professional'
                            ssml = create_ssml_emotions(voice_region, voice_name, style, text)
                            with self.synthesis_lock:
                                synthesize_emotion_with_ssml(text, ssml)
                    os.remove(file_path)
                    obswebsockets_manager.set_source_visibility("In Game", "Pajama Sam", False)
                    print(f"Deleted file: {file_path}")
                    last_mod_time = current_mod_time  # Update last_mod_time after processing

    def twitch(self):
        self.connect_to_twitch()
        self.join_channel()
        user_voices = load_user_voice_mappings()
        user_prompt_status = {}
        ignored_users = ["streamelements", "pokemoncommunitygame", "lolrankbot", "nightbot"]
        ignored_starts = ["!", "http", "https"]
        ignored_substrings = ["bitch", "sex"]
        allowed_repeats = ["O", "o", ".", "?", "m", "h"]
        max_word_length = 20
        allowed_words = ["Incomprehensibilities", "Supercalifragilisticexpialidocious", "<3", "the", "of", "a", "o",
                         "O", ".", "..", "...", "beta", "B", "b", "Beta"]
        beta_call = ["beta", "Beta"]

        while True:
            time.sleep(0.5)  # Sleep to reduce CPU usage

            try:
                readbuffer = self.irc.recv(1024).decode()
            except Exception as e:
                print(e)
                continue

            for line in readbuffer.split("\r\n"):
                if line == "":
                    continue
                if line.startswith("PING"):
                    self.irc.send("PONG :tmi.twitch.tv\r\n".encode("utf-8"))
                    continue

                user = get_user(line)
                message = self.get_message(line)
                if (user in ignored_users or any(message.startswith(start) for start in ignored_starts)
                        or any(substring in message for substring in ignored_substrings)
                        or is_spam_message(message, allowed_words, allowed_repeats, max_word_length)):
                    continue

                if user not in user_voices:
                    if user not in user_prompt_status:
                        self.ask_user_m_or_f(user, user_prompt_status)
                        user_prompt_status[user] = "pending"
                    elif user_prompt_status[user] == "pending":
                        preference = extract_preference_from_message(message)
                        if preference:
                            self.user_preferences[user] = {"gender": preference}
                            user_prompt_status[user] = "responded"
                            self.send_message(
                                f"{user}, your voice preference '{preference}' has been recorded. Thank you!\r\n")
                            voice_details, _ = get_or_assign_voice_id(user, user_voices, self.user_preferences)
                            user_voices[user] = (voice_details, True)
                            save_user_voice_mappings(user_voices=user_voices)  # Save after assigning new voice
                        else:
                            self.send_message(f"{user}, please specify 'M', 'F', or 'Random' for your "
                                              f"voice preference. Your response was not understood.\r\n")
                else:
                    voice_details, first_message = get_or_assign_voice_id(user, user_voices, self.user_preferences)
                    with self.synthesis_lock:
                        synthesize_message(user, message, user_voices, self.user_preferences)
                    save_user_txt_files(user, message)  # optional recording of messages for Korie.
                    if first_message:
                        save_user_voice_mappings(user_voices=user_voices)  # Save updates if it's the first message
                    if any(message.startswith(start_2) for start_2 in beta_call):
                        formatted_message = f"This person in Twitch chat ({user}) says: {message}"
                        write_response_to_file(formatted_message)


    def ask_user_m_or_f(self, user, user_prompt_status):
        self.send_message(
            f"@{user}, please choose a type of voice you'd like, M (Male), F (Female), or R (Random)!\r\n")
        user_prompt_status[user] = "pending"
        print(f"Asked {user} to choose a voice type.")

    def main(self):
        t1 = threading.Thread(target=self.twitch, daemon=True)
        t1.start()

        file_thread = threading.Thread(target=self.check_file)
        file_thread.daemon = True
        file_thread.start()

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("Program exited by user")


if __name__ == "__main__":
    bot_manager = AzureBotTwitchManager()
    bot_manager.main()
