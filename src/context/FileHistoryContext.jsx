// src/context/FileHistoryContext.js
import React, { createContext, useContext, useState, useEffect } from 'react';
import { supabase } from '../lib/supabase';

const FileHistoryContext = createContext();

export const useFileHistory = () => useContext(FileHistoryContext);

export const FileHistoryProvider = ({ children }) => {
  const [recentFiles, setRecentFiles] = useState([]);
  const [loading, setLoading] = useState(true);

  // Charger les fichiers récents au démarrage
  useEffect(() => {
    fetchRecentFiles();
  }, []);

  // Fonction pour récupérer les fichiers récents depuis Supabase
  const fetchRecentFiles = async () => {
    try {
      setLoading(true);
      const { data, error } = await supabase
        .from('cards')
        .select('*')
        .order('created_at', { ascending: false })
        .limit(10); // Limitez le nombre de fiches à afficher

      if (error) {
        throw error;
      }

      setRecentFiles(data || []);
    } catch (error) {
      console.error("Erreur lors de la récupération des fichiers récents:", error);
    } finally {
      setLoading(false);
    }
  };

  // Fonction pour ajouter un fichier à l'historique
  const addFileToHistory = (newFile) => {
    setRecentFiles((prevFiles) => {
      // Éviter les doublons en filtrant par ID
      const fileExists = prevFiles.some(file => file.id === newFile.id);
      if (fileExists) {
        // Si le fichier existe déjà, le déplacer en premier
        return [
          newFile,
          ...prevFiles.filter(file => file.id !== newFile.id)
        ];
      }
      // Sinon, ajouter le nouveau fichier en premier
      return [newFile, ...prevFiles];
    });
  };

  return (
    <FileHistoryContext.Provider value={{ 
      recentFiles, 
      loading, 
      fetchRecentFiles, 
      addFileToHistory 
    }}>
      {children}
    </FileHistoryContext.Provider>
  );
};