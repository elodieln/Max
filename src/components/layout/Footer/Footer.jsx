import React from 'react';
import { Link } from 'react-router-dom';
import './Footer.css';

const Footer = () => {
  return (
    <footer className="footer">
      <div className="footer-content">
        <div className="footer-sections-container">
          <div className="footer-logo">
            <img src="/src/assets/images/logo-max.png" alt="Logo MAX" className="footer-logo-img" />
          </div>
          
          <div className="footer-section">
            <h3>Navigation</h3>
            <ul>
              <li><Link to="/">Accueil</Link></li>
              <li><Link to="/courses">Cours</Link></li>
              <li><Link to="/chatbot">Chatbot</Link></li>
              <li><Link to="/create-card">Créer une fiche</Link></li>
            </ul>
          </div>

          <div className="footer-section">
            <h3>Ressources</h3>
            <ul>
              <li><Link to="/favorites/courses">Cours favoris</Link></li>
              <li><Link to="/favorites/cards">Fiches favorites</Link></li>
            </ul>
          </div>

          <div className="footer-section">
            <h3>Légal</h3>
            <ul>
              <li><Link to="/mentions-legales">Mentions légales</Link></li>
              <li><Link to="/confidentialite">Politique de confidentialité</Link></li>
            </ul>
          </div>
        </div>
      </div>
      
      <div className="footer-bottom">
        <p>&copy; 2024 Max. Tous droits réservés.</p>
      </div>
    </footer>
  );
};

export default Footer;