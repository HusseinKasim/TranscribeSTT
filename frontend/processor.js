class MicProcessor extends AudioWorkletProcessor {
    // Process inputs of AudioWorkletNode 
    process(inputs){
        const input = inputs[0][0]; // Take input of mic (first input device) as mono (first channel)
        if(input)
        {
            this.port.postMessage(input); // Send result to 'script.js' file
        }
        return true; // Run continuously
    }
}

// Set processor name
registerProcessor('mic-processor', MicProcessor);