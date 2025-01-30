// src/services/courses.js
import { supabase } from '../lib/supabase'

export const fetchCours = async () => {
  try {
    const { data, error } = await supabase
      .from('courses')
      .select('*')
      .order('id')

    if (error) {
      throw error
    }

    return data
  } catch (error) {
    console.error('Erreur lors de la récupération des cours:', error)
    throw error
  }
}

export const updateFavori = async (coursId, isFavori) => {
  try {
    // Pour gérer les favoris, on utilise la table saved_courses
    if (isFavori) {
      const { error } = await supabase
        .from('saved_courses')
        .insert([{ course_id: coursId, user_email: 'email_utilisateur' }]) // À remplacer par l'email de l'utilisateur connecté
      if (error) throw error
    } else {
      const { error } = await supabase
        .from('saved_courses')
        .delete()
        .match({ course_id: coursId, user_email: 'email_utilisateur' }) // À remplacer par l'email de l'utilisateur connecté
      if (error) throw error
    }

    return true
  } catch (error) {
    console.error('Erreur lors de la mise à jour du favori:', error)
    return false
  }
}