import React, { useState } from 'react';
import { Menu } from '@headlessui/react';
import { NavLink } from 'react-router-dom';
import { FiMenu, FiX } from 'react-icons/fi';
import logoMax from '../../../assets/images/logo-max.png';
import './Header.css';

const Header = () => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  const toggleMenu = () => {
    setIsMenuOpen(!isMenuOpen);
  };

  return (
    <header className="header">
      <nav className="nav-container">
        {/* Logo et bouton menu */}
        <div className="left-nav">
          <NavLink to="/" className="logo-container">
            <img src={logoMax} alt="MAX - Assistant électronique" className="logo" />
          </NavLink>
          
          <button 
            className="mobile-menu-button"
            onClick={toggleMenu}
            aria-label={isMenuOpen ? "Fermer le menu" : "Ouvrir le menu"}
          >
            {isMenuOpen ? <FiX size={24} /> : <FiMenu size={24} />}
          </button>
        </div>

        {/* Navigation principale */}
        <div className={`nav-content ${isMenuOpen ? 'nav-active' : ''}`}>
          <div className="nav-links">
            <NavLink 
              to="/courses" 
              className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
              onClick={() => setIsMenuOpen(false)}
            >
              Les cours
            </NavLink>
            <NavLink 
              to="/create-card" 
              className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
              onClick={() => setIsMenuOpen(false)}
            >
              Créer une fiche
            </NavLink>
          </div>

          <div className="right-nav">
            <NavLink 
              to="/chatbot" 
              className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
              onClick={() => setIsMenuOpen(false)}
            >
              Max le chatbot
            </NavLink>
            <Menu as="div" className="favorites-menu">
              <Menu.Button className="favorites-button">
                Mes favoris
                <span className="arrow-down"></span>
              </Menu.Button>
              <Menu.Items className="dropdown-menu">
                <Menu.Item>
                  {({ active }) => (
                    <NavLink
                      to="/favorites/courses"
                      className={({ isActive }) => `dropdown-item ${isActive ? 'active' : ''} ${active ? 'hover' : ''}`}
                      onClick={() => setIsMenuOpen(false)}
                    >
                      Mes cours
                    </NavLink>
                  )}
                </Menu.Item>
                <Menu.Item>
                  {({ active }) => (
                    <NavLink
                      to="/favorites/cards"
                      className={({ isActive }) => `dropdown-item ${isActive ? 'active' : ''} ${active ? 'hover' : ''}`}
                      onClick={() => setIsMenuOpen(false)}
                    >
                      Fiches et Quizz
                    </NavLink>
                  )}
                </Menu.Item>
              </Menu.Items>
            </Menu>
          </div>
        </div>
      </nav>
    </header>
  );
};

export default Header;