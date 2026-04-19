"""
Knowledge Base System (Unit I & V)
Stores questions, answers, topic mappings, and generic FOL rules.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from question_bank_data import QUESTION_BLUEPRINT, SKILL_ALIASES, TOPIC_METADATA


class KnowledgeBase:
    def __init__(self):
        self.skill_aliases = {self._normalize_token(k): v for k, v in SKILL_ALIASES.items()}
        self.skill_topics = self._initialize_topics()
        self.questions = self._initialize_questions()
        self.ideal_answers = self._initialize_ideal_answers()

    def _initialize_questions(self) -> Dict[str, Dict[str, List[Dict[str, Any]]]]:
        question_id = 1
        built: Dict[str, Dict[str, List[Dict[str, Any]]]] = {}

        for topic, difficulty_map in QUESTION_BLUEPRINT.items():
            built[topic] = {}
            for difficulty, entries in difficulty_map.items():
                built[topic][difficulty] = []
                for raw in entries:
                    question = dict(raw)
                    question["id"] = question_id
                    question["topic"] = topic
                    question["difficulty"] = difficulty
                    question["difficulty_level"] = difficulty
                    question["keywords"] = [k.lower() for k in question.get("keywords", [])]
                    question["concepts"] = [c.lower() for c in question.get("concepts", [])]
                    question.setdefault("role_tags", [])
                    question.setdefault("skill_tags", [])
                    question["fol_rules"] = self._build_generic_fol_rules(question)
                    built[topic][difficulty].append(question)
                    question_id += 1

        return built

    def _build_generic_fol_rules(self, question: Dict[str, Any]) -> List[Dict[str, Any]]:
        keywords = list(question.get("keywords", []))
        concepts = list(question.get("concepts", []))
        example = (question.get("ideal_answer") or {}).get("example", "")
        difficulty = question.get("difficulty", "beginner")

        min_words = {"beginner": 18, "intermediate": 28, "advanced": 40}.get(difficulty, 20)
        partial_words = max(10, min_words // 2)

        good_predicates = []
        for keyword in keywords[:2]:
            good_predicates.append({"fn": "Contains", "args": [keyword]})
        if concepts:
            good_predicates.append({"fn": "Explains", "args": [concepts[0]]})
        if example:
            good_predicates.append({"fn": "ExemplifiesCode", "args": []})
        good_predicates.append({"fn": "IsDetailed", "args": [min_words]})

        partial_focus = concepts[0] if concepts else (keywords[0] if keywords else question["topic"])
        partial_predicates = [
            {"fn": "Contains", "args": [partial_focus]},
            {"fn": "IsDetailed", "args": [partial_words]},
        ]

        return [
            {"type": "GoodAnswer", "predicates": good_predicates, "connective": "AND", "weight": 1.0},
            {"type": "PartialAnswer", "predicates": partial_predicates, "connective": "AND", "weight": 0.5},
        ]

    def _initialize_topics(self) -> Dict[str, Dict[str, List[str]]]:
        return {self._normalize_token(topic): data for topic, data in TOPIC_METADATA.items()}

    def _initialize_ideal_answers(self) -> Dict[int, Dict[str, Any]]:
        ideal_answers: Dict[int, Dict[str, Any]] = {}
        for question in self.get_all_questions():
            ideal_answers[question["id"]] = question.get("ideal_answer", {"key_points": [], "example": ""})
        return ideal_answers

    def _normalize_token(self, token: Any) -> str:
        return str(token or "").strip().lower()

    def expand_skill_to_topics(self, token: Any) -> List[str]:
        normalized = self._normalize_token(token)
        if not normalized:
            return []
        if normalized in self.questions:
            return [normalized]
        return [t for t in self.skill_aliases.get(normalized, []) if t in self.questions]

    def resolve_topics_from_profile(self, profile: Dict[str, Any]) -> List[str]:
        ordered_topics: List[str] = []
        seen = set()

        def add_topics(items: List[str]) -> None:
            for item in items:
                topic = self._normalize_token(item)
                if topic in self.questions and topic not in seen:
                    seen.add(topic)
                    ordered_topics.append(topic)

        skills = [self._normalize_token(skill) for skill in profile.get("skills", [])]
        role = self._normalize_token(profile.get("target_role", ""))

        for skill in skills:
            add_topics(self.expand_skill_to_topics(skill))

        add_topics(self.expand_skill_to_topics(role))

        if not ordered_topics:
            default_role_topics = self.expand_skill_to_topics("software engineer")
            add_topics(default_role_topics)

        if "behavioral" not in seen:
            ordered_topics.append("behavioral")

        return ordered_topics

    def get_topic_weight_map(self, profile: Dict[str, Any]) -> Dict[str, float]:
        topics = self.resolve_topics_from_profile(profile)
        total = max(len(topics), 1)
        weights: Dict[str, float] = {}
        for idx, topic in enumerate(topics):
            weights[topic] = max(0.2, round(1.0 - (idx * (0.7 / total)), 3))
        return weights

    def get_all_questions(self) -> List[Dict[str, Any]]:
        result: List[Dict[str, Any]] = []
        for topic in self.questions.values():
            for difficulty in topic.values():
                result.extend(difficulty)
        return result

    def get_questions_by_topic(self, topic: str, level: Optional[str] = None) -> List[Dict[str, Any]]:
        topic_key = self._normalize_token(topic)
        if topic_key not in self.questions:
            return []
        if level is None:
            combined: List[Dict[str, Any]] = []
            for diff_questions in self.questions[topic_key].values():
                combined.extend(diff_questions)
            return combined
        return list(self.questions[topic_key].get(self._normalize_token(level), []))

    def get_question_by_id(self, q_id: int) -> Optional[Dict[str, Any]]:
        q_id_str = str(q_id)
        for question in self.get_all_questions():
            if str(question["id"]) == q_id_str:
                return question
        return None

    def explore_topics_bfs(self) -> List[Dict[str, Any]]:
        nodes: List[Dict[str, Any]] = []
        for topic in self.questions:
            nodes.append({"name": topic.title(), "level": "topic"})
            for difficulty, questions in self.questions[topic].items():
                nodes.append({"name": difficulty.capitalize(), "level": "difficulty"})
                for question in questions:
                    nodes.append({"name": question["question"], "id": question["id"], "level": "question"})
        return nodes
