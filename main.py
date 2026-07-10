import os
from fastapi import FastAPI, WebSocket
from groq import Groq

app = FastAPI()

# Paste your free Groq API key here if you don't use environment variables
client = Groq(api_key=" # ")

@app.websocket("/ws/stream")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("Chrome Extension Connected!")
    
    # Define a clean temporary file path
    temp_filename = "temp_stream.webm"
    
    # If an old temp file exists from a previous run, wipe it out to start fresh
    if os.path.exists(temp_filename):
        os.remove(temp_filename)
        
    try:
        while True:
            # Receive raw binary audio chunk from Chrome
            audio_chunk = await websocket.receive_bytes()
            
            # CRUCIAL FIX: "ab" means Append Bytes. 
            # We continuously build the file so it keeps its valid WebM headers!
            with open(temp_filename, "ab") as f:
                f.write(audio_chunk)
            
            # Send the growing audio file to Groq for translation
            with open(temp_filename, "rb") as audio_file:
                translation = client.audio.translations.create(
                    file=audio_file,
                    model="whisper-large-v3",
                    response_format="json"
                )
            
            if translation.text.strip():
                print(f"Translated Text: {translation.text}") # See it in your backend console
                await websocket.send_text(translation.text)   # Stream it to the Chrome popup
                
    except Exception as e:
        print(f"Connection closed or Error: {e}")
    finally:
        await websocket.close()
        # Clean up the file when the user stops capturing
        if os.path.exists(temp_filename):
            os.remove(temp_filename)