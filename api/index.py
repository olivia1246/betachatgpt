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
            <p>&copy; 2006 OpenAI - Created by <a href="https://www.youtube.com/watch?v=IfTBofqT9Kw&t=1s">Faked Vault</a> - Recreation by <a href="https://github.com/olivia1246">olivia1246</a></p>
        </div>
  </center>

    <!-- Include SAM JS Library -->
    <script src="https://cdn.jsdelivr.net/npm/sam-js@latest"></script>
    
    <script>
        let sam = new SamJs();
        let currentSpeech;  // Holds the current speech for stopping

        document.getElementById('chat-box').value = "";

        function sendMessage() {
            let input = document.getElementById('user-input').value;
            if (!input) return;

            // Stop any current TTS playback
            stopTTS();

            let chatBox = document.getElementById('chat-box');
            chatBox.value = "Generating...\n";

            let askButton = document.getElementById('ask-button');
            askButton.disabled = true;
            askButton.textContent = "Generating...";

            fetch('/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ input: input })
            })
            .then(response => response.json())
            .then(data => {
                chatBox.value = data.response + "\n";
                document.getElementById('user-input').value = '';
                chatBox.scrollTop = chatBox.scrollHeight;

                askButton.textContent = "Ask";
                askButton.disabled = false;

                // Play the response using SAM TTS
                playTTS(data.response);
            })
            .catch(error => {
                chatBox.value = "Error occurred. Please try again.\n";
                askButton.textContent = "Ask";
                askButton.disabled = false;

                // Play the error message using SAM TTS
                playTTS("Error occurred. Please try again.");
            });
        }

        function playTTS(text) {
            stopTTS();  // Stop any ongoing playback

            currentSpeech = sam.speak(text);
            currentSpeech.catch(() => {});  // Handle cases where playback fails
        }

        function stopTTS() {
            if (currentSpeech) {
                currentSpeech.abort();  // Stop the current speech playback
                currentSpeech = null;  // Reset the currentSpeech variable
            }
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
