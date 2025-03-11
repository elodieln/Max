import { supabase } from '../lib/supabase';

// Fonction pour stocker une fiche générée dans Supabase
export const saveGeneratedFile = async (fileData, pdfBlob) => {
  try {
    console.log("Début de la sauvegarde du fichier");
    
    // Utiliser l'URL du blob local au lieu d'essayer d'uploader dans Supabase Storage
    const publicUrl = fileData.url;
    
    // Sauvegarder les métadonnées dans la table 'cards'
    const { data, error } = await supabase
      .from('cards')
      .insert({
        name: fileData.name,
        pdf_url: publicUrl,
        progress: 1,
        created_by: 'elisa.hagege@edu.ece.fr',
        created_at: new Date().toISOString()
      })
      .select();
      
    if (error) {
      console.error("Erreur lors de la sauvegarde des métadonnées:", error);
      throw new Error(`Erreur de base de données: ${error.message}`);
    }
    
    console.log("Métadonnées sauvegardées avec succès:", data);
    
    // On retourne l'ID du fichier sauvegardé
    return data[0].id;
  
  } catch (error) {
    console.error("Exception lors de la sauvegarde du fichier:", error);
    throw error;
  }
};

// Fonction pour récupérer toutes les fiches générées
export const getAllFiles = async () => {
  try {
    const { data, error } = await supabase
      .from('cards')
      .select('*')
      .order('created_at', { ascending: false });
      
    if (error) {
      console.error("Erreur lors de la récupération des fichiers:", error);
      throw new Error("Impossible de récupérer les fichiers");
    }
    
    return data;
  } catch (error) {
    console.error("Erreur lors de la récupération des fichiers:", error);
    throw error;
  }
};

// Fonction pour ajouter une fiche aux favoris
export const addToFavorites = async (fileId) => {
  try {
    const { data, error } = await supabase
      .from('saved_cards')
      .insert({
        card_id: fileId,
        user_email: 'elisa.hagege@edu.ece.fr',
        created_at: new Date().toISOString()
      })
      .select();
      
    if (error) {
      console.error("Erreur lors de l'ajout aux favoris:", error);
      throw new Error("Impossible d'ajouter aux favoris");
    }
    
    return data[0].id;
  } catch (error) {
    console.error("Erreur lors de l'ajout aux favoris:", error);
    throw error;
  }
};

// Fonction pour retirer une fiche des favoris
export const removeFromFavorites = async (fileId) => {
  try {
    const { error } = await supabase
      .from('saved_cards')
      .delete()
      .eq('card_id', fileId);
      
    if (error) {
      console.error("Erreur lors du retrait des favoris:", error);
      throw new Error("Impossible de retirer des favoris");
    }
    
    return true;
  } catch (error) {
    console.error("Erreur lors du retrait des favoris:", error);
    throw error;
  }
};

export const getFavoriteFiles = async () => {
  try {
    // Récupérer les IDs des fiches sauvegardées
    const { data: savedCardsData, error: savedCardsError } = await supabase
      .from('saved_cards')
      .select('card_id')
      .eq('user_email', 'elisa.hagege@edu.ece.fr');
      
    if (savedCardsError) {
      console.error("Erreur lors de la récupération des favoris:", savedCardsError);
      throw new Error("Impossible de récupérer les favoris");
    }
    
    // Si aucun favori, retourner un tableau vide
    if (!savedCardsData || savedCardsData.length === 0) {
      return [];
    }
    
    // Extraire les IDs des fiches favoris
    const cardIds = savedCardsData.map(item => item.card_id);
    
    // Récupérer les données complètes des fiches depuis la table cards
    const { data: cardsData, error: cardsError } = await supabase
      .from('cards')
      .select('*')
      .in('id', cardIds);
      
    if (cardsError) {
      console.error("Erreur lors de la récupération des fiches:", cardsError);
      throw new Error("Impossible de récupérer les détails des favoris");
    }
    
    return cardsData || [];
  } catch (error) {
    console.error("Erreur lors de la récupération des favoris:", error);
    return [];
  }
};

export const isFileInFavorites = async (fileId) => {
  try {
    // Regardons la structure exacte de la table saved_cards
    const { data, error } = await supabase
      .from('saved_cards')
      .select('*') // Sélectionnons toutes les colonnes pour voir la structure
      .eq('card_id', fileId);
      
    if (error) {
      console.error("Erreur lors de la vérification des favoris:", error);
      throw new Error("Impossible de vérifier les favoris");
    }
    
    return data && data.length > 0;
  } catch (error) {
    console.error("Erreur lors de la vérification des favoris:", error);
    throw error;
  }
};