from flask import Flask, request, jsonify, render_template_string
from g4f.client import Client

app = Flask(__name__)

# Your HTML template with updated TTS handling
HTML_TEMPLATE = '''
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ChatGPT 1.0</title>
</head>
<body>
  <center>
        <img width="128" alt="ChatGPT-Logo" src="https://upload.wikimedia.org/wikipedia/commons/thumb/e/ef/ChatGPT-Logo.svg/128px-ChatGPT-Logo.svg.png"></a>
        <h1>ChatGPT 1.0</h1>
        <p>How can I help you today?</p>
        <textarea id="chat-box" rows="10" cols="80" readonly></textarea>
        <br>
        <h3>Message ChatGPT</h3>
        <textarea type="text" id="user-input" rows="5" cols="80"></textarea>
        <br>
        <br>
        <button id="ask-button" onclick="sendMessage()">Ask</button>
        <br>
        <div class="footer">
            <p><a href="/login">Log In</a>        <a href="/signup">Sign Up</a>        <a href="/preferences">Preferences</a>        <a href="http://frogfind.com/read.php?a=https://en.wikipedia.org/wiki/ChatGPT">About Us</a></p>
            <p>ChatGPT 1.0 is still in beta and may make mistakes. Please consider double-checking important information.</p>
            <p>&copy; 2006 OpenAI - Created by <a href="https://www.youtube.com/watch?v=IfTBofqT9Kw&t=1s">Faked Vault</a> - Recreation by <a href="https://github.com/olivia1246/betachatgpt">olivia1246</a> - Powered by <a href="https://github.com/xtekky/gpt4free">GPT4Free</a></p>
        </div>
  </center>

    <!-- Include SAM JS Library -->
    <script src="https://cdn.jsdelivr.net/npm/sam-js@latest"></script>
    
    <script>
        // Initialize SAM
        let sam = new SamJs();
        let currentAudioContext;  // Holds the current AudioContext for stopping

        // Initialize the chat box with an empty message
        document.getElementById('chat-box').value = "";

        function sendMessage() {
            var input = document.getElementById('user-input').value;
            if (!input) return;

            // Stop any current TTS playback
            stopTTS();

            // Clear the chat box and set the "Generating..." message
            var chatBox = document.getElementById('chat-box');
            chatBox.value = "";  // Clear previous conversation

            // Disable the button and change the text to "Generating..."
            var askButton = document.getElementById('ask-button');
            askButton.disabled = true;
            askButton.textContent = "Generating...";

            // Send the user input to the server
            fetch('/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ input: input })
            })
            .then(response => response.json())
            .then(data => {
                // Display the generated response in the chat box
                chatBox.value = data.response + "\\n";  // Append the bot's response
                document.getElementById('user-input').value = '';  // Clear the user input
                chatBox.scrollTop = chatBox.scrollHeight;  // Scroll to the bottom of the chat

                // Reset the button to "Ask" and enable it
                askButton.textContent = "Ask";
                askButton.disabled = false;

                // Play the response using SAM TTS
                playTTS(data.response);
            })
            .catch(error => {
                // Handle any errors
                var errorMessage = "Error occurred. Please try again.";
                chatBox.value = errorMessage + "\\n";
                askButton.textContent = "Ask";
                askButton.disabled = false;

                // Play the error message using SAM TTS
                playTTS(errorMessage);
            });
        }

        // Split text into chunks based on a maximum length
        function splitTextIntoChunks(text, maxLength = 200) {
            let chunks = [];
            let currentChunk = '';

            const words = text.split(' ');
            for (let i = 0; i < words.length; i++) {
                if ((currentChunk.length + words[i].length + 1) <= maxLength) {
                    currentChunk += (currentChunk ? ' ' : '') + words[i];
                } else {
                    if (currentChunk) chunks.push(currentChunk); // Push non-empty chunk
                    currentChunk = words[i];
                }
            }
            if (currentChunk) chunks.push(currentChunk); // Push remaining chunk
            return chunks.filter(chunk => chunk.length > 0); // Ensure no empty chunks
        }

        // Function to play the TTS for the given text
        function playTTS(text) {
            stopTTS(); // Stop any ongoing playback

            let chunks = splitTextIntoChunks(text); // Split the text into manageable chunks
            playNextChunk(chunks, 0); // Start playing the chunks one by one
        }

        // Function to play each chunk in sequence
        function playNextChunk(chunks, index) {
            if (index >= chunks.length) {
                console.log("All chunks played.");
                currentAudioContext = null; // Reset the audio context
                return; // All chunks have been played
            }

            let chunk = chunks[index];
            console.log("Playing chunk:", chunk);

            // Play the speech for this chunk using SAM
            currentAudioContext = sam.speak(chunk);
            currentAudioContext.then(() => {
                // When the current chunk finishes, play the next one
                playNextChunk(chunks, index + 1);
            }).catch((error) => {
                console.log("Error during speech playback:", error);
                currentAudioContext = null; // Reset on error
                playNextChunk(chunks, index + 1); // Attempt to play the next chunk
            });
        }

        // Function to stop TTS playback
        function stopTTS() {
            if (currentAudioContext && typeof currentAudioContext.abort === 'function') {
                try {
                    currentAudioContext.abort(); // Attempt to abort the audio
                } catch (error) {
                    console.log("Failed to stop audio:", error);
                }
            }
            currentAudioContext = null; // Clear the context
        }
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    # Serve the HTML page
    return render_template_string(HTML_TEMPLATE)

@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json.get('input')

    # Revised prompt for the AI to act like a beta model
    beta_prompt = (
        "Imagine you are a beta version of an AI model named ChatGPT 1.0, released in 2006. "
        "You are familiar with most significant events and information up to that year. "
        "However, for anything beyond 2006, respond as if you're predicting the future based on your understanding and make subtle guesses about what might have occurred. "
        "Do not explicitly inform the user about your beta status or the nature of your responses. "
        "Here is the User's Input: "
    )

    full_input = beta_prompt + user_input

    # Use g4f client to call the GPT model
    client = Client()
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": full_input}]
    )

    # Extract the response content
    bot_response = response.choices[0].message.content
    return jsonify({'response': bot_response})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
