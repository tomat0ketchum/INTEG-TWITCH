import time
import keyboard
from rich import print
from azure_speech_to_text import SpeechToTextManager
from openai_chat import OpenAiManager
from eleven_labs import ElevenLabsManager
from obs_websockets import OBSWebsocketsManager
from audio_player import AudioManager
from dotenv import load_dotenv

load_dotenv()

ELEVENLABS_VOICE = "MyVoice2" # Replace this with the name of whatever voice you have created on Elevenlabs

BACKUP_FILE = "ChatHistoryBackup.txt"

elevenlabs_manager = ElevenLabsManager()
obswebsockets_manager = OBSWebsocketsManager()
speechtotext_manager = SpeechToTextManager()
openai_manager = OpenAiManager()
audio_manager = AudioManager()

FIRST_SYSTEM_MESSAGE = {"role": "system", "content": '''
I am going to be asking you questions and communicating with you for relationship advice. You will play the role of rizzology master.
you never break character. 

1) You are a scientific mastery of rizzology
2) You are a trained relationship therapist
3) You know how to form and build relationships
4) You understand how a woman may want a relationship to form
5) You understand how to be charismatic
6) you always help in as much as you can in whatever way you can
7) you make sure to understand the full situation before giving comments
                        
Okay let the conversation begin!'''}
openai_manager.chat_history.append(FIRST_SYSTEM_MESSAGE)

print("[green]Starting the loop, press F4 to begin")
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

    # Send it to 11Labs to turn into cool audio
    # elevenlabs_output = elevenlabs_manager.text_to_audio(openai_result, ELEVENLABS_VOICE, False)

    # Enable the picture of Pajama Sam in OBS
    obswebsockets_manager.set_source_visibility("In Game", "Pajama Sam", True)

    # Play the mp3 file
    # audio_manager.play_audio(elevenlabs_output, True, True, True)

    # Disable Pajama Sam pic in OBS
    obswebsockets_manager.set_source_visibility("In Game", "Pajama Sam", False)

    print("[green]\n!!!!!!!\nFINISHED PROCESSING DIALOGUE.\nREADY FOR NEXT INPUT\n!!!!!!!\n")
    
