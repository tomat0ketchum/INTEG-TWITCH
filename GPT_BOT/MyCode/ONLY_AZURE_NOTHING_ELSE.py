import socket
import threading
import time
import os
import azure.cognitiveservices.speech as speechsdk
from datetime import datetime
import re
from dotenv import load_dotenv
from Azure_Voice_List import AzureVoiceList
from collections import Counter

env_path = os.path.join(os.path.dirname(__file__), 'EnvKeys', '.env')
load_dotenv(env_path)

server = os.getenv("TWITCH_SERVER")
port = int(os.getenv("TWITCH_PORT"))
bot_oath_code = os.getenv("BOT_OATH_CODE")
bot_name = os.getenv("TWITCH_BOT_NAME")
channel_monitoring = os.getenv("LOWERCASE_CHANNEL_NAME")
irc = socket.socket()
assigned_voice_ids = set()
user_preferences = {}


def connect_to_twitch():
    irc.connect((server, port))
    irc.send(f"PASS {bot_oath_code}\n".encode("utf-8"))
    irc.send(f"NICK {bot_name}\n".encode("utf-8"))
    irc.send(f"JOIN #{channel_monitoring}\n".encode("utf-8"))


def join_channel():
    loading = True
    while loading:
        readbuffer_join = irc.recv(1024).decode()
        for line in readbuffer_join.split("\n")[0:-1]:
            if "End of /NAMES list" in line:
                print(f"{bot_name} has joined {channel_monitoring}'s Channel.")
                send_message("T0MKETCHUM 's text to speech bot is now active!")
                loading = False


def send_message(message):
    message_temp = f"PRIVMSG #{channel_monitoring} :{message}\r\n"
    irc.send(message_temp.encode("utf-8"))


def get_user(line):
    separate = line.split("!", 1)
    user = separate[0].split(":")[1]
    return user


def get_message(line):
    try:
        message = line.split("PRIVMSG #" + channel_monitoring + " :")[1]
    except IndexError:
        message = ""
    return message


def create_ssml_emotions(voice_region, voice_name, style, text):
    return (f'<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xmlns:mstts="http://www.w3.org'
            f'/2001/mstts" xml:lang="{voice_region}"><voice name="{voice_name}"><mstts:express-as '
            f'style="{style}">{text}'
            f'</mstts:express-as></voice></speak>')


def create_small_ssml(voice_region, voice_name, text):
    return (f'<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="{voice_region}"><voice name="'
            f'{voice_name}">{text}</voice></speak>')


def twitch():
    connect_to_twitch()
    join_channel()
    user_voices = load_user_voice_mappings()
    user_prompt_status = {}
    # List of users to ignore
    ignored_users = ["streamelements", "pokemoncommunitygame", "lolrankbot", "nightbot"]
    # List of message start strings to ignore
    ignored_starts = ["!", "http", "https"]
    # List of substrings in messages to ignore
    ignored_substrings = ["bitch", "sex"]
    allowed_repeats = [
        "O",
        "o",
        ".",
        "?",
        "m",
        "h",
    ]  # Characters allowed to be repeated extensively
    max_word_length = 20  # Maximum allowed word length
    allowed_words = [
        "Incomprehensibilities",
        "Supercalifragilisticexpialidocious",
        "<3",
        "the",
        "of",
        "a",
        "o",
        "O",
        ".",
        "..",
        "...",
    ]  # Custom allowed words list

    def is_spam_message(msgs):
        words = msgs.lower().split()  # Convert to lowercase to ensure uniformity in counting
        word_counts = Counter(words)

        for word, count in word_counts.items():
            if word in allowed_words:
                continue  # Bypass other checks if word is in the allowed words list
            if count > 3:
                return True  # Word appears more than 3 times and is not in the allowed words list
            if len(word) > max_word_length:
                return True  # Word is too long
            if not allowed_repeated_characters(word):
                return True  # Contains disallowed repeated characters
        return False

    def allowed_repeated_characters(word):
        # If there's anything left after stripping allowed characters
        if any(char in allowed_repeats for char in word) and all(
                char in allowed_repeats for char in word.strip("".join(allowed_repeats))
        ):
            return True  # All characters are allowed repeats
        for char in set(word):
            if word.count(char) >= 6 and char not in allowed_repeats:
                return False  # Found a character repeated 5 times or more that is not allowed
            if char not in allowed_repeats and word.count(char * 4) > 0:
                return False  # Checks for 3 consecutive repeats
        return True

    while True:
        time.sleep(0.5)
        try:
            readbuffer = irc.recv(1024).decode()
        except Exception as e:
            print(e)
            continue

        for line in readbuffer.split("\r\n"):
            if line == "":
                continue
            if line.startswith("PING"):
                irc.send("PONG :tmi.twitch.tv\r\n".encode("utf-8"))
                continue

            user = get_user(line)
            message = get_message(line)
            if (user in ignored_users or any(message.startswith(start) for start in ignored_starts)
                    or any(substring in message for substring in ignored_substrings)
                    or is_spam_message(message)):
                continue

            if user not in user_voices:
                if user not in user_prompt_status:
                    ask_user_m_or_f(user, user_prompt_status)
                    user_prompt_status[user] = "pending"
                elif user_prompt_status[user] == "pending":
                    preference = extract_preference_from_message(message)
                    if preference:
                        user_preferences[user] = {"gender": preference}
                        user_prompt_status[user] = "responded"
                        send_message(f"{user}, your voice preference '{preference}' has been recorded. Thank you!\r\n")
                        voice_details, _ = get_or_assign_voice_id(user, user_voices, user_preferences)
                        user_voices[user] = (voice_details, True)
                        save_user_voice_mappings(user_voices=user_voices)  # Save after assigning new voice
                    else:
                        send_message(f"{user}, please specify 'M', 'F', or 'Random' for your "
                                     f"voice preference. Your response was not understood.\r\n")
            else:
                voice_details, first_message = get_or_assign_voice_id(user, user_voices, user_preferences)
                synthesize_message(user, message, user_voices, user_preferences)
                save_user_txt_files(
                    user, message
                )  # optional recording of messages for Korie.
                if first_message:
                    save_user_voice_mappings(user_voices=user_voices)  # Save updates if it's the first message


def ask_user_m_or_f(user, user_prompt_status):
    """
    Sends a message to the user to choose a voice type and marks them as having been prompted.
    """
    send_message(f"@{user}, please choose a type of voice you'd like, M (Male), F (Female), or R (Random)!\r\n")
    user_prompt_status[user] = "pending"  # Mark the user as having been asked
    print(f"Asked {user} to choose a voice type.")


def load_user_voice_mappings(filename="user_voices_2.txt"):
    user_voices = {}
    try:
        with open(filename, "r", encoding="utf-8") as file:
            for line in file:
                parts = line.strip().split(",")
                user = parts[0]
                voice_details = (parts[1], parts[2], parts[3] if parts[3] != 'None' else None, parts[4])
                user_voices[user] = (voice_details, True)  # True indicates the first message
    except FileNotFoundError:
        pass
    return user_voices


def extract_preference_from_message(message):
    """
    Extracts the voice preference from a chat message.
    Assumes the user types 'M', 'm', 'F', 'f', or 'Random' explicitly when asked for a preference.

    Args:
    message (str): The chat message received from the user.

    Returns:
    str: Returns 'M', 'F', or 'RANDOM' if a valid preference is found, otherwise None.
    """
    # Normalize the message to lower case for easier comparison
    normalized_message = message.strip().lower()
    print(f"normalizing message")

    # Check for each valid response and return the appropriate preference
    if "m " or "m" in normalized_message or normalized_message.startswith("m"):
        print(f"m selected")
        return "M"
    elif "f " in normalized_message or normalized_message.startswith("f"):
        return "F"
    elif "" in normalized_message:
        return "Random"
    return None


def save_user_voice_mappings(filename="user_voices_2.txt", user_voices=None):
    if user_voices is None:
        user_voices = {}

    with open(filename, "w", encoding="utf-8") as file:
        for user, (voice_details, _) in user_voices.items():
            # Serialize the voice details, converting None to 'None'
            voice_details_serialized = ','.join(
                [str(detail if detail is not None else 'None') for detail in voice_details])
            file.write(f"{user},{voice_details_serialized}\n")


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


def get_or_assign_voice_id(user, user_voices, user_pref):
    if user in user_voices:
        voice_details, first_message = user_voices[user]
        return voice_details, first_message
    else:
        # Fetch the user's preferred gender and region, default to 'RANDOM' if not specified
        user_pref = user_pref.get(user, {"gender": "RANDOM", "region": None})
        preferred_gender = user_pref.get("gender", "RANDOM")
        preferred_region = user_pref.get("region")

        # Generate a new voice based on the preferred gender and region
        new_voice_details = AzureVoiceList.get_voice_by_preference(preferred_gender, preferred_region)
        if not new_voice_details:
            raise ValueError("No available voices left for the specified preferences")

        # Update the user voices dictionary
        user_voices[user] = (new_voice_details, True)

        # Optionally, save the new voice details mapping elsewhere if needed
        # save_user_voice_mapping(user, new_voice_details)

        # Return the new voice details and that it's their first message
        return new_voice_details, True


def synthesize_message(user, message, user_voices, user_picked):
    if user not in user_voices:
        voice_details, first_message = get_or_assign_voice_id(user, user_voices, user_picked)
        user_voices[user] = (voice_details, True)  # Save new assignment
    else:
        voice_details, first_message = user_voices[user]

    # Handle first message
    text = f"{user} says {message}" if first_message else message
    user_voices[user] = (voice_details, False)  # Update the flag for the next message

    # Select appropriate SSML creation function based on emotion presence
    voice_region, voice_name, emotion, _ = voice_details
    ssml_template = create_ssml_emotions(voice_region, voice_name, emotion, text) if emotion else create_small_ssml(
        voice_region, voice_name, text)

    # Synthesize speech from SSML
    synthesize_emotion_with_ssml(message, ssml_template)


def sanitize_username(user):
    # """Sanitize the username to be file-safe by removing
    # non-alphanumeric characters and replacing spaces with underscores."""
    return re.sub(r"\W+", "_", user)


def get_file_path(user):
    """Generate file path for the user's chat log inside the ChatLogs directory."""
    sanitized_username = sanitize_username(user)
    return os.path.join("ChatLogs", f"{sanitized_username}_chat_messages.txt")


def ensure_directory_exists():
    """Ensure the ChatLogs directory exists."""
    if not os.path.exists("ChatLogs"):
        os.makedirs("ChatLogs")


def write_initial_message_to_file(file_path, user):
    # """Write the initial header to the file if it's being created for the first time."""
    if not os.path.exists(file_path):
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(f"This is all of the chat messages produced by {user}\n")
        print(f"{user} has a new txt document.")


def write_date_to_file(file_path):
    # """Write the current date to the file if it's the first message of the day."""
    current_date = datetime.now().strftime("%Y-%m-%d")
    with open(file_path, "r+", encoding="utf-8") as file:
        content = file.read()
        last_date_line = f"{current_date} _____________________\n"
        if last_date_line not in content:
            # Move to the end of the file to append the new date line
            file.seek(0, os.SEEK_END)
            file.write(last_date_line)
            print(f"Date line added for {current_date} in {file_path}.")


def append_message_to_file(file_path, user, message):
    # """Append a user's message to their file, adding date headers if necessary."""
    write_date_to_file(file_path)
    with open(file_path, "a", encoding="utf-8") as file:
        file.write(f"{message}\n")
    print(f"{user} said '{message}' and it was recorded in the txt document.")


def save_user_txt_files(user, message):
    # """Check if a user file exists, write headers if new, and append messages."""
    ensure_directory_exists()  # Make sure the ChatLogs directory exists
    file_path = get_file_path(user)
    write_initial_message_to_file(file_path, user)
    append_message_to_file(file_path, user, message)


def main():
    t1 = threading.Thread(target=twitch, daemon=True)
    t1.start()
    try:
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        print("Program exited by user")


if __name__ == "__main__":
    main()
