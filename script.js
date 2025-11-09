const mic_btn = document.querySelector(".record_button")
const txt_area = document.querySelector(".textarea")

let chunks = []; // Recorded audio data
let is_recording = false;

mic_btn.addEventListener("click", ToggleMic);

let ws;

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
        micNode = new AudioWorkletNode(audioContext, 'mic-processor');

        // Connect source to AudioWorkletNode to be processed
        source.connect(micNode);

        // Implement Websocket 
        ws = new WebSocket("wss://transcribestt.onrender.com/api/data");
        ws.onopen = () => {

            // Fetch processed mic data as chunks from AudioWorkletNode processor
            micNode.port.onmessage = (event) => {
                
                // Send chunks to backend via Websocket 
                ws.send(JSON.stringify({sample_rate: audioContext.sampleRate, msg: event.data}));    
            };
        
            // Clear textarea
            txt_area.innerHTML = "";

            // Return JSON message from backend
            ws.onmessage = (event) => {
                    let response = JSON.parse(event.data)['message'];

                    // Filter out spaces
                    if(response && response.includes(' '))
                    {
                        response = response.replace(/\s/g, '').trim();    
                    }
                    
                    // Filter out |
                    if(response && response.includes("|"))
                    {
                        response = response.replace(/\|/g, ' ');
                    }

                    // Update textarea
                    txt_area.innerHTML += response;
            };
        };  
    }
};

// Toggle mic recording functionality
async function ToggleMic(){
    is_recording = !is_recording;
    if(is_recording)
    {
        CollectSteam(is_recording);
        console.log("Started");
    }
}
