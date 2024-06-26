from Azure_Bot_Twitch_Manager import AzureBotTwitchManager
from Attempt_2_Bots import OpenAiManager
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


#
# From the snapshot of your system resources, you have provided the following key details about your CPU:
#
# Base Speed: 4.05 GHz
# Cores: 8
# Logical Processors: 16
# Memory Usage: 19.63 GB used out of 63 GB (30%)
# Given these specifications, here's how to think about threading in Python:
#
# 1. Logical Processors and Threading Your CPU has 8 cores and 16 logical processors. In theory, you can run 16
# threads concurrently, each one potentially operating on a different logical processor. However, the practical
# number of threads that can run efficiently might differ based on the task and how Python handles threading with the
# Global Interpreter Lock (GIL).
#
# 2. Impact of the GIL Python's GIL allows only one thread to execute Python bytecode at a time, which means that
# CPU-bound tasks won't benefit much from threading in Python; they can't truly run in parallel in the same process.
# For CPU-bound tasks, you'd be better off using the multiprocessing module, which bypasses the GIL by using separate
# memory spaces and allows parallel execution.
#
# 3. Efficient Use of Threads for I/O-bound Tasks For I/O-bound tasks (such as network operations, file I/O, etc.),
# threading can be very efficient. The GIL is released when a thread is waiting for I/O operations, allowing other
# threads to run Python code.
#
# 4. Memory Considerations You have a generous amount of RAM (63 GB), with about 30% usage currently. This is ample
# for handling multiple threads, as each thread will consume some amount of memory. The exact memory usage will
# depend on the tasks being performed.
#
# 5. Balancing Threads with Other Tasks If you are running other applications and tasks alongside your Python
# application, you'll want to balance the number of threads to ensure the system remains responsive. While you could
# technically utilize up to 16 threads, using too many might affect the performance of other applications.
#
# Recommendation: I/O-bound Python scripts: You can comfortably use a higher number of threads (up to 16 or slightly
# more), especially if they are mostly waiting on I/O. CPU-bound Python scripts: Consider using fewer threads or
# switch to multiprocessing, particularly if the tasks are intensive and can benefit from parallel processing across
# multiple cores. Ultimately, the ideal number of threads depends on the specific workload and other tasks your
# system is handling. It might be worthwhile to experiment with different configurations to find what works best for
# your needs, starting with a moderate number of threads and adjusting based on the system's response and performance.
