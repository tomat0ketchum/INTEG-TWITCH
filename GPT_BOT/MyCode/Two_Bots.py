import openai
import os
from dotenv import load_dotenv
import tiktoken
from rich import print
from azure_speech_to_text import SpeechToTextManager
import time
import threading
import keyboard
import ast

env_path = os.path.join(os.path.dirname(__file__), 'EnvKeys', '.env')
load_dotenv(env_path)
load_dotenv()


def ensure_chatlogs_directory_exists():
    chatlogs_dir = 'ChatLogs'
    if not os.path.exists(chatlogs_dir):
        os.makedirs(chatlogs_dir)


def write_response_to_file_general(response):
    ensure_chatlogs_directory_exists()
    file_path = 'ChatLogs/CHATGPT_RESPONSE_2'
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(response)


def write_response_to_file_beta(response):
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
        self.chat_history_beta = []  # Stores the entire conversation for Beta
        self.chat_history_general = []  # Stores the entire conversation for General Bot
        self.load_chat_history_beta()
        self.load_chat_history_general()
        try:
            self.client = openai.OpenAI(api_key=os.environ['OPENAI_API_KEY'])
        except TypeError:
            exit("Ooops! You forgot to set OPENAI_API_KEY in your environment!")

    def load_chat_history_beta(self):
        backup_file = "ChatHistoryBackup.txt"
        if os.path.exists(backup_file):
            try:
                with open(backup_file, "r", encoding='utf-8') as file:
                    content = file.read()
                    self.chat_history_beta = ast.literal_eval(content)
            except (UnicodeDecodeError, SyntaxError):
                try:
                    with open(backup_file, "r", encoding='latin-1') as file:
                        content = file.read()
                        self.chat_history_beta = ast.literal_eval(content)
                except Exception as e:
                    print(f"Error loading chat history for Beta: {e}")
            except Exception as e:
                print(f"Error loading chat history for Beta: {e}")
            else:
                print("[green]Loaded chat history for Beta.")

    def load_chat_history_general(self):
        backup_file_general = "ChatHistoryBackup2.txt"
        if os.path.exists(backup_file_general):
            try:
                with open(backup_file_general, "r", encoding='utf-8') as file:
                    content = file.read()
                    self.chat_history_general = ast.literal_eval(content)
            except (UnicodeDecodeError, SyntaxError):
                try:
                    with open(backup_file_general, "r", encoding='latin-1') as file:
                        content = file.read()
                        self.chat_history_general = ast.literal_eval(content)
                except Exception as e:
                    print(f"Error loading chat history for General Bot: {e}")
            except Exception as e:
                print(f"Error loading chat history for General Bot: {e}")
            else:
                print("[green]Loaded chat history for General Bot.")

    def classify_message(self, prompt):
        classification_prompt = [
            {"role": "user",
             "content": f" The following message needs to be classified. ?\n\nMessage: {prompt}\n\n If it is related to league of legends Respond with 'LEAGUE!!!' or if it is related not to league repsond with 'NOT!!!'."}
        ]
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=classification_prompt,
            max_tokens=5,
            n=1,
            stop=None,
            temperature=0.5,
        )
        return response.choices[0].message.content.strip()

    def chat_with_history_beta(self, prompt=""):
        if not prompt:
            print("Didn't receive input!")
            return

        first_system_message = {"role": "system",
                                "content": '''
                                Content for bot one. Send a message no matter what is said, that says 
" you need to set up your bot prompt for the general bot. "

'''}

        # Add the system message if not already added
        if len(self.chat_history_beta) == 0:
            self.chat_history_beta.append(first_system_message)

        self.chat_history_beta.append({"role": "user", "content": prompt})

        # Check total token limit. Remove old messages as needed
        print(
            f"[coral]Chat History (Beta) has a current token length of {num_tokens_from_messages(self.chat_history_beta)}")
        while num_tokens_from_messages(self.chat_history_beta) > 128000:
            self.chat_history_beta.pop(1)  # We skip the 1st message since it's the system message
            print(f"Popped a message! New token length is: {num_tokens_from_messages(self.chat_history_beta)}")

        print("[yellow]\nAsking ChatGPT (Beta) a question...")
        completion = self.client.chat.completions.create(
            model="gpt-4-turbo",
            messages=self.chat_history_beta
        )

        openai_answer = completion.choices[0].message.content
        self.chat_history_beta.append({"role": completion.choices[0].message.role, "content": openai_answer})

        write_response_to_file_beta(openai_answer)
        return openai_answer

    def chat_with_history_general(self, prompt=""):
        if not prompt:
            print("Didn't receive input!")
            return

        first_system_message_2 = {"role": "system",
                                  "content": '''
                                  Content for bot two. Send a message no matter what is said, that says 
" you need to set up your bot prompt for the general bot. "

'''}

        if len(self.chat_history_general) == 0:
            self.chat_history_general.append(first_system_message_2)

        self.chat_history_general.append({"role": "user", "content": prompt})

        # Check total token limit. Remove old messages as needed
        print(
            f"[coral]Chat History (General) has a current token length of {num_tokens_from_messages(self.chat_history_general)}")
        while num_tokens_from_messages(self.chat_history_general) > 16000:
            self.chat_history_general.pop(1)
            print(f"Popped a message! New token length is: {num_tokens_from_messages(self.chat_history_general)}")

        print("[yellow]\nAsking ChatGPT (General) a question...")
        completion = self.client.chat.completions.create(
            model="gpt-3.5-turbo-16k",
            messages=self.chat_history_general
        )

        openai_answer = completion.choices[0].message.content
        self.chat_history_general.append({"role": completion.choices[0].message.role, "content": openai_answer})

        write_response_to_file_general(openai_answer)
        return openai_answer

    def handle_message(self, prompt):
        classification = self.classify_message(prompt)
        if classification == "LEAGUE!!!":     # This is a classifier based on the message prompt to api, change it based on application. 
            return self.chat_with_history_beta(prompt)
        else:
            return self.chat_with_history_general(prompt)

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

    def main(self):
        speechtotext_manager = SpeechToTextManager()
        backup_file = "ChatHistoryBackup.txt"
        backup_file_general = "ChatHistoryBackup2.txt"

        print("[green]Starting the loop, press [ to begin")

        def handle_file_check():
            while True:
                text_from_file = self.check_file()
                if text_from_file:
                    print(f"[yellow]Received from file: {text_from_file}")
                    self.handle_message(text_from_file)

        file_thread = threading.Thread(target=handle_file_check)
        file_thread.daemon = True
        file_thread.start()

        while True:
            if keyboard.read_key() != "[":
                time.sleep(0.1)
                continue

            print("[green]User pressed [ key! Now listening to your microphone:")

            mic_result = speechtotext_manager.speechtotext_from_mic_continuous()

            if mic_result == '':
                print("[red]Did not receive any input from your microphone!")
                continue

            response = self.handle_message(mic_result)
            print(response)

            with open(backup_file, "w") as file:
                file.write(str(self.chat_history_beta))
            with open(backup_file_general, "w") as file:
                file.write(str(self.chat_history_general))


if __name__ == '__main__':
    OpenAiManager().main()
