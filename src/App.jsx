import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Header from './components/layout/Header/Header';
import './App.css';

// Import des pages (à décommenter au fur et à mesure que les composants sont créés)
// import CoursesPage from './pages/Courses/CoursesPage';
// import ChatbotPage from './pages/Chatbot/ChatbotPage';
// import CoursesFavoritesPage from './pages/Favorites/CoursesFavorites/CoursesFavoritesPage';
// import CardsFavoritesPage from './pages/Favorites/CardsFavorites/CardsFavoritesPage';
// import AICardsPage from './pages/AICards/AICardsPage';

function App() {
  return (
    <Router>
      <div className="app">
        <Header />
        <main className="main-content">
          <Routes>
            {/* Routes à décommenter au fur et à mesure */}
            {/* <Route path="/courses" element={<CoursesPage />} />
            <Route path="/chatbot" element={<ChatbotPage />} />
            <Route path="/favorites/courses" element={<CoursesFavoritesPage />} />
            <Route path="/favorites/cards" element={<CardsFavoritesPage />} />
            <Route path="/create-card" element={<AICardsPage />} /> */}
            <Route path="/" element={<div>Page d'accueil</div>} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;