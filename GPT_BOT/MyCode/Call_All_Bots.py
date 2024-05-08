from Azure_Bot_Twitch_Manager import AzureBotTwitchManager
from Gpt_Bot_Beta import OpenAiManager
import threading
import time


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

