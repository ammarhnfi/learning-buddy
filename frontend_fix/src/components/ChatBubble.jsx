import React from 'react';
import ReactMarkdown from 'react-markdown';

function ChatBubble({ text, isBot }) {
  const isUser = !isBot;

  const baseStyles = 'px-4 py-2 rounded-lg max-w-[80%] break-words';
  const userStyles = 'bg-blue-600 text-white self-end rounded-br-none chat-bubble-user';
  const botStyles = 'bg-gray-200 dark:bg-gray-700 text-gray-900 dark:text-white self-start rounded-bl-none chat-bubble-bot';

  // Special case for loading bubble
  if (text === '...') {
    return (
      <div className="self-start">
        <div className={`${baseStyles} ${botStyles} px-5`}>
          <div className="flex space-x-1 animate-pulse">
            <div className="w-2 h-2 bg-gray-400 rounded-full"></div>
            <div className="w-2 h-2 bg-gray-400 rounded-full animation-delay-200"></div>
            <div className="w-2 h-2 bg-gray-400 rounded-full animation-delay-400"></div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div
        className={`${baseStyles} ${isUser ? userStyles : botStyles}`}
      >
        <div className="prose dark:prose-invert max-w-none text-sm">
          <ReactMarkdown>{text}</ReactMarkdown>
        </div>
      </div>
    </div>
  );
}

export default ChatBubble;