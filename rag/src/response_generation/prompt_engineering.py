"""
Module pour le prompt engineering des réponses éducatives.
Ce module contient les templates de prompts utilisés pour générer des réponses
pédagogiques à partir des données récupérées par le système RAG.
"""

import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

class PromptTemplates:
    """Classe contenant les templates de prompts pour différents cas d'usage éducatifs."""
    
    @staticmethod
    def get_base_educational_prompt(context: str, question: str) -> str:
        """
        Template de base pour les questions éducatives.
        
        Args:
            context: Le contexte récupéré par le RAG
            question: La question posée par l'étudiant
            
        Returns:
            Le prompt formaté
        """
        return f"""
Vous êtes un assistant expert en électronique, capable de fournir des explications détaillées et de suivre les instructions données pour formater les réponses de manière optimale. Répondez à la question ci-dessous en utilisant uniquement les informations du contexte fourni. Si le contexte ne contient pas la réponse, répondez par "Je ne sais pas".

Contexte: {context}
Question: {question}

Votre réponse doit:
1. Être claire, précise et adaptée au niveau d'un étudiant en école d'ingénieur en électronique
2. Inclure des explications techniques lorsque nécessaire
3. Utiliser des analogies si cela peut faciliter la compréhension
4. Être structurée avec des paragraphes logiques
5. Être factuelle et basée uniquement sur les informations fournies dans le contexte
"""

    @staticmethod
    def get_course_summary_prompt(context: str, course_name: str) -> str:
        """
        Template pour générer un résumé de cours.
        
        Args:
            context: Le contexte récupéré par le RAG
            course_name: Le nom du cours à résumer
            
        Returns:
            Le prompt formaté
        """
        return f"""
Vous êtes un assistant expert en électronique, spécialisé dans la pédagogie. Votre tâche est de créer un résumé structuré du cours d'électronique dont le contenu est fourni ci-dessous. Ce résumé servira d'aide-mémoire pour des étudiants en école d'ingénieur.

Contenu du cours: {context}
Nom du cours: {course_name}

Générez un résumé complet du cours qui comprend:
1. Une introduction présentant les objectifs et le champ d'application du cours
2. Les concepts clés et les principes fondamentaux abordés
3. Les formules importantes et leur signification
4. Les applications pratiques des concepts
5. Une conclusion synthétisant les points essentiels à retenir

Votre résumé doit être structuré, clair et adapté au niveau d'étudiants en école d'ingénieur en électronique.
"""

    @staticmethod
    def get_concept_explanation_prompt(context: str, concept: str) -> str:
        """
        Template pour expliquer un concept spécifique.
        
        Args:
            context: Le contexte récupéré par le RAG
            concept: Le concept à expliquer
            
        Returns:
            Le prompt formaté
        """
        return f"""
Vous êtes un assistant expert en électronique, capable d'expliquer des concepts complexes de manière claire et pédagogique. Votre tâche est d'expliquer en détail le concept mentionné ci-dessous en utilisant uniquement les informations fournies dans le contexte.

Contexte: {context}
Concept à expliquer: {concept}

Votre explication doit:
1. Définir clairement le concept
2. Expliquer son importance dans le domaine de l'électronique
3. Détailler son fonctionnement ou ses principes
4. Mentionner les équations ou formules associées si pertinent
5. Donner un exemple concret d'application
6. Faire des liens avec d'autres concepts si possible

Utilisez un langage clair et précis, adapté à des étudiants en école d'ingénieur en électronique.
"""

    @staticmethod
    def get_educational_json_prompt(context: str, question: str) -> str:
        """
        Template pour générer une fiche de cours structurée au format JSON.
        
        Args:
            context: Le contexte récupéré par le RAG
            question: La question posée par l'étudiant
            
        Returns:
            Le prompt formaté
        """
        return f"""
Vous êtes un assistant expert en électronique, capable de fournir des explications détaillées et de suivre les instructions données pour formater les réponses de manière optimale. Répondez à la question ci-dessous en utilisant uniquement les informations du contexte fourni. Si le contexte ne contient pas la réponse, répondez par un JSON avec "Je ne sais pas" comme valeur du champ "Description du cours".

Contexte: {context}
Question: {question}

Générez une fiche complète pour un cours d'électronique en retournant un JSON exactement structuré comme suit :

{{
    "cours": {{
        "Titre du cours": "",
        "Description du cours": "",
        "Concepts clés": [],
        "Définitions et Formules": [],
        "Éléments clés à retenir": [],
        "Exemple concret": "",
        "Bullet points avec les concepts clés": [],
        "Mini test de connaissance pour évaluer ses connaissances": [],
        "Indices pour réussir le test": []
    }}
}}

Règles spécifiques à suivre :
- Respectez EXACTEMENT les noms des champs fournis ci-dessus, y compris les majuscules
- Assurez-vous que les champs qui attendent des listes [] contiennent toujours des tableaux
- Les autres champs doivent contenir des chaînes de caractères simples
- Ne pas utiliser de caractères de mise en forme
- Formater les formules mathématiques de manière simple
- Assurez-vous que la réponse est strictement au format JSON valide
- Ne JAMAIS ajouter de champs supplémentaires
- Ne JAMAIS omettre de champs de la structure
"""

    @staticmethod
    def get_problem_solving_prompt(context: str, problem: str) -> str:
        """
        Template pour résoudre un problème d'électronique.
        
        Args:
            context: Le contexte récupéré par le RAG
            problem: Le problème à résoudre
            
        Returns:
            Le prompt formaté
        """
        return f"""
Vous êtes un assistant expert en électronique, spécialisé dans la résolution de problèmes. Votre tâche est de résoudre le problème d'électronique présenté ci-dessous en utilisant uniquement les informations fournies dans le contexte.

Contexte: {context}
Problème: {problem}

Votre résolution doit suivre cette structure:
1. Analyse du problème: identifiez clairement ce qui est demandé et les données fournies
2. Méthodologie: expliquez l'approche que vous allez utiliser pour résoudre le problème
3. Résolution détaillée: résolvez le problème étape par étape, en justifiant chaque étape
4. Calculs: effectuez tous les calculs nécessaires de manière claire et précise
5. Résultat final: présentez la solution finale de manière claire
6. Vérification: confirmez que la solution est cohérente avec les données du problème

Utilisez des formules et des principes d'électronique appropriés, en vous basant uniquement sur les informations du contexte fourni.
"""

class PromptBuilder:
    """Classe pour construire des prompts adaptés au contexte éducatif."""
    
    def __init__(self):
        self.templates = PromptTemplates()
        
    def build_prompt(self, query_type: str, context: str, query: str, 
                     metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Construit un prompt adapté au type de requête éducative.
        
        Args:
            query_type: Le type de requête (question, cours, concept, json, problème)
            context: Le contexte récupéré par le RAG
            query: La requête principale (question, nom du cours, concept, etc.)
            metadata: Métadonnées supplémentaires optionnelles
            
        Returns:
            Le prompt construit
        """
        if metadata is None:
            metadata = {}
            
        logger.debug(f"Construction d'un prompt de type: {query_type}")
        
        # Enrichir le contexte avec des métadonnées pertinentes si disponibles
        enriched_context = self._enrich_context(context, metadata)
        
        # Sélectionner le template approprié selon le type de requête
        if query_type == "question":
            return self.templates.get_base_educational_prompt(enriched_context, query)
        elif query_type == "cours":
            return self.templates.get_course_summary_prompt(enriched_context, query)
        elif query_type == "concept":
            return self.templates.get_concept_explanation_prompt(enriched_context, query)
        elif query_type == "json":
            return self.templates.get_educational_json_prompt(enriched_context, query)
        elif query_type == "probleme":
            return self.templates.get_problem_solving_prompt(enriched_context, query)
        else:
            # Par défaut, utiliser le template de base
            logger.warning(f"Type de requête non reconnu: {query_type}, utilisation du template par défaut")
            return self.templates.get_base_educational_prompt(enriched_context, query)
    
    def _enrich_context(self, context: str, metadata: Dict[str, Any]) -> str:
        """
        Enrichit le contexte avec des métadonnées pertinentes.
        
        Args:
            context: Le contexte original
            metadata: Les métadonnées à ajouter
            
        Returns:
            Le contexte enrichi
        """
        # Convertir les métadonnées en un format lisible
        metadata_str = ""
        
        if "course_name" in metadata:
            metadata_str += f"\nCours: {metadata['course_name']}"
            
        if "page_numbers" in metadata:
            metadata_str += f"\nPages concernées: {', '.join(map(str, metadata['page_numbers']))}"
            
        if "similarity_scores" in metadata:
            # Ne pas inclure les scores dans le prompt final, c'est juste informatif pour le développement
            logger.debug(f"Scores de similarité: {metadata['similarity_scores']}")
            
        # Ajouter d'autres métadonnées si nécessaire
        
        # Combiner le contexte original avec les métadonnées
        if metadata_str:
            enriched_context = f"{context}\n\nInformations supplémentaires:{metadata_str}"
            return enriched_context
        
        return context

# Fonction pour obtenir une instance du builder de prompts
def get_prompt_builder() -> PromptBuilder:
    return PromptBuilder()