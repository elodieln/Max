# src/extractors/pdf_processor.py
from pypdf import PdfReader
from pdf2image import convert_from_path
import io
import logging
import base64
from PIL import Image
from typing import List, Dict, Any
import os
import re

logger = logging.getLogger(__name__)

class PDFProcessor:
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.reader = PdfReader(pdf_path)
        self.chunk_size = 500  # Taille cible pour les chunks de texte
        self.overlap = 100     # Chevauchement entre les chunks
        
    def extract_content(self) -> List[Dict[str, Any]]:
        """
        Extrait le contenu du PDF page par page avec un meilleur découpage et métadonnées
        Inclut maintenant des chunks mixtes pour le RAG multimodal
        """
        try:
            chunks = []
            # Convertir les pages en images
            pages = convert_from_path(self.pdf_path)
            
            # Extraire le contenu pour chaque page
            for page_num, (page_text, page_image) in enumerate(zip(self.reader.pages, pages), 1):
                # Extraction et nettoyage du texte
                text = self._clean_text(page_text.extract_text())
                
                # Détecter la section du cours
                section = self._detect_section(text)
                
                # Créer les chunks de texte
                text_chunks = self._create_text_chunks(text, page_num, section)
                chunks.extend(text_chunks)
                
                # Sauvegarder l'image de la page
                img_buffer = io.BytesIO()
                page_image.save(img_buffer, format='PNG')
                img_base64 = base64.b64encode(img_buffer.getvalue()).decode()
                
                # Détecter le type de contenu de l'image
                content_type = self._detect_content_type(text)
                
                # Ajouter le chunk d'image avec métadonnées
                chunks.append({
                    'type': 'image',
                    'content': img_base64,
                    'page_number': page_num,
                    'metadata': {
                        'section': section,
                        'content_type': content_type,
                        'has_formula': self._has_formula(text),
                        'has_diagram': self._has_diagram(text)
                    }
                })
                
                # NOUVELLE PARTIE: Ajouter un chunk mixte (texte + image)
                chunks.append({
                    'type': 'mixed',
                    'content': text,  # Le texte complet de la page
                    'image_data': img_base64,  # L'image complète de la page
                    'page_number': page_num,
                    'metadata': {
                        'section': section,
                        'content_type': content_type,
                        'has_formula': self._has_formula(text),
                        'has_diagram': self._has_diagram(text),
                        'is_multimodal': True
                    }
                })
                
                logger.info(f"Processed page {page_num} - Section: {section}, Content type: {content_type}")
            
            return chunks
            
        except Exception as e:
            logger.error(f"Error extracting content from PDF: {str(e)}")
            raise
            
    def _clean_text(self, text: str) -> str:
        """Nettoie et formate le texte"""
        # Corriger les espaces manquants après les points
        text = re.sub(r'\.([A-Z])', r'. \1', text)
        # Corriger les espaces manquants autour des emails
        text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)
        # Supprimer les espaces multiples
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    def _create_text_chunks(self, text: str, page_num: int, section: str) -> List[Dict[str, Any]]:
        """Crée des chunks de texte avec chevauchement"""
        chunks = []
        words = text.split()
        chunk_words = self.chunk_size // 5  # Estimation moyenne de 5 caractères par mot
        
        for i in range(0, len(words), chunk_words - self.overlap // 5):
            chunk_text = ' '.join(words[i:i + chunk_words])
            if len(chunk_text) > 50:  # Ignorer les chunks trop petits
                chunks.append({
                    'type': 'text',
                    'content': chunk_text,
                    'page_number': page_num,
                    'metadata': {
                        'section': section,
                        'position': i,
                        'has_formula': self._has_formula(chunk_text),
                        'has_diagram': self._has_diagram(chunk_text)
                    }
                })
        return chunks
    
    def _detect_section(self, text: str) -> str:
        """Détecte la section du cours basée sur un pattern plus générique"""
        
        # Détection basée sur la numérotation romaine classique des cours
        roman_sections = {
            'section_1': r'I\.[\s\n]',
            'section_2': r'II\.[\s\n]',
            'section_3': r'III\.[\s\n]',
            'section_4': r'IV\.[\s\n]',
            'section_5': r'V\.[\s\n]'
        }
        
        # Détection des sections principales
        sections = {
            'introduction': r'Introduction|Présentation|Sommaire',
            'théorie': r'Théorie|Définition|Concept',
            'pratique': r'Pratique|Application|Mise en œuvre',
            'conclusion': r'Conclusion|Résumé|Synthèse'
        }
        
        # D'abord chercher les sections numérotées
        for section, pattern in roman_sections.items():
            if re.search(pattern, text, re.IGNORECASE):
                return section
        
        # Ensuite chercher les sections classiques
        for section, pattern in sections.items():
            if re.search(pattern, text, re.IGNORECASE):
                return section
                
        return 'général'
    
    def _detect_content_type(self, text: str) -> str:
        """Détecte le type de contenu basé sur le texte environnant"""
        if self._has_formula(text):
            return 'formula'
        elif self._has_diagram(text):
            return 'diagram'
        elif 'Figure' in text or 'Graphique' in text:
            return 'figure'
        return 'text'
    
    def _has_formula(self, text: str) -> bool:
        """Détecte la présence de formules mathématiques"""
        formula_patterns = [
            r'[=+\-*/^()]',  # Opérateurs mathématiques
            r'[α-ωΑ-Ω]',     # Lettres grecques
            r'\d+[\.,]\d+',  # Nombres décimaux
        ]
        return any(re.search(pattern, text) for pattern in formula_patterns)
    
    def _has_diagram(self, text: str) -> bool:
        """Détecte la présence de diagrammes ou schémas électriques"""
        diagram_keywords = [
            'circuit', 'schéma', 'diagramme', 'montage',
            'transistor', 'résistance', 'condensateur',
            'amplificateur', 'capteur'
        ]
        return any(keyword in text.lower() for keyword in diagram_keywords)
    
    def _detect_electronics_metadata(self, text: str) -> Dict[str, bool]:
        """Détecte les concepts d'électronique dans le texte"""
        return {
            'has_component_description': bool(re.search(r'transistor|resistance|capacitor|diode', text, re.IGNORECASE)),
            'has_measurements': bool(re.search(r'volt|ampere|ohm|hertz|decibel', text, re.IGNORECASE)),
            'has_calculations': bool(re.search(r'calcul|equation|formule', text, re.IGNORECASE))
        }
    
    def _extract_metadata(self, text: str) -> Dict[str, Any]:
        """Extrait des métadonnées génériques utiles pour tous types de cours"""
        return {
            'has_formula': self._has_formula(text),
            'has_diagram': self._has_diagram(text),
            'has_numerical_values': bool(re.search(r'\d+(?:\.\d+)?(?:\s*[VΩAWHz])', text)),  # Détection de valeurs avec unités
            'type': 'cours'  # Pour potentiellement différencier cours/TD/TP plus tard
        }