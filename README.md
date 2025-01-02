# Azure Voice Chat Assistant

A real-time voice chat application using Azure OpenAI and Azure Speech Services.

## Features

- Text-to-Speech conversion
- Speech-to-Text recognition
- Interactive Voice Chat with AI
- Real-time streaming responses
- Debug mode for development

## Prerequisites

1. Python 3.8 or higher
2. Azure OpenAI Service subscription
3. Azure Speech Services subscription
4. Visual Studio Build Tools with C++ workload (for PyAudio installation)

## Installation

1. Clone this repository:
```bash
git clone https://github.com/iiinvent/azure-openai-realtime
cd azure-openai-realtime
```

2. Install PyAudio (Windows):
```bash
pip install pipwin
pipwin install pyaudio
```

For other operating systems or if you encounter issues, see [PyAudio Installation Guide](https://people.csail.mit.edu/hubert/pyaudio/).

3. Install other dependencies:
```bash
pip install -r requirements.txt
```

## Configuration

1. Create a `.env` file in the project root with the following content:
```env
SPEECH_KEY=your_speech_key
SPEECH_REGION=your_speech_region
AZURE_OPENAI_KEY=your_openai_key
AZURE_OPENAI_ENDPOINT=your_openai_endpoint
AZURE_OPENAI_DEPLOYMENT=your_deployment_name
```

2. Replace the placeholder values with your actual Azure credentials:
   - `SPEECH_KEY`: Your Azure Speech Services key
   - `SPEECH_REGION`: Region of your Speech Services (e.g., eastus2)
   - `AZURE_OPENAI_KEY`: Your Azure OpenAI key
   - `AZURE_OPENAI_ENDPOINT`: Your Azure OpenAI realtime endpoint
   - `AZURE_OPENAI_DEPLOYMENT`: Your Azure OpenAI model deployment name

## Usage

Run the application:
```bash
python chat.py
```

For debug mode with detailed logging:
```bash
python chat.py --debug
```

### Available Options

1. Text-to-Speech: Convert written text to spoken audio
2. Speech-to-Text: Convert your voice to text
3. Voice Chat with AI: Have a conversation with the AI assistant
4. Exit: Close the application

### Voice Chat Commands

- Say "exit" to end the conversation
- Wait for the "Listening..." prompt before speaking
- Speak clearly and naturally

## Troubleshooting

1. PyAudio Installation Issues:
   - Make sure Visual Studio Build Tools with C++ workload is installed
   - Try installing the appropriate PyAudio wheel from [Unofficial Windows Binaries](https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio)

2. Audio Device Issues:
   - Ensure your microphone is properly connected and set as the default input device
   - Check Windows privacy settings to allow microphone access

3. Connection Issues:
   - Verify your Azure credentials in the .env file
   - Check your internet connection
   - Run in debug mode to see detailed error messages: `python chat.py --debug`

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.
