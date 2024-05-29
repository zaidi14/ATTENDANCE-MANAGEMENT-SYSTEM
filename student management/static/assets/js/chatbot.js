function toggleChatbot() {
    var chatbotContainer = document.getElementById('chatbot-container');
    if (chatbotContainer.style.display === 'none') {
        chatbotContainer.style.display = 'block';
    } else {
        chatbotContainer.style.display = 'none';
    }
}

function sendMessage() {
    var userInput = document.getElementById('user-input').value;
    if (!userInput) {
        console.log('No user input');
        return;
    }

    appendMessage('user', userInput);
    console.log('User message appended:', userInput);

    // Your fetch code to send the message to the backend remains the same
    // Replace '/webhook' with your actual endpoint URL
    fetch('/webhook', {
        method: 'POST',
        body: JSON.stringify({ message: userInput }),
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        appendMessage('bot', data.response);
        console.log('Bot response received:', data.response);
    })
    .catch(error => console.error('Error:', error));

    document.getElementById('user-input').value = '';
}

function appendMessage(sender, message) {
    var messageElement = document.createElement('div');
    messageElement.classList.add('message', sender);
    messageElement.textContent = message;
    document.getElementById('chatbot-box').appendChild(messageElement);
    document.getElementById('chatbot-box').scrollTop = document.getElementById('chatbot-box').scrollHeight;
    console.log('Message appended:', sender, message);
}


