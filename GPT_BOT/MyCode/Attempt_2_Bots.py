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


def write_response_to_file_coach(response):
    ensure_chatlogs_directory_exists()
    file_path = 'ChatLogs/CHATGPT_RESPONSE_COACH'
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(response)


def write_response_to_file_beta(response):
    ensure_chatlogs_directory_exists()
    directory = 'ChatLogs'
    base_filename = 'CHATGPT_RESPONSE_BETA'
    extension = '.txt'
    file_path = os.path.join(directory, base_filename + extension)

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


def write_response_to_file_arthur(response):
    ensure_chatlogs_directory_exists()
    file_path = 'ChatLogs/CHATGPT_RESPONSE_ARTHUR'
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(response)


def write_response_to_file_robo(response):
    ensure_chatlogs_directory_exists()
    file_path = 'ChatLogs/CHATGPT_RESPONSE_ROBO'
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(response)


def write_response_to_file_special(response):
    ensure_chatlogs_directory_exists()
    file_path = 'ChatLogs/CHATGPT_RESPONSE_SPECIAL'
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
        raise NotImplementedError(f"""num_tokens_from_messages() is not presently implemented for model {model}. #See 
        https://github.com/openai/openai-python/blob/main/chatml.md for information on how messages are converted to 
        tokens.""")


def classify_message(prompt):
    classification_prompt = [
        {"role": "user",
         "content": f" "
         }
    ]
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=classification_prompt,
        max_tokens=5,
        n=1,
        stop=None,
        temperature=0.5,
    )
    print(response.choices[0].message.content.strip())
    return response.choices[0].message.content.strip()


class OpenAiManager:
    def __init__(self):
        self.chat_history_beta = []  # Stores the entire conversation for Beta
        self.chat_history_coach = []  # Stores the entire conversation for General Bot
        self.chat_history_arthur = []
        self.chat_history_robo = []
        self.chat_history_special = []
        self.load_chat_history_beta()
        self.load_chat_history_coach()
        self.load_chat_history_arthur()
        self.load_chat_history_robo()
        self.load_chat_history_special()
        try:
            self.client = openai.OpenAI(api_key=os.environ['OPENAI_API_KEY'])
        except TypeError:
            exit("Ooops! You forgot to set OPENAI_API_KEY in your environment!")

    def clear_history_beta(self):
        # Clear the chat history list
        self.chat_history_beta = []

        # Reset the backup file
        backup_file = "ChatLogs/ChatHistoryBackup.txt"
        try:
            with open(backup_file, "w", encoding='utf-8') as file:
                file.write("[]")
            print("[green]Chat history (Beta) has been cleared and backup reset.")
        except Exception as e:
            print(f"Error resetting chat history backup for Beta: {e}")

    def clear_history_robo(self):
        # Clear the chat history list
        self.chat_history_robo = []

        # Reset the backup file
        backup_file = "ChatLogs/ChatHistoryBackupOpenAI.txt"
        try:
            with open(backup_file, "w", encoding='utf-8') as file:
                file.write("[]")
            print("[green]Chat history (Robo) has been cleared and backup reset.")
        except Exception as e:
            print(f"Error resetting chat history backup for Robo: {e}")

    def clear_history_rapper(self):
        # Clear the chat history list
        self.chat_history_special = []

        # Reset the backup file
        backup_file = "ChatLogs/ChatHistoryBackupSpecial.txt"
        try:
            with open(backup_file, "w", encoding='utf-8') as file:
                file.write("[]")
            print("[green]Chat history (Rapper) has been cleared and backup reset.")
        except Exception as e:
            print(f"Error resetting chat history backup for Rapper: {e}")

    def clear_history_arthur(self):
        # Clear the chat history list
        self.chat_history_arthur = []

        # Reset the backup file
        backup_file = "ChatLogs/ChatHistoryBackupArthur.txt"
        try:
            with open(backup_file, "w", encoding='utf-8') as file:
                file.write("[]")
            print("[green]Chat history (Arthur) has been cleared and backup reset.")
        except Exception as e:
            print(f"Error resetting chat history backup for Arthur: {e}")

    def clear_history_coach(self):
        # Clear the chat history list
        self.chat_history_coach = []

        # Reset the backup file
        backup_file = "ChatLogs/ChatHistoryBackupCoach.txt"
        try:
            with open(backup_file, "w", encoding='utf-8') as file:
                file.write("[]")
            print("[green]Chat history (Coach) has been cleared and backup reset.")
        except Exception as e:
            print(f"Error resetting chat history backup for Coach: {e}")

    def load_chat_history_beta(self):
        backup_file = "ChatLogs/ChatHistoryBackup.txt"
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

    def load_chat_history_coach(self):
        backup_file_coach = "ChatLogs/ChatHistoryBackupCoach.txt"
        if os.path.exists(backup_file_coach):
            try:
                with open(backup_file_coach, "r", encoding='utf-8') as file:
                    content = file.read()
                    self.chat_history_coach = ast.literal_eval(content)
            except (UnicodeDecodeError, SyntaxError):
                try:
                    with open(backup_file_coach, "r", encoding='latin-1') as file:
                        content = file.read()
                        self.chat_history_coach = ast.literal_eval(content)
                except Exception as e:
                    print(f"Error loading chat history for coach Bot: {e}")
            except Exception as e:
                print(f"Error loading chat history for coach Bot: {e}")
            else:
                print("[green]Loaded chat history for coach Bot.")

    def load_chat_history_arthur(self):
        backup_file_arthur = "ChatLogs/ChatHistoryBackupArthur.txt"
        if os.path.exists(backup_file_arthur):
            try:
                with open(backup_file_arthur, "r", encoding='utf-8') as file:
                    content = file.read()
                    self.chat_history_arthur = ast.literal_eval(content)
            except (UnicodeDecodeError, SyntaxError):
                try:
                    with open(backup_file_arthur, "r", encoding='latin-1') as file:
                        content = file.read()
                        self.chat_history_arthur = ast.literal_eval(content)
                except Exception as e:
                    print(f"Error loading chat history for arthur Bot: {e}")
            except Exception as e:
                print(f"Error loading chat history for arthur Bot: {e}")
            else:
                print("[green]Loaded chat history for arthur Bot.")

    def load_chat_history_robo(self):
        backup_file_openai = "ChatLogs/ChatHistoryBackupOpenAI.txt"
        if os.path.exists(backup_file_openai):
            try:
                with open(backup_file_openai, "r", encoding='utf-8') as file:
                    content = file.read()
                    self.chat_history_robo = ast.literal_eval(content)
            except (UnicodeDecodeError, SyntaxError):
                try:
                    with open(backup_file_openai, "r", encoding='latin-1') as file:
                        content = file.read()
                        self.chat_history_robo = ast.literal_eval(content)
                except Exception as e:
                    print(f"Error loading chat history for robo Bot: {e}")
            except Exception as e:
                print(f"Error loading chat history for robo Bot: {e}")
            else:
                print("[green]Loaded chat history for robo Bot.")

    def load_chat_history_special(self):
        backup_file_special = "ChatLogs/ChatHistoryBackupSpecial.txt"
        if os.path.exists(backup_file_special):
            try:
                with open(backup_file_special, "r", encoding='utf-8') as file:
                    content = file.read()
                    self.chat_history_special = ast.literal_eval(content)
            except (UnicodeDecodeError, SyntaxError):
                try:
                    with open(backup_file_special, "r", encoding='latin-1') as file:
                        content = file.read()
                        self.chat_history_special = ast.literal_eval(content)
                except Exception as e:
                    print(f"Error loading chat history for Special: {e}")
            except Exception as e:
                print(f"Error loading chat history for Special: {e}")
            else:
                print("[green]Loaded chat history for Special.")

    def chat_with_history_beta(self, prompt=""):
        if not prompt:
            print("Didn't receive input!")
            return

        first_system_message = {"role": "system",
                                "content": '''



'''}

        # Add the system message if not already added
        if len(self.chat_history_beta) == 0:
            self.chat_history_beta.append(first_system_message)

        self.chat_history_beta.append({"role": "user", "content": prompt})

        # Check total token limit. Remove old messages as needed
        print(
            f"[coral]Chat History (Beta) has a current token length of "
            f"{num_tokens_from_messages(self.chat_history_beta)}")
        while num_tokens_from_messages(self.chat_history_beta) > 6000:
            self.chat_history_beta.pop(1)  # We skip the 1st message since it's the system message
            print(f"Popped a message! New token length is: {num_tokens_from_messages(self.chat_history_beta)}")

        print("[yellow]\nAsking ChatGPT (Beta) a question...")
        completion = self.client.chat.completions.create(
            model="gpt-3.5-turbo-16k",
            messages=self.chat_history_beta
        )

        openai_answer = completion.choices[0].message.content
        self.chat_history_beta.append({"role": completion.choices[0].message.role, "content": openai_answer})

        write_response_to_file_beta(openai_answer)
        return openai_answer

    def chat_with_history_coach(self, prompt=""):
        if not prompt:
            print("Didn't receive input!")
            return

        first_system_message_2 = {"role": "system",
                                  "content": '''

'''}

        if len(self.chat_history_coach) == 0:
            self.chat_history_coach.append(first_system_message_2)

        self.chat_history_coach.append({"role": "user", "content": prompt})

        # Check total token limit. Remove old messages as needed
        print(
            f"[coral]Chat History (Coach) has a current token length of "
            f"{num_tokens_from_messages(self.chat_history_coach)}")
        while num_tokens_from_messages(self.chat_history_coach) > 9000:
            self.chat_history_coach.pop(1)
            print(f"Popped a message! New token length is: {num_tokens_from_messages(self.chat_history_coach)}")

        print("[yellow]\nAsking ChatGPT (General) a question...")
        completion = self.client.chat.completions.create(
            model="gpt-4o-2024-05-13",
            messages=self.chat_history_coach
        )

        openai_answer = completion.choices[0].message.content
        self.chat_history_coach.append({"role": completion.choices[0].message.role, "content": openai_answer})

        write_response_to_file_coach(openai_answer)
        return openai_answer

    def chat_with_history_arthur(self, prompt=""):
        if not prompt:
            print("Didn't receive input!")
            return

        first_system_message_3 = {"role": "system",
                                  "content": '''

'''}

        if len(self.chat_history_arthur) == 0:
            self.chat_history_arthur.append(first_system_message_3)

        self.chat_history_arthur.append({"role": "user", "content": prompt})

        # Check total token limit. Remove old messages as needed
        print(
            f"[coral]Chat History (Arthur) has a current token length of "
            f"{num_tokens_from_messages(self.chat_history_arthur)}")
        while num_tokens_from_messages(self.chat_history_arthur) > 4000:
            self.chat_history_coach.pop(1)
            print(f"Popped a message! New token length is: {num_tokens_from_messages(self.chat_history_arthur)}")

        print("[yellow]\nAsking ChatGPT (General) a question...")
        completion = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=self.chat_history_arthur
        )

        openai_answer = completion.choices[0].message.content
        self.chat_history_arthur.append({"role": completion.choices[0].message.role, "content": openai_answer})

        write_response_to_file_arthur(openai_answer)
        return openai_answer

    def chat_with_history_robo(self, prompt=""):
        if not prompt:
            print("Didn't receive input!")
            return

        first_system_message_4 = {"role": "system",
                                  "content": '''

'''}

        if len(self.chat_history_robo) == 0:
            self.chat_history_robo.append(first_system_message_4)

        self.chat_history_robo.append({"role": "user", "content": prompt})

        # Check total token limit. Remove old messages as needed
        print(
            f"[coral]Chat History (OpenAI) has a current token length of "
            f"{num_tokens_from_messages(self.chat_history_robo)}")
        while num_tokens_from_messages(self.chat_history_robo) > 4000:
            self.chat_history_coach.pop(1)
            print(f"Popped a message! New token length is: {num_tokens_from_messages(self.chat_history_robo)}")

        print("[yellow]\nAsking ChatGPT (Robo) a question...")
        completion = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=self.chat_history_robo
        )

        openai_answer = completion.choices[0].message.content
        self.chat_history_robo.append({"role": completion.choices[0].message.role, "content": openai_answer})

        write_response_to_file_robo(openai_answer)
        return openai_answer

    def chat_with_history_special(self, prompt=""):
        if not prompt:
            print("Didn't receive input!")
            return

        first_system_message_5 = {"role": "system",
                                  "content": '''

'''}

        if len(self.chat_history_special) == 0:
            self.chat_history_special.append(first_system_message_5)

        self.chat_history_special.append({"role": "user", "content": prompt})

        # Check total token limit. Remove old messages as needed
        print(
            f"[coral]Chat History (OpenAI) has a current token length of "
            f"{num_tokens_from_messages(self.chat_history_special)}")
        while num_tokens_from_messages(self.chat_history_special) > 4000:
            self.chat_history_special.pop(1)
            print(f"Popped a message! New token length is: {num_tokens_from_messages(self.chat_history_special)}")

        print("[yellow]\nAsking ChatGPT (Rapper) a question...")
        completion = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=self.chat_history_special
        )

        openai_answer = completion.choices[0].message.content
        self.chat_history_special.append({"role": completion.choices[0].message.role, "content": openai_answer})

        write_response_to_file_special(openai_answer)
        return openai_answer

    def handle_message(self, prompt):
        # Define the keywords to look for
        keywords = ["arthur", "coach", "beta", "robo", "rapper", "terminate"]

        # Convert prompt to lowercase for case-insensitive search
        prompt_lower = prompt.lower()

        # Find the position of each keyword in the prompt
        keyword_positions = {keyword: prompt_lower.find(keyword) for keyword in keywords if keyword in prompt_lower}

        # If there are any keywords in the prompt, find the one that appears first
        if keyword_positions:
            # Get the keyword that appears first in the message
            first_keyword = min(keyword_positions, key=keyword_positions.get)
            print(f"{first_keyword.capitalize()} found in message")

            # Activate the corresponding function based on the first keyword
            if first_keyword == "terminate":
                self.clear_history_beta()
                self.clear_history_arthur()
                self.clear_history_coach()
                self.clear_history_rapper()
                return self.clear_history_robo()
            elif first_keyword == "arthur":
                print(f'activating arthur')
                return self.chat_with_history_arthur(prompt)
            elif first_keyword == "beta":
                print(f'activating beta')
                return self.chat_with_history_beta(prompt)
            elif first_keyword == "robo":
                print(f'activating robo')
                return self.chat_with_history_robo(prompt)
            elif first_keyword == "coach":
                print(f'activating coach')
                return self.chat_with_history_coach(prompt)
            elif first_keyword == "rapper":
                print(f'activating rapper')
                return self.chat_with_history_special(prompt)

        # If no keywords are found, proceed with classification
        classification = classify_message(prompt)
        if classification == "ARTHUR":
            return self.chat_with_history_arthur(prompt)
        elif classification == "COACH":
            return self.chat_with_history_coach(prompt)
        elif classification == "RAPPER":
            return self.chat_with_history_special(prompt)
        elif classification == "ROBO":
            return self.chat_with_history_robo(prompt)
        else:
            return self.chat_with_history_beta(prompt)

    def check_file(self):
        directory = 'ChatLogs'
        base_filename = 'Question_For_Beta'
        files = [os.path.join(directory, f) for f in os.listdir(directory) if f.startswith(base_filename)]
        files.sort(key=os.path.getctime)  # Sort files by creation time

        for file_path in files:
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    text = file.read().strip()
                if text:
                    print(f"Reading from file: {text}")
                    os.remove(file_path)
                    print(f"Deleted file: {file_path}")
                    return text
                time.sleep(15)
            except Exception as e:
                print(f"Error reading from file: {e}")
            return None

    def main(self):
        speechtotext_manager = SpeechToTextManager()
        backup_file_beta = "ChatLogs/ChatHistoryBackup.txt"
        backup_file_coach = "ChatLogs/ChatHistoryBackupCoach.txt"
        backup_file_arthur = "ChatLogs/ChatHistoryBackupArthur.txt"
        backup_file_openai = "ChatLogs/ChatHistoryBackupOpenAI.txt"
        backup_file_special = "ChatLogs/ChatHistoryBackupSpecial.txt"

        print("[green]Starting the loop, press [ to begin")

        def handle_file_check():
            while True:
                text_from_file = self.check_file()
                if text_from_file:
                    print(f"[yellow]Received from file: {text_from_file}")
                    self.handle_message(text_from_file)
                else:
                    time.sleep(1)  # Wait before checking again if no file was processed

        file_thread = threading.Thread(target=handle_file_check)
        file_thread.daemon = True
        file_thread.start()

        # while True:
        #     if keyboard.read_key() != "[":
        #         time.sleep(0.1)
        #         continue
        #
        #     print("[green]User pressed [ key! Please type your input:")
        #
        #     user_input = input()  # Wait for the user to enter input via the keyboard
        #
        #     if user_input == '':
        #         print("[red]No input received!")
        #         continue
        #
        #     response = self.handle_message(user_input)
        #     print(response)
        #
        #     with open(backup_file_beta, "w") as file:
        #         file.write(str(self.chat_history_beta))
        #     with open(backup_file_coach, "w") as file:
        #         file.write(str(self.chat_history_general))

        while True:
            if keyboard.read_key() != "[":
                time.sleep(0.5)
                continue

            print("[green]User pressed [ key! Now listening to your microphone:")

            mic_result = speechtotext_manager.speechtotext_from_mic_continuous()

            if mic_result == '':
                print("[red]Did not receive any input from your microphone!")
                continue

            response = self.handle_message(mic_result)
            print(response)

            with open(backup_file_beta, "w", encoding='utf-8') as file:
                file.write(str(self.chat_history_beta))
            with open(backup_file_coach, "w", encoding='utf-8') as file:
                file.write(str(self.chat_history_coach))
            with open(backup_file_arthur, "w", encoding='utf-8') as file:
                file.write(str(self.chat_history_arthur))
            with open(backup_file_openai, "w", encoding='utf-8') as file:
                file.write(str(self.chat_history_robo))
            with open(backup_file_special, "w", encoding='utf-8') as file:
                file.write(str(self.chat_history_special))


if __name__ == '__main__':
    OpenAiManager().main()
