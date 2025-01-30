// src/pages/Courses/CoursesPage.jsx
import React, { useState, useEffect } from 'react';
import SearchBar from '../../components/SearchBar';
import FilterButtons from '../../components/FilterButtons';
import CoursList from '../../components/CoursList';
import { fetchCours } from '../../services/courses';

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
        console.log('Données reçues:', coursData); // Debug
        setCours(coursData);
        setFilteredCours(coursData);
      } catch (err) {
        console.error('Erreur:', err);
        setError(`Erreur lors du chargement des cours: ${err.message}`);
      } finally {
        setLoading(false);
      }
    };

    loadCours();
  }, []);

  return loading ? (
    <div className="min-h-screen bg-[#007179]">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 sm:py-24">
        <p className="text-white text-center">Chargement...</p>
      </div>
    </div>
  ) : (
    <div className="min-h-screen bg-[#007179]">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 sm:py-24">
        <h1 className="text-2xl sm:text-3xl font-bold text-white mb-8">
          L'ensemble des cours
        </h1>

        <div className="space-y-6">
          <SearchBar onSearch={handleSearch} />
          <FilterButtons 
            currentNiveau={currentNiveau}
            onNiveauChange={handleNiveauChange}
          />
          {error ? (
            <p className="text-red-500">{error}</p>
          ) : (
            <CoursList cours={filteredCours} />
          )}
        </div>
      </div>
    </div>
  );
};

export default CoursesPage;