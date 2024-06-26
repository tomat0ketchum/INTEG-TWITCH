import random


class AzureVoiceList:
    voices = [
        ("en-US", "en-US-JennyNeural", "cheerful", "F"),
        ("en-US", "en-US-JennyNeural", "unfriendly", "F"),  # Female ->
        ("en-US", "en-US-JennyNeural", "whispering", "F"),
        ("en-US", "en-US-JennyNeural", "shouting", "F"),
        ("en-US", "en-US-JennyNeural", "hopeful", "F"),
        ("en-US", "en-US-JennyNeural", "sad", "F"),
        ("en-US", "en-US-JennyNeural", "excited", "F"),
        ("en-US", "en-US-JennyNeural", "angry", "F"),
        ("en-US", "en-US-JennyNeural", "gentle", "F"),
        ("en-US", "en-US-JennyNeural", "terrified", "F"),
        ("en-US", "en-US-JennyNeural", "friendly", "F"),
        ("en-US", "en-US-JennyNeural", "customerservice", "F"),
        ("en-US", "en-US-JennyNeural", "newscast", "F"),
        ("en-US", "en-US-JennyNeural", "assistant", "F"),
        ("en-US", "en-US-JennyNeural", "chat", "F"),  # Female
        ("en-US", "en-US-AriaNeural", "cheerful", "F"),
        ("en-US", "en-US-AriaNeural", "newscast-casual", "F"),  # Female ->
        ("en-US", "en-US-AriaNeural", "newscast-formal", "F"),
        ("en-US", "en-US-AriaNeural", "sad", "F"),
        ("en-US", "en-US-AriaNeural", "excited", "F"),
        ("en-US", "en-US-AriaNeural", "shouting", "F"),
        ("en-US", "en-US-AriaNeural", "terrified", "F"),
        ("en-US", "en-US-AriaNeural", "friendly", "F"),
        ("en-US", "en-US-AriaNeural", "customerservice", "F"),
        ("en-US", "en-US-AriaNeural", "empathetic", "F"),
        ("en-US", "en-US-AriaNeural", "narration-professional", "F"),
        ("en-US", "en-US-AriaNeural", "chat", "F"),
        ("en-US", "en-US-AriaNeural", "angry", "F"),  # Female
        ("en-US", "en-US-DavisNeural", "default", "M"),
        ("en-US", "en-US-DavisNeural", "chat", "M"),  # Male ->
        ("en-US", "en-US-DavisNeural", "angry", "M"),
        ("en-US", "en-US-DavisNeural", "whispering", "M"),
        ("en-US", "en-US-DavisNeural", "cheerful", "M"),
        ("en-US", "en-US-DavisNeural", "excited", "M"),
        ("en-US", "en-US-DavisNeural", "friendly", "M"),
        ("en-US", "en-US-DavisNeural", "hopeful", "M"),
        ("en-US", "en-US-DavisNeural", "sad", "M"),
        ("en-US", "en-US-DavisNeural", "terrified", "M"),
        ("en-US", "en-US-DavisNeural", "shouting", "M"),
        ("en-US", "en-US-DavisNeural", "unfriendly", "M"),  # Male
        ("en-US", "en-US-JaneNeural", "default", "F"),
        ("en-US", "en-US-JaneNeural", "angry", "F"),  # Female ->
        ("en-US", "en-US-JaneNeural", "cheerful", "F"),
        ("en-US", "en-US-JaneNeural", "excited", "F"),
        ("en-US", "en-US-JaneNeural", "friendly", "F"),
        ("en-US", "en-US-JaneNeural", "hopeful", "F"),
        ("en-US", "en-US-JaneNeural", "sad", "F"),
        ("en-US", "en-US-JaneNeural", "shouting", "F"),
        ("en-US", "en-US-JaneNeural", "terrified", "F"),
        ("en-US", "en-US-JaneNeural", "unfriendly", "F"),
        ("en-US", "en-US-JaneNeural", "whispering", "F"),  # Female
        ("en-US", "en-US-JasonNeural", "default", "M"),
        ("en-US", "en-US-JasonNeural", "angry", "M"),  # Male ->
        ("en-US", "en-US-JasonNeural", "cheerful", "M"),
        ("en-US", "en-US-JasonNeural", "excited", "M"),
        ("en-US", "en-US-JasonNeural", "friendly", "M"),
        ("en-US", "en-US-JasonNeural", "hopeful", "M"),
        ("en-US", "en-US-JasonNeural", "sad", "M"),
        ("en-US", "en-US-JasonNeural", "shouting", "M"),
        ("en-US", "en-US-JasonNeural", "terrified", "M"),
        ("en-US", "en-US-JasonNeural", "unfriendly", "M"),
        ("en-US", "en-US-JasonNeural", "whispering", "M"),  # Male
        ("en-US", "en-US-SaraNeural", "default", "F"),
        ("en-US", "en-US-SaraNeural", "angry", "F"),  # Female ->
        ("en-US", "en-US-SaraNeural", "cheerful", "F"),
        ("en-US", "en-US-SaraNeural", "excited", "F"),
        ("en-US", "en-US-SaraNeural", "friendly", "F"),
        ("en-US", "en-US-SaraNeural", "hopeful", "F"),
        ("en-US", "en-US-SaraNeural", "sad", "F"),
        ("en-US", "en-US-SaraNeural", "shouting", "F"),
        ("en-US", "en-US-SaraNeural", "terrified", "F"),
        ("en-US", "en-US-SaraNeural", "unfriendly", "F"),
        ("en-US", "en-US-SaraNeural", "whispering", "F"),  # Female
        ("en-US", "en-US-TonyNeural", "default", "M"),
        ("en-US", "en-US-TonyNeural", "angry", "M"),  # Male ->
        ("en-US", "en-US-TonyNeural", "cheerful", "M"),
        ("en-US", "en-US-TonyNeural", "excited", "M"),
        ("en-US", "en-US-TonyNeural", "friendly", "M"),
        ("en-US", "en-US-TonyNeural", "hopeful", "M"),
        ("en-US", "en-US-TonyNeural", "sad", "M"),
        ("en-US", "en-US-TonyNeural", "shouting", "M"),
        ("en-US", "en-US-TonyNeural", "terrified", "M"),
        ("en-US", "en-US-TonyNeural", "unfriendly", "M"),
        ("en-US", "en-US-TonyNeural", "whispering", "M"),  # Male
        ("en-US", "en-US-NancyNeural", "default", "F"),
        ("en-US", "en-US-NancyNeural", "angry", "F"),  # Female ->
        ("en-US", "en-US-NancyNeural", "cheerful", "F"),
        ("en-US", "en-US-NancyNeural", "excited", "F"),
        ("en-US", "en-US-NancyNeural", "friendly", "F"),
        ("en-US", "en-US-NancyNeural", "hopeful", "F"),
        ("en-US", "en-US-NancyNeural", "sad", "F"),
        ("en-US", "en-US-NancyNeural", "shouting", "F"),
        ("en-US", "en-US-NancyNeural", "terrified", "F"),
        ("en-US", "en-US-NancyNeural", "unfriendly", "F"),
        ("en-US", "en-US-NancyNeural", "whispering", "F"),  # Female
        ("en-US", "en-US-GuyNeural", "default", "M"),
        ("en-US", "en-US-GuyNeural", "newscast", "M"),  # Male ->
        ("en-US", "en-US-GuyNeural", "cheerful", "M"),
        ("en-US", "en-US-GuyNeural", "excited", "M"),
        ("en-US", "en-US-GuyNeural", "hopeful", "M"),
        ("en-US", "en-US-GuyNeural", "sad", "M"),
        ("en-US", "en-US-GuyNeural", "angry", "M"),
        ("en-US", "en-US-GuyNeural", "friendly", "M"),
        ("en-US", "en-US-GuyNeural", "terrified", "M"),
        ("en-US", "en-US-GuyNeural", "shouting", "M"),  # Male
        ("en-US", "de-DE-FlorianMultilingualNeural", None, "M"),  # Male
        ("en-IE", "en-IE-EmilyNeural", None, "F"),  # Female
        ("en-IE", "en-IE-ConnorNeural", None, "M"),
        ("en-AU", "en-AU-NatashaNeural", None, "F"),
        ("en-AU", "en-AU-WilliamNeural", None, "M"),
        ("en-AU", "en-AU-AnnetteNeural", None, "F"),
        ("en-AU", "en-AU-CarlyNeural", None, "F"),
        ("en-AU", "en-AU-DarrenNeural", None, "M"),
        ("en-AU", "en-AU-DuncanNeural", None, "M"),
        ("en-AU", "en-AU-ElsieNeural", None, "F"),
        ("en-AU", "en-AU-FreyaNeural", None, "F"),
        ("en-AU", "en-AU-JoanneNeural", None, "F"),
        ("en-AU", "en-AU-KenNeural", None, "M"),
        ("en-AU", "en-AU-KimNeural", None, "F"),
        ("en-AU", "en-AU-NeilNeural", None, "M"),
        ("en-AU", "en-AU-TimNeural", None, "M"),
        ("en-AU", "en-AU-TinaNeural", None, "F"),
        ("en-CA", "en-CA-ClaraNeural", None, "F"),
        ("en-CA", "en-CA-LiamNeural", None, "M"),
        ("en-IN", "en-IN-PrabhatNeural", None, "M"),
        ("en-IN", "en-IN-NeerjaNeural", None, "F"),
        ("en-KE", "en-KE-AsiliaNeural", None, "F"),
        ("en-KE", "en-KE-ChilembaNeural", None, "M"),
        ("en-NZ", "en-NZ-MollyNeural", None, "F"),
        ("en-NZ", "en-NZ-MitchellNeural", None, "M"),
        ("en-NG", "en-NG-EzinneNeural", None, "F"),
        ("en-NG", "en-NG-AbeoNeural", None, "M"),
        ("en-PH", "en-PH-RosaNeural", None, "F"),
        ("en-PH", "en-PH-JamesNeural", None, "M"),
        ("en-SG", "en-SG-LunaNeural", None, "F"),
        ("en-SG", "en-SG-WayneNeural", None, "M"),
        ("en-ZA", "en-ZA-LeahNeural", None, "F"),
        ("en-ZA", "en-ZA-LukeNeural", None, "M"),
        ("en-GB", "en-GB-SoniaNeural", None, "F"),
        ("en-GB", "en-GB-RyanNeural", None, "M"),
        ("en-GB", "en-GB-LibbyNeural", None, "F"),
        ("en-GB", "en-GB-AbbiNeural", None, "F"),
        ("en-GB", "en-GB-AlfieNeural", None, "M"),
        ("en-GB", "en-GB-BellaNeural", None, "F"),
        ("en-GB", "en-GB-ElliotNeural", None, "M"),
        ("en-GB", "en-GB-EthanNeural", None, "M"),
        ("en-GB", "en-GB-HollieNeural", None, "F"),
        ("en-GB", "en-GB-MaisieNeural", None, "F"),
        ("en-GB", "en-GB-NoahNeural", None, "M"),
        ("en-GB", "en-GB-OliverNeural", None, "M"),
        ("en-GB", "en-GB-OliviaNeural", None, "F"),
        ("en-GB", "en-GB-ThomasNeural", None, "M"),
        ("en-US", "en-US-AvaNeural", None, "F"),
        ("en-US", "en-US-AndrewNeural", None, "M"),
        ("en-US", "en-US-EmmaNeural", None, "F"),
        ("en-US", "en-US-BrianNeural", None, "M"),
        ("en-US", "en-US-AmberNeural", None, "F"),
        ("en-US", "en-US-AnaNeural", None, "F"),
        ("en-US", "en-US-AshleyNeural", None, "F"),
        ("en-US", "en-US-BrandonNeural", None, "M"),
        ("en-US", "en-US-ChristopherNeural", None, "M"),
        ("en-US", "en-US-CoraNeural", None, "F"),
        ("en-US", "en-US-ElizabethNeural", None, "F"),
        ("en-US", "en-US-EricNeural", None, "M"),
        ("en-US", "en-US-JacobNeural", None, "M"),
        ("en-US", "en-US-MichelleNeural", None, "F"),
        ("en-US", "en-US-RogerNeural", None, "M"),
        ("en-US", "en-US-SteffanNeural", None, "M"),
        ("en-US", "en-US-BlueNeural", None, "M"),
        ("en-US", "en-US-MonicaNeural", None, "F")  # Number = line -5, so line 175-5 = voice 170
    ]

    @classmethod
    def read_used_voices(cls):
        used_voices = set()
        try:
            with open("user_voices_2.txt", "r") as file:
                for line in file:
                    parts = line.strip().split(',')
                    if len(parts) > 2:
                        used_voices.add(parts[2])  # Assuming the voice ID is the third item in each line
        except FileNotFoundError:
            print("File not found. Continuing without excluding any voices.")
        return used_voices

    @classmethod
    def get_voice_by_preference(cls, gender_preference="R", region_preference=None):
        used_voices = cls.read_used_voices()
        # Filter voices based only on region preference and exclude used voices
        filtered_voices = [
            voice for voice in cls.voices
            if (region_preference is None or voice[0] == region_preference) and voice[1] not in used_voices
        ]

        if not filtered_voices:
            raise ValueError("No available voices left for the specified preferences")

        # If gender preference is RANDOM, select any voice from the filtered list
        if gender_preference == "R":
            return random.choice(filtered_voices)

        # If gender preference is not RANDOM, further filter by gender
        gender_filtered_voices = [voice for voice in filtered_voices if voice[3] == gender_preference]
        if not gender_filtered_voices:
            raise ValueError("No available voices match the specified gender preference")

        return random.choice(gender_filtered_voices)


# Example usage:
selector = AzureVoiceList()
# print(selector.get_voice_by_preference())  # Random gender, any region
#print(selector.get_voice_by_preference(gender_preference="M"))  # Male voice, any region
#print(selector.get_voice_by_preference(gender_preference="F", region_preference="en-US"))  # Female voice, US region