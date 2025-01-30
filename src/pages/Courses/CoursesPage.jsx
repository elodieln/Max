import React, { useState, useEffect } from 'react';  // Ajout de useState ici
import SearchBar from '../../components/SearchBar';
import FilterButtons from '../../components/FilterButtons';
import CoursList from '../../components/CoursList';
import { fetchCours, updateFavori } from '../../services/courses';


const CoursesPage = () => {
  const [cours, setCours] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filteredCours, setFilteredCours] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [currentNiveau, setCurrentNiveau] = useState('');

  useEffect(() => {
    loadCours();
  }, []);

  const loadCours = async () => {
    try {
      setLoading(true);
      const coursData = await fetchCours();
      setCours(coursData);
      setFilteredCours(coursData);
    } catch (err) {
      setError(`Erreur lors du chargement des cours: ${err.message}`);
      console.error('Erreur:', err);
    } finally {
      setLoading(false);
    }
  };

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

  if (loading) {
    return (
      <div className="min-h-screen pt-20 px-4 sm:px-6 lg:px-8 bg-[#007179]">
        <div className="flex justify-center items-center">
          <p className="text-white text-xl">Chargement des cours...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen pt-20 px-4 sm:px-6 lg:px-8 bg-[#007179]">
        <div className="flex justify-center items-center">
          <p className="text-white text-xl">{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen pt-20 px-4 sm:px-6 lg:px-8 bg-[#007179]">
      <div className="max-w-7xl mx-auto space-y-8">
        <h1 className="text-3xl font-bold text-white">
          L'ensemble des cours
        </h1>

        <div className="space-y-6">
          <SearchBar onSearch={handleSearch} />
          <FilterButtons 
            currentNiveau={currentNiveau} 
            onNiveauChange={handleNiveauChange}
          />
          <CoursList 
            cours={filteredCours}
          />
        </div>
      </div>
    </div>
  );
};

export default CoursesPage;