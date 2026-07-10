let mediaRecorder;
let socket;

document.getElementById('startBtn').addEventListener('click', async () => {
  const subtitlesContainer = document.getElementById('subtitles');
  
  // Clear out the placeholder text when starting
  subtitlesContainer.innerHTML = '';

  socket = new WebSocket('ws://localhost:8000/ws/stream');
  
  socket.onmessage = (event) => {
    const translatedText = event.data.strip ? event.data.strip() : event.data;
    if (!translatedText) return;

    // 1. Create a brand new bubble element
    const bubble = document.createElement('div');
    bubble.className = 'subtitle-bubble';
    bubble.innerText = translatedText;

    // 2. Append the new bubble to the scrolling container
    subtitlesContainer.appendChild(bubble);

    // 3. Auto-scroll to the bottom so the user always sees the newest translation
    subtitlesContainer.scrollTop = subtitlesContainer.scrollHeight;
  };

  socket.onerror = (error) => {
    console.error("WebSocket Error: ", error);
    subtitlesContainer.innerHTML = `<div class="subtitle-bubble" style="border-left-color: #ef4444; color: #b91c1c;">Backend connection error. Ensure Uvicorn is running!</div>`;
  };

  chrome.tabCapture.capture({ audio: true, video: false }, (stream) => {
    if (!stream) {
      alert('Could not capture audio. Please click inside the web page first.');
      return;
    }

    const audioContext = new AudioContext();
    const source = audioContext.createMediaStreamSource(stream);
    source.connect(audioContext.destination);

    mediaRecorder = new MediaRecorder(stream, { mimeType: 'audio/webm' });
    
    mediaRecorder.ondataavailable = async (event) => {
      if (event.data.size > 0 && socket.readyState === WebSocket.OPEN) {
        const arrayBuffer = await event.data.arrayBuffer();
        socket.send(arrayBuffer);
      }
    };

    mediaRecorder.start(3000); 
    
    document.getElementById('startBtn').innerText = "Streaming & Translating Live...";
    document.getElementById('startBtn').disabled = true;
  });
});