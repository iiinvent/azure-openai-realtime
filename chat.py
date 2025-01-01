import os
import sys
import json
import asyncio
import websockets
import azure.cognitiveservices.speech as speechsdk
from dotenv import load_dotenv
import logging
import argparse

# Set up argument parser
parser = argparse.ArgumentParser(description='Azure Speech Services Chat Application')
parser.add_argument('--debug', action='store_true', help='Enable debug logging')

# Set up logging
logging.basicConfig(
    level=logging.WARNING,
    format='%(message)s'
)
logger = logging.getLogger(__name__)

async def send_message(websocket, message):
    """Send a message to the WebSocket connection."""
    await websocket.send(json.dumps(message))
    logger.debug(f"Sent message: {message}")

async def receive_message(websocket):
    """Receive a message from the WebSocket connection."""
    response = await websocket.recv()
    logger.debug(f"Received message: {response}")
    return json.loads(response)

async def chat_completion(deployment, messages, session_id):
    """Create a chat completion using WebSocket connection."""
    endpoint = os.getenv('AZURE_OPENAI_ENDPOINT')
    api_key = os.getenv('AZURE_OPENAI_KEY')
    
    # Format WebSocket URL to match the realtime endpoint
    ws_url = f"wss://{endpoint.replace('https://', '')}?api-version=2024-10-01-preview&deployment={deployment}"
    
    logger.debug(f"Connecting to WebSocket URL: {ws_url}")
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "api-key": api_key
    }
    
    async with websockets.connect(ws_url, extra_headers=headers) as websocket:
        # Wait for session.created event
        response = await receive_message(websocket)
        logger.debug(f"Initial response: {response}")
        
        if response.get("type") != "session.created":
            error_details = response.get("error", {})
            raise Exception(f"Expected session.created event, got: {response}")
            
        session_id = response.get("session", {}).get("id")
        logger.debug(f"Session ID: {session_id}")
        
        # Add type field to each message
        content_messages = []
        for msg in messages:
            content_messages.append({
                "type": "input_text",
                "text": msg["content"]
            })
        
        # Create a conversation item
        create_item_request = {
            "type": "conversation.item.create",
            "item": {
                "type": "message",
                "role": "user",
                "content": content_messages
            }
        }
        
        logger.debug("Creating conversation item")
        await send_message(websocket, create_item_request)
        response = await receive_message(websocket)
        logger.debug(f"Conversation item creation response: {response}")
        
        if "error" in response:
            error_details = response.get("error", {})
            raise Exception(f"Conversation item creation error: {error_details}")
            
        # Wait for item.created event
        if response.get("type") != "conversation.item.created":
            raise Exception("Expected conversation.item.created event")
            
        # Create a response
        response_request = {
            "type": "response.create",
            "response": {}
        }
        
        logger.debug("Requesting response")
        await send_message(websocket, response_request)
        
        final_response = None
        while True:
            try:
                response = await receive_message(websocket)
                logger.debug(f"Received response: {response}")
                
                if "error" in response:
                    error_details = response.get("error", {})
                    raise Exception(f"API Error: {error_details}")
                    
                response_type = response.get("type", "")
                
                if response_type == "response.done":
                    final_response = response.get("response", {})
                    break
                elif response_type == "error":
                    error_details = response.get("error", {})
                    raise Exception(f"Stream Error: {error_details}")
                    
            except websockets.exceptions.ConnectionClosed as e:
                logger.debug(f"WebSocket connection closed: {str(e)}")
                break
            except Exception as e:
                logger.error(f"Error processing response: {str(e)}")
                raise
                
        return final_response

async def initialize_session(deployment):
    """Initialize a realtime session."""
    endpoint = os.getenv('AZURE_OPENAI_ENDPOINT')
    api_key = os.getenv('AZURE_OPENAI_KEY')
    
    ws_url = f"wss://{endpoint.replace('https://', '')}?api-version=2024-10-01-preview&deployment={deployment}"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "api-key": api_key
    }
    
    async with websockets.connect(ws_url, extra_headers=headers) as websocket:
        # Send session initialization request
        request = {
            "type": "session.create",
            "session": {
                "deployment_id": deployment,
                "output_format": "text"
            }
        }
        
        logger.debug("Initializing session")
        await send_message(websocket, request)
        
        response = await receive_message(websocket)
        logger.debug(f"Session initialization response: {response}")
        
        if "error" in response:
            error_details = response.get("error", {})
            raise Exception(f"Session initialization error: {error_details}")
            
        return response.get("session", {}).get("id")

def initialize_speech_services():
    """Initialize Azure Speech Services with error logging."""
    try:
        speech_key = os.getenv('SPEECH_KEY')
        speech_region = os.getenv('SPEECH_REGION')
        
        logger.debug(f"Speech Region: {speech_region}")
        logger.debug(f"Speech Key length: {len(speech_key) if speech_key else 'None'}")
        
        if not all([speech_key, speech_region]):
            raise ValueError("Missing required Speech Services configuration")
            
        speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=speech_region)
        return speech_config
        
    except Exception as e:
        logger.error(f"Error initializing Speech Services: {str(e)}")
        logger.error(f"Error type: {type(e)}")
        raise

async def main():
    """Main function to run the Azure Speech Services demo."""
    try:
        # Parse command line arguments
        args = parser.parse_args()
        if args.debug:
            logger.setLevel(logging.DEBUG)
            logging.getLogger().setLevel(logging.DEBUG)
        else:
            logger.setLevel(logging.WARNING)
            logging.getLogger().setLevel(logging.WARNING)
        
        # Load environment variables
        load_dotenv()
        logger.debug("Environment variables loaded")
        
        # Initialize services
        speech_config = initialize_speech_services()
        deployment = os.getenv('AZURE_OPENAI_DEPLOYMENT')
        logger.debug("Services initialized successfully")
        
        # Configure speech config for better interaction
        speech_config.speech_synthesis_voice_name = "en-US-JennyNeural"
        speech_config.speech_recognition_language = "en-US"
        
        # Test the connection
        logger.debug("Testing WebSocket connection...")
        test_response = await chat_completion(deployment, [{"role": "user", "content": "test"}], None)
        logger.debug("WebSocket connection test successful")
        
    except Exception as e:
        logger.error(f"Initialization error: {str(e)}")
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
                    logger.error(f"Text-to-speech error: {str(e)}")
                
                input("\nPress Enter to continue...")
                
            elif choice == "2":
                try:
                    print("\nInitializing speech recognition...")
                    audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
                    recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)
                    
                    # Add audio feedback
                    synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config)
                    synthesizer.speak_text_async("I'm listening. Please speak.").get()
                    
                    result = recognizer.recognize_once()
                    
                    if result.reason == speechsdk.ResultReason.RecognizedSpeech:
                        print(f"\nRecognized text: {result.text}")
                        synthesizer.speak_text_async("I heard you say: " + result.text).get()
                    elif result.reason == speechsdk.ResultReason.NoMatch:
                        print(f"\nNo speech could be recognized: {result.no_match_details}")
                        synthesizer.speak_text_async("I couldn't understand what you said. Please try again.").get()
                    else:
                        print(f"\nRecognition canceled: {result.reason}")
                        synthesizer.speak_text_async("Something went wrong. Please try again.").get()
                        
                except Exception as e:
                    logger.error(f"Speech-to-text error: {str(e)}")
                
                input("\nPress Enter to continue...")
                
            elif choice == "3":
                try:
                    print("\nStarting voice chat (say 'exit' to end)...")
                    audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
                    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)
                    speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config)
                    
                    # Initialize conversation history
                    conversation_history = [
                        {"role": "system", "content": "You are a helpful assistant. Keep your responses concise and natural."}
                    ]
                    
                    # Welcome message
                    welcome_msg = "Hello! I'm your AI assistant. You can start speaking when you see 'Listening...'. Say 'exit' when you're done."
                    print("\nAI: " + welcome_msg)
                    speech_synthesizer.speak_text_async(welcome_msg).get()
                    
                    done = False
                    while not done:
                        try:
                            # Clear prompt
                            print("\nListening...")
                            
                            # Get speech input
                            result = speech_recognizer.recognize_once_async().get()
                            
                            if result.reason == speechsdk.ResultReason.RecognizedSpeech:
                                text = result.text.strip()
                                if not text:  # Skip empty input
                                    continue
                                    
                                print(f"\nYou: {text}")
                                
                                if text.lower() == "exit":
                                    goodbye_msg = "Goodbye! Have a great day!"
                                    print("\nAI: " + goodbye_msg)
                                    speech_synthesizer.speak_text_async(goodbye_msg).get()
                                    done = True
                                    continue
                                
                                # Process conversation
                                conversation_history.append({"role": "user", "content": text})
                                
                                print("\nThinking...")
                                try:
                                    # Get AI response
                                    response = await chat_completion(
                                        deployment,
                                        conversation_history,
                                        None
                                    )
                                    
                                    # Extract the transcript from the response
                                    if isinstance(response, dict) and 'output' in response:
                                        for item in response['output']:
                                            if item.get('type') == 'message' and item.get('role') == 'assistant':
                                                for content in item.get('content', []):
                                                    if content.get('type') == 'audio':
                                                        response = content.get('transcript', '')
                                                        break
                                    
                                    if not response:
                                        raise Exception("No valid response received")
                                        
                                    print("\nAI:", response)
                                    conversation_history.append({"role": "assistant", "content": response})
                                    
                                    # Speak the response
                                    speech_synthesizer.speak_text_async(response).get()
                                    
                                except Exception as e:
                                    error_msg = "I encountered an error processing your request. Please try again."
                                    print(f"\nError: {str(e)}")
                                    speech_synthesizer.speak_text_async(error_msg).get()
                                    logger.error(f"Chat completion error: {str(e)}")
                                    continue
                                    
                            elif result.reason == speechsdk.ResultReason.NoMatch:
                                error_msg = "Sorry, I couldn't understand that. Please try speaking again."
                                print(f"\nNo speech could be recognized: {result.no_match_details}")
                                speech_synthesizer.speak_text_async(error_msg).get()
                                
                            else:
                                error_msg = "Sorry, there was an issue with speech recognition. Please try again."
                                print(f"\nRecognition canceled: {result.reason}")
                                speech_synthesizer.speak_text_async(error_msg).get()
                                
                        except Exception as e:
                            logger.error(f"Voice chat loop error: {str(e)}")
                            print(f"\nAn error occurred: {str(e)}")
                            break
                            
                except Exception as e:
                    logger.error(f"Voice chat initialization error: {str(e)}")
                    print(f"\nError starting voice chat: {str(e)}")
                
                input("\nPress Enter to continue...")
                
            elif choice == "4":
                print("\nGoodbye!")
                break
                
            else:
                print("\nInvalid choice. Please try again.")
                
        except Exception as e:
            logger.error(f"Main loop error: {str(e)}")
            print(f"\nAn error occurred: {str(e)}")
            input("\nPress Enter to continue...")

if __name__ == "__main__":
    asyncio.run(main())
