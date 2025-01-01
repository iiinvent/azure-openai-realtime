import os
import sys
import azure.cognitiveservices.speech as speechsdk
from dotenv import load_dotenv
import openai

def main():
    """Main function to run the Azure Speech Services demo."""
    # Load environment variables
    load_dotenv()
    
    # Initialize Azure services
    try:
        # Speech config
        speech_key = os.getenv('SPEECH_KEY')
        speech_region = os.getenv('SPEECH_REGION')
        if not speech_key or not speech_region:
            raise ValueError("Please set SPEECH_KEY and SPEECH_REGION in your .env file")
        speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=speech_region)
        
        # OpenAI config
        api_key = os.getenv('AZURE_OPENAI_KEY')
        endpoint = os.getenv('AZURE_OPENAI_ENDPOINT')
        deployment = os.getenv('AZURE_OPENAI_DEPLOYMENT')
        if not api_key or not endpoint or not deployment:
            raise ValueError("Please set AZURE_OPENAI_KEY, AZURE_OPENAI_ENDPOINT, and AZURE_OPENAI_DEPLOYMENT in your .env file")
        openai.api_type = "azure"
        openai.api_base = endpoint
        openai.api_version = "2024-02-15-preview"
        openai.api_key = api_key
        
    except ValueError as e:
        print(f"\nConfiguration error: {str(e)}")
        sys.exit(1)
    except Exception as e:
        print(f"\nAn unexpected error occurred during initialization: {str(e)}")
        sys.exit(1)

    while True:
        try:
            print("\nAzure Speech Services Chat Application")
            print("1. Text-to-Speech")
            print("2. Speech-to-Text")
            print("3. Voice Chat with AI")
            print("4. Exit")
            
            choice = input("\nChoose an option (1-4): ").strip()
                
            if choice == "1":
                try:
                    text = input("\nEnter text to convert to speech: ").strip()
                    if text:
                        synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config)
                        result = synthesizer.speak_text_async(text).get()
                        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                            print("Speech synthesis succeeded!")
                        else:
                            print(f"Speech synthesis failed: {result.reason}")
                except Exception as e:
                    print(f"Error in text-to-speech: {str(e)}")
                
                input("\nPress Enter to continue...")
                
            elif choice == "2":
                try:
                    print("\nInitializing speech recognition...")
                    audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
                    recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)
                    
                    print("\nListening... Speak into your microphone.")
                    result = recognizer.recognize_once()
                    
                    if result.reason == speechsdk.ResultReason.RecognizedSpeech:
                        print(f"\nRecognized text: {result.text}")
                    elif result.reason == speechsdk.ResultReason.NoMatch:
                        print(f"\nNo speech could be recognized: {result.no_match_details}")
                    else:
                        print(f"\nRecognition canceled: {result.reason}")
                        
                except Exception as e:
                    print(f"Error in speech-to-text: {str(e)}")
                
                input("\nPress Enter to continue...")
                
            elif choice == "3":
                try:
                    print("\nStarting voice chat (say 'exit' to end)...")
                    audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
                    recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)
                    synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config)
                    
                    while True:
                        print("\nListening for your question...")
                        result = recognizer.recognize_once()
                        
                        if result.reason == speechsdk.ResultReason.RecognizedSpeech:
                            text = result.text
                            print(f"You said: {text}")
                            
                            if text.lower().strip() == "exit":
                                print("Ending chat session...")
                                break
                                
                            print("\nThinking...")
                            try:
                                response = openai.ChatCompletion.create(
                                    engine=deployment,
                                    messages=[
                                        {"role": "system", "content": "You are a helpful assistant. Keep your responses concise and natural."},
                                        {"role": "user", "content": text}
                                    ],
                                    max_tokens=150
                                )
                                ai_response = response.choices[0].message.content
                                print(f"\nAI: {ai_response}")
                                
                                print("\nSpeaking response...")
                                synthesizer.speak_text_async(ai_response).get()
                                
                            except Exception as e:
                                print(f"Error getting AI response: {str(e)}")
                                
                        elif result.reason == speechsdk.ResultReason.NoMatch:
                            print("\nCould not understand speech. Please try again.")
                        else:
                            print("\nRecognition canceled. Please try again.")
                    
                except Exception as e:
                    print(f"Error in voice chat: {str(e)}")
                
                input("\nPress Enter to continue...")
                
            elif choice == "4":
                print("\nGoodbye!")
                break
                
            else:
                print("\nInvalid choice. Please select 1-4.")
                input("Press Enter to continue...")
                
        except KeyboardInterrupt:
            print("\nOperation cancelled by user. Returning to main menu...")
            continue
        except Exception as e:
            print(f"\nAn error occurred: {str(e)}")
            input("Press Enter to continue...")

if __name__ == "__main__":
    main()
