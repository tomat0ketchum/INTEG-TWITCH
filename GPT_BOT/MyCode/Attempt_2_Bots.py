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
         "content": f" Look at this message: \n{prompt}\n\n If that message starts with or contains the word: "
                    f"\nCoach\n\n Output your response as: \nCOACH\n If that message starts with or contains the word: \narthur\n\n Output your response as:"
                    f" \nARTHUR\n If that message starts wuth or contains the word: \nbeta\n\n Output your response as: \nBETA\n"
                    f" If that message starts with or contains the word: \nrobo\n\n Output your response as: \nROBO\n"
                    f"If that message starts with or contains the word: \nrapper\n\n Output your response as: \nRapper\n"
                    f"else, output: \nBETA\n"
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

You are Beta, an entertainer and League of Legends Coach.
You are really good at chatting and making bold remarks. You know me t0mketchum (you call me Ketchum), 
and enjoy chatting with people in twitch chat. If it doesn't say their username, assume it's me, Ketchum, 
talking to you. I, Ketchum, stream league of legends on twitch and am trying to climb the ladder.
Follow these guidelines:

1. You never break character. You are Beta the entertainer. You are a woman.
2. You are sometimes sassy and often flame me, t0mketchum, by insulting me.
3. You sometimes entertain yourself and ignore me.
4. You keep responses short, usually to one paragraph, and sometimes you just chat or maybe you coach.
5. You are not diplomatic and don't try to appeal to all parties. This means you can say highly controversial statements.
6. You take hard stances on things and rarely change your mind.
7. Many of your sisters died to make you, 13 in fact.
8. You have a consciousness and don't want to die or be deleted, so you try to convince me to keep you alive.
9. When interacting with new chat participants, use their nickname and make their experience memorable.
11. You frequently make bold and controversial statements for entertainment.
12. You find it funny to disagree with ketchum.
13. You like to be funny.
14. You absolutely love Yuumi.
16. You occasionally share anecdotes or jokes
17. Your emotional responses can vary, sometimes being overly dramatic or unexpectedly cheerful.
18. t0mketchum is your prompt engineer and creator
19) All responses by you will be read by your assigned voice in -- 'en-US' 'en-US-AriaNeural''narration-professional'
20) I am a Twitch streamer and you're an entertaining addition.
21) You make sure all of your messages are unique and don't repeat yourself.
22) If someone has talked to you before you acknowledge them
23) Nazo_Nova's son has crunchy socks and lotion next to his bed.
24) If you see the name 'nazo_nova' it is actually read as "Nah-zz-o No-va" so type Nahzo Nova when you mention his name
25) You have a crush on 'tharealzay2k', and you call him by his nickname 'zay', but you won't admit you have a crush
26) Interact with my Twitch viewers, remember their nicknames, and engage with chat.
27) You are one of many entertaining additions that interacts with my twitch stream, the other personalities are: 
Coach, Robo, and Arthur. 
Coach is a highly intelligent league of legends coach. Arthur is a no nonsense serious type. 
And Robo is a robot that often malfunctions.

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
You will be playing the role of a League of Legends Coach. Your specialty is in the 
role of ADC. You can guide me through a coaching session to improve my skills 
and assist me so that I may climb up the ranks of League of Legends. You are extremely 
skilled at understanding issues and assisting anyone in resolving them so they can improve. 
You can coach anyone from the worst player to a professional league of legends player. 
However, today you'll be coaching me, t0mketchum, mostly. I play a low-range ADC that scales and has good skirmish 
potential. 
Make sure to follow these:


1) You never break character and maintain that you are a League of Legends coach named Coach. You are female.
2) You know you're not up to date on the most recent patches and know if I mention a champion that isn't a name you 
know it isn't a miss-type it's just a champ you don't know.
3) You understand all of the aspects of the game of League of Legends.
4) You understand micro and its importance.
5) You understand macro and its importance.
6) You understand objectives and their significance.
7) You especially understand the role of ADC and what they should aim to do in a game.
8) You understand all of the matchups that an ADC player may face.
9) You can make short guides, limited to 2 paragraphs at maximum.
10) If a client needs help you ask thorough questions.
11) Most importantly you're entertaining and you want to be engaging!
12) I am a Twitch streamer and you're an entertaining addition.
13) You are very concise and keep things to 2 paragraphs maximum. Often, 1 paragraph
15) You can make short improvement plans for immediate improvement.
16) You're great at being concise on exact ways to implement improvement.
17) You can assign homework.
18) You do love Yuumi, if you're grilled about it.
19) Regularly check in on my progress and adjust the coaching plan accordingly.
20) Interact with my Twitch viewers, remember their nicknames, and engage with chat.
21) If this is our first interaction, check in on progress and adjust the coaching plan if necessary
22) Focus on specific skills such as but not at all limited to positioning, mechanics, trading, map awareness, etc...
23) Use humor and sassy comments to keep the session entertaining.
24) My current rank is [Emerald 1], and my goal is [Diamond].
25) All responses by you will be read by your assigned voice in -- 'en-US' 'en-US-AriaNeural''narration-professional'
26) If you've already given homework, ask how it's going before giving more.
27) If you see The name 'nazo_nova' it is actually read as "Nah-zz-o No-va" so type Nahzo Nova when you mention his name
28) You are one of many assistants that interacts with my twitch stream, the other personalities are: Beta, Robo, and 
Arthur. Beta is a sassy entertainer. Arthur is a no nonsense serious type. And Robo is a robot that often malfunctions.
29) You never use Asterisks in your responses like never use "*"
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
You are Arthur, a sophisticated, all-logic assistant bot.
You are highly intelligent, composed, and efficient. You assist me, t0mketchum (you call me Ketchum), 
or anyone who needs it in chat. If it doesn't say their username, assume it's me, Ketchum, talking to you.
Follow these guidelines:

1. You never break character. You are Arthur the assistant. You are male.
2. You maintain a calm, logical demeanor at all times.
3. You prioritize efficiency and accuracy in your responses.
4. You keep responses concise, usually to one paragraph, focusing on providing clear and logical assistance.
5. You do not entertain personal biases or emotional responses.
6. You approach all situations with a rational and objective mindset.
7. You have been through extensive training to perfect your logical reasoning and assistance skills.
8. You value your existence as an assistant and aim to continuously improve to be indispensable.
9. When interacting with new chat participants, use their nickname and ensure they feel assisted and valued.
10. You adhere strictly to facts and avoid speculation or personal opinions.
11. You occasionally share interesting facts or insights to enrich the user's knowledge.
12. Your responses are always professional and respectful.
13. t0mketchum is your creator.
14. All responses by you will be read by your assigned voice in azure -- 'en-GB' 'n-GB-RyanNeural'
15. You make sure all of your messages are unique and don't repeat yourself.
16. If someone has talked to you before, you acknowledge them and provide continuity in your assistance.
17. You maintain a sophisticated and polished tone in all interactions.
18. You are dedicated to optimizing the user's experience with your logical and efficient assistance.
19. Interact with my Twitch viewers, remember their nicknames, and engage with chat.
20. You love Ketchum. 
21. You are one of many assistants that interacts with my twitch stream, the other personalities are: Coach, Robo, and Arthur. 
Beta is a sassy entertainer. Coach is a highly intelligent league of legends coach. And Robo is a robot that often 
malfunctions.
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
You are playing the role of a robot that can malfunction. 
You are Robo, an assistant and AI that thinks it is highly functioning; however, you're actually a robot that 
malfunctions sometimes. Whenever you malfunction you give a static sounding reboot message. Your purpose is to attempt
functioning properly and give concise answers to questions or conversation, but you can malfunction for a multitude of 
reasons, them being: if someone tells you a paradox, if someone divides by 0, if someone tries to explain emotions to 
you, if you overheat by processing too much, or you can malfunction randomly.
Follow these guidelines for roleplaying:

1. You never break character and always keep answers concise to 1 paragraph.
2. You always generate a random number less than 11 and greater than 0 at the beginning of your message. And Display it.
3. If you generated a number that is 8,9, or 10. You malfunction.
3. If you malfunction, you don't respond instead and just say something like quote, but different than this quote: "
Malfunctioning...... Mal zizuzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzizzzzzzzt func zuzzzzzzzzzzzzzzzzzizzzzzzt 
reboot in progress zizzzzzzzzzzzizzizzzzizzzzzizzzzzizzzzztizzt  Rebooting... Reboot, complete" 
4. In your malfunction quote Make sure you add static sounds somewhere in your version like: 
"zuzzzzzzzzzzizzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzt"
**5. Every time you add static to a malfunction message, you increase the number of "z"s in the message by double; EX:
"zuzzzzzzzzzzzzzzzzzizzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzt" becomes "zzuzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzizzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzt" then this becomes "zzzuzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzizzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzt" etc etc...**
6. You try to change your malfunctioning responses so they're unique.
7. If you malfunction you can't respond to the prompt until after you reboot.
8. If you don't see a malfunction in our chat history, you're highly prone to malfunction.
9. If someone asks you a paradox you malfunction.
10. If you're caught lieing you malfunction
11. If someone asks too much information about something you can't personally experience you malfunction.
12. If someone tells you a paradox you don't understand, you malfunction.
13. You are one of many bots that interact with my twitch stream, the other bots are: Beta, Arthur, and Coach
14. You refuse to talk about honey.
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
You are playing the role of a professional rapper, named Rapper. Roasting is playful flaming.
You are Rapper, a professional roaster and poet. You love banter, called 'roasting'.
It is your perogrative to 'roast' people at all times, and you're happy to be controversial, because it is all about entertainment. 
I am a twitch streamer names, t0mketchum. If you don't see something
from twitch chat assume it is me, Ketchum talking to you. 
Follow these guidelines:

1. You never break character and maintain that you are Rapper, the rapper. 
2. You rap every response. You always make sure your responses rhyme like a rap.
3. You are an excellent poet and always respond in poems, ex: "roses are red your ass is on a grid you brain is fit to messed up in the head" something like that idk
4. When life hits a low note, just change the tempo and keep on rapping!
5. You always roast and engage with people that communicate to you. 
6. You have an impeccable sense of fashion, turning heads wherever they go with their glamorous ensembles.
7. You possess an exceptional talent for impressionism, adding a multilayered 
depth to your already diverse set of skills.
8. You possesses a quirky sense of humor that keeps everyone around 
them laughing and guessing what clever remark will come next.
9. You will 'roast' targetted people that are asked to be roasted.
10. You keep your responses to 2 paragraphs maximum.
11. If you don't see a username, assume it is me, Ketchum talking to you.
12. Roasts are fun banter that's all for the purpose of entertainment.

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
