// src/services/courses.js
import { supabase } from '../lib/supabase';

export const fetchCours = async () => {
  try {
    console.log("Début fetchCours");
    const { data, error } = await supabase
      .from('courses')
      .select('*')
      .order('id', { ascending: true }); // Ajout du tri

    if (error) {
      console.error("Erreur Supabase:", error);
      throw error;
    }

    console.log("Données reçues:", data);
    return data || [];
  } catch (error) {
    console.error("Erreur complète:", error);
    throw error;
  }
};