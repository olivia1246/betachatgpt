from flask import Flask, request, jsonify, render_template_string
from g4f.client import Client

app = Flask(__name__)

# Your HTML template with the minimalist design
HTML_TEMPLATE = '''
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ChatGPT 1.0</title>
</head>
<body>
  <center>
        <h1>ChatGPT 1.0</h1>
        <p>How can I help you today?</p>
        <textarea id="chat-box" rows="10" cols="80" readonly></textarea>
        <br>
        <h3>Message ChatGPT</h3>
        <textarea type="text" id="user-input" rows="5" cols="80"></textarea>
        <br>
        <br>
        <button id="ask-button" onclick="sendMessage()">Ask</button>
        <div class="footer">
            <p>ChatGPT 1.0 is still in beta and may make mistakes. Please consider double-checking important information.</p>
            <p>&copy; 2006 OpenAI - Created by Faked Vault</p>
        </div>
  </center>
        
    <script>
        // Initialize the chat box with an empty message
        document.getElementById('chat-box').value = "";

        function sendMessage() {
            var input = document.getElementById('user-input').value;
            if (!input) return;

            // Clear input after submission
            document.getElementById('user-input').value = '';

            // Disable the button and change text to "Generating..."
            var askButton = document.getElementById('ask-button');
            askButton.disabled = true;
            askButton.textContent = "Generating...";

            // Fetch response from the server
            fetch('/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ input: input })
            })
            .then(response => response.json())
            .then(data => {
                var chatBox = document.getElementById('chat-box');
                chatBox.value += data.response + "\\n";
                chatBox.scrollTop = chatBox.scrollHeight; // Scroll to the bottom
                
                // Re-enable the button and reset text to "Ask"
                askButton.textContent = "Ask";
                askButton.disabled = false;
            });
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
