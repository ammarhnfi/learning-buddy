import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App.jsx';
import { ThemeProvider } from './hooks/UseTheme.jsx';
import './styles/chatbot.css'; // Import Tailwind/custom styles

// Create a root element for the widget
const chatbotRootElement = document.createElement('div');
chatbotRootElement.id = 'chatbot-widget-root';
document.body.appendChild(chatbotRootElement);

// Render the App into the new root element
const root = ReactDOM.createRoot(chatbotRootElement);
root.render(
  <React.StrictMode>
    <ThemeProvider>
      <App />
    </ThemeProvider>
  </React.StrictMode>
);