import React from 'react';
import { Routes, Route } from 'react-router-dom';
import Header from './components/layout/Header/Header';
import Footer from './components/layout/Footer/Footer';
import CoursesPage from './pages/Courses/CoursesPage';
import CoursesFavoritesPage from './pages/Favorites/CoursesFavorites/CoursesFavoritesPage';
import AICardsPage from './pages/AICards/AICardsPage';
// Import the CardsFavoritesPage component with the correct path
import CardsFavoritesPage from './pages/Favorites/CardsFavorites/CardsFavoritesPage';

function App() {
  return (
    <div className="bg-[#007179]">
      <Header />
      <main>
        <Routes>
          <Route path="/" element={<CoursesPage />} />
          <Route path="/courses" element={<CoursesPage />} />
          <Route path="/create-card" element={<AICardsPage />} />
          <Route path="/chatbot" element={<div>Chatbot</div>} />
          <Route path="/favorites/courses" element={<CoursesFavoritesPage />} />
          <Route path="/favorites/cards" element={<CardsFavoritesPage />} />
        </Routes>
      </main>
      <Footer />
    </div>
  );
}

export default App;