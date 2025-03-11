// src/services/favorites.js
import { supabase } from '../lib/supabase';


export const addToFavorites = async (courseId) => {
  const TEST_USER_EMAIL = 'elisa.hagege@edu.ece.fr'; // Email test
  
  try {
    console.log('Tentative d\'ajout aux favoris:', { courseId, TEST_USER_EMAIL });
    
    const { data, error } = await supabase
      .from('saved_courses')
      .insert([{
        user_email: TEST_USER_EMAIL,
        course_id: courseId
      }])
      .select();

    if (error) {
      console.error('Erreur Supabase:', error);
      throw error;
    }

    console.log('Réponse Supabase:', data);
    return data;
  } catch (error) {
    console.error('Erreur lors de l\'ajout aux favoris:', error);
    throw error;
  }
};

export const removeFromFavorites = async (courseId) => {
  const TEST_USER_EMAIL = 'elisa.hagege@edu.ece.fr'; // Email test
  
  try {
    const { data, error } = await supabase
      .from('saved_courses')
      .delete()
      .match({
        user_email: TEST_USER_EMAIL,
        course_id: courseId
      });

    if (error) throw error;
    return data;
  } catch (error) {
    console.error('Erreur lors de la suppression des favoris:', error);
    throw error;
  }
};

export const checkIsFavorite = async (courseId) => {
  const TEST_USER_EMAIL = 'elisa.hagege@edu.ece.fr'; // Email test
  
  try {
    const { data, error } = await supabase
      .from('saved_courses')
      .select('*')
      .eq('course_id', courseId)
      .eq('user_email', TEST_USER_EMAIL)
      .single();

    if (error && error.code !== 'PGRST116') {
      console.error('Erreur Supabase:', error);
      throw error;
    }

    return !!data;
  } catch (error) {
    console.error('Erreur lors de la vérification des favoris:', error);
    return false;
  }
};

export const getFavoriteCourses = async () => {
  const TEST_USER_EMAIL = 'elisa.hagege@edu.ece.fr';

  try {
    // Joindre saved_courses avec courses pour obtenir les détails complets
    const { data, error } = await supabase
      .from('saved_courses')
      .select(`
        course_id,
        courses:courses(id, name, pdf_url, photo_url)
      `)
      .eq('user_email', TEST_USER_EMAIL);

    if (error) {
      console.error("Erreur Supabase:", error);
      throw error;
    }

    // Transformer les données pour correspondre au format attendu
    const formattedCourses = data?.map(item => ({
      id: item.courses.id,
      name: item.courses.name,
      pdf_url: item.courses.pdf_url,
      photo_url: item.courses.photo_url,
      year: 'ING2'
    })) || [];

    console.log("Cours favoris formatés:", formattedCourses);
    return formattedCourses;

  } catch (error) {
    console.error('Erreur dans getFavoriteCourses:', error);
    return [];
  }
};