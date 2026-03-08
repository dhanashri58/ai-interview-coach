# """
# Intelligent Question Selection using Informed Search (Unit III)
# Implements Best-First Search with heuristics
# """

# import random
# from typing import List, Dict, Any, Optional
# import numpy as np
# from datetime import datetime  # <-- IMPORT MISSING! THIS WAS THE ERROR

# class QuestionSelector:
#     def __init__(self, knowledge_base):
#         self.kb = knowledge_base
#         self.question_history = []
#         self.performance_history = []
#         self.difficulty_scores = {"beginner": 1, "intermediate": 2, "advanced": 3}
        
#     def select_next_question(self, user_profile: Dict, previous_answers: List[Dict]) -> Optional[Dict]:
#         """
#         Select next question using heuristic search (Best-First Search approach)
        
#         Heuristic function h(q) = w1*relevance + w2*difficulty_match + w3*novelty + w4*weakness_focus
#         """
#         # Get all available questions
#         candidate_questions = self._get_candidate_questions(user_profile)
        
#         if not candidate_questions:
#             # If no questions found, return a default question
#             return self._get_default_question()
        
#         # Score each question using heuristic
#         scored_questions = []
#         for q in candidate_questions:
#             score = self._calculate_heuristic(q, user_profile, previous_answers)
#             scored_questions.append((score, q))
        
#         # Sort by score (highest first) and return best
#         scored_questions.sort(key=lambda x: x[0], reverse=True)
        
#         if scored_questions:
#             selected = scored_questions[0][1]
#             # Add to history
#             if selected.get('id'):
#                 self.question_history.append(selected['id'])
#             return selected
        
#         return self._get_default_question()
    
#     def _get_default_question(self) -> Dict:
#         """Return a default question if no questions found"""
#         return {
#             "id": 1,
#             "question": "What is a list in Python? Explain with example.",
#             "topic": "python",
#             "difficulty_level": "beginner",
#             "difficulty": "beginner",
#             "keywords": ["mutable", "ordered", "sequence", "collection", "[]"],
#             "concepts": ["mutable", "indexing", "slicing"]
#         }
    
#     def _calculate_heuristic(self, question: Dict, profile: Dict, previous_answers: List[Dict]) -> float:
#         """
#         Heuristic function h(q) = w1*relevance + w2*difficulty_match + w3*novelty + w4*weakness_focus
#         """
#         # Weights for different factors
#         w1, w2, w3, w4 = 0.3, 0.3, 0.2, 0.2
        
#         relevance = self._calculate_relevance(question, profile)
#         difficulty_match = self._calculate_difficulty_match(question, profile)
#         novelty = self._calculate_novelty(question)
#         weakness_focus = self._calculate_weakness_focus(question, previous_answers)
        
#         score = (w1 * relevance + w2 * difficulty_match + 
#                 w3 * novelty + w4 * weakness_focus)
        
#         return score
    
#     def _calculate_relevance(self, question: Dict, profile: Dict) -> float:
#         """Calculate how relevant question is to user's target role"""
#         target_role = profile.get("target_role", "").lower() if profile else ""
        
#         # Map roles to topics
#         role_topics = {
#             "software engineer": ["python", "dsa", "algorithms"],
#             "data scientist": ["python", "sql", "machine learning"],
#             "backend developer": ["python", "sql", "java"],
#             "frontend developer": ["javascript", "react", "html"],
#             "devops engineer": ["python", "linux", "aws"],
#             "data analyst": ["sql", "python", "excel"],
#             "machine learning engineer": ["python", "machine learning", "algorithms"],
#             "full stack developer": ["python", "javascript", "sql", "react"],
#             "cloud architect": ["aws", "python", "linux"],
#             "product manager": ["general", "business", "analytics"]
#         }
        
#         # Get question topic
#         question_topic = question.get("topic", "").lower()
        
#         # Check if question's topic is relevant to target role
#         for role, topics in role_topics.items():
#             if role in target_role:
#                 if question_topic in topics:
#                     return 1.0
#                 elif any(topic in question_topic for topic in topics):
#                     return 0.7
        
#         return 0.5
    
#     def _calculate_difficulty_match(self, question: Dict, profile: Dict) -> float:
#         """Calculate how well question difficulty matches user's level"""
#         user_level = profile.get("experience_level", "entry") if profile else "entry"
        
#         # Normalize user level
#         if "entry" in user_level.lower() or "0-2" in user_level.lower():
#             user_level = "beginner"
#         elif "mid" in user_level.lower() or "3-5" in user_level.lower():
#             user_level = "intermediate"
#         elif "senior" in user_level.lower() or "5+" in user_level.lower():
#             user_level = "advanced"
#         else:
#             user_level = "beginner"
        
#         # Get question difficulty - check multiple possible keys
#         q_difficulty = question.get("difficulty_level") or question.get("difficulty") or "beginner"
        
#         # Score based on difficulty match
#         difficulty_scores = {"beginner": 1, "intermediate": 2, "advanced": 3}
#         user_score = difficulty_scores.get(user_level, 1)
#         q_score = difficulty_scores.get(q_difficulty, 1)
        
#         # Perfect match gives 1.0, one level difference gives 0.7, two levels gives 0.3
#         diff = abs(user_score - q_score)
#         if diff == 0:
#             return 1.0
#         elif diff == 1:
#             return 0.7
#         else:
#             return 0.3
    
#     def _calculate_novelty(self, question: Dict) -> float:
#         """Calculate novelty (has this question been asked recently?)"""
#         q_id = question.get("id")
        
#         if q_id in self.question_history[-3:]:  # Last 3 questions
#             return 0.2
#         elif q_id in self.question_history[-5:]:  # Last 5 questions
#             return 0.5
#         else:
#             return 1.0
    
#     def _calculate_weakness_focus(self, question: Dict, previous_answers: List[Dict]) -> float:
#         """Focus on topics where user performed poorly"""
#         if not previous_answers:
#             return 0.5
        
#         # Identify weak topics
#         weak_topics = self._identify_weak_topics(previous_answers)
        
#         # Check if question targets weak topics
#         q_topic = question.get("topic", "").lower()
        
#         if q_topic in weak_topics:
#             return 1.0
#         elif any(weak_topic in q_topic for weak_topic in weak_topics):
#             return 0.7
#         else:
#             return 0.3
    
#     def _identify_weak_topics(self, previous_answers: List[Dict]) -> List[str]:
#         """Identify topics where user scored low"""
#         weak_topics = []
        
#         for answer in previous_answers:
#             if answer.get("score", 5) < 6:  # Score below 6/10
#                 topic = answer.get("topic", "")
#                 if topic:
#                     weak_topics.append(topic.lower())
        
#         return list(set(weak_topics))  # Remove duplicates
    
#     def _get_initial_question(self, profile: Dict) -> Optional[Dict]:
#         """Get first question based on user profile"""
#         if not profile:
#             return self._get_default_question()
        
#         target_role = profile.get("target_role", "").lower()
        
#         # Determine topic based on role
#         if "data" in target_role:
#             topic = "sql"
#         elif "frontend" in target_role:
#             topic = "javascript"
#         else:
#             topic = "python"  # Default
        
#         level = profile.get("experience_level", "entry")
#         if "entry" in level.lower() or "0-2" in level.lower():
#             difficulty = "beginner"
#         elif "mid" in level.lower() or "3-5" in level.lower():
#             difficulty = "intermediate"
#         else:
#             difficulty = "advanced"
        
#         # Try to get questions from knowledge base
#         questions = self.kb.get_questions_by_topic(topic, difficulty)
        
#         if questions and len(questions) > 0:
#             selected = random.choice(questions)
#             return selected
        
#         # Try with different difficulty if no questions found
#         difficulties = ["beginner", "intermediate", "advanced"]
#         for diff in difficulties:
#             if diff != difficulty:
#                 questions = self.kb.get_questions_by_topic(topic, diff)
#                 if questions and len(questions) > 0:
#                     return random.choice(questions)
        
#         return self._get_default_question()
    
#     def _get_candidate_questions(self, profile: Dict) -> List[Dict]:
#         """Get all possible questions based on profile"""
#         candidates = []
        
#         if not profile:
#             # Return default questions
#             return [self._get_default_question()]
        
#         target_role = profile.get("target_role", "").lower()
        
#         # Determine topics to consider based on role
#         if "data" in target_role:
#             topics = ["sql", "python"]
#         elif "frontend" in target_role:
#             topics = ["javascript", "react"]
#         elif "devops" in target_role:
#             topics = ["python", "linux"]
#         elif "full stack" in target_role:
#             topics = ["python", "javascript", "sql"]
#         else:
#             topics = ["python", "dsa", "sql"]  # Default topics
        
#         # Get user level
#         level = profile.get("experience_level", "entry")
#         if "entry" in level.lower() or "0-2" in level.lower():
#             user_level = "beginner"
#             levels_to_try = ["beginner", "intermediate"]
#         elif "mid" in level.lower() or "3-5" in level.lower():
#             user_level = "intermediate"
#             levels_to_try = ["intermediate", "beginner", "advanced"]
#         else:
#             user_level = "advanced"
#             levels_to_try = ["advanced", "intermediate"]
        
#         # Collect questions from knowledge base
#         for topic in topics:
#             for level in levels_to_try:
#                 try:
#                     questions = self.kb.get_questions_by_topic(topic, level)
#                     if questions and isinstance(questions, list):
#                         for q in questions:
#                             # Ensure each question has required fields
#                             if isinstance(q, dict):
#                                 if 'id' not in q:
#                                     q['id'] = hash(q.get('question', '')) % 10000
#                                 if 'difficulty' not in q:
#                                     q['difficulty'] = level
#                                 if 'difficulty_level' not in q:
#                                     q['difficulty_level'] = level
#                                 candidates.append(q)
#                 except Exception as e:
#                     print(f"Error getting questions for {topic}/{level}: {e}")
#                     continue
        
#         # Remove duplicates based on question id
#         unique_candidates = []
#         seen_ids = set()
#         for q in candidates:
#             q_id = q.get('id')
#             if q_id and q_id not in seen_ids:
#                 seen_ids.add(q_id)
#                 unique_candidates.append(q)
        
#         return unique_candidates if unique_candidates else [self._get_default_question()]
    
#     def update_performance(self, question_id: int, score: float, topic: str):
#         """Update performance history for adaptive learning"""
#         self.performance_history.append({
#             "q_id": question_id,
#             "score": score,
#             "topic": topic,
#             "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Now works because datetime is imported
#         })
"""
Intelligent Question Selection using Informed Search (Unit III)
Implements Best-First Search with heuristics
"""

import random
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
from datetime import datetime

class QuestionSelector:
    def __init__(self, knowledge_base):
        self.kb = knowledge_base
        self.question_history = []  # Stores IDs of questions already asked
        self.performance_history = []
        self.difficulty_scores = {"beginner": 1, "intermediate": 2, "advanced": 3}
        
    def select_next_question(self, user_profile: Dict, previous_answers: List[Dict]) -> Optional[Dict]:
        """
        Select next question using heuristic search (Best-First Search approach)
        NEVER repeats a question that has been asked before
        """
        # Get all available questions
        candidate_questions = self._get_candidate_questions(user_profile)
        
        # FILTER OUT QUESTIONS THAT HAVE BEEN ASKED BEFORE
        available_questions = []
        for q in candidate_questions:
            q_id = q.get('id')
            if q_id and q_id not in self.question_history:
                available_questions.append(q)
        
        # If no available questions, return None (interview complete)
        if not available_questions:
            return None
        
        # Score each available question using heuristic
        scored_questions = []
        for q in available_questions:
            score = self._calculate_heuristic(q, user_profile, previous_answers)
            scored_questions.append((score, q))
        
        # Sort by score (highest first) and return best
        scored_questions.sort(key=lambda x: x[0], reverse=True)
        
        if scored_questions:
            selected = scored_questions[0][1]
            # Add to history so it won't be asked again
            if selected.get('id'):
                self.question_history.append(selected['id'])
            return selected
        
        return None  # No questions available
    
    def _get_default_question(self) -> Dict:
        """Return a default question if no questions found"""
        # Check if default question was already asked
        if 1 in self.question_history:
            # Find another default question
            for q_id in [2, 3, 4, 5]:
                if q_id not in self.question_history:
                    return {
                        "id": q_id,
                        "question": f"What is variable in Python? Explain with example {q_id}.",
                        "topic": "python",
                        "difficulty_level": "beginner",
                        "difficulty": "beginner",
                        "keywords": ["variable", "assignment", "data", "type", "value"],
                        "concepts": ["variables", "data types", "assignment"]
                    }
        
        return {
            "id": 1,
            "question": "What is a list in Python? Explain with example.",
            "topic": "python",
            "difficulty_level": "beginner",
            "difficulty": "beginner",
            "keywords": ["mutable", "ordered", "sequence", "collection", "[]"],
            "concepts": ["mutable", "indexing", "slicing"]
        }
    
    def _calculate_heuristic(self, question: Dict, profile: Dict, previous_answers: List[Dict]) -> float:
        """
        Heuristic function h(q) = w1*relevance + w2*difficulty_match + w3*novelty + w4*weakness_focus
        """
        # Weights for different factors
        w1, w2, w3, w4 = 0.3, 0.3, 0.2, 0.2
        
        relevance = self._calculate_relevance(question, profile)
        difficulty_match = self._calculate_difficulty_match(question, profile)
        novelty = self._calculate_novelty(question)
        weakness_focus = self._calculate_weakness_focus(question, previous_answers)
        
        score = (w1 * relevance + w2 * difficulty_match + 
                w3 * novelty + w4 * weakness_focus)
        
        return score
    
    def _calculate_relevance(self, question: Dict, profile: Dict) -> float:
        """Calculate how relevant question is to user's target role"""
        target_role = profile.get("target_role", "").lower() if profile else ""
        
        # Map roles to topics
        role_topics = {
            "software engineer": ["python", "dsa", "algorithms"],
            "data scientist": ["python", "sql", "machine learning"],
            "backend developer": ["python", "sql", "java"],
            "frontend developer": ["javascript", "react", "html"],
            "devops engineer": ["python", "linux", "aws"],
            "data analyst": ["sql", "python", "excel"],
            "machine learning engineer": ["python", "machine learning", "algorithms"],
            "full stack developer": ["python", "javascript", "sql", "react"],
            "cloud architect": ["aws", "python", "linux"],
            "product manager": ["general", "business", "analytics"]
        }
        
        # Get question topic
        question_topic = question.get("topic", "").lower()
        
        # Check if question's topic is relevant to target role
        for role, topics in role_topics.items():
            if role in target_role:
                if question_topic in topics:
                    return 1.0
                elif any(topic in question_topic for topic in topics):
                    return 0.7
        
        return 0.5
    
    def _calculate_difficulty_match(self, question: Dict, profile: Dict) -> float:
        """Calculate how well question difficulty matches user's level"""
        user_level = profile.get("experience_level", "entry") if profile else "entry"
        
        # Normalize user level
        if "entry" in user_level.lower() or "0-2" in user_level.lower():
            user_level = "beginner"
        elif "mid" in user_level.lower() or "3-5" in user_level.lower():
            user_level = "intermediate"
        elif "senior" in user_level.lower() or "5+" in user_level.lower():
            user_level = "advanced"
        else:
            user_level = "beginner"
        
        # Get question difficulty - check multiple possible keys
        q_difficulty = question.get("difficulty_level") or question.get("difficulty") or "beginner"
        
        # Score based on difficulty match
        difficulty_scores = {"beginner": 1, "intermediate": 2, "advanced": 3}
        user_score = difficulty_scores.get(user_level, 1)
        q_score = difficulty_scores.get(q_difficulty, 1)
        
        # Perfect match gives 1.0, one level difference gives 0.7, two levels gives 0.3
        diff = abs(user_score - q_score)
        if diff == 0:
            return 1.0
        elif diff == 1:
            return 0.7
        else:
            return 0.3
    
    def _calculate_novelty(self, question: Dict) -> float:
        """Calculate novelty - prefer questions not asked recently"""
        q_id = question.get("id")
        
        if q_id in self.question_history:
            return 0.0  # Never select already asked questions
        elif q_id in self.question_history[-3:]:  # Last 3 questions
            return 0.2
        elif q_id in self.question_history[-5:]:  # Last 5 questions
            return 0.5
        else:
            return 1.0
    
    def _calculate_weakness_focus(self, question: Dict, previous_answers: List[Dict]) -> float:
        """Focus on topics where user performed poorly recently, and move away from topics where user performed well"""
        if not previous_answers:
            return 0.5
            
        q_topic = question.get("topic", "").lower()
        
        # Find the most recent score for this question's topic
        latest_score = None
        for answer in reversed(previous_answers):
            topic = answer.get("topic", "").lower()
            if topic == q_topic or topic in q_topic or q_topic in topic:
                latest_score = answer.get("score", 5)
                break
                
        if latest_score is None:
            # Topic hasn't been tested yet
            return 0.5
            
        # Score goes UP (higher priority) if latest score was bad (< 6)
        # Score goes DOWN (lower priority) if latest score was good (>= 6)
        # Latest_score is between 0 and 10.
        # weakness_focus ranges from 1.0 (for score 0) to 0.0 (for score 10)
        focus = 1.0 - (latest_score / 10.0)
        
        # Bound it just in case
        return max(0.0, min(1.0, focus))
        
    def get_predicted_questions(self, user_profile: Dict, previous_answers: List[Dict], n: int = 3) -> List[Tuple[float, Dict]]:
        """
        Returns the top N candidate questions with their heuristic scores.
        Used for the UI Question Path panel to show the AI's internal decision process.
        """
        # Get all candidate questions
        candidate_questions = self._get_candidate_questions(user_profile)
        
        # Filter out already asked questions
        available_questions = []
        for q in candidate_questions:
            q_id = q.get('id')
            if q_id and q_id not in self.question_history:
                available_questions.append(q)
                
        if not available_questions:
            return []
            
        # Score each available question using heuristic
        scored_questions = []
        for q in available_questions:
            score = self._calculate_heuristic(q, user_profile, previous_answers)
            scored_questions.append((score, q))
            
        # Sort by score (highest first)
        scored_questions.sort(key=lambda x: x[0], reverse=True)
        
        return scored_questions[:n]
    
    def _get_initial_question(self, profile: Dict) -> Optional[Dict]:
        """Get first question based on user profile"""
        if not profile:
            return self._get_default_question()
        
        target_role = profile.get("target_role", "").lower()
        
        # Determine topic based on role
        if "data" in target_role:
            topic = "sql"
        elif "frontend" in target_role:
            topic = "javascript"
        else:
            topic = "python"  # Default
        
        level = profile.get("experience_level", "entry")
        if "entry" in level.lower() or "0-2" in level.lower():
            difficulty = "beginner"
        elif "mid" in level.lower() or "3-5" in level.lower():
            difficulty = "intermediate"
        else:
            difficulty = "advanced"
        
        # Try to get questions from knowledge base
        questions = self.kb.get_questions_by_topic(topic, difficulty)
        
        # Filter out already asked questions
        available_questions = []
        if questions:
            for q in questions:
                if q.get('id') not in self.question_history:
                    available_questions.append(q)
        
        if available_questions:
            selected = random.choice(available_questions)
            self.question_history.append(selected.get('id'))
            return selected
        
        # Try with different difficulty if no questions found
        difficulties = ["beginner", "intermediate", "advanced"]
        for diff in difficulties:
            if diff != difficulty:
                questions = self.kb.get_questions_by_topic(topic, diff)
                available_questions = []
                if questions:
                    for q in questions:
                        if q.get('id') not in self.question_history:
                            available_questions.append(q)
                if available_questions:
                    selected = random.choice(available_questions)
                    self.question_history.append(selected.get('id'))
                    return selected
        
        return self._get_default_question()
    
    def _get_candidate_questions(self, profile: Dict) -> List[Dict]:
        """Get all possible questions based on profile"""
        candidates = []
        
        if not profile:
            # Return default questions
            return [self._get_default_question()]
        
        target_role = profile.get("target_role", "").lower()
        
        # Determine topics to consider based on role
        if "data" in target_role:
            topics = ["sql", "python"]
        elif "frontend" in target_role:
            topics = ["javascript", "react"]
        elif "devops" in target_role:
            topics = ["python", "linux"]
        elif "full stack" in target_role:
            topics = ["python", "javascript", "sql"]
        else:
            topics = ["python", "dsa", "sql"]  # Default topics
        
        # Get user level
        level = profile.get("experience_level", "entry")
        if "entry" in level.lower() or "0-2" in level.lower():
            user_level = "beginner"
            levels_to_try = ["beginner", "intermediate"]
        elif "mid" in level.lower() or "3-5" in level.lower():
            user_level = "intermediate"
            levels_to_try = ["intermediate", "beginner", "advanced"]
        else:
            user_level = "advanced"
            levels_to_try = ["advanced", "intermediate"]
        
        # Collect questions from knowledge base
        for topic in topics:
            for level in levels_to_try:
                try:
                    questions = self.kb.get_questions_by_topic(topic, level)
                    if questions and isinstance(questions, list):
                        for q in questions:
                            # Ensure each question has required fields
                            if isinstance(q, dict):
                                if 'id' not in q:
                                    q['id'] = hash(q.get('question', '')) % 10000
                                if 'difficulty' not in q:
                                    q['difficulty'] = level
                                if 'difficulty_level' not in q:
                                    q['difficulty_level'] = level
                                
                                # Only add if not already in history
                                if q.get('id') not in self.question_history:
                                    candidates.append(q)
                except Exception as e:
                    print(f"Error getting questions for {topic}/{level}: {e}")
                    continue
        
        # Remove duplicates based on question id
        unique_candidates = []
        seen_ids = set()
        for q in candidates:
            q_id = q.get('id')
            if q_id and q_id not in seen_ids:
                seen_ids.add(q_id)
                unique_candidates.append(q)
        
        return unique_candidates
    
    def update_performance(self, question_id: int, score: float, topic: str):
        """Update performance history for adaptive learning"""
        self.performance_history.append({
            "q_id": question_id,
            "score": score,
            "topic": topic,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
    
    def reset_history(self):
        """Reset question history for a new interview session"""
        self.question_history = []
        self.performance_history = []