import { useState, useEffect } from 'react';
import ChatbotWidget from './components/ChatbotWidget';
import Header from './components/Header';
import RoadmapView from './components/RoadmapView';
import Dashboard from './components/Dashboard';
import Home from './components/Home';
import CourseDetail from './components/CourseDetail';
import Profile from './components/Profile';

function App() {
  const [currentUserEmail, setCurrentUserEmail] = useState('dina.wijaya1@example.com'); // Default user
  const [currentView, setCurrentView] = useState('dashboard'); // 'dashboard', 'roadmap', 'home', 'course-detail'
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [pendingChatMessage, setPendingChatMessage] = useState('');
  const [selectedCourseId, setSelectedCourseId] = useState(null);
  const [theme, setTheme] = useState('light');

  // Handle Theme Change
  useEffect(() => {
    if (theme === 'dark') {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [theme]);

  const handleLogin = () => {
    setIsLoggedIn(true);
  };

  const handleLogout = () => {
    setIsLoggedIn(false);
    setCurrentView('dashboard');
    setPendingChatMessage('');
  };

  const handleSummarize = () => {
    // Set pending message and open chat
    setPendingChatMessage("Tolong rangkum hasil belajar saya sejauh ini dan berikan saran langkah selanjutnya.");
    const chatWidget = document.getElementById('chatbot-widget-trigger');
    if (chatWidget) chatWidget.click();
  };

  const handleSelectCourse = (courseId) => {
    setSelectedCourseId(courseId);
    setCurrentView('course-detail');
  };

  const handleBackFromDetail = () => {
    setCurrentView('dashboard'); // Or back to previous view if we track history, but dashboard is safe default
    setSelectedCourseId(null);
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 transition-colors duration-200">
      <Header
        currentUserEmail={currentUserEmail}
        onUserChange={setCurrentUserEmail}
        onNavigate={setCurrentView}
        currentView={currentView}
        isLoggedIn={isLoggedIn}
        onLogin={handleLogin}
        onLogout={handleLogout}
        currentTheme={theme}
        onToggleTheme={() => setTheme(theme === 'light' ? 'dark' : 'light')}
      />

      <main className="pt-20 pb-10 px-4">
        {!isLoggedIn ? (
          <Home onLogin={handleLogin} />
        ) : (
          <>
            {currentView === 'roadmap' ? (
              <RoadmapView userEmail={currentUserEmail} onSelectCourse={handleSelectCourse} />
            ) : currentView === 'home' ? (
              <Home onLogin={() => { }} />
            ) : currentView === 'course-detail' ? (
              <CourseDetail courseId={selectedCourseId} onBack={handleBackFromDetail} />
            ) : currentView === 'profile' ? (
              <Profile userEmail={currentUserEmail} />
            ) : (
              <Dashboard
                userEmail={currentUserEmail}
                onSummarize={handleSummarize}
                onSelectCourse={handleSelectCourse}
              />
            )}
          </>
        )}
      </main>

      {
        isLoggedIn && (
          <ChatbotWidget
            currentUserEmail={currentUserEmail}
            pendingMessage={pendingChatMessage}
            onMessageSent={() => setPendingChatMessage('')}
            theme={theme}
          />
        )
      }
    </div >
  );
}

export default App;