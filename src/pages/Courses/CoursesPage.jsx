// src/pages/Courses/CoursesPage.jsx
import React, { useState, useEffect } from 'react';
import { fetchCours } from '../../services/courses';
import SearchBar from '../../components/SearchBar';
import FilterButtons from '../../components/FilterButtons';
import CoursList from '../../components/CoursList';

const CoursesPage = () => {
  const [cours, setCours] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filteredCours, setFilteredCours] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [currentNiveau, setCurrentNiveau] = useState('');

  useEffect(() => {
    const loadCours = async () => {
      try {
        const coursData = await fetchCours();
        const sortedCours = coursData.sort((a, b) => 
          a.name.localeCompare(b.name, 'fr', { sensitivity: 'base' })
        );
        setCours(sortedCours);
        setFilteredCours(sortedCours);
      } catch (err) {
        console.error('Erreur:', err);
        setError('Erreur lors du chargement des cours');
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
    let filtered = [...cours]; // Crée une copie du tableau
    
    if (term) {
      filtered = filtered.filter(cours => 
        cours.name.toLowerCase().includes(term.toLowerCase()) ||
        cours.year.toLowerCase().includes(term.toLowerCase())
      );
    }
    
    if (niveau) {
      filtered = filtered.filter(cours => 
        cours.year === niveau
      );
    }
    
    // Maintenir le tri alphabétique
    filtered.sort((a, b) => 
      a.name.localeCompare(b.name, 'fr', { sensitivity: 'base' })
    );
    
    setFilteredCours(filtered);
  };

  return (
    <div className="flex flex-col min-h-screen bg-[#007179]">
      <div className="flex-1 w-full max-w-7xl mx-auto px-4 md:px-6 lg:px-8">
        <div className="pt-20 md:pt-24 lg:pt-28">
          <h1 className="text-2xl md:text-3xl font-bold text-white mb-6 md:mb-8">
            L'ensemble des cours
          </h1>

          <div className="space-y-4 md:space-y-6">
            <div className="w-full">
              <SearchBar onSearch={handleSearch} />
            </div>

            <div className="flex flex-wrap gap-2 md:gap-3">
              <FilterButtons 
                currentNiveau={currentNiveau} 
                onNiveauChange={handleNiveauChange}
              />
            </div>

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