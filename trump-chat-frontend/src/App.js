import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import styled from '@emotion/styled';
import { TextField, IconButton } from '@mui/material';
import SendIcon from '@mui/icons-material/Send';

// Conteneur global : tout l'écran en flex, fond noir
const Container = styled.div`
  display: flex;
  height: 100vh;
  background-color: #000; /* Fond noir */
  color: #fff;            /* Texte blanc */
`;

/* 
   Section "chat" : occupe 1/3 de la largeur, 
   fond noir, bordure à droite, colonne (header, messages, input)
*/
const ChatSection = styled.div`
  width: 33%;
  height: 100%;
  display: flex;
  flex-direction: column;
  border-right: 1px solid #333;
`;

/* 
   Header du chat : image de Trump, nom, handle, description
*/
const ChatHeader = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #333;
`;

const TrumpAvatar = styled.img`
  width: 60px;
  height: 60px;
  border-radius: 50%;
  margin-bottom: 10px;
`;

const TrumpName = styled.div`
  font-size: 18px;
  font-weight: bold;
  margin-bottom: 5px;
`;

const TrumpHandle = styled.div`
  font-size: 14px;
  color: #71767b;
  margin-bottom: 10px;
`;

const TrumpDescription = styled.div`
  font-size: 14px;
  color: #e1e8ed;
  text-align: center;
`;

/* 
   Zone qui liste les messages, défilable
*/
const MessagesContainer = styled.div`
  flex: 1;
  overflow-y: auto;
  padding: 10px;
  scroll-behavior: smooth;

  /* Masquer la scrollbar sur Chrome/Safari */
  &::-webkit-scrollbar {
    display: none;
  }
`;

/* 
   Chaque message (container) : on va gérer la disposition (gauche/droite)
   selon qui parle. 
*/
const MessageWrapper = styled.div`
  display: flex;
  margin-bottom: 15px;
  justify-content: ${props => (props.isUser ? 'flex-end' : 'flex-start')};
`;

/* 
   Image à côté de chaque message (avatar).
   On l'affiche à gauche pour Trump, à droite pour l'utilisateur
   selon la prop isUser. 
*/
const MessageAvatar = styled.img`
  width: 40px;
  height: 40px;
  border-radius: 50%;
  margin: ${props => (props.isUser ? '0 0 0 10px' : '0 10px 0 0')};
`;

/*
   La bulle du message en elle-même.
   Fond bleu (#1da1f2) pour l’utilisateur, gris foncé (#333) pour Trump
*/
const MessageBubble = styled.div`
  background-color: ${props => (props.isUser ? '#1da1f2' : '#333')};
  color: #fff;
  border-radius: 15px;
  padding: 10px;
  max-width: 70%;
  word-wrap: break-word;
`;

/* 
   Zone pour afficher l'heure ou autre info (petite typo)
*/
const Timestamp = styled.div`
  font-size: 12px;
  color: #71767b;
  margin-top: 5px;
`;

/* 
   Le bloc input (tout en bas) : champ + bouton
*/
const InputContainer = styled.div`
  border-top: 1px solid #333;
  padding: 10px;
  display: flex;
  background-color: #000;
`;

/* 
   La partie "droite" (blanche) de la page, 
   comme dans l'ancien code : .content
*/
const Content = styled.div`
  flex: 1;
  background-color: #fff;
`;

function App() {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const messagesEndRef = useRef(null);

  useEffect(() => {
    fetchChatHistory();
  }, []);

  useEffect(() => {
    // Au chargement ou quand messages change, scroller en bas
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

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
    <Container>
      {/* Section gauche : Chat */}
      <ChatSection>
        {/* Header : Donald J. Trump */}
        <ChatHeader>
          <TrumpAvatar src="/images/donald_trump.jpg" alt="Donald Trump" />
          <TrumpName>Donald J. Trump</TrumpName>
          <TrumpHandle>@realDonaldTrump</TrumpHandle>
          <TrumpDescription>
            45th President of the United States of America <br />
            DonaldJTrump.com <br />
            A rejoint X en mars 2009
          </TrumpDescription>
        </ChatHeader>

        {/* Liste des messages */}
        <MessagesContainer>
          {messages.map((interaction, index) => {
            const interactionKey = Object.keys(interaction)[0];
            const { user, trump } = interaction[interactionKey];

            // On affiche d'abord le message user (droite),
            // puis le message de Trump (gauche), s'il existe
            return (
              <React.Fragment key={index}>
                {/* Message user */}
                {user && (
                  <MessageWrapper isUser>
                    {/* Avatar user (à droite) */}
                    <MessageBubble isUser>{user.message}</MessageBubble>
                    <MessageAvatar
                      isUser
                      src="/images/user.png"
                      alt="Utilisateur"
                    />
                  </MessageWrapper>
                )}

                {/* Message Trump */}
                {trump && (
                  <MessageWrapper>
                    {/* Avatar trump (à gauche) */}
                    <MessageAvatar
                      src="/images/donald_trump.jpg"
                      alt="Donald Trump"
                    />
                    <MessageBubble>{trump.message}</MessageBubble>
                  </MessageWrapper>
                )}
              </React.Fragment>
            );
          })}
          <div ref={messagesEndRef} />
        </MessagesContainer>

        {/* Input (en bas) */}
        <form onSubmit={handleSendMessage} style={{ margin: 0 }}>
          <InputContainer>
            <TextField
              fullWidth
              variant="outlined"
              placeholder="Écrire un message..."
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              size="small"
              sx={{
                '& .MuiOutlinedInput-root': {
                  borderRadius: '20px',
                  backgroundColor: '#192734',
                  color: '#e1e8ed',
                  border: '1px solid #333',
                },
                '& .MuiOutlinedInput-root input::placeholder': {
                  color: '#71767b',
                },
              }}
            />
            <IconButton
              type="submit"
              color="primary"
              disabled={!inputMessage.trim()}
              style={{ marginLeft: '10px', backgroundColor: '#1da1f2', color: '#fff' }}
            >
              <SendIcon />
            </IconButton>
          </InputContainer>
        </form>
      </ChatSection>

      {/* Section droite (blanche) */}
      <Content>
        {/* 
          Ici tu peux mettre ce que tu veux 
          (carte, infos, jeu, etc.) 
        */}
      </Content>
    </Container>
  );
}

export default App;
