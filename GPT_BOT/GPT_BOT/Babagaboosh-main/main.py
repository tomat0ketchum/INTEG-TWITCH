import os
import azure.cognitiveservices.speech as speechsdk
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Retrieve key and region from environment variables
speech_key = os.getenv("AZURE_TTS_KEY")
service_region = os.getenv("AZURE_TTS_REGION")

# Initialize speech config
speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config)

# Perform speech recognition
print("Say something...")
result = speech_recognizer.recognize_once()

# Check the result
if result.reason == speechsdk.ResultReason.RecognizedSpeech:
    print("Recognized: {}".format(result.text))
elif result.reason == speechsdk.ResultReason.NoMatch:
    print("No speech could be recognized.")
elif result.reason == speechsdk.ResultReason.Canceled:
    cancellation_details = result.cancellation_details
    print(f"Speech Recognition canceled: {cancellation_details.reason}")
    if cancellation_details.reason == speechsdk.CancellationReason.Error:
        print(f"Error details: {cancellation_details.error_details}")
