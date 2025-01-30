// src/services/courses.js
import { supabase } from '../lib/supabase';

export const fetchCours = async () => {
  try {
    console.log("Début fetchCours");
    const { data, error } = await supabase
      .from('courses')
      .select('*');

    console.log("Réponse Supabase:", { data, error }); // Debug

    if (error) {
      console.error("Erreur Supabase:", error);
      throw error;
    }

    return data || [];
  } catch (error) {
    console.error("Erreur fetchCours:", error);
    throw error;
  }
};