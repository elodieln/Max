import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Header from './components/layout/Header/Header';
import './App.css';

// Composants temporaires pour le développement
const TempHome = () => <div className="temp-page">Page d'accueil</div>;
const TempCourses = () => <div className="temp-page">Page des cours</div>;
const TempChatbot = () => <div className="temp-page">Page du chatbot</div>;
const TempCreateCard = () => <div className="temp-page">Page de création de fiche</div>;
const TempFavoritesCourses = () => <div className="temp-page">Page des cours favoris</div>;
const TempFavoritesCards = () => <div className="temp-page">Page des fiches favorites</div>;
// {<TempCourses />} etc sont des composants temporaires pour le développement
function App() {
  return (
    <Router>
      <div className="app">
        <Header />
        <main className="main-content">
          <Routes>
            <Route path="/" element={<TempHome />} />
            <Route path="/courses" element={<TempCourses />} />
            <Route path="/chatbot" element={<TempChatbot />} />
            <Route path="/create-card" element={<TempCreateCard />} />
            <Route path="/favorites/courses" element={<TempFavoritesCourses />} />
            <Route path="/favorites/cards" element={<TempFavoritesCards />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;