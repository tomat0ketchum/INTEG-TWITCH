import os
import socket
import threading
import time
import re
from datetime import datetime, timedelta
from dotenv import load_dotenv
import azure.cognitiveservices.speech as speechsdk
from collections import Counter
from Azure_Voice_List import AzureVoiceList
from obs_websockets import OBSWebsocketsManager


# from azure_speech_to_text import SpeechToTextManager
def shorten_text(text, max_words=40):
    words = text.split()
    if len(words) > max_words:
        return ' '.join(words[:max_words]) + '...'
    return text
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
    directory = 'ChatLogs'
    base_filename = 'Question_For_Beta'
    extension = '.txt'
    file_path = os.path.join(directory, base_filename + extension)

    # Ensure the directory exists
    os.makedirs(directory, exist_ok=True)

    # Check if the base file already exists
    if os.path.exists(file_path):
        # File exists, find the next available file with a number
        i = 1
        while os.path.exists(os.path.join(directory, f"{base_filename}_{i}{extension}")):
            i += 1
        file_path = os.path.join(directory, f"{base_filename}_{i}{extension}")
    else:
        # Check for any numbered versions and decide the file path
        i = 1
        while os.path.exists(os.path.join(directory, f"{base_filename}_{i}{extension}")):
            i += 1
        # If i is still 1, it means no numbered files exist, use the base file path
        if i == 1:
            file_path = os.path.join(directory, base_filename + extension)
        else:
            # Reset to non-numbered version as all numbered versions exist
            file_path = os.path.join(directory, base_filename + extension)

    # Write to the determined file path
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
    elif "" in normalized_message:
        return "R"
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
    return os.path.join("TwitchChatLogs", f"{sanitized_username}_chat_messages.txt")


def ensure_directory_exists():
    if not os.path.exists("TwitchChatLogs"):
        os.makedirs("TwitchChatLogs")


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

        # AIChatMonitor attributes
        # 'coach': 'ChatLogs/CHATGPT_RESPONSE_COACH',
        # 'robo': 'ChatLogs/CHATGPT_RESPONSE_ROBO',
        # 'arthur': 'ChatLogs/CHATGPT_RESPONSE_ARTHUR',
        # 'special': 'ChatLogs/CHATGPT_RESPONSE_SPECIAL'
        self.file_paths = {
            'beta': 'ChatLogs/CHATGPT_RESPONSE_BETA',
        }
        self.last_mod_times = {key: 0.0 for key in self.file_paths}
        self.last_check_time = datetime.now()
        self.check_interval = timedelta(minutes=15)
        self.chat_collection_duration = timedelta(minutes=.5)
        self.inactivity_period = timedelta(minutes=15)
        self.special_ending_for_mic = timedelta(minutes=.1)
        self.message_buffer = []

    def monitor_files(self):
        while True:
            time.sleep(0.5)
            current_time = datetime.now()

            if current_time - self.last_check_time >= self.check_interval:
                print("Checking interval...")
                if self.check_inactivity():
                    self.send_message("I'm thinking of a response...")
                    self.collect_twitch_messages()
                print("Resetting last check time.")
                self.last_check_time = current_time

            for key, file_path in self.file_paths.items():
                if os.path.exists(file_path):
                    current_mod_time = os.path.getmtime(file_path)
                    if current_mod_time > self.last_mod_times[key]:
                        print(f"File '{file_path}' found and modified since last check. Resetting interval.")
                        self.handle_file_modification(file_path, key)
                        self.last_mod_times[key] = current_mod_time
                        time.sleep(45)
                    #    self.send_message("T0MKETCHUM 's text to speech bot is done recording twitch chat!")

    def check_inactivity(self):
        for key, file_path in self.file_paths.items():
            if os.path.exists(file_path):
                current_mod_time = os.path.getmtime(file_path)
                print(f"Checking inactivity... {current_mod_time}")
                if datetime.now() - datetime.fromtimestamp(current_mod_time) <= self.inactivity_period:
                    print("false response")
                    return False
        return True

    def collect_twitch_messages(self):
        print("Collecting Twitch messages for the next minute...")
        end_time = datetime.now() + self.chat_collection_duration
        messages = []
        result = []
        final_submission = []

        while datetime.now() < end_time:
            # Simulate collecting messages from Twitch chat
            # Replace the following line with the actual implementation of message collection
            print("Collecting...")
            message = self.get_twitch_message(timeout=30)
            if message:
                messages.append(message)
                print(f"Collected {message}")
            time.sleep(0.5)
            result.append(message)
            print(result)

        if not any(result):
            default_message = ("(Say something engaging and entertaining or controversial)\n"
                               "(The stream needs entertainment. Pick a random unique and new topic)\n"
                               "(You may receive many of these.)\n "
                               "(This is an automated message, not something to respond directly to.)\n")
            final_submission.append(default_message)
            print(f"Sending: {default_message}")
        if any(result):
            intro_message = (f"*For context this is what most recently occurred, be entertaining and engage "
                             f"with viewers*: ")
            final_submission.append(intro_message)
            # Ensure each item in result is a string before joining
            final_submission.extend([str(r) for r in result if r])

        combined_message = "\n".join(final_submission)
        write_response_to_file(combined_message)

    def get_twitch_message(self, timeout=10):
        start_time = datetime.now()
        end_time = start_time + timedelta(seconds=timeout)

        while datetime.now() < end_time:
            if self.message_buffer:
                user, message = self.message_buffer.pop(0)
                formatted_message = f"This person in Twitch chat ({user}) says: {message}"
                return formatted_message

            time.sleep(0.5)  # Sleep to reduce CPU usage

        print("Timeout reached, returning None")
        return None

    def handle_file_modification(self, file_path, key):
        print(f"Redundant sloppy coding 334")
        with open(file_path, 'r', encoding='utf-8') as file:
            text = file.read().strip()
            if text:
                print(f"Redundant sloppy coding 338")
                # Process the file content as needed
        print(f"Found file: {file_path}")

    # def process_file_content(self, text, key):
    #     # Placeholder function to process the content of the modified file
    #     # Replace with actual implementation
    #     print(f"Processing content from {key}: {text}")

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
        last_mod_time_num = 0.0  # Initialize as 0.0 to handle initial case
        last_mod_time_one = 0.0
        last_mod_time_robo = 0.0
        last_mod_time_arthur = 0.0
        last_mod_time_special = 0.0
        file_path_coach = 'ChatLogs/CHATGPT_RESPONSE_COACH'
        file_path_robo = 'ChatLogs/CHATGPT_RESPONSE_ROBO'
        file_path_arthur = 'ChatLogs/CHATGPT_RESPONSE_ARTHUR'
        file_path_special = 'ChatLogs/CHATGPT_RESPONSE_SPECIAL'
        directory = 'ChatLogs'
        beta_base_filename = 'CHATGPT_RESPONSE_BETA'
        extension = '.txt'
        while True:
            time.sleep(0.5)
            if os.path.exists(file_path_coach):
                current_mod_time = os.path.getmtime(file_path_coach)
                if current_mod_time > last_mod_time_num:
                    with open(file_path_coach, 'r', encoding='utf-8') as file:
                        text = file.read().strip()
                        if text:
                            obswebsockets_manager.set_source_visibility("In Game", "Pajama Sam", True)
                            obswebsockets_manager.set_filter_visibility("desktop", "Coach Move Filter", True)

                            # Optionally manipulate the text here if needed, similar to the second snippet
                            # For example, removing a number from the first line
                            first_line, *remaining_lines = text.split('\n')
                            first_line = re.sub(r'^\d+\s*', '', first_line)
                            text = '\n'.join([first_line] + remaining_lines)

                            print(f"Reading from file: {text}")
                            voice_region = 'en-US'
                            voice_name = 'en-US-AriaNeural'
                            style = 'newscast-casual'
                            ssml = create_ssml_emotions(voice_region, voice_name, style, text)
                            with self.synthesis_lock:
                                synthesize_emotion_with_ssml(text, ssml)

                    # If you want to remove the file after processing
                    os.remove(file_path_coach)

                    obswebsockets_manager.set_filter_visibility("desktop", "Coach Move Filter", False)
                    obswebsockets_manager.set_source_visibility("In Game", "Pajama Sam", False)
                    print(f"Deleted file: {file_path_coach}")
                    last_mod_time_num = current_mod_time  # Update last_mod_time after processing
                # Find all files that start with beta_base_filename
            all_beta_files = [f for f in os.listdir(directory) if f.startswith(beta_base_filename)]
            all_beta_files = sorted(all_beta_files, key=lambda x: os.path.getmtime(os.path.join(directory, x)))

            if all_beta_files:
                file_path_beta = os.path.join(directory, all_beta_files[0])  # Oldest file first
                current_mod_time_2 = os.path.getmtime(file_path_beta)

                if current_mod_time_2 > last_mod_time_one:  # Explicitly use last_mod_time in the comparison
                    with open(file_path_beta, 'r+', encoding='utf-8') as file:
                        text = file.read().strip()

                        if text:

                            first_line, *remaining_lines = text.split('\n')
                            first_line = re.sub(r'^\d+\s*', '', first_line)
                            text = '\n'.join([first_line] + remaining_lines)
                            obswebsockets_manager.set_source_visibility("In Game", "Beta", True)

                            obswebsockets_manager.set_filter_visibility("desktop", "Beta Move Filter", True)
                            print(f"Reading from file: {text}")
                            voice_region = 'en-US'
                            voice_name = 'en-US-JaneNeural'
                            style = 'friendly'
                            ssml = create_ssml_emotions(voice_region, voice_name, style, text)
                            shortened_text = shorten_text(text)
                            self.send_message(shortened_text)
                            with self.synthesis_lock:
                                synthesize_emotion_with_ssml(text, ssml)

                        obswebsockets_manager.set_filter_visibility("desktop", "Beta Move Filter", False)


                    time_of_now_2 = datetime.now()
                    time.sleep(0.5)
                    obswebsockets_manager.set_source_visibility("In Game", "Beta", False)
                    # print(f"Processed and updated file: {file_path_beta} {time_of_now_2}")
                    time.sleep(.5)
                    last_mod_time_one = current_mod_time_2  # Update last_mod_time after processing

                    # Delete the file after processing
                    os.remove(file_path_beta)
                    print(f"Removed {file_path_beta}")
            if os.path.exists(file_path_robo):
                current_mod_time_robo = os.path.getmtime(file_path_robo)
                if current_mod_time_robo > last_mod_time_robo:  # Explicitly use last_mod_time in the comparison
                    with open(file_path_robo, 'r', encoding='utf-8') as file:
                        text = file.read().strip()
                        if text:
                            obswebsockets_manager.set_source_visibility("In Game", "Robo Bot", True)
                            obswebsockets_manager.set_filter_visibility("desktop", "Robo Move Filter", True)
                            # removing number from first line
                            first_line, *remaining_lines = text.split('\n')
                            first_line = re.sub(r'^\d+\s*', '', first_line)
                            text = '\n'.join([first_line] + remaining_lines)

                            print(f"Reading from file: {text}")
                            voice_region = 'en-US'
                            voice_name = 'en-US-GuyNeural'
                            style = 'newscast'
                            ssml = create_ssml_emotions(voice_region, voice_name, style, text)
                            with self.synthesis_lock:
                                synthesize_emotion_with_ssml(text, ssml)
                    os.remove(file_path_robo)
                    obswebsockets_manager.set_filter_visibility("desktop", "Robo Move Filter", False)
                    obswebsockets_manager.set_source_visibility("In Game", "Robo Bot", False)
                    print(f"Deleted file: {file_path_robo}")
                    last_mod_time_robo = current_mod_time_robo  # Update last_mod_time after processing
            if os.path.exists(file_path_arthur):
                current_mod_time_arthur = os.path.getmtime(file_path_arthur)
                if current_mod_time_arthur > last_mod_time_arthur:  # Explicitly use last_mod_time in the comparison
                    with open(file_path_arthur, 'r', encoding='utf-8') as file:
                        text = file.read().strip()
                        if text:
                            obswebsockets_manager.set_source_visibility("In Game", "Arthur Bot", True)
                            obswebsockets_manager.set_filter_visibility("desktop", "Arthur Move Filter", True)
                            print(f"Reading from file: {text}")
                            voice_region = 'en-GB'
                            voice_name = 'en-GB-RyanNeural'
                            style = None
                            ssml = create_ssml_emotions(voice_region, voice_name, style, text)
                            with self.synthesis_lock:
                                synthesize_emotion_with_ssml(text, ssml)
                    os.remove(file_path_arthur)
                    obswebsockets_manager.set_filter_visibility("desktop", "Arthur Move Filter", False)
                    obswebsockets_manager.set_source_visibility("In Game", "Arthur Bot", False)
                    print(f"Deleted file: {file_path_arthur}")
                    last_mod_time_arthur = current_mod_time_arthur  # Update last_mod_time after processing
            if os.path.exists(file_path_special):
                current_mod_time_special = os.path.getmtime(file_path_special)
                if current_mod_time_special > last_mod_time_special:  # Explicitly use last_mod_time in the comparison
                    with open(file_path_special, 'r', encoding='utf-8') as file:
                        text = file.read().strip()
                        if text:
                            obswebsockets_manager.set_source_visibility("In Game", "Rapper Bot", True)
                            obswebsockets_manager.set_filter_visibility("desktop", "Rapper Move Filter", True)
                            print(f"Reading from file: {text}")
                            voice_region = 'en-US'
                            voice_name = 'en-US-JasonNeural'
                            style = 'angry'
                            ssml = create_ssml_emotions(voice_region, voice_name, style, text)
                            with self.synthesis_lock:
                                synthesize_emotion_with_ssml(text, ssml)
                    os.remove(file_path_special)
                    obswebsockets_manager.set_filter_visibility("desktop", "Rapper Move Filter", False)
                    obswebsockets_manager.set_source_visibility("In Game", "Rapper Bot", False)
                    print(f"Deleted file: {file_path_special}")
                    last_mod_time_special = current_mod_time_special  # Update last_mod_time after processing

    def twitch(self):
        self.connect_to_twitch()
        self.join_channel()
        user_voices = load_user_voice_mappings()
        user_prompt_status = {}
        ignored_users = ["streamelements", "pokemoncommunitygame", "lolrankbot", "nightbot", "sery_bot"]
        ignored_starts = ["!", "http", "https"]
        ignored_substrings = ["bitch", "sex"]
        allowed_repeats = ["O", "o", ".", "?", "m", "h"]
        max_word_length = 20
        allowed_words = ["Incomprehensibilities", "Supercalifragilisticexpialidocious", "<3", "the", "of", "a", "o",
                         "O", ".", "..", "...", "beta", "B", "b", "Beta"]
        bot_call = ["beta", "Beta", "BETA", "Beta,", "beta,", "robo", "Robo", "ROBO", "robo,", "Robo,", "Arthur",
                     "ARTHUR", "Arthur,", "arthur", "Coach", "coach", "COACH", "rapper", "RAPPER", "rapper,"]

        while True:
            time.sleep(0.5)  # Sleep to reduce CPU usage

            try:
                readbuffer = self.irc.recv(1024).decode()
                print("readbuffer 536")
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

                self.message_buffer.append((user, message))

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
                        print(f'synthesized from here line 571')
                    save_user_txt_files(user, message)  # optional recording of messages for Korie.
                    if first_message:
                        save_user_voice_mappings(user_voices=user_voices)  # Save updates if it's the first message
                    if any(message.startswith(start_2) for start_2 in bot_call):
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

        ai_monitor_thread = threading.Thread(target=self.monitor_files)
        ai_monitor_thread.daemon = True
        ai_monitor_thread.start()

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("Program exited by user")


if __name__ == "__main__":
    bot_manager = AzureBotTwitchManager()
    bot_manager.main()
