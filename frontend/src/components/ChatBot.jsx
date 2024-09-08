import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import './ChatBot.css';

const Chatbot = () => {
    const [userInput, setUserInput] = useState('');
    const [messages, setMessages] = useState([{ text: "Hello, How can I help you?" }]);
    const endOfMessagesRef = useRef(null);

    const handleSubmit = async () => {
        if (userInput.trim() === '') return;

        setMessages([...messages, { sender: 'user', text: userInput }]);

        try {
            const res = await axios.post('http://localhost:5000/chatbot', {
                query: userInput
            });
            setMessages([...messages, { sender: 'user', text: userInput }, { sender: 'bot', text: res.data.answer || res.data.error }]);
        } catch (error) {
            setMessages([...messages, { sender: 'user', text: userInput }, { sender: 'bot', text: "Error connecting to the chatbot." }]);
        }
        
        setUserInput('');
    };

    const handleKeyDown = (e) => {
        if (e.key === 'Enter') {
            handleSubmit();
        }
    };

    useEffect(() => {
        endOfMessagesRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    return (
        <div className="chat-container">
            <div className="chat-header">Chat with SU Bot</div>
            
            <div className="chat-window">
                {messages.map((message, index) => (
                    <div key={index} className="chat-message">
                        <div className={message.sender === 'user' ? 'user-message' : 'bot-response'}>
                            {message.text}
                        </div>
                    </div>
                ))}
                <div ref={endOfMessagesRef} />
            </div>
            
            <div className="input-container">
                <input
                    type="text"
                    className="input-field"
                    value={userInput}
                    onChange={(e) => setUserInput(e.target.value)}
                    onKeyDown={handleKeyDown}  // Listening for Enter key
                    placeholder="Ask me about Sitare university"
                />
                <button className="send-button" onClick={handleSubmit}>
                    <i className="fas fa-paper-plane" aria-hidden="true"></i>
                </button>
            </div>
        </div>
    );
};

export default Chatbot;
