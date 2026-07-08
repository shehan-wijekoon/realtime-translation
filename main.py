import os
from fastapi import FastAPI, WebSocket
from groq import Groq

app = FastAPI()

# Paste your free Groq API key here if you don't use environment variables
client = Groq(api_key="PASTE_YOUR_GROQ_API_KEY_HERE")

@app.websocket("/ws/stream")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("Chrome Extension Connected!")
    
    try:
        while True:
            # Receive raw binary audio chunk from the Chrome extension
            audio_chunk = await websocket.receive_bytes()
            
            temp_filename = "temp_chunk.webm"
            with open(temp_filename, "wb") as f:
                f.write(audio_chunk)
            
            # Send directly to Groq's single-step English translation endpoint
            with open(temp_filename, "rb") as audio_file:
                translation = client.audio.translations.create(
                    file=audio_file,
                    model="whisper-large-v3",
                    response_format="json"
                )
            
            if translation.text.strip():
                # Send the translated text straight back up the open WebSocket tunnel
                await websocket.send_text(translation.text)
                
    except Exception as e:
        print(f"Connection closed or Error: {e}")
    finally:
        await websocket.close()