// src/services/courses.js
import { supabase } from '../lib/supabase';

export const fetchCours = async () => {
  console.log("Tentative de connexion à Supabase..."); // Debug
  
  try {
    // Vérifier que le client est bien initialisé
    if (!supabase) {
      throw new Error("Client Supabase non initialisé");
    }

    // Log la configuration
    console.log("Configuration Supabase:", {
      url: supabase.supabaseUrl,
      hasKey: !!supabase.supabaseKey
    });

    // Faire la requête avec plus de détails
    const { data, error, status, statusText } = await supabase
      .from('courses')
      .select('*');

    // Log complet de la réponse
    console.log("Réponse complète:", {
      status,
      statusText,
      data,
      error
    });

    if (error) {
      throw error;
    }

    // Vérification des données
    if (!data) {
      console.warn("Pas de données reçues");
      return [];
    }

    console.log("Nombre de cours récupérés:", data.length);
    return data;
  } catch (error) {
    console.error("Erreur détaillée:", {
      message: error.message,
      code: error.code,
      details: error?.details,
      hint: error?.hint
    });
    throw error;
  }
};