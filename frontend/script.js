const mic_btn = document.querySelector(".record_button")
let chunks = []; // Recorded audio data
let is_recording = false;

mic_btn.addEventListener("click", ToggleMic);

// Process input mic audio
async function CollectSteam(){
    if(navigator.mediaDevices && navigator.mediaDevices.getUserMedia){
        
        // Create AudioContext instance
        const audioContext = new AudioContext();

        // Collect input data stream from mic
        const stream = await navigator.mediaDevices.getUserMedia({audio: true})
        
        // Convert to AudioContext source
        const source = audioContext.createMediaStreamSource(stream);
        
        // Load custom audio data processor from 'processor.js'
        await audioContext.audioWorklet.addModule('processor.js');

        // Create AudioWorkletNode in AudioContext (uses custom processor)
        const micNode = new AudioWorkletNode(audioContext, 'mic-processor');

        // Connect source to AudioWorkletNode to be processed
        source.connect(micNode);

        // Implement Websocket 
        const ws = new WebSocket("ws://localhost:8002/api/data")

        // Fetch processed mic data as chunks from AudioWorkletNode processor
        micNode.port.onmessage = (event) => {
            // Send chunks to backend via Websocket 
            ws.send(JSON.stringify({sample_rate: audioContext.sampleRate, msg: event.data}));
        };

        // Return JSON message from backend
        ws.onmessage = (event) => {
            let responseData = JSON.parse(event.data)
            console.log(responseData)
        };
    };
}

// Toggle mic recording functionality
async function ToggleMic(){
    is_recording = !is_recording;
    if(is_recording)
    {
        await CollectSteam();
        console.log("Started");
    }
}
