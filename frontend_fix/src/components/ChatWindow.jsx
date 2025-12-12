import React, { useState, useRef, useEffect } from 'react';
import ChatBubble from './ChatBubble';
import RecommendationModal from './RecommendationModal';
import { getBotResponse, getSmartRecommendation, getSkillAnalysis } from '../services/api';

function ChatWindow({ onClose, currentUserEmail, initialMessage, onInitialMessageSent }) {
  // Helper function to extract number from text (e.g., "berikan 6 rekomendasi" -> 6)
  const extractNumberFromText = (text) => {
    const matches = text.match(/(\d+)/g);
    if (matches && matches.length > 0) {
      const num = parseInt(matches[0], 10);
      // Clamp to reasonable range (1-20)
      return Math.max(1, Math.min(num, 20));
    }
    return 5; // Default to 5
  };

  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [userName, setUserName] = useState('');
  const messagesEndRef = useRef(null);
  const hasSentInitial = useRef(false);
  const [recommendations, setRecommendations] = useState([]);
  const [showRecommendations, setShowRecommendations] = useState(false);

  const quickActions = [
    "Rangkum Hasil Belajar",
    "Rekomendasi Kursus",
    "Skill Apa yang paling berkembang?"
  ];

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]);

  // Fetch User Name
  useEffect(() => {
    const fetchUserName = async () => {
      try {
        const response = await fetch('/dashboard/users');
        if (response.ok) {
          const users = await response.json();
          const user = users.find(u => u.email === currentUserEmail);
          if (user) {
            setUserName(user.name);
          } else {
            setUserName(currentUserEmail.split('@')[0]);
          }
        }
      } catch (error) {
        console.error("Failed to fetch user name", error);
        setUserName(currentUserEmail.split('@')[0]);
      }
    };
    if (currentUserEmail) {
      fetchUserName();
    }
  }, [currentUserEmail]);

  // Set Welcome Message
  useEffect(() => {
    if (userName) {
      setMessages([
        { text: `Halo ${userName}, apa yang bisa saya bantu?`, isBot: true }
      ]);
    }
  }, [userName]);

  // Handle Initial Message (from Dashboard)
  useEffect(() => {
    if (initialMessage && !hasSentInitial.current && userName) {
      hasSentInitial.current = true;
      handleSend(null, initialMessage);
      if (onInitialMessageSent) onInitialMessageSent();
    }
  }, [initialMessage, userName]);

  const isRequestingNewRecommendation = (text) => {
    const lowerText = text.toLowerCase();
    const requestKeywords = ["berikan", "tampilkan", "ambil", "minta", "cari", "dapatkan"];
    const hasRequestKeyword = requestKeywords.some(kw => lowerText.includes(kw));
    const hasRekomendasi = lowerText.includes("rekomendasi");
    // Treat short/explicit quick-action labels as requests as well
    const trimmed = lowerText.trim();
    const explicitQuickRequests = ["rekomendasi kursus", "rekomendasi"];

    if (explicitQuickRequests.includes(trimmed)) return true;

    return hasRekomendasi && hasRequestKeyword;
  };

  const handleSend = async (e, textOverride = null) => {
    if (e) e.preventDefault();
    const textToSend = textOverride || input;
    if (!textToSend.trim()) return;

    const userMessage = { text: textToSend, isBot: false };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsTyping(true);

    try {
      // Check if user is requesting NEW recommendations
      if (isRequestingNewRecommendation(textToSend)) {
        const topN = extractNumberFromText(textToSend);
        const id = currentUserEmail || userName || '';
        const recs = await getSmartRecommendation(id, topN);
        if (Array.isArray(recs) && recs.length > 0) {
          setRecommendations(recs);
          setShowRecommendations(true);
          const botMessage = { text: `Saya menampilkan ${recs.length} rekomendasi kursus untuk Anda.`, isBot: true };
          setMessages(prev => [...prev, botMessage]);
        } else {
          const botMessage = { text: "Maaf, saya tidak bisa menemukan rekomendasi kursus untuk Anda saat ini.", isBot: true };
          setMessages(prev => [...prev, botMessage]);
        }
      } else {
        // For all other questions (including follow-up about recommendations),
        // let the chatbot handle it with full context
        const botText = await getBotResponse(textToSend, currentUserEmail);
        const botMessage = { text: botText, isBot: true };
        setMessages(prev => [...prev, botMessage]);
      }
    } catch (error) {
      console.error("Error getting bot response:", error);
      const errorMessage = { text: "Maaf, saya sedang mengalami gangguan. Coba lagi nanti.", isBot: true };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsTyping(false);
    }
  };

  return (
    <div className="flex flex-col h-full bg-white dark:bg-gray-800">
      {/* Header */}
      <div className="flex justify-between items-center p-4 border-b border-gray-200 dark:border-gray-700 bg-blue-600 text-white rounded-t-lg">
        <div className="flex items-center">
          <div className="h-8 w-8 bg-white rounded-full flex items-center justify-center mr-3">
            <span className="text-blue-600 font-bold">LB</span>
          </div>
          <h3 className="font-semibold">Learning Buddy</h3>
        </div>
        <div className="flex items-center space-x-2">
          

          <button
            onClick={async () => {
              // Skill analyzer quick action
              try {
                setIsTyping(true);
                const targetEmail = currentUserEmail || userName || '';
                if (!targetEmail) {
                  setMessages(prev => [...prev, { text: 'Email pengguna tidak ditemukan.', isBot: true }]);
                  setIsTyping(false);
                  return;
                }
                const data = await getSkillAnalysis(targetEmail);
                console.log("Skill analysis data:", data);
                console.log("Data analysis field:", data?.analysis);
                if (data && data.analysis) {
                  const { analysis, skill_development } = data;
                  const summaryLines = [];
                  summaryLines.push(`⚠️ Level kelemahan: ${analysis.weakness_level}`);
                  if (analysis.findings && analysis.findings.length) {
                    summaryLines.push('\n📊 Temuan:');
                    analysis.findings.forEach(f => summaryLines.push(`- ${f}`));
                  }
                  if (analysis.suggestions && analysis.suggestions.length) {
                    summaryLines.push('\n💡 Saran:');
                    analysis.suggestions.forEach(s => summaryLines.push(`- ${s}`));
                  }
                  
                  // Add skill development info
                  if (skill_development && skill_development.top_skills && skill_development.top_skills.length > 0) {
                    summaryLines.push('\n🎯 Skill yang Paling Berkembang:');
                    const mostDev = skill_development.most_developed;
                    if (mostDev) {
                      summaryLines.push(`${mostDev.skill}: ${mostDev.proficiency_label} (${mostDev.proficiency}%)`);
                    }
                    
                    summaryLines.push('\n📈 Top 5 Skills:');
                    skill_development.top_skills.forEach((skill, idx) => {
                      summaryLines.push(`${idx + 1}. ${skill.skill}: ${skill.proficiency_label} (${skill.proficiency}%)`);
                    });
                  }
                  
                  setMessages(prev => [...prev, { text: summaryLines.join('\n'), isBot: true }]);
                } else {
                  console.error("Invalid response structure. Full data:", JSON.stringify(data));
                  setMessages(prev => [...prev, { text: 'Gagal menganalisis skill untuk pengguna ini. Periksa console untuk detail.', isBot: true }]);
                }
              } catch (err) {
                console.error("Skill analysis error:", err);
                const msg = err && err.message ? err.message : 'Terjadi kesalahan saat menganalisis skill.';
                setMessages(prev => [...prev, { text: msg, isBot: true }]);
              } finally {
                setIsTyping(false);
              }
            }}
            className="px-2 py-1 bg-white text-blue-600 rounded-md text-sm hover:bg-blue-50"
            title="Skill Analyzer"
          >
            Skill Analyzer
          </button>

          <button
            onClick={onClose}
            className="text-white hover:text-gray-200 focus:outline-none"
          >
            <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      </div>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50 dark:bg-gray-900">
        {messages.map((msg, index) => (
          <ChatBubble key={index} text={msg.text} isBot={msg.isBot} />
        ))}
        {isTyping && (
          <div className="flex justify-start">
            <div className="bg-white dark:bg-gray-800 p-3 rounded-lg rounded-tl-none shadow-sm border border-gray-200 dark:border-gray-700">
              <div className="flex space-x-2">
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.4s' }}></div>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Quick Actions */}
      <div className="px-4 py-2 bg-white dark:bg-gray-800 border-t border-gray-100 dark:border-gray-700 overflow-x-auto whitespace-nowrap">
        <div className="flex space-x-2">
          {quickActions.map((action, idx) => (
            <button
              key={idx}
              onClick={() => handleSend(null, action)}
              className="px-3 py-1 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 text-xs rounded-full hover:bg-blue-100 hover:text-blue-700 transition-colors border border-gray-200 dark:border-gray-600"
            >
              {action}
            </button>
          ))}
        </div>
      </div>

      {/* Input Area */}
      <form onSubmit={handleSend} className="p-4 border-t border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 rounded-b-lg">
        <div className="flex space-x-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Tanya sesuatu..."
            className="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-full focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
          />
          <button
            type="submit"
            disabled={!input.trim() || isTyping}
            className={`p-2 rounded-full text-white ${!input.trim() || isTyping
              ? 'bg-gray-400 cursor-not-allowed'
              : 'bg-blue-600 hover:bg-blue-700'
              }`}
          >
            <svg className="h-5 w-5 transform rotate-90" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
            </svg>
          </button>
        </div>
      </form>
      <RecommendationModal
        open={showRecommendations}
        onClose={() => setShowRecommendations(false)}
        recommendations={recommendations}
        user={userName}
      />
    </div>
  );
}

export default ChatWindow;