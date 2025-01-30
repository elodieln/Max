// src/pages/Courses/CoursesPage.jsx
import React, { useState, useEffect } from 'react';
import SearchBar from '../../components/SearchBar';
import FilterButtons from '../../components/FilterButtons';
import CoursList from '../../components/CoursList';
import { fetchCours } from '../../services/courses';

// Définition du composant avec une fonction fléchée
const CoursesPage = () => {
  const [cours, setCours] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filteredCours, setFilteredCours] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [currentNiveau, setCurrentNiveau] = useState('');

  // Effet pour charger les cours
  useEffect(() => {
    const loadCours = async () => {
      try {
        console.log("Début du chargement des cours...");
        setLoading(true);
        
        const coursData = await fetchCours();
        console.log("Données des cours reçues:", coursData);
        
        setCours(coursData);
        setFilteredCours(coursData);
      } catch (err) {
        console.error("Erreur dans CoursesPage:", err);
        setError(`Erreur: ${err.message}`);
      } finally {
        setLoading(false);
      }
    };

    loadCours();
  }, []);

  const handleSearch = (term) => {
    setSearchTerm(term);
    filterCours(term, currentNiveau);
  };

  const handleNiveauChange = (niveau) => {
    const newNiveau = niveau === currentNiveau ? '' : niveau;
    setCurrentNiveau(newNiveau);
    filterCours(searchTerm, newNiveau);
  };

  const filterCours = (term, niveau) => {
    let filtered = cours;
    if (term) {
      filtered = filtered.filter(cours => 
        cours.name.toLowerCase().includes(term.toLowerCase())
      );
    }
    if (niveau) {
      filtered = filtered.filter(cours => 
        cours.year === niveau
      );
    }
    setFilteredCours(filtered);
  };

  return (

    <div className="flex flex-col min-h-screen bg-[#007179]">
      {/* Container principal avec padding adaptatif */}
      <div className="flex-1 w-full max-w-7xl mx-auto px-4 md:px-6 lg:px-8">
        {/* En-tête avec espacement responsive */}
        <div className="pt-20 md:pt-24 lg:pt-28">
          <h1 className="text-2xl md:text-3xl font-bold text-white mb-6 md:mb-8">
            L'ensemble des cours
          </h1>

          {/* Zone de recherche et filtres */}
          <div className="space-y-4 md:space-y-6">
            {/* Barre de recherche responsive */}
            <div className="w-full">
              <SearchBar onSearch={handleSearch} />
            </div>

            {/* Filtres avec espacement adaptatif */}
            <div className="flex flex-wrap gap-2 md:gap-3">
              <FilterButtons 
                currentNiveau={currentNiveau} 
                onNiveauChange={handleNiveauChange}
              />
            </div>

            {/* Liste des cours ou messages d'état */}
            <div className="w-full">
              {loading ? (
                <div className="flex justify-center py-8">
                  <p className="text-white text-lg">Chargement...</p>
                </div>
              ) : error ? (
                <div className="flex justify-center py-8">
                  <p className="text-red-400">{error}</p>
                </div>
              ) : (
                <CoursList cours={filteredCours} />
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};


export default CoursesPage;