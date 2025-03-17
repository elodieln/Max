import React from 'react';
import { Routes, Route } from 'react-router-dom';
import Header from './components/layout/Header/Header';
import Footer from './components/layout/Footer/Footer';
import CoursesPage from './pages/Courses/CoursesPage';
// Modifier le chemin d'importation pour correspondre à votre structure
import CoursesFavoritesPage from './pages/Favorites/CoursesFavorites/CoursesFavoritesPage';
import AICardsPage from './pages/AICards/AICardsPage';
import ChatbotPage from './pages/Chatbot/ChatbotPage';



function App() {
  return (
    <div className="bg-[#007179]">
      <Header />
      <main>
        <Routes>
          <Route path="/" element={<CoursesPage />} />
          <Route path="/courses" element={<CoursesPage />} />
          <Route path="/create-card" element={<AICardsPage />} />
          <Route path="/chatbot" element={<ChatbotPage />} />
          {/* Remplacer le div par le composant */}
          <Route path="/favorites/courses" element={<CoursesFavoritesPage />} />
          <Route path="/favorites/cards" element={<div>Fiches</div>} />
        </Routes>
      </main>
      <Footer />
    </div>
  );
}

export default App;