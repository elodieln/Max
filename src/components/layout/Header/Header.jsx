import React from 'react';
import { Menu } from '@headlessui/react';
import { Link } from 'react-router-dom';
import logoMax from '../../assets/images/logo-max.png'; // Ajuste le chemin selon ta structure
import './Header.css';

const Header = () => {
  return (
    <header className="header">
      <nav className="nav-container">
        {/* Logo et navigation gauche */}
        <div className="left-nav">
          <Link to="/" className="logo-container">
            <img src={logoMax} alt="MAX - Assistant électronique" className="logo" />
          </Link>
          <div className="nav-links">
            <Link to="/courses" className="nav-link">Les cours</Link>
            <Link to="/create-card" className="nav-link">Créer une fiche</Link>
          </div>
        </div>

        {/* Navigation droite */}
        <div className="right-nav">
          <Link to="/chatbot" className="nav-link">Max le chatbot</Link>
          <Menu as="div" className="favorites-menu">
            <Menu.Button className="favorites-button">
              Mes favoris
              <span className="arrow-down"></span>
            </Menu.Button>
            <Menu.Items className="dropdown-menu">
              <Menu.Item>
                {({ active }) => (
                  <Link
                    to="/favorites/courses"
                    className={`dropdown-item ${active ? 'active' : ''}`}
                  >
                    Mes cours
                  </Link>
                )}
              </Menu.Item>
              <Menu.Item>
                {({ active }) => (
                  <Link
                    to="/favorites/cards"
                    className={`dropdown-item ${active ? 'active' : ''}`}
                  >
                    Fiches et Quizz
                  </Link>
                )}
              </Menu.Item>
            </Menu.Items>
          </Menu>
        </div>
      </nav>
    </header>
  );
};

export default Header;