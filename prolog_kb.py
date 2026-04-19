try:
    from pyswip import Prolog
except ImportError:
    Prolog = None

from typing import List, Dict, Optional

class PrologKnowledgeBase:
    """
    Wraps the PROLOG knowledge base, providing query methods
    that mirror the Python KnowledgeBase API.
    """
    
    def __init__(self, pl_file: str = "knowledge.pl"):
        self._query_log = []
        if Prolog is None:
            self.available = False
            self.error_msg = "pyswip not installed"
            return
            
        self.prolog = Prolog()
        try:
            # Absolute path might be needed for some systems
            self.prolog.consult(pl_file)
            self.available = True
            self._log_query(f"consult('{pl_file}')")
        except Exception as e:
            self.available = False
            self.error_msg = str(e)

    def _log_query(self, query_str: str):
        self._query_log.append(f"?- {query_str}.")

    def get_questions_for_role(self, role: str) -> List[Dict]:
        """Query: matches_role(ID, Role) → return list of question dicts"""
        if not self.available:
            return []
        
        query = f"matches_role(ID, '{role}'), question(ID, Topic, Diff, Text)"
        self._log_query(query)
        
        results = []
        try:
            for sol in self.prolog.query(query):
                results.append({
                    "id": int(sol["ID"]),
                    "topic": str(sol["Topic"]),
                    "difficulty": str(sol["Diff"]),
                    "question": str(sol["Text"])
                })
        except Exception:
            pass
        return results
    
    def evaluate_answer_prolog(self, question_id: int, answer: str) -> Dict:
        """
        Query PROLOG to check keyword coverage.
        """
        if not self.available:
            return {"matched_keywords": [], "score_component": 0.0}
        
        answer_lower = answer.lower()
        query = f"keyword({question_id}, KW)"
        self._log_query(query)
        
        matched = []
        total_kws = self._count_keywords(question_id)
        
        try:
            for sol in self.prolog.query(query):
                kw = str(sol["KW"])
                if kw.lower() in answer_lower:
                    matched.append(kw)
        except Exception:
            pass
            
        score = len(matched) / float(max(1, total_kws))
        return {
            "matched_keywords": matched, 
            "total_count": total_kws,
            "score_component": round(score, 2)
        }
    
    def get_recommendation(self, weak_topic: str) -> Optional[str]:
        """Query: recommend_topic(WeakTopic, NextTopic)"""
        if not self.available:
            return None
        
        query = f"recommend_topic({weak_topic.lower()}, Next)"
        self._log_query(query)
        
        try:
            for sol in self.prolog.query(query):
                return str(sol["Next"])
        except Exception:
            pass
        return None
    
    def is_easy_question(self, question_id: int) -> bool:
        """Query: easy_question(ID)"""
        if not self.available:
            return False
        
        query = f"easy_question({question_id})"
        self._log_query(query)
        
        try:
            return bool(list(self.prolog.query(query)))
        except Exception:
            return False
    
    def _count_keywords(self, question_id: int) -> int:
        try:
            return len(list(self.prolog.query(f"keyword({question_id}, _)")))
        except Exception:
            return 0
    
    def get_prolog_query_log(self) -> List[str]:
        """Returns the list of PROLOG queries executed this session"""
        return self._query_log
