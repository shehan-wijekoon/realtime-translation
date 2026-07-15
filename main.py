import os
from fastapi import FastAPI, WebSocket
from groq import Groq

app = FastAPI()

# Paste your free Groq API key here if you don't use environment variables
client = Groq(api_key="#")

@app.websocket("/ws/stream")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("Chrome Extension Connected!")
    
    temp_filename = "temp_chunk.webm"
    header_bytes = b"" # This will store Chrome's initialization header
    
    try:
        while True:
            audio_chunk = await websocket.receive_bytes()
            
            # The very first chunk contains the vital WebM file headers.
            # We save it once so we can reuse it.
            if not header_bytes:
                header_bytes = audio_chunk
            
            # Write a FRESH file every time ("wb") using the saved header + the new chunk data
            with open(temp_filename, "wb") as f:
                f.write(header_bytes + audio_chunk)
            
            # Send exactly 3-6 seconds of audio to Groq (protects your limits!)
            with open(temp_filename, "rb") as audio_file:
                translation = client.audio.translations.create(
                    file=audio_file,
                    model="whisper-large-v3",
                    response_format="json"
                )
            
            if translation.text.strip():
                print(f"Clean Fresh Chunk: {translation.text}")
                await websocket.send_text(translation.text)
                
    except Exception as e:
        print(f"Connection closed or Error: {e}")
    finally:
        try:
            await websocket.close()
        except:
            pass
        if os.path.exists(temp_filename):
            os.remove(temp_filename)