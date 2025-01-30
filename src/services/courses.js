// src/services/courses.js
import { supabase } from '../lib/supabase';

export const fetchCours = async () => {
  try {
    console.log("Début fetchCours"); // Debug
    const { data, error } = await supabase
      .from('courses')
      .select('*');

    console.log("Résultat requête:", { data, error }); // Debug

    if (error) {
      throw new Error(error.message);
    }

    return data || [];
  } catch (error) {
    console.error("Erreur fetchCours:", error);
    throw error;
  }
};