from Azure_Bot_Twitch_Manager import AzureBotTwitchManager
from Two_Bots import OpenAiManager
import threading
import time
from dotenv import load_dotenv
import os

env_path = os.path.join(os.path.dirname(__file__), 'EnvKeys', '.env')
load_dotenv(env_path)


def activate_thread_1():
    twitch_manager = AzureBotTwitchManager()
    twitch_manager.main()
    while True:
        print("Thread 1 running...")
        time.sleep(1)



def activate_thread_2():
    openai_manager = OpenAiManager()
    openai_manager.main()
    while True:
        print("Thread 2 running...")
        time.sleep(1)


if __name__ == "__main__":
    t1 = threading.Thread(target=activate_thread_1, daemon=True)
    t2 = threading.Thread(target=activate_thread_2, daemon=True)

    t1.start()
    t2.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Program exited by user")


