import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import styled from '@emotion/styled';
import { TextField, IconButton, Paper, Box } from '@mui/material';
import SendIcon from '@mui/icons-material/Send';

const ChatContainer = styled(Box)`
  display: flex;
  height: 100vh;
  padding: 20px;
  background-color: #f5f5f5;
`;

const ChatWindow = styled(Paper)`
  width: 400px;
  margin-right: 20px;
  display: flex;
  flex-direction: column;
  height: calc(100vh - 40px);
  border-radius: 15px;
  overflow: hidden;
`;

const ChatMessages = styled(Box)`
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  display: flex;
  flex-direction: column;
`;

const MessageInput = styled(Box)`
  padding: 20px;
  border-top: 1px solid #ddd;
  display: flex;
  gap: 10px;
  background-color: white;
`;

const TrumpFigure = styled(Box)`
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
`;

const Message = styled(Box)`
  margin-bottom: 10px;
  padding: 12px 16px;
  border-radius: 20px;
  max-width: 80%;
  word-wrap: break-word;
  ${props => props.isUser ? `
    background-color: #1da1f2;
    color: white;
    align-self: flex-end;
    border-bottom-right-radius: 5px;
  ` : `
    background-color: #e8f5fe;
    color: black;
    align-self: flex-start;
    border-bottom-left-radius: 5px;
  `}
`;

const TrumpImage = styled('img')`
  max-height: 80vh;
  object-fit: contain;
`;

function App() {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    fetchChatHistory();
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const fetchChatHistory = async () => {
    try {
      const response = await axios.get('http://localhost:8000/chat-history');
      setMessages(response.data.chat_history || []);
    } catch (error) {
      console.error('Error fetching chat history:', error);
    }
  };

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!inputMessage.trim()) return;

    try {
      const response = await axios.post('http://localhost:8000/send-message', {
        message: inputMessage
      });
      setMessages(response.data.chat_history);
      setInputMessage('');
    } catch (error) {
      console.error('Error sending message:', error);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage(e);
    }
  };

  return (
    <ChatContainer>
      <ChatWindow elevation={3}>
        <ChatMessages>
          {messages.map((interaction, index) => {
            const interactionKey = Object.keys(interaction)[0];
            const { user, trump } = interaction[interactionKey];
            return (
              <React.Fragment key={index}>
                <Message isUser>
                  {user.message}
                </Message>
                {trump && (
                  <Message>
                    {trump.message}
                  </Message>
                )}
              </React.Fragment>
            );
          })}
          <div ref={messagesEndRef} />
        </ChatMessages>
        <MessageInput component="form" onSubmit={handleSendMessage}>
          <TextField
            fullWidth
            variant="outlined"
            placeholder="Message Trump..."
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            size="small"
            sx={{ 
              '& .MuiOutlinedInput-root': {
                borderRadius: '20px',
              }
            }}
          />
          <IconButton type="submit" color="primary" disabled={!inputMessage.trim()}>
            <SendIcon />
          </IconButton>
        </MessageInput>
      </ChatWindow>
      <TrumpFigure>
        <TrumpImage 
          src="/trump-figure.png" 
          alt="Trump"
        />
      </TrumpFigure>
    </ChatContainer>
  );
}

export default App; 