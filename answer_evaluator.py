"""
Answer Evaluation using Logical Agents (Unit IV)
Implements Forward Chaining for inference
"""

import re
from typing import Dict, List, Any
import difflib

class AnswerEvaluator:
    def __init__(self, knowledge_base):
        self.kb = knowledge_base
        self.keyword_weights = {
            "exact_match": 1.0,
            "partial_match": 0.5,
            "concept_match": 0.7,
            "example_provided": 0.3
        }
    
    def evaluate_answer(self, question_id: int, user_answer: str) -> Dict:
        """
        Evaluate answer using logical inference (Forward Chaining)
        Returns: feedback dictionary with score and improvement suggestions
        """
        # Get ideal answer structure
        ideal = self.kb.get_ideal_answer(question_id)
        question = self.kb.get_question_by_id(question_id)
        
        if not question:
            return self._generate_fallback_feedback()
        
        # Forward chaining inference process
        facts = self._extract_facts(user_answer)
        ideal_facts = self._extract_ideal_facts(ideal)
        
        # Apply inference rules
        matched_facts = self._apply_forward_chaining(facts, ideal_facts)
        
        # Calculate scores
        keyword_score = self._evaluate_keywords(user_answer, question.get("keywords", []))
        concept_score = self._evaluate_concepts(user_answer, question.get("concepts", []))
        example_score = self._evaluate_example(user_answer, ideal.get("example", ""))
        
        # Check for common mistakes
        mistakes_found = self._check_common_mistakes(user_answer, ideal.get("common_mistakes", []))
        
        # Calculate total score (weighted average)
        total_score = (
            keyword_score * 0.4 +
            concept_score * 0.4 +
            example_score * 0.2
        ) * 10  # Convert to 10-point scale
        
        # Generate feedback
        feedback = self._generate_feedback(
            question_id=question_id,
            user_answer=user_answer,
            keyword_score=keyword_score,
            concept_score=concept_score,
            example_score=example_score,
            total_score=total_score,
            matched_facts=matched_facts,
            missing_concepts=self._find_missing_concepts(user_answer, question.get("concepts", [])),
            mistakes_found=mistakes_found,
            ideal=ideal
        )
        
        # Feature 2: Human Feedback on Answers
        try:
            import streamlit as st
            if st.session_state.get('ai_enhanced_mode', False):
                from utils import call_gemini
                
                kw = question.get("keywords", [])
                matched_kw = [k for k in kw if k.lower() in user_answer.lower()]
                missing = self._find_missing_concepts(user_answer, question.get("concepts", []))
                
                prompt = (
                    f"You are a technical interview coach. The candidate was asked: '{question.get('question', '')}'.\n"
                    f"They answered: '{user_answer}'.\n"
                    f"The evaluation system detected they scored {round(total_score, 1)}/10.\n"
                    f"They mentioned these correct keywords: {', '.join(matched_kw) if matched_kw else 'None'}.\n"
                    f"They missed these important concepts: {', '.join(missing) if missing else 'None'}.\n"
                    f"Write 2-3 sentences of constructive coaching feedback. Be specific, "
                    f"encouraging, and tell them exactly what to add next time. No bullet points."
                )
                
                llm_feedback = call_gemini(prompt, feature_name="Feature 2: Coach Feedback")
                if llm_feedback:
                    feedback["llm_feedback"] = llm_feedback
                else:
                    feedback["llm_feedback"] = " ".join(feedback["suggestions"])
            else:
                feedback["llm_feedback"] = " ".join(feedback["suggestions"])
        except Exception:
            feedback["llm_feedback"] = " ".join(feedback["suggestions"])
        
        return feedback
    
    def _extract_facts(self, text: str) -> List[str]:
        """Extract factual statements from answer"""
        # Simple fact extraction based on sentences
        sentences = re.split(r'[.!?]+', text)
        facts = [s.strip() for s in sentences if len(s.strip()) > 10]
        return facts
    
    def _extract_ideal_facts(self, ideal: Dict) -> List[str]:
        """Extract facts from ideal answer"""
        return ideal.get("key_points", [])
    
    def _apply_forward_chaining(self, user_facts: List[str], ideal_facts: List[str]) -> List[str]:
        """
        Forward chaining: Match user facts against ideal facts
        Returns list of matched ideal facts
        """
        matched = []
        
        for ideal in ideal_facts:
            # Check if any user fact is similar to this ideal fact
            for user_fact in user_facts:
                similarity = difflib.SequenceMatcher(None, 
                                                     ideal.lower(), 
                                                     user_fact.lower()).ratio()
                if similarity > 0.6:  # Threshold for matching
                    matched.append(ideal)
                    break
        
        return matched
    
    def _evaluate_keywords(self, answer: str, keywords: List[str]) -> float:
        """Check presence of keywords in answer"""
        if not keywords:
            return 1.0
        
        answer_lower = answer.lower()
        found = [kw for kw in keywords if kw.lower() in answer_lower]
        
        return len(found) / len(keywords)
    
    def _evaluate_concepts(self, answer: str, concepts: List[str]) -> float:
        """Check understanding of concepts"""
        if not concepts:
            return 1.0
        
        # Concepts require more than just keyword matching
        # Look for explanation of each concept
        answer_lower = answer.lower()
        understood = 0
        
        for concept in concepts:
            # Check if concept is mentioned with some context
            if concept.lower() in answer_lower:
                # Look for explanatory words near the concept
                words = answer_lower.split()
                if concept in answer_lower and len(answer_lower.split()) > 20:
                    understood += 1
        
        return understood / len(concepts) if concepts else 1.0
    
    def _evaluate_example(self, answer: str, ideal_example: str) -> float:
        """Check if user provided relevant example"""
        if not ideal_example:
            return 1.0
        
        # Look for code-like patterns or examples
        has_code = bool(re.search(r'[a-zA-Z0-9_]+\([^\)]*\)|\=\s*[\'"].+[\'"]', answer))
        has_numbers = bool(re.search(r'\d+', answer))
        has_operators = bool(re.search(r'[+\-*/=<>]', answer))
        
        # Check for example structure using the helper function
        if has_code and has_numbers and has_operators:
            return 1.0
        elif has_code or self._has_example_structure(answer):
            return 0.7
        else:
            return 0.3
    
    # ============= FIX: ADD THIS MISSING FUNCTION =============
    def _has_example_structure(self, text: str) -> bool:
        """Check if text contains example-like structure"""
        example_indicators = [
            r'for example',
            r'e\.g\.',
            r'like',
            r'such as',
            r'instance',
            r'example:',
            r'example -',
            r'for instance',
            r'consider',
            r'suppose',
            r'let\'s say'
        ]
        
        # Check for example indicators
        for indicator in example_indicators:
            if re.search(indicator, text.lower()):
                return True
            return False
        
        # Check for code-like patterns
        code_patterns = [
            r'=\s*[\'"].+[\'"]',  # assignments with quotes
            r'def\s+\w+\s*\(',    # function definitions
            r'class\s+\w+',        # class definitions
            r'if\s+.+:',           # if statements
            r'for\s+.+:',          # for loops
            r'while\s+.+:',        # while loops
            r'print\s*\(',         # print statements
            r'return\s+'           # return statements
        ]
        
        for pattern in code_patterns:
            if re.search(pattern, text):
                return True
        
        return False
    # ===========================================================
    
    def _check_common_mistakes(self, answer: str, common_mistakes: List[str]) -> List[str]:
        """Check for common mistakes"""
        found = []
        for mistake in common_mistakes:
            # Simple check - can be improved with more sophisticated NLP
            if mistake.lower() in answer.lower():
                found.append(mistake)
        return found
    
    def _find_missing_concepts(self, answer: str, concepts: List[str]) -> List[str]:
        """Identify which concepts are missing from answer"""
        missing = []
        answer_lower = answer.lower()
        
        for concept in concepts:
            if concept.lower() not in answer_lower:
                missing.append(concept)
        
        return missing
    
    def _generate_feedback(self, **kwargs) -> Dict:
        """Generate comprehensive feedback"""
        return {
            "score": round(kwargs["total_score"], 1),
            "strengths": self._identify_strengths(kwargs),
            "weaknesses": self._identify_weaknesses(kwargs),
            "missing_concepts": kwargs.get("missing_concepts", []),
            "mistakes": kwargs.get("mistakes_found", []),
            "suggestions": self._generate_suggestions(kwargs),
            "ideal_answer": {
                "key_points": kwargs["ideal"].get("key_points", []),
                "example": kwargs["ideal"].get("example", "")
            }
        }
    
    def _identify_strengths(self, kwargs: Dict) -> List[str]:
        """Identify what user did well"""
        strengths = []
        
        if kwargs["keyword_score"] > 0.7:
            strengths.append("Good use of technical terminology")
        if kwargs["concept_score"] > 0.7:
            strengths.append("Clear understanding of core concepts")
        if kwargs["example_score"] > 0.7:
            strengths.append("Provided relevant examples")
        if len(kwargs.get("matched_facts", [])) > 2:
            strengths.append("Covered multiple important points")
        
        return strengths if strengths else ["Basic understanding shown"]
    
    def _identify_weaknesses(self, kwargs: Dict) -> List[str]:
        """Identify areas for improvement"""
        weaknesses = []
        
        if kwargs["keyword_score"] < 0.4:
            weaknesses.append("Missing key technical terms")
        if kwargs["concept_score"] < 0.4:
            weaknesses.append("Concepts need clearer explanation")
        if kwargs["example_score"] < 0.4:
            weaknesses.append("Could provide more relevant examples")
        if kwargs.get("missing_concepts"):
            weaknesses.append(f"Missed concepts: {', '.join(kwargs['missing_concepts'][:3])}")
        
        return weaknesses
    
    def _generate_suggestions(self, kwargs: Dict) -> List[str]:
        """Generate improvement suggestions"""
        suggestions = []
        
        if kwargs.get("missing_concepts"):
            for concept in kwargs["missing_concepts"][:2]:
                suggestions.append(f"Explain '{concept}' in more detail")
        
        if kwargs.get("mistakes"):
            for mistake in kwargs["mistakes"][:2]:
                suggestions.append(f"Avoid: {mistake}")
        
        if kwargs["example_score"] < 0.5:
            suggestions.append("Add a concrete code example")
        
        if kwargs["keyword_score"] < 0.6:
            suggestions.append("Use more specific technical terminology")
        
        if not suggestions:
            suggestions.append("Great answer! Consider adding more real-world applications")
        
        return suggestions
    
    def _generate_fallback_feedback(self) -> Dict:
        """Generate feedback when question not found"""
        return {
            "score": 5.0,
            "strengths": ["Answer provided"],
            "weaknesses": ["Could not evaluate against ideal answer"],
            "missing_concepts": [],
            "mistakes": [],
            "suggestions": ["Structure your answer with key points first, then explain"],
            "ideal_answer": {
                "key_points": ["Point 1", "Point 2", "Point 3"],
                "example": "Example here"
            }
        }

