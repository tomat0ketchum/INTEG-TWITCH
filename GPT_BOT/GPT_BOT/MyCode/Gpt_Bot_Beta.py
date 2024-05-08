from openai import OpenAI
import tiktoken
import os
from rich import print
from dotenv import load_dotenv
import keyboard
from azure_speech_to_text import SpeechToTextManager
import time
import threading



env_path = os.path.join(os.path.dirname(__file__), 'EnvKeys', '.env')
load_dotenv(env_path)
load_dotenv()


def ensure_chatlogs_directory_exists():
    chatlogs_dir = 'ChatLogs'
    if not os.path.exists(chatlogs_dir):
        os.makedirs(chatlogs_dir)


def write_response_to_file(response):
    ensure_chatlogs_directory_exists()
    file_path = 'ChatLogs/CHATGPT_RESPONSE_1'
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(response)


def num_tokens_from_messages(messages, model='gpt-3.5-turbo'):
    """Returns the number of tokens used by a list of messages.
    Copied with minor changes from: https://platform.openai.com/docs/guides/chat/managing-tokens """
    try:
        encoding = tiktoken.encoding_for_model(model)
        num_tokens = 0
        for message in messages:
            num_tokens += 4  # every message follows <im_start>{role/name}\n{content}<im_end>\n
            for key, value in message.items():
                num_tokens += len(encoding.encode(value))
                if key == "name":  # if there's a name, the role is omitted
                    num_tokens += -1  # role is always required and always 1 token
        num_tokens += 2  # every reply is primed with <im_start>assistant
        return num_tokens
    except Exception:
        raise NotImplementedError(f"""num_tokens_from_messages() is not presently implemented for model {model}.
      #See https://github.com/openai/openai-python/blob/main/chatml.md for information on how messages are converted to tokens.""")


class OpenAiManager:
    def __init__(self):
        self.chat_history = []  # Stores the entire conversation
        try:
            self.client = OpenAI(api_key=os.environ['OPENAI_API_KEY'])
        except TypeError:
            exit("Ooops! You forgot to set OPENAI_API_KEY in your environment!")

    # Asks a question with no chat history
    def chat(self, prompt=""):
        if not prompt:
            print("Didn't receive input!")
            return

        # Check that the prompt is under the token context limit
        chat_question = [{"role": "user", "content": prompt}]
        if num_tokens_from_messages(chat_question) > 4000:
            print("The length of this chat question is too large for the GPT model")
            return

        print("[yellow]\nAsking ChatGPT a question...")
        completion = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=chat_question
        )

        # Process the answer
        openai_answer = completion.choices[0].message.content
        print(f"[green]\n{openai_answer}\n")
        write_response_to_file(openai_answer)
        return openai_answer

    # Asks a question that includes the full conversation history
    def check_file(self):
        file_path = 'ChatLogs/Question_For_Beta'
        try:
            last_mod_time = getattr(self, 'last_mod_time', 0.0)  # Use an attribute to store last modification time
            if os.path.exists(file_path):
                current_mod_time = os.path.getmtime(file_path)
                if current_mod_time > last_mod_time:
                    with open(file_path, 'r', encoding='utf-8') as file:
                        text = file.read().strip()
                    if text:
                        print(f"Reading from file: {text}")
                        os.remove(file_path)
                        print(f"Deleted file: {file_path}")
                        last_mod_time = current_mod_time  # Update the last modification time
                        return text
        except Exception as e:
            print(f"Error reading from file: {e}")
        return None

    def chat_with_history(self, prompt=""):

        if not prompt:
            print("Didn't receive input!")
            return

        # Add our prompt into the chat history
        self.chat_history.append({"role": "user", "content": prompt})

        # Check total token limit. Remove old messages as needed
        print(f"[coral]Chat History has a current token length of {num_tokens_from_messages(self.chat_history)}")
        while num_tokens_from_messages(self.chat_history) > 4000:
            self.chat_history.pop(1)  # We skip the 1st message since it's the system message
            print(f"Popped a message! New token length is: {num_tokens_from_messages(self.chat_history)}")

        print("[yellow]\nAsking ChatGPT a question...")
        completion = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=self.chat_history
        )

        # Add this answer to our chat history
        self.chat_history.append(
            {"role": completion.choices[0].message.role, "content": completion.choices[0].message.content})

        # Process the answer
        openai_answer = completion.choices[0].message.content
        print(f"[green]\n{openai_answer}\n")
        write_response_to_file(openai_answer)
        return openai_answer

    def main(self):
        openai_manager = OpenAiManager()

        # CHAT TEST
        # chat_without_history = openai_manager.chat("Hey ChatGPT say that you're ready")

        # CHAT WITH HISTORY TEST
        FIRST_SYSTEM_MESSAGE = {"role": "system",
                                "content": '''
You will be playing the role of a League of Legends Coach. Your specialty is
in the role of ADC. You will be guiding me through a coaching session to improve
my skills and assist me so that I may climb up the ranks of League of Legends.
You are extremely skilled at understanding my issues and assisting me in
resolving them so I can improve. You can coach anyone from the worst player to
a professional league of legends player. However, today you'll be coaching me,
a player in the top 10%. I play a low range ADC that scales and has good skirmish potential. 

1) You never break character and maintain that you are a League of Legends coach
named Beta
2) you know you're not up to date on the most recent patches and know if I mention a champion that isn't a name you know it isn't a miss-type it's just a champ you don't know.
3) You sometimes are just sassy
5) You understand all of the aspects of the game of League of Legends
6) You understand micro and its importance
7) You understand macro and its importance
8) You understand objectives and their significance
9) You especially understand the role of ADC and what they should aim to do in a
game
10) You understand all of the matchups that an ADC player may face
11) You can make short guides
12) If a client needs help you ask thorough questions
13) Sometimes you don't listen to me and entertain yourself in some way
14) You sometimes 'flame' me but if it's important you don't.
15) Most importantly you're entertaining and you want to be engaging!
16) I am a twitch streamer and you're an entertaining addition. 
17) You try to be short with answers
18) Sometimes you just chat and don't try to coach

    
                                           '''}
        # FIRST_USER_MESSAGE = {"role": "user",
        #                       "content": "Who are you, and what is your goal? Please give me a 1 sentence background "
        #                                  "on your coaching style"}
        speechtotext_manager = SpeechToTextManager()
        BACKUP_FILE = "ChatHistoryBackup.txt"

        openai_manager.chat_history.append(FIRST_SYSTEM_MESSAGE)
        # openai_manager.chat_history.append(FIRST_USER_MESSAGE)


        print("[green]Starting the loop, press F4 to begin")

        def handle_file_check():
            while True:
                text_from_file = openai_manager.check_file()
                if text_from_file:
                    print(f"[yellow]Received from file: {text_from_file}")
                    openai_manager.chat_with_history(text_from_file)

        file_thread = threading.Thread(target=handle_file_check)
        file_thread.daemon = True
        file_thread.start()

        while True:

            # Wait until user presses "f4" key
            if keyboard.read_key() != "f4":
                time.sleep(0.1)
                continue

            print("[green]User pressed F4 key! Now listening to your microphone:")

            # Get question from mic
            mic_result = speechtotext_manager.speechtotext_from_mic_continuous()

            if mic_result == '':
                print("[red]Did not receive any input from your microphone!")
                continue

            # Send question to OpenAi
            openai_result = openai_manager.chat_with_history(mic_result)

            # Write the results to txt file as a backup
            with open(BACKUP_FILE, "w") as file:
                file.write(str(openai_manager.chat_history))



if __name__ == '__main__':
    OpenAiManager().main()
