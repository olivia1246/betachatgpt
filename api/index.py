from flask import Flask, request, jsonify, render_template_string
from g4f.client import Client

app = Flask(__name__)

# Your HTML template with the minimalist design
HTML_TEMPLATE = '''
<html lang="en">
<head>
    <meta http-equiv="Content-Type" content="text/html; charset=iso-8859-1">
    <title>ChatGPT 1.0</title>
    <style>
        .footer a { text-decoration: none; }
        .footer { margin-top: 20px; }
    </style>
</head>
<body>
  <center>
        <img width="128" alt="ChatGPT-Logo" src="https://upload.wikimedia.org/wikipedia/commons/thumb/e/ef/ChatGPT-Logo.svg/128px-ChatGPT-Logo.svg.png">
        <h1>ChatGPT 1.0</h1>
        <p>How can I help you today?</p>
        <textarea id="chat-box" rows="10" cols="80" disabled></textarea>
        <br>
        <h3>Message ChatGPT</h3>
        <textarea type="text" id="user-input" rows="5" cols="80"></textarea>
        <br>
        <br>
        <input type="button" id="ask-button" value="Ask" onclick="sendMessage()">
        <div class="footer">
            <p><a href="/login">Log In</a> | <a href="/signup">Sign Up</a> | <a href="/preferences">Preferences</a> | <a href="http://frogfind.com/read.php?a=https://en.wikipedia.org/wiki/ChatGPT">About Us</a></p>
            <p>ChatGPT 1.0 is still in beta and may make mistakes. Please consider double-checking important information.</p>
            <p>&copy; 2006 OpenAI - Created by <a href="https://www.youtube.com/watch?v=IfTBofqT9Kw&t=1s">Faked Vault</a> - Recreation by <a href="https://github.com/olivia1246">olivia1246</a></p>
        </div>
  </center>
        
    <script>
        // Initialize the chat box with an empty message
        document.getElementById('chat-box').value = "";

        function sendMessage() {
            var input = document.getElementById('user-input').value;
            if (!input) return;

            var askButton = document.getElementById('ask-button');
            askButton.disabled = true;

            var countdown = 20;
            askButton.value = "Ask (" + countdown + ")";

            var interval = setInterval(function() {
                countdown--;
                askButton.value = "Ask (" + countdown + ")";
                if (countdown <= 0) {
                    clearInterval(interval);
                    askButton.value = "Ask";
                    askButton.disabled = false;
                }
            }, 1000);

            var xhr;
            // IE6 ActiveXObject for AJAX request
            if (window.XMLHttpRequest) {
                xhr = new XMLHttpRequest();  // Other browsers (IE7+, modern)
            } else {
                xhr = new ActiveXObject("Microsoft.XMLHTTP");  // IE6
            }

            xhr.open("POST", "/chat", true);
            xhr.setRequestHeader("Content-Type", "application/json");

            xhr.onreadystatechange = function() {
                if (xhr.readyState == 4 && xhr.status == 200) {
                    var data = JSON.parse(xhr.responseText);
                    var chatBox = document.getElementById('chat-box');
                    chatBox.value += "You: " + input + "\\n";
                    chatBox.value += "ChatGPT: " + data.response + "\\n";
                    document.getElementById('user-input').value = '';
                    chatBox.scrollTop = chatBox.scrollHeight; // Scroll to the bottom
                }
            };

            xhr.send(JSON.stringify({ input: input }));
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
