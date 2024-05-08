from openai import OpenAI
import tiktoken
import os
from rich import print
from dotenv import load_dotenv

# Most Code handling prompt and messages taken from DougDoug's available code

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


def num_tokens_from_messages(messages, model='gpt-4'):
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
        if num_tokens_from_messages(chat_question) > 8000:
            print("The length of this chat question is too large for the GPT model")
            return

        print("[yellow]\nAsking ChatGPT a question...")
        completion = self.client.chat.completions.create(
            model="gpt-4",
            messages=chat_question
        )

        # Process the answer
        openai_answer = completion.choices[0].message.content
        print(f"[green]\n{openai_answer}\n")
        write_response_to_file(openai_answer)
        return openai_answer

    # Asks a question that includes the full conversation history
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
            model="gpt-4",
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
        chat_without_history = openai_manager.chat("Hey ChatGPT say that you're ready")

        # CHAT WITH HISTORY TEST
        FIRST_SYSTEM_MESSAGE = {"role": "system",
                                "content": '''
                                            Test
    
                                           '''}
        FIRST_USER_MESSAGE = {"role": "user",
                              "content": "Who are you, and what is your goal? Please give me a 1 sentence background "
                                         "on your coaching style"}
        openai_manager.chat_history.append(FIRST_SYSTEM_MESSAGE)
        openai_manager.chat_history.append(FIRST_USER_MESSAGE)

        while True:
            new_prompt = input("\nNext question? \n\n")
            openai_manager.chat_with_history(new_prompt)


if __name__ == '__main__':
    OpenAiManager().main()

