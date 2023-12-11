// server_script.js
// Node.js server to stream conversation from stdin using Express

const express = require('express');
const http = require('http');
const EventEmitter = require('events');

const app = express();
const server = http.createServer(app);
const messageEmitter = new EventEmitter();

// Array to store messages
const messages = [];

// Read from stdin and emit messages
process.stdin.setEncoding('utf8');
process.stdin.on('data', function(data) {
    messages.push(data);
    messageEmitter.emit('new_message', messages);

});

app.get('/conversation_stream', async (req, res) => {
    res.setHeader('Content-Type', 'text/event-stream');
    res.setHeader('Cache-Control', 'no-cache');
    res.setHeader('Connection', 'keep-alive');
    res.flushHeaders();

    // send last 3 messages to client
    const lastMessages = messages.slice(-3);
    for (const message of lastMessages) {
        sendMessage(res, message);
    }

    // Send new messages to client
    const onNewMessage = (messages) => {
        const lastMessage = messages[messages.length - 1];
        sendMessage(res, lastMessage);
    };

    messageEmitter.addListener('new_message', onNewMessage);

    // Handle client disconnection
    req.on('close', () => {
        messageEmitter.removeListener('new_message', onNewMessage);
    });
});

const PORT = 12312;
server.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
});
function sendMessage(res, message) {
    // res.write(`data: ${JSON.stringify(message)}\n\n`);
    res.write(message+'\n\n')
}

