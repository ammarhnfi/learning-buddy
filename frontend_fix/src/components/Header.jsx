import React from 'react';
import { Menu, X, User, LogOut, Sun, Moon } from 'lucide-react';
import UserSelector from './UserSelector';

function Header({ currentUserEmail, onUserChange, onNavigate, currentView, isLoggedIn, onLogin, onLogout, currentTheme, onToggleTheme }) {
    const [isMenuOpen, setIsMenuOpen] = React.useState(false);

    return (
        <header className="fixed w-full bg-white/80 dark:bg-gray-900/80 backdrop-blur-md z-50 border-b border-gray-100 dark:border-gray-800 transition-colors duration-200">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="flex justify-between items-center h-16">
                    {/* Logo */}
                    <div className="flex-shrink-0 flex items-center gap-2 cursor-pointer" onClick={() => onNavigate('home')}>
                        <div className="w-8 h-8 bg-gradient-to-br from-blue-600 to-indigo-600 rounded-lg flex items-center justify-center text-white font-bold text-xl">
                            L
                        </div>
                        <span className="font-bold text-xl bg-clip-text text-transparent bg-gradient-to-r from-blue-600 to-indigo-600">
                            Learning Buddy
                        </span>
                    </div>

                    {/* Desktop Navigation */}
                    <nav className="hidden md:flex space-x-8">
                        {isLoggedIn && (
                            <>
                                <a
                                    href="#"
                                    onClick={(e) => { e.preventDefault(); onNavigate('home'); }}
                                    className={`text-base font-medium ${currentView === 'home' ? 'text-blue-600' : 'text-gray-500 hover:text-gray-900 dark:text-gray-300 dark:hover:text-white'}`}
                                >
                                    Home
                                </a>
                                <a
                                    href="#"
                                    onClick={(e) => { e.preventDefault(); onNavigate('roadmap'); }}
                                    className={`text-base font-medium ${currentView === 'roadmap' ? 'text-blue-600' : 'text-gray-500 hover:text-gray-900 dark:text-gray-300 dark:hover:text-white'}`}
                                >
                                    Roadmap
                                </a>
                                <a
                                    href="#"
                                    onClick={(e) => { e.preventDefault(); onNavigate('dashboard'); }}
                                    className={`text-base font-medium ${currentView === 'dashboard' ? 'text-blue-600' : 'text-gray-500 hover:text-gray-900 dark:text-gray-300 dark:hover:text-white'}`}
                                >
                                    Dashboard
                                </a>
                            </>
                        )}
                    </nav>

                    {/* User Section / Login Button */}
                    <div className="hidden md:flex items-center gap-4">
                        {/* Theme Toggle */}
                        <button
                            onClick={onToggleTheme}
                            className="p-2 rounded-full text-gray-500 hover:bg-gray-100 dark:text-gray-400 dark:hover:bg-gray-800 transition-colors"
                            title={currentTheme === 'dark' ? "Ganti ke Mode Terang" : "Ganti ke Mode Gelap"}
                        >
                            {currentTheme === 'dark' ? <Sun size={20} /> : <Moon size={20} />}
                        </button>

                        {isLoggedIn ? (
                            <>
                                <button
                                    onClick={(e) => { e.preventDefault(); onNavigate('profile'); }}
                                    className={`flex items-center gap-3 pl-2 pr-4 py-1.5 rounded-full border transition-all ${currentView === 'profile' ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20' : 'border-transparent hover:bg-gray-50 dark:hover:bg-gray-800'}`}
                                >
                                    <div className="w-8 h-8 rounded-full bg-gradient-to-r from-blue-500 to-indigo-500 flex items-center justify-center text-white font-bold text-sm shadow-sm">
                                        <User size={16} />
                                    </div>
                                    <span className="text-sm font-medium text-gray-700 dark:text-gray-200">Profile</span>
                                </button>

                                <UserSelector currentUserEmail={currentUserEmail} onUserChange={onUserChange} />

                                <button
                                    onClick={onLogout}
                                    className="p-2 text-gray-400 hover:text-red-600 transition-colors"
                                    title="Keluar"
                                >
                                    <LogOut size={20} />
                                </button>
                            </>
                        ) : (
                            <button
                                onClick={onLogin}
                                className="px-5 py-2 rounded-full bg-blue-600 text-white font-medium hover:bg-blue-700 transition-all shadow-md hover:shadow-lg transform hover:-translate-y-0.5"
                            >
                                Masuk / Daftar
                            </button>
                        )}
                    </div>

                    {/* Mobile Menu Button */}
                    <div className="md:hidden flex items-center">
                        <button
                            onClick={() => setIsMenuOpen(!isMenuOpen)}
                            className="text-gray-500 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white focus:outline-none"
                        >
                            {isMenuOpen ? <X size={24} /> : <Menu size={24} />}
                        </button>
                    </div>
                </div>
            </div>

            {/* Mobile Menu */}
            {isMenuOpen && (
                <div className="md:hidden bg-white dark:bg-gray-900 border-t border-gray-100 dark:border-gray-800">
                    <div className="px-4 pt-2 pb-4 space-y-1">
                        {isLoggedIn && (
                            <>
                                <a
                                    href="#"
                                    onClick={(e) => { e.preventDefault(); onNavigate('home'); setIsMenuOpen(false); }}
                                    className="block px-3 py-2 rounded-md text-base font-medium text-gray-700 hover:text-gray-900 hover:bg-gray-50 dark:text-gray-300 dark:hover:text-white dark:hover:bg-gray-800"
                                >
                                    Home
                                </a>
                                <a
                                    href="#"
                                    onClick={(e) => { e.preventDefault(); onNavigate('roadmap'); setIsMenuOpen(false); }}
                                    className="block px-3 py-2 rounded-md text-base font-medium text-gray-700 hover:text-gray-900 hover:bg-gray-50 dark:text-gray-300 dark:hover:text-white dark:hover:bg-gray-800"
                                >
                                    Roadmap
                                </a>
                                <a
                                    href="#"
                                    onClick={(e) => { e.preventDefault(); onNavigate('dashboard'); setIsMenuOpen(false); }}
                                    className="block px-3 py-2 rounded-md text-base font-medium text-gray-700 hover:text-gray-900 hover:bg-gray-50 dark:text-gray-300 dark:hover:text-white dark:hover:bg-gray-800"
                                >
                                    Dashboard
                                </a>
                                <a
                                    href="#"
                                    onClick={(e) => { e.preventDefault(); onNavigate('profile'); setIsMenuOpen(false); }}
                                    className="block px-3 py-2 rounded-md text-base font-medium text-gray-700 hover:text-gray-900 hover:bg-gray-50 dark:text-gray-300 dark:hover:text-white dark:hover:bg-gray-800"
                                >
                                    Profile
                                </a>
                                <div className="px-3 py-2">
                                    <UserSelector currentUserEmail={currentUserEmail} onUserChange={onUserChange} />
                                </div>
                                <button
                                    onClick={() => { onLogout(); setIsMenuOpen(false); }}
                                    className="w-full text-left block px-3 py-2 rounded-md text-base font-medium text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20"
                                >
                                    Keluar
                                </button>
                            </>
                        )}
                        {!isLoggedIn && (
                            <button
                                onClick={() => { onLogin(); setIsMenuOpen(false); }}
                                className="w-full mt-4 px-5 py-3 rounded-xl bg-blue-600 text-white font-medium hover:bg-blue-700 transition-colors shadow-md"
                            >
                                Masuk / Daftar
                            </button>
                        )}
                    </div>
                </div>
            )}
        </header>
    );
}

export default Header;
