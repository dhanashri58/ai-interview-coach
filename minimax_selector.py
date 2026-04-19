import math
from typing import List, Dict, Optional

class MinimaxQuestionSelector:
    def __init__(self, knowledge_base, depth=3):
        self.kb = knowledge_base
        self.depth = depth
        self.nodes_explored = 0
        self.pruned_branches = 0

    def select_next_question(self, profile: dict, answered: List[Dict]) -> Optional[Dict]:
        all_q = self.kb.get_all_questions()
        answered_ids = {a.get('question_id') for a in answered}
        
        # User's selected skills and target role
        chosen_skills = [s.lower() for s in profile.get("skills", [])]
        target_role = str(profile.get("target_role", "")).lower()
        
        # STRICT FILTER: Question must match at least one chosen skill
        remaining = [
            q for q in all_q 
            if q.get('id') not in answered_ids and 
            (q.get('topic', '').lower() in chosen_skills or any(s in q.get('question', '').lower() for s in chosen_skills))
        ]
        
        if not remaining:
            # Fallback to all if strict filter returns nothing (unlikely with KB)
            remaining = [q for q in all_q if q.get('id') not in answered_ids]
            
        if not remaining:
            return None
        
        # Max limit to keep search efficient - avoid slice syntax to satisfy some linters
        search_pool = []
        for i in range(min(len(remaining), 8)):
            search_pool.append(remaining[i])
            
        best_score = 999.0 # AI is MIN player
        best_q = search_pool[0]
        
        self.nodes_explored = 0
        self.pruned_branches = 0
        
        for q in search_pool:
            score = self.minimax(q, self.depth - 1, -999.0, 999.0, True)
            if score < best_score:
                best_score = score
                best_q = q
        
        return best_q

    def minimax(self, question, depth, alpha, beta, is_max_player):
        self.nodes_explored += 1
        
        if depth == 0:
            return float(self.evaluate_difficulty(question))
        
        if is_max_player:
            # Candidate wants to MAXIMISE score
            max_eval = -999.0
            eval_val = float(self.evaluate_difficulty(question))
            max_eval = max(max_eval, eval_val)
            alpha = max(alpha, eval_val)
            if beta <= alpha:
                self.pruned_branches += 1
            return max_eval
        else:
            # AI wants to MINIMISE candidate's score (pick hardest)
            min_eval = 999.0
            eval_val = float(self.evaluate_difficulty(question))
            min_eval = min(min_eval, eval_val)
            beta = min(beta, eval_val)
            if beta <= alpha:
                self.pruned_branches += 1
            return min_eval

    def evaluate_difficulty(self, question):
        diff = str(question.get('difficulty', 'beginner')).lower()
        mapping = {"beginner": 8, "intermediate": 5, "advanced": 2}
        return mapping.get(diff, 5)
