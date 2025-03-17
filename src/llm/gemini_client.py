# src/llm/gemini_client.py
import os
import base64
import logging
from typing import List, Dict, Any, Union, Optional
import json
import re

# Utiliser un bloc try/except pour l'import problématique
try:
    from openai import OpenAI
except ImportError:
    # Message d'erreur mais continuez l'exécution
    print("ATTENTION: Module OpenAI non trouvé. Exécutez 'pip install openai'")
    # Définir une classe factice pour éviter les erreurs de syntaxe
    class OpenAI:
        def __init__(self, **kwargs):
            pass

logger = logging.getLogger(__name__)

class GeminiClient:
    """Client pour l'interprétation multimodale des données via Gemini à travers OpenRouter"""
    
    # Variables de classe pour suivre les états d'erreur
    _auth_error_reported = False
    _service_error_reported = False
    
    def __init__(self):
        self.api_key = os.getenv('OPENROUTER_API_KEY')
        if not self.api_key:
            if not GeminiClient._auth_error_reported:
                logger.warning("OPENROUTER_API_KEY not found in environment variables")
                GeminiClient._auth_error_reported = True
            self.client = None
        else:
            try:
                self.client = OpenAI(
                    base_url="https://openrouter.ai/api/v1",
                    api_key=self.api_key
                )
                self.model = "google/gemini-2.0-flash-001"  # ou "google/gemini-2.0-flash-001" selon disponibilité
                logger.info(f"Initialized OpenRouter client with {self.model}")
            except Exception as e:
                if not GeminiClient._service_error_reported:
                    logger.error(f"Failed to initialize OpenRouter client: {str(e)}")
                    GeminiClient._service_error_reported = True
                self.client = None
    
    async def analyze_schema(self, image_data: str, context: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyse un schéma électronique avec Gemini via OpenRouter
        
        Args:
            image_data: Image en base64
            context: Contexte textuel associé au schéma (optionnel)
            
        Returns:
            Dict contenant l'analyse du schéma
        """
        # Vérifier si l'authentification OpenRouter est disponible
        if not self.client or not self.api_key:
            # Ne pas logger l'erreur si déjà rapportée
            return {
                "description": "Service d'analyse non disponible.",
                "components": [],
                "circuit_type": "inconnu",
                "formulas": []
            }
                
        try:
            # Préparer le prompt pour analyser un schéma électronique
            prompt = """
            Analyse ce schéma électronique et fournis les informations suivantes:
            1. Type de circuit (amplificateur, filtre, alimentation, etc.)
            2. Composants principaux identifiés
            3. Fonctionnalité du circuit
            4. Principe de fonctionnement
            
            Sois précis et technique. Si des formules sont présentes, explique-les.
            """
            
            if context:
                prompt += f"\n\nContexte du schéma: {context}"
            
            # Créer le contenu du message avec l'image en base64
            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/png;base64,{image_data}"}
                        }
                    ]
                }
            ]
            
            # Appeler OpenRouter
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=1000
            )
            
            # Extraire la réponse
            analysis_text = response.choices[0].message.content
            
            # Structurer la réponse
            analysis = {
                "description": analysis_text,
                "components": self._extract_components(analysis_text),
                "circuit_type": self._extract_circuit_type(analysis_text),
                "formulas": self._extract_formulas(analysis_text)
            }
            
            return analysis
        
        except Exception as e:
            # Ne rapporter l'erreur qu'une seule fois par type d'erreur
            error_type = type(e).__name__
            error_key = f"error_{error_type}"
            
            if not hasattr(GeminiClient, error_key):
                setattr(GeminiClient, error_key, True)
                logger.error(f"Error analyzing schema: {str(e)}")
            
            return {
                "description": "Échec de l'analyse du schéma.",
                "components": [],
                "circuit_type": "inconnu",
                "formulas": []
            }
    
    async def generate_response(self, query: str, relevant_chunks: List[Dict[str, Any]]) -> str:
        """
        Génère une réponse basée sur la requête et les chunks pertinents
        
        Args:
            query: Requête utilisateur
            relevant_chunks: Liste des chunks pertinents (texte et images)
            
        Returns:
            Réponse générée
        """
        # Vérifier si l'authentification OpenRouter est disponible
        if not self.client or not self.api_key:
            return "Service de réponse non disponible. Veuillez vérifier votre configuration OpenRouter."
            
        try:
            # Construire le contexte à partir des chunks
            context_text = "Informations pertinentes:\n"
            images = []
            
            for chunk in relevant_chunks:
                if chunk['chunk_type'] in ['text', 'mixed']:
                    if chunk['chunk_text']:
                        context_text += f"\n{chunk['chunk_text']}\n"
                        
                if chunk['chunk_type'] in ['image', 'mixed']:
                    if chunk.get('image_data'):
                        images.append({
                            "type": "image_url",
                            "image_url": {"url": f"data:image/png;base64,{chunk['image_data']}"}
                        })
            
            # Construire le prompt pour Gemini
            prompt = f"""
            En tant qu'assistant spécialisé en électronique, réponds à la question suivante en te basant
            sur les informations fournies. Si la réponse n'est pas contenue dans les informations
            fournies, indique-le clairement.
            
            Question: {query}
            
            {context_text}
            """
            
            # Préparer la liste des contenus
            contents = [{"type": "text", "text": prompt}]
            # Limiter le nombre d'images envoyées (max 5)
            for img in images[:5]:
                contents.append(img)
            
            # Créer le message
            messages = [
                {
                    "role": "user",
                    "content": contents
                }
            ]
            
            # Générer la réponse
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=1500
            )
            
            return response.choices[0].message.content
        
        except Exception as e:
            # Ne rapporter l'erreur qu'une seule fois par type d'erreur
            error_type = type(e).__name__
            error_key = f"error_{error_type}"
            
            if not hasattr(GeminiClient, error_key):
                setattr(GeminiClient, error_key, True)
                logger.error(f"Error generating response: {str(e)}")
            
            return f"Désolé, je n'ai pas pu traiter votre requête. Veuillez vérifier votre configuration ou réessayer plus tard."
    
    async def rewrite_query(self, original_query: str) -> str:
        """
        Réécrit une requête pour optimiser la recherche vectorielle dans un contexte d'électronique,
        en insistant sur les aspects techniques liés au dopage des semi-conducteurs et à la formation d'une jonction PN.
        
        Args:
            original_query: Requête originale de l'utilisateur
            
        Returns:
            Requête reformulée, mettant l'accent sur le dopage (type N et P), les porteurs de charge et la jonction PN.
        """
        # Vérifier si l'authentification OpenRouter est disponible
        if not self.client or not self.api_key:
            return original_query

        try:
            prompt = f"""
            Reformule la requête suivante pour optimiser la recherche dans un contexte d'électronique, 
            en mettant l'accent sur les mécanismes de dopage dans les semi-conducteurs.
            En particulier, insiste sur la différence entre le dopage de type N (avec des atomes donneurs, par exemple le phosphore)
            et le dopage de type P (avec des atomes accepteurs, par exemple le bore), et sur l'impact de ces dopages sur la formation d'une jonction PN.
            Assure-toi d'inclure les termes techniques tels que 'porteurs de charge', 'niveau de Fermi', 'zone de déplétion' et 'jonction PN'.
            
            Voici la requête originale:
            "{original_query}"
            
            Réponds uniquement avec la requête reformulée.
            """
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=100
            )
            rewritten_query = response.choices[0].message.content.strip().strip('"')
            return rewritten_query

        except Exception as e:
            # Ne pas rapporter l'erreur si elle a déjà été signalée
            if not hasattr(GeminiClient, "_rewrite_error_reported"):
                GeminiClient._rewrite_error_reported = True
                logger.error(f"Error rewriting query: {str(e)}")
            return original_query


    
    def _extract_components(self, text: str) -> List[str]:
        """Extrait les composants électroniques mentionnés dans le texte"""
        components = []
        component_patterns = [
            r"résistance[s]?", r"condensateur[s]?", r"transistor[s]?", 
            r"diode[s]?", r"capteur[s]?", r"amplificateur[s]?",
            r"bobine[s]?", r"inductance[s]?", r"transformateur[s]?"
        ]
        
        for pattern in component_patterns:
            matches = re.findall(pattern, text.lower())
            components.extend(matches)
        
        return list(set(components))
    
    def _extract_circuit_type(self, text: str) -> str:
        """Détermine le type de circuit basé sur le texte"""
        circuit_types = {
            "amplificateur": ["amplificateur", "ampli"],
            "filtre": ["filtre", "passe-bas", "passe-haut", "passe-bande"],
            "alimentation": ["alimentation", "convertisseur", "régulateur"],
            "oscillateur": ["oscillateur", "multivibrateur"],
            "pont": ["pont", "wheatstone"],
            "capteur": ["capteur", "détecteur", "transducteur"]
        }
        
        text_lower = text.lower()
        for circuit_type, keywords in circuit_types.items():
            for keyword in keywords:
                if keyword in text_lower:
                    return circuit_type
        
        return "non identifié"
    
    def _extract_formulas(self, text: str) -> List[str]:
        """Extrait les formules mathématiques du texte"""
        formulas = []
        
        # Motifs de base pour les formules
        formula_patterns = [
            r"[A-Za-z]+\s*=\s*[A-Za-z0-9\+\-\*\/\(\)\s]+",  # e.g., "Vout = Vin * R2/R1"
            r"[A-Za-z\d\s\+\-\*\/\(\)=]{5,}",  # Séquences ressemblant à des formules
        ]
        
        for pattern in formula_patterns:
            matches = re.findall(pattern, text)
            formulas.extend([m.strip() for m in matches if "=" in m])
        
        return list(set(formulas))