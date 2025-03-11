import React, { useState, useEffect } from 'react';
import { supabase } from '../../../lib/supabase';  // Modifié ici
import SearchBar from '../../../components/SearchBar';  // Modifié ici
import FilterButtons from '../../../components/FilterButtons';  // Modifié ici
import CoursList from '../../../components/CoursList';  // Ajouté ici
import './CoursesFavoritesPage.css';

const CoursesFavoritesPage = () => {
 const [cours, setCours] = useState([]);
 const [loading, setLoading] = useState(true);
 const [error, setError] = useState(null);
 const [filteredCours, setFilteredCours] = useState([]);
 const [searchTerm, setSearchTerm] = useState('');
 const [currentNiveau, setCurrentNiveau] = useState('');

 const loadFavoriteCours = async () => {
   try {
     setLoading(true);
     const TEST_USER_EMAIL = 'elisa.hagege@edu.ece.fr';

     // Récupérer les favoris avec une jointure sur courses
     const { data: favoritesData, error: favoritesError } = await supabase
       .from('saved_courses')
       .select(`
         course_id,
         courses!inner(id, name, pdf_url, photo_url)
       `)
       .eq('user_email', TEST_USER_EMAIL);

     console.log("Données reçues de Supabase:", favoritesData);

     if (favoritesError) {
       console.error("Erreur Supabase:", favoritesError);
       throw favoritesError;
     }

     if (favoritesData && favoritesData.length > 0) {
       const formattedCourses = favoritesData.map(item => ({
         id: item.courses.id,
         name: item.courses.name,
         pdf_url: item.courses.pdf_url,
         photo_url: item.courses.photo_url,
         year: 'ING2'
       }));

       console.log("Cours formatés:", formattedCourses);
       setCours(formattedCourses);
       setFilteredCours(formattedCourses);
     } else {
       console.log("Aucun favori trouvé");
       setCours([]);
       setFilteredCours([]);
     }
   } catch (err) {
     console.error('Erreur complète:', err);
     setError('Erreur lors du chargement des cours favoris');
   } finally {
     setLoading(false);
   }
 };

 useEffect(() => {
   loadFavoriteCours();
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
     filtered = filtered.filter(course => 
       course.name.toLowerCase().includes(term.toLowerCase())
     );
   }
   if (niveau) {
     filtered = filtered.filter(course => course.year === niveau);
   }
   setFilteredCours(filtered);
 };

 if (loading) {
   return (
     <div className="min-h-screen pt-20 px-4 sm:px-6 lg:px-8 bg-[#007179]">
       <div className="flex justify-center items-center">
         <p className="text-white text-xl">Chargement des cours favoris...</p>
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
         Mes cours favoris
       </h1>
       <div className="space-y-6">
         <SearchBar onSearch={handleSearch} />
         <FilterButtons 
           currentNiveau={currentNiveau} 
           onNiveauChange={handleNiveauChange}
         />
         {filteredCours.length === 0 ? (
           <div className="text-center text-white py-10">
             <p>Aucun cours favori trouvé</p>
           </div>
         ) : (
           <CoursList cours={filteredCours} />
         )}
       </div>
     </div>
   </div>
 );
};

export default CoursesFavoritesPage;

