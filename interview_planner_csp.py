"""
Unit III: Constraint Satisfaction Problem (CSP)
Unit V: Backtracking Algorithm

Demonstrates modeling an interview syllabus as a Constraint Satisfaction Problem
and resolving it using the Backtracking search strategy to ensure exact difficulty
counts, topic diversity, and no duplicated questions.
"""

from typing import List, Dict
import random

class ConstraintSatisfactionPlanner:
    def __init__(self, knowledge_base):
        self.kb = knowledge_base
        
    def generate_interview_plan(self) -> List[Dict]:
        """
        Generate a 10-question plan using Backtracking search.
        Constraints:
          - Exactly 4 Beginner, 4 Intermediate, 2 Advanced
          - >= 3 Distinct Topics
          - No repeated questions
        """
        # Pre-fetch the domain (all questions)
        domain = []
        for topic, diff_dict in self.kb.questions.items():
            for diff, q_list in diff_dict.items():
                for q in q_list:
                    # Enrich question dict with topic/diff if missing
                    q_copy = dict(q)
                    q_copy['topic'] = topic
                    q_copy['difficulty_level'] = diff
                    domain.append(q_copy)
                
        # Shuffle domain to ensure variety across runs (random heuristic)
        random.shuffle(domain)
        
        assignment = []
        constraints = {
            "beginner_target": 4,
            "intermediate_target": 4,
            "advanced_target": 2,
            "min_topics": 3,
            "total_questions": 10
        }
        
        feasible, msg = self._is_feasible(domain, constraints)
        if not feasible:
            print(f"CSP Error: {msg}")
            return []
        
        success = self._backtrack(assignment, domain, constraints)
        if success:
            return assignment
        return []

    def _is_feasible(self, domain, constraints):
        counts = {"beginner": 0, "intermediate": 0, "advanced": 0}
        for q in domain:
            counts[q.get("difficulty_level", "beginner")] += 1
            
        if counts["beginner"] < constraints["beginner_target"]:
            return False, f"Not enough beginner questions: need {constraints['beginner_target']}, have {counts['beginner']}"
        if counts["intermediate"] < constraints["intermediate_target"]:
            return False, f"Not enough intermediate questions: need {constraints['intermediate_target']}, have {counts['intermediate']}"
        if counts["advanced"] < constraints["advanced_target"]:
            return False, f"Not enough advanced questions: need {constraints['advanced_target']}, have {counts['advanced']}"
            
        return True, "OK"

    def _backtrack(self, assignment: List[Dict], domain: List[Dict], constraints: Dict) -> bool:
        # Check if assignment is complete
        if len(assignment) == constraints["total_questions"]:
            # Final constraint: must span at least 3 distinct topics
            topics = set(q.get("topic") for q in assignment)
            if len(topics) >= constraints["min_topics"]:
                return True
            return False
            
        # Count current state
        counts = {"beginner": 0, "intermediate": 0, "advanced": 0}
        assigned_ids = set()
        for q in assignment:
            diff = q.get("difficulty_level", "beginner")
            counts[diff] += 1
            assigned_ids.add(q["id"])
            
        # Iterate over unused values in domain
        for q in domain:
            if q["id"] in assigned_ids:
                continue # Uniqueness constraint
                
            diff = q.get("difficulty_level", "beginner")
            
            # Bound rules (Forward Checking equivalent)
            if diff == "beginner" and counts["beginner"] >= constraints["beginner_target"]:
                continue
            if diff == "intermediate" and counts["intermediate"] >= constraints["intermediate_target"]:
                continue
            if diff == "advanced" and counts["advanced"] >= constraints["advanced_target"]:
                continue
                
            # Assign
            assignment.append(q)
            
            # Recursive call
            if self._backtrack(assignment, domain, constraints):
                return True
                
            # Backtrack
            assignment.pop()
            
        return False
