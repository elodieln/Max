import React from 'react';
import { Menu } from '@headlessui/react';
import { NavLink } from 'react-router-dom';
import logoMax from '../../../assets/images/logo-max.png';
import './Header.css';

const Header = () => {
  return (
    <header className="header">
      <nav className="nav-container">
        {/* Logo et navigation gauche */}
        <div className="left-nav">
          <NavLink to="/" className="logo-container">
            <img src={logoMax} alt="MAX - Assistant électronique" className="logo" />
          </NavLink>
          <div className="nav-links">
            <NavLink 
              to="/courses" 
              className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
            >
              Les cours
            </NavLink>
            <NavLink 
              to="/create-card" 
              className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
            >
              Créer une fiche
            </NavLink>
          </div>
        </div>

        {/* Navigation droite */}
        <div className="right-nav">
          <NavLink 
            to="/chatbot" 
            className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
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
                  >
                    Fiches et Quizz
                  </NavLink>
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