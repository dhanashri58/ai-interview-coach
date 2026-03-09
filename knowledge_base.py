"""
Knowledge Base System (Unit I & V)
Stores questions, answers, and evaluation criteria
"""

import json
from typing import List, Dict, Any

class KnowledgeBase:
    def __init__(self):
        self.questions = self._initialize_questions()
        self.skill_topics = self._initialize_topics()
        self.ideal_answers = self._initialize_ideal_answers()
    
    def _initialize_questions(self) -> Dict:
        """Initialize question bank with categories and difficulty levels"""
        return {
            "python": {
                "beginner": [
                    {
                        "id": 1,
                        "question": "What is a list in Python? Explain with example.",
                        "topic": "python",
                        "difficulty": "beginner",
                        "difficulty_level": "beginner",
                        "keywords": ["mutable", "ordered", "sequence", "collection", "[]"],
                        "concepts": ["mutable", "indexing", "slicing"]
                    },
                    {
                        "id": 2,
                        "question": "What is the difference between tuple and list?",
                        "topic": "python",
                        "difficulty": "beginner",
                        "difficulty_level": "beginner",
                        "keywords": ["immutable", "mutable", "faster", "parentheses", "brackets"],
                        "concepts": ["immutability", "performance", "syntax"]
                    },
                    {
                        "id": 3,
                        "question": "Explain if-else statement with example.",
                        "topic": "python",
                        "difficulty": "beginner",
                        "difficulty_level": "beginner",
                        "keywords": ["condition", "branch", "elif", "else", "indentation"],
                        "concepts": ["conditional", "flow control", "boolean"]
                    }
                ],
                "intermediate": [
                    {
                        "id": 4,
                        "question": "Explain decorators in Python with example.",
                        "topic": "python",
                        "difficulty": "intermediate",
                        "difficulty_level": "intermediate",
                        "keywords": ["@", "wrapper", "function", "modify", "behavior"],
                        "concepts": ["higher-order functions", "syntax sugar", "metaprogramming"]
                    },
                    {
                        "id": 5,
                        "question": "What is list comprehension? Provide examples.",
                        "topic": "python",
                        "difficulty": "intermediate",
                        "difficulty_level": "intermediate",
                        "keywords": ["concise", "create", "transform", "filter", "syntax"],
                        "concepts": ["functional", "iteration", "expression"]
                    }
                ],
                "advanced": [
                    {
                        "id": 6,
                        "question": "Explain generators and yield keyword.",
                        "topic": "python",
                        "difficulty": "advanced",
                        "difficulty_level": "advanced",
                        "keywords": ["iterator", "lazy", "memory", "yield", "state"],
                        "concepts": ["lazy evaluation", "memory efficiency", "iteration protocol"]
                    },
                    {
                        "id": 101,
                        "question": "Explain metaclasses in Python and their use cases.",
                        "topic": "python",
                        "difficulty": "advanced",
                        "difficulty_level": "advanced",
                        "keywords": ["type", "class", "metaclass", "behavior", "singleton"],
                        "concepts": ["metaprogramming", "class creation", "object model"]
                    }
                ]
            },
            "sql": {
                "beginner": [
                    {
                        "id": 7,
                        "question": "What is SQL and what are its main types of commands?",
                        "topic": "sql",
                        "difficulty": "beginner",
                        "difficulty_level": "beginner",
                        "keywords": ["database", "DDL", "DML", "DCL", "query"],
                        "concepts": ["data definition", "data manipulation", "data control"]
                    },
                    {
                        "id": 8,
                        "question": "Explain SELECT statement with example.",
                        "topic": "sql",
                        "difficulty": "beginner",
                        "difficulty_level": "beginner",
                        "keywords": ["SELECT", "FROM", "WHERE", "retrieve", "data"],
                        "concepts": ["projection", "selection", "filtering"]
                    }
                ],
                "intermediate": [
                    {
                        "id": 9,
                        "question": "What is JOIN? Explain different types of JOINs.",
                        "topic": "sql",
                        "difficulty": "intermediate",
                        "difficulty_level": "intermediate",
                        "keywords": ["INNER", "LEFT", "RIGHT", "FULL", "combine"],
                        "concepts": ["relational algebra", "table relationships", "foreign keys"]
                    }
                ],
                "advanced": [
                    {
                        "id": 102,
                        "question": "Explain window functions and how they differ from GROUP BY.",
                        "topic": "sql",
                        "difficulty": "advanced",
                        "difficulty_level": "advanced",
                        "keywords": ["over", "partition", "rank", "row_number", "aggregate"],
                        "concepts": ["window functions", "aggregation", "analytic functions"]
                    }
                ]
            },
            "dsa": {
                "beginner": [
                    {
                        "id": 10,
                        "question": "What is an array? Explain time complexity of array operations.",
                        "topic": "dsa",
                        "difficulty": "beginner",
                        "difficulty_level": "beginner",
                        "keywords": ["contiguous", "memory", "index", "O(1)", "O(n)"],
                        "concepts": ["random access", "time complexity", "memory allocation"]
                    }
                ],
                "intermediate": [
                    {
                        "id": 11,
                        "question": "Explain binary search algorithm with example.",
                        "topic": "dsa",
                        "difficulty": "intermediate",
                        "difficulty_level": "intermediate",
                        "keywords": ["divide", "conquer", "sorted", "logarithmic", "mid"],
                        "concepts": ["divide and conquer", "searching", "logarithmic time"]
                    }
                ],
                "advanced": [
                    {
                        "id": 103,
                        "question": "Explain dynamic programming and the concept of memoization.",
                        "topic": "dsa",
                        "difficulty": "advanced",
                        "difficulty_level": "advanced",
                        "keywords": ["overlapping", "subproblems", "optimal", "cache", "bottom-up"],
                        "concepts": ["dynamic programming", "memoization", "optimization"]
                    }
                ]
            },
            "javascript": {
                "beginner": [
                    {
                        "id": 12,
                        "question": "What is JavaScript and how is it different from Java?",
                        "topic": "javascript",
                        "difficulty": "beginner",
                        "difficulty_level": "beginner",
                        "keywords": ["scripting", "dynamic", "browser", "interpreted", "prototype"],
                        "concepts": ["interpreted language", "client-side", "dynamic typing"]
                    }
                ]
            }
        }
    
    def _initialize_topics(self) -> Dict:
        """Initialize topic relationships for adaptive learning"""
        return {
            "python": {
                "prerequisites": ["basic programming concepts"],
                "core_topics": ["data_structures", "control_flow", "functions", "OOP"],
                "advanced_topics": ["decorators", "generators", "context managers"],
                "difficulty_progression": {
                    "beginner": ["data_structures", "control_flow"],
                    "intermediate": ["functions", "OOP", "modules"],
                    "advanced": ["decorators", "generators", "metaprogramming"]
                }
            },
            "sql": {
                "prerequisites": ["database concepts"],
                "core_topics": ["basics", "queries", "filtering"],
                "advanced_topics": ["joins", "subqueries", "indexes", "optimization"],
                "difficulty_progression": {
                    "beginner": ["basics", "simple queries"],
                    "intermediate": ["joins", "subqueries", "aggregation"],
                    "advanced": ["optimization", "stored procedures", "triggers"]
                }
            }
        }
    
    def _initialize_ideal_answers(self) -> Dict:
        """Store ideal answer structures for evaluation"""
        return {
            1: {
                "key_points": [
                    "List is a mutable data structure",
                    "It maintains order of elements",
                    "Can contain mixed data types",
                    "Defined using square brackets []",
                    "Supports indexing and slicing"
                ],
                "example": "my_list = [1, 2, 'hello', 3.14]",
                "common_mistakes": [
                    "Confusing with tuples (immutability)",
                    "Wrong syntax with parentheses"
                ]
            },
            2: {
                "key_points": [
                    "List is mutable, tuple is immutable",
                    "List uses [], tuple uses ()",
                    "Tuples are faster for iteration",
                    "Tuples can be used as dictionary keys"
                ],
                "example": "list_ex = [1,2,3]\ntuple_ex = (1,2,3)",
                "common_mistakes": [
                    "Trying to modify tuple elements",
                    "Using wrong brackets"
                ]
            },
            3: {
                "key_points": [
                    "Used for conditional execution",
                    "Syntax: if condition: block",
                    "Can have elif for multiple conditions",
                    "else for default case",
                    "Proper indentation is crucial"
                ],
                "example": "if x > 0:\n    print('positive')\nelif x < 0:\n    print('negative')\nelse:\n    print('zero')",
                "common_mistakes": [
                    "Missing colon after condition",
                    "Wrong indentation",
                    "Using assignment (=) instead of comparison (==)"
                ]
            }
        }
    
    # ============= FIXED METHOD WITH CORRECT INDENTATION =============
    def get_questions_by_topic(self, topic: str, level: str) -> List:
        """Get questions for specific topic and difficulty level"""
        try:
            # Check if topic exists
            if topic in self.questions:
                # Check if level exists for that topic
                if level in self.questions[topic]:
                    return self.questions[topic][level]
            
            # Try case-insensitive match
            for t in self.questions:
                if t.lower() == topic.lower():
                    if level in self.questions[t]:
                        return self.questions[t][level]
            
            # If no exact match, return empty list
            return []
            
        except Exception as e:
            print(f"Error in get_questions_by_topic: {e}")
            return []  # Return empty list on error, not [1]
    
    def get_question_by_id(self, q_id: int) -> Dict:
        """Retrieve specific question by ID"""
        for topic in self.questions:
            for level in self.questions[topic]:
                for q in self.questions[topic][level]:
                    if q["id"] == q_id:
                        return q
        return None
    
    def get_ideal_answer(self, q_id: int) -> Dict:
        """Get ideal answer structure for a question"""
        return self.ideal_answers.get(q_id, {
            "key_points": [],
            "example": "",
            "common_mistakes": []
        })


    def explore_topics_bfs(self) -> List[Dict]:
        """
        Unit II: Uninformed Search - Breadth-First Search (BFS)
        Traverses the knowledge base tree level by level.
        Tree Structure: Root -> Topics -> Difficulties -> Questions
        """
        queue = []
        result = []
        
        # Enqueue Root
        queue.append({
            "level": "root", 
            "name": "Knowledge Base Data", 
            "children": list(self.questions.keys())
        })
        
        while queue:
            node = queue.pop(0)
            result.append(node)
            
            if node["level"] == "root":
                for topic in node["children"]:
                    queue.append({
                        "level": "topic",
                        "name": topic.upper(),
                        "parent": "root",
                        "children": list(self.questions[topic].keys())
                    })
                    
            elif node["level"] == "topic":
                topic = node["name"].lower()
                for diff in node["children"]:
                    queue.append({
                        "level": "difficulty",
                        "name": diff.capitalize(),
                        "parent": topic,
                        "children": self.questions[topic][diff]
                    })
                    
            elif node["level"] == "difficulty":
                topic = node["parent"]
                diff = node["name"].lower()
                for q in node["children"]:
                    queue.append({
                        "level": "question",
                        "id": q["id"],
                        "name": q["question"],
                        "parent": f"{topic} -> {diff}",
                        "topic": topic,
                        "difficulty": diff
                    })
                    
        return result

