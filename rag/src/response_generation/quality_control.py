"""
Module pour le contrôle de la qualité des réponses.
Ce module contient des outils pour évaluer et améliorer la qualité des réponses générées.
"""

import logging
import re
import json
from typing import Dict, List, Any, Tuple, Optional

logger = logging.getLogger(__name__)

class QualityControl:
    """
    Classe pour évaluer et améliorer la qualité des réponses générées.
    """
    
    def __init__(self):
        """Initialise le contrôleur de qualité."""
        # Seuils de qualité
        self.min_response_length = 50  # Nombre minimal de caractères
        self.max_response_length = 4000  # Nombre maximal de caractères recommandé
        self.min_coherence_score = 0.7  # Score minimal de cohérence
        
        # Motifs à rechercher
        self.patterns = {
            "incomplete_json": r'[{[](?:[^{}[\]]*[{[][^{}[\]]*[}\]][^{}[\]]*)*[^{}[\]]*$',
            "hallucination_indicators": [
                r"je ne suis pas sûr",
                r"je ne suis pas certain",
                r"je n'ai pas cette information",
                r"je ne peux pas confirmer",
                r"il est possible que",
                r"il se pourrait que"
            ],
            "irrelevant_content": [
                r"en tant qu'assistant",
                r"en tant qu'ia",
                r"je suis un assistant",
                r"je suis une intelligence artificielle",
                r"je n'ai pas accès à"
            ]
        }
        
        logger.info("Contrôleur de qualité initialisé")
    
    def check_response_quality(self, response: Any, query_type: str = "question") -> Dict[str, Any]:
        """
        Vérifie la qualité d'une réponse générée.
        
        Args:
            response: La réponse à vérifier (texte ou dictionnaire)
            query_type: Le type de requête
            
        Returns:
            Dictionnaire contenant les résultats de l'évaluation
        """
        # Convertir la réponse en texte si nécessaire
        response_text = self._convert_to_text(response)
        
        # Initialiser les résultats
        results = {
            "quality_score": 0.0,
            "issues": [],
            "warnings": [],
            "is_acceptable": False,
            "suggestions": []
        }
        
        # Vérifier la longueur
        length_score, length_issues = self._check_length(response_text)
        
        # Vérifier la cohérence et la structure
        coherence_score, coherence_issues = self._check_coherence(response_text, query_type)
        
        # Vérifier les hallucinations potentielles
        hallucination_score, hallucination_issues = self._check_hallucinations(response_text)
        
        # Vérifier le contenu non pertinent
        relevance_score, relevance_issues = self._check_relevance(response_text)
        
        # Vérifier le format JSON pour les requêtes de type JSON
        json_score, json_issues = 1.0, []
        if query_type == "json":
            json_score, json_issues = self._check_json_format(response)
        
        # Ajouter tous les problèmes identifiés
        results["issues"].extend(length_issues + coherence_issues + hallucination_issues + 
                                relevance_issues + json_issues)
        
        # Calculer le score global (moyenne pondérée)
        weights = {
            "length": 0.15,
            "coherence": 0.35,
            "hallucination": 0.25,
            "relevance": 0.15,
            "json": 0.1 if query_type == "json" else 0
        }
        
        # Ajuster les poids si ce n'est pas une requête JSON
        if query_type != "json":
            remaining_weight = weights["json"]
            weights["json"] = 0
            weights["coherence"] += remaining_weight / 2
            weights["hallucination"] += remaining_weight / 2
        
        quality_score = (
            length_score * weights["length"] +
            coherence_score * weights["coherence"] +
            hallucination_score * weights["hallucination"] +
            relevance_score * weights["relevance"] +
            json_score * weights["json"]
        )
        
        # Arrondir le score à 2 décimales
        results["quality_score"] = round(quality_score, 2)
        
        # Déterminer si la réponse est acceptable
        results["is_acceptable"] = quality_score >= 0.7 and len(results["issues"]) <= 2
        
        # Générer des suggestions d'amélioration
        results["suggestions"] = self._generate_suggestions(results["issues"])
        
        # Classer certains problèmes comme avertissements
        self._categorize_issues_and_warnings(results)
        
        return results
    
    def _convert_to_text(self, response: Any) -> str:
        """
        Convertit une réponse en texte.
        
        Args:
            response: La réponse à convertir
            
        Returns:
            La réponse sous forme de texte
        """
        if isinstance(response, str):
            return response
        elif isinstance(response, dict):
            try:
                return json.dumps(response, ensure_ascii=False, indent=2)
            except Exception as e:
                logger.error(f"Erreur lors de la conversion du dictionnaire en texte: {str(e)}")
                return str(response)
        else:
            return str(response)
    
    def _check_length(self, text: str) -> Tuple[float, List[str]]:
        """
        Vérifie la longueur de la réponse.
        
        Args:
            text: Le texte à vérifier
            
        Returns:
            Score de qualité et liste des problèmes identifiés
        """
        issues = []
        length = len(text)
        
        if length < self.min_response_length:
            issues.append(f"Réponse trop courte ({length} caractères)")
            return 0.3, issues
        
        if length > self.max_response_length:
            issues.append(f"Réponse trop longue ({length} caractères)")
            return 0.7, issues
        
        # Score basé sur la longueur idéale (entre 200 et 2000 caractères)
        if length < 200:
            score = 0.5 + (length - self.min_response_length) / (200 - self.min_response_length) * 0.3
        elif length <= 2000:
            score = 1.0
        else:
            score = 1.0 - (length - 2000) / (self.max_response_length - 2000) * 0.3
        
        return score, issues
    
    def _check_coherence(self, text: str, query_type: str) -> Tuple[float, List[str]]:
        """
        Vérifie la cohérence et la structure de la réponse.
        
        Args:
            text: Le texte à vérifier
            query_type: Le type de requête
            
        Returns:
            Score de qualité et liste des problèmes identifiés
        """
        issues = []
        
        # Vérifier la présence de paragraphes
        paragraphs = text.split("\n\n")
        if len(paragraphs) < 2 and query_type != "json" and len(text) > 200:
            issues.append("Manque de structure (pas assez de paragraphes)")
        
        # Vérifier la présence de phrases incomplètes
        sentences = re.split(r'[.!?]\s', text)
        incomplete_sentences = [s for s in sentences if len(s.strip()) > 5 and len(s.strip()) < 20]
        if len(incomplete_sentences) > len(sentences) / 3:
            issues.append("Nombreuses phrases courtes ou incomplètes")
        
        # Vérifier la répétition excessive
        words = re.findall(r'\b\w+\b', text.lower())
        word_count = {}
        for word in words:
            if len(word) > 3:  # Ignorer les mots courts
                word_count[word] = word_count.get(word, 0) + 1
        
        repetitive_words = [word for word, count in word_count.items() 
                         if count > 5 and word not in ["pour", "avec", "dans", "comme", "cette", "plus"]]
        
        if repetitive_words:
            issues.append(f"Répétition excessive des mots: {', '.join(repetitive_words[:3])}")
        
        # Calculer le score
        if issues:
            return max(0.5, 1.0 - len(issues) * 0.15), issues
        else:
            return 1.0, issues
    
    def _check_hallucinations(self, text: str) -> Tuple[float, List[str]]:
        """
        Vérifie les indicateurs potentiels d'hallucinations.
        
        Args:
            text: Le texte à vérifier
            
        Returns:
            Score de qualité et liste des problèmes identifiés
        """
        issues = []
        text_lower = text.lower()
        
        # Rechercher des indicateurs d'hallucination
        found_indicators = []
        for pattern in self.patterns["hallucination_indicators"]:
            if re.search(pattern, text_lower):
                found_indicators.append(pattern)
        
        if found_indicators:
            issues.append("Présence d'indicateurs d'incertitude ou d'hallucination")
        
        # Calculer le score
        score = 1.0 - len(found_indicators) * 0.15
        return max(0.0, score), issues
    
    def _check_relevance(self, text: str) -> Tuple[float, List[str]]:
        """
        Vérifie la présence de contenu non pertinent.
        
        Args:
            text: Le texte à vérifier
            
        Returns:
            Score de qualité et liste des problèmes identifiés
        """
        issues = []
        text_lower = text.lower()
        
        # Rechercher des indicateurs de contenu non pertinent
        found_indicators = []
        for pattern in self.patterns["irrelevant_content"]:
            if re.search(pattern, text_lower):
                found_indicators.append(pattern)
        
        if found_indicators:
            issues.append("Présence de contenu non pertinent ou de formules génériques")
        
        # Calculer le score
        score = 1.0 - len(found_indicators) * 0.2
        return max(0.0, score), issues
    
    def _check_json_format(self, response: Any) -> Tuple[float, List[str]]:
        """
        Vérifie la validité et la structure du format JSON.
        
        Args:
            response: La réponse à vérifier
            
        Returns:
            Score de qualité et liste des problèmes identifiés
        """
        issues = []
        
        # Si la réponse est déjà un dictionnaire, vérifier sa structure
        if isinstance(response, dict):
            if "cours" not in response:
                issues.append("Structure JSON incorrecte: clé 'cours' manquante")
                return 0.5, issues
            
            cours = response.get("cours", {})
            required_fields = [
                "Titre du cours", "Description du cours", "Concepts clés",
                "Définitions et Formules", "Éléments clés à retenir",
                "Exemple concret", "Bullet points avec les concepts clés",
                "Mini test de connaissance pour évaluer ses connaissances",
                "Indices pour réussir le test"
            ]
            
            missing_fields = [field for field in required_fields if field not in cours]
            if missing_fields:
                issues.append(f"Champs obligatoires manquants: {', '.join(missing_fields)}")
            
            # Vérifier que les listes sont bien des listes
            list_fields = [
                "Concepts clés", "Définitions et Formules", "Éléments clés à retenir",
                "Bullet points avec les concepts clés", 
                "Mini test de connaissance pour évaluer ses connaissances",
                "Indices pour réussir le test"
            ]
            
            invalid_lists = [field for field in list_fields 
                          if field in cours and not isinstance(cours[field], list)]
            
            if invalid_lists:
                issues.append(f"Champs qui devraient être des listes mais ne le sont pas: {', '.join(invalid_lists)}")
            
            # Calculer le score
            if issues:
                return max(0.3, 1.0 - len(issues) * 0.2), issues
            else:
                return 1.0, issues
        else:
            # Vérifier si la réponse est une chaîne contenant du JSON
            if isinstance(response, str):
                try:
                    # Essayer d'extraire et de parser le JSON
                    json_start = response.find("{")
                    json_end = response.rfind("}") + 1
                    
                    if json_start >= 0 and json_end > json_start:
                        json_str = response[json_start:json_end]
                        json_obj = json.loads(json_str)
                        
                        # Rappel récursif avec l'objet JSON parsé
                        return self._check_json_format(json_obj)
                    else:
                        issues.append("Format JSON introuvable dans la réponse")
                        return 0.0, issues
                except json.JSONDecodeError:
                    issues.append("JSON invalide")
                    return 0.0, issues
            else:
                issues.append("La réponse n'est pas au format JSON attendu")
                return 0.0, issues
    
    def _generate_suggestions(self, issues: List[str]) -> List[str]:
        """
        Génère des suggestions d'amélioration basées sur les problèmes identifiés.
        
        Args:
            issues: Liste des problèmes identifiés
            
        Returns:
            Liste de suggestions d'amélioration
        """
        suggestions = []
        
        for issue in issues:
            if "trop courte" in issue:
                suggestions.append("Développer davantage les explications et ajouter plus de détails")
            elif "trop longue" in issue:
                suggestions.append("Rendre la réponse plus concise en se concentrant sur les points essentiels")
            elif "structure" in issue:
                suggestions.append("Améliorer la structure en divisant la réponse en paragraphes logiques")
            elif "phrases courtes" in issue:
                suggestions.append("Combiner les phrases courtes et ajouter des transitions")
            elif "Répétition" in issue:
                suggestions.append("Utiliser des synonymes pour éviter les répétitions")
            elif "incertitude" in issue:
                suggestions.append("Éviter les formulations qui expriment du doute ou de l'incertitude")
            elif "contenu non pertinent" in issue:
                suggestions.append("Supprimer les mentions à 'l'assistant' ou à 'l'IA' et se concentrer sur le contenu éducatif")
            elif "JSON" in issue:
                suggestions.append("Corriger la structure JSON pour qu'elle corresponde exactement au format requis")
        
        return suggestions
    
    def _categorize_issues_and_warnings(self, results: Dict[str, Any]) -> None:
        """
        Catégorise les problèmes entre issues (critiques) et warnings (avertissements).
        
        Args:
            results: Dictionnaire des résultats à modifier in-place
        """
        warnings = []
        critical_issues = []
        
        for issue in results["issues"]:
            if ("trop longue" in issue or 
                "Répétition" in issue or 
                issue.startswith("Champs qui devraient")):
                warnings.append(issue)
            else:
                critical_issues.append(issue)
        
        results["issues"] = critical_issues
        results["warnings"] = warnings

# Fonction pour obtenir une instance du contrôleur de qualité
def get_quality_control() -> QualityControl:
    return QualityControl()