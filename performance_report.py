"""
Performance Report Generation (Unit VI - Planning)
Generates comprehensive feedback and learning path
"""

from typing import List, Dict, Any
from datetime import datetime
import numpy as np
from learning_path_astar import AStarLearningPath

class PerformanceReport:
    def __init__(self):
        self.report_templates = {
            "strength": [
                "Strong understanding of {topic}",
                "Good grasp on {concept} concepts",
                "Excellent problem-solving approach in {area}"
            ],
            "weakness": [
                "Need improvement in {topic}",
                "Focus more on {concept}",
                "Practice more {area}-related questions"
            ],
            "improvement": [
                "Review {topic} fundamentals",
                "Study {concept} with practical examples",
                "Work on {area} problem-solving"
            ]
        }
    
    def generate_report(self, user_profile: Dict, answers: List[Dict]) -> Dict:
        """
        Generate comprehensive performance report
        """
        if not answers:
            return self._generate_empty_report(user_profile)
        
        # Calculate various metrics
        overall_score = self._calculate_overall_score(answers)
        topic_performance = self._analyze_topic_performance(answers)
        strengths = self._identify_strengths(topic_performance)
        weaknesses = self._identify_weaknesses(topic_performance)
        learning_path = self._generate_learning_path(weaknesses, user_profile)
        
        # Calculate improvement over time
        progress = self._calculate_progress(answers)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(weaknesses, strengths)
        
        report = {
            "report_id": f"RPT_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "user_profile": user_profile,
            "summary": {
                "total_questions": len(answers),
                "overall_score": overall_score,
                "performance_level": self._get_performance_level(overall_score),
                "completion_rate": self._calculate_completion_rate(answers)
            },
            "detailed_analysis": {
                "by_topic": topic_performance,
                "by_difficulty": self._analyze_difficulty_performance(answers),
                "progress_over_time": progress,
                "strongest_topics": strengths[:3],
                "weakest_topics": weaknesses[:3]
            },
            "learning_path": learning_path,
            "recommendations": recommendations,
            "next_steps": self._generate_next_steps(weaknesses, user_profile),
            "resources": self._suggest_resources(weaknesses)
        }
        
        # Feature 3: Report Narrative Summary
        try:
            import streamlit as st
            if st.session_state.get('ai_enhanced_mode', False):
                from utils import call_gemini
                
                role = user_profile.get("target_role", "candidate")
                
                # Extract learning path details
                module_names_list = ", ".join([step['goal'] for step in learning_path if step.get('phase') != 'optimal_plan'])
                
                total_hours = "unknown"
                for step in learning_path:
                    if step.get('phase') == 'optimal_plan':
                        total_hours = step.get('estimated_time', 'unknown')
                        break
                        
                # Simplify topic scores to a readable string
                topic_scores_str = ", ".join([f"{topic}: {data['average_score']}/10" for topic, data in topic_performance.items()])
                
                prompt = (
                    f"You are an AI career coach reviewing an interview performance.\n"
                    f"The candidate interviewed for: {role}\n"
                    f"Their topic scores were: {topic_scores_str}\n"
                    f"The optimal study path calculated is: {module_names_list} totalling {total_hours}.\n"
                    f"Write a 3-sentence personalised coaching summary. Mention their strongest topic, "
                    f"their weakest topic, and end with an encouraging closing line. "
                    f"Be conversational, not robotic."
                )
                
                llm_summary = call_gemini(prompt, feature_name="Feature 3: Report Summary")
                if llm_summary:
                    report["llm_summary"] = llm_summary
        except Exception as e:
            print("Failed to generate LLM summary:", e)
        
        return report
    
    def _generate_empty_report(self, user_profile: Dict) -> Dict:
        """Generate empty report when no answers available"""
        return {
            "report_id": f"RPT_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "user_profile": user_profile,
            "summary": {
                "total_questions": 0,
                "overall_score": 0.0,
                "performance_level": "not_started",
                "completion_rate": 0.0
            },
            "detailed_analysis": {
                "by_topic": {},
                "by_difficulty": {
                    "beginner": {"average_score": 0, "questions_attempted": 0, "readiness": "not_attempted"},
                    "intermediate": {"average_score": 0, "questions_attempted": 0, "readiness": "not_attempted"},
                    "advanced": {"average_score": 0, "questions_attempted": 0, "readiness": "not_attempted"}
                },
                "progress_over_time": [],
                "strongest_topics": [],
                "weakest_topics": []
            },
            "learning_path": [
                {
                    "phase": "foundation",
                    "focus": "getting_started",
                    "goal": "Complete your first interview session",
                    "estimated_time": "10 minutes",
                    "priority": "high"
                }
            ],
            "recommendations": [
                "Start your first interview practice session",
                "Complete your profile with target role",
                "Practice regularly to track progress"
            ],
            "next_steps": [
                "Click 'Start New Interview' to begin",
                "Answer questions to receive feedback",
                "Review your performance after each session"
            ],
            "resources": [
                {"name": "Interview Tips", "type": "guide", "url": "#"},
                {"name": "Common Questions", "type": "practice", "url": "#"}
            ]
        }
    
    def _calculate_overall_score(self, answers: List[Dict]) -> float:
        """Calculate weighted average score"""
        if not answers:
            return 0.0
        
        scores = [a.get("score", 0) for a in answers]
        return round(sum(scores) / len(scores), 1)
    
    def _calculate_completion_rate(self, answers: List[Dict]) -> float:
        """Calculate completion rate (assuming target is 10 questions)"""
        target_questions = 10
        completion = min(len(answers) / target_questions, 1.0)
        return round(completion * 100, 1)
    
    def _get_performance_level(self, score: float) -> str:
        """Get performance level based on score"""
        if score >= 8.5:
            return "expert"
        elif score >= 7.0:
            return "advanced"
        elif score >= 5.0:
            return "intermediate"
        elif score >= 3.0:
            return "beginner"
        else:
            return "needs_practice"
    
    def _analyze_topic_performance(self, answers: List[Dict]) -> Dict:
        """Analyze performance by topic"""
        topic_scores = {}
        topic_counts = {}
        
        for answer in answers:
            topic = answer.get("topic", "general")
            score = answer.get("score", 0)
            
            if topic not in topic_scores:
                topic_scores[topic] = 0
                topic_counts[topic] = 0
            
            topic_scores[topic] += score
            topic_counts[topic] += 1
        
        # Calculate averages
        performance = {}
        for topic in topic_scores:
            avg_score = topic_scores[topic] / topic_counts[topic]
            performance[topic] = {
                "average_score": round(avg_score, 1),
                "questions_attempted": topic_counts[topic],
                "level": self._get_performance_level(avg_score)
            }
        
        return performance
    
    def _analyze_difficulty_performance(self, answers: List[Dict]) -> Dict:
        """Analyze performance by difficulty level"""
        difficulty_map = {"beginner": [], "intermediate": [], "advanced": []}
        
        for answer in answers:
            diff = answer.get("difficulty", "beginner")
            score = answer.get("score", 0)
            if diff in difficulty_map:
                difficulty_map[diff].append(score)
        
        performance = {}
        for diff, scores in difficulty_map.items():
            if scores:
                avg_score = sum(scores) / len(scores)
                performance[diff] = {
                    "average_score": round(avg_score, 1),
                    "questions_attempted": len(scores),
                    "readiness": self._calculate_readiness(avg_score)
                }
            else:
                performance[diff] = {
                    "average_score": 0,
                    "questions_attempted": 0,
                    "readiness": "not_attempted"
                }
        
        return performance
    
    def _calculate_readiness(self, score: float) -> str:
        """Calculate readiness level for next difficulty"""
        if score >= 8:
            return "ready_for_next"
        elif score >= 6:
            return "practice_more"
        else:
            return "needs_foundation"
    
    def _identify_strengths(self, topic_performance: Dict) -> List[Dict]:
        """Identify top performing topics"""
        strengths = []
        for topic, data in topic_performance.items():
            strengths.append({
                "topic": topic,
                "score": data["average_score"],
                "level": data["level"]
            })
        
        # Sort by score descending
        strengths.sort(key=lambda x: x["score"], reverse=True)
        return strengths
    
    def _identify_weaknesses(self, topic_performance: Dict) -> List[Dict]:
        """Identify bottom performing topics"""
        weaknesses = []
        for topic, data in topic_performance.items():
            weaknesses.append({
                "topic": topic,
                "score": data["average_score"],
                "level": data["level"]
            })
        
        # Sort by score ascending
        weaknesses.sort(key=lambda x: x["score"])
        return weaknesses
    
    def _calculate_progress(self, answers: List[Dict]) -> List[Dict]:
        """Calculate progress over time (for graph)"""
        progress = []
        for i, answer in enumerate(answers):
            progress.append({
                "question_number": i + 1,
                "score": answer.get("score", 0),
                "topic": answer.get("topic", "general")
            })
        return progress
    
    def _generate_learning_path(self, weaknesses: List[Dict], profile: Dict) -> List[Dict]:
        """Generate optimal learning path using A* Search algorithm"""
        # We need the current scores as the initial state of the A* search
        # If the user has never answered a question, all topics default to 0
        topic_scores = {}
        for w in weaknesses:
            topic_scores[w["topic"].lower()] = w["score"]
            
        # If user has no weaknesses recorded yet (e.g., brand new profile)
        if not topic_scores:
            target_role = profile.get("target_role", "software engineer").lower()
            if "data" in target_role:
                topic_scores = {"python": 0, "sql": 0}
            else:
                topic_scores = {"python": 0, "dsa": 0}
                
        # Run A* Algorithm (Target mastery defaults to 8.0)
        astar = AStarLearningPath(topic_scores)
        optimal_modules, total_hours = astar.find_path()
        
        learning_path = []
        
        if optimal_modules:
            for mod in optimal_modules:
                learning_path.append({
                    "phase": mod.difficulty,
                    "focus": mod.topic.upper(),
                    "goal": mod.name,
                    "estimated_time": f"{mod.hours_cost} hours",
                    "priority": "high" if mod.difficulty == "beginner" else "medium"
                })
                
            # Add summary element at the end referencing the total optimized cost
            learning_path.insert(0, {
                "phase": "optimal_plan",
                "focus": "A* Search Minimal Path",
                "goal": f"Reach mastery in all topics",
                "estimated_time": f"Total: {total_hours} hours",
                "priority": "critical"
            })
        else:
            # Fallback if A* fails to find path
            learning_path.append({
                "phase": "practice",
                "focus": "mixed topics",
                "goal": f"Practice full interviews",
                "estimated_time": "3-4 days",
                "priority": "medium"
            })
            
        return learning_path
    
    def _generate_recommendations(self, weaknesses: List[Dict], strengths: List[Dict]) -> List[str]:
        """Generate personalized recommendations"""
        recommendations = []
        
        if weaknesses:
            weak_topics = [w["topic"] for w in weaknesses[:2]]
            recommendations.append(f"Focus on improving {', '.join(weak_topics)}")
        
        if strengths:
            strong_topics = [s["topic"] for s in strengths[:2]]
            recommendations.append(f"Leverage your strength in {', '.join(strong_topics)} for complex problems")
        
        recommendations.append("Practice daily with timed mock interviews")
        recommendations.append("Review concepts you missed before next session")
        
        return recommendations
    
    def _generate_next_steps(self, weaknesses: List[Dict], profile: Dict) -> List[str]:
        """Generate immediate next steps"""
        steps = []
        
        if weaknesses:
            steps.append(f"Start with {weaknesses[0]['topic']} fundamentals")
        
        steps.append("Take a mock interview in 2 days")
        steps.append("Track your progress with daily practice")
        
        return steps
    
    def _suggest_resources(self, weaknesses: List[Dict]) -> List[Dict]:
        """Suggest learning resources based on weaknesses"""
        resources = []
        
        resource_db = {
            "python": [
                {"name": "Python Official Tutorial", "type": "documentation", "url": "https://docs.python.org/3/tutorial/"},
                {"name": "Real Python", "type": "tutorials", "url": "https://realpython.com/"},
                {"name": "Python Practice", "type": "interactive", "url": "https://www.hackerrank.com/domains/python"}
            ],
            "sql": [
                {"name": "SQL Tutorial - W3Schools", "type": "tutorial", "url": "https://www.w3schools.com/sql/"},
                {"name": "Mode SQL Tutorial", "type": "tutorial", "url": "https://mode.com/sql-tutorial/"},
                {"name": "SQL Practice", "type": "interactive", "url": "https://www.sql-practice.com/"}
            ],
            "dsa": [
                {"name": "GeeksforGeeks", "type": "tutorial", "url": "https://www.geeksforgeeks.org/data-structures/"},
                {"name": "LeetCode", "type": "practice", "url": "https://leetcode.com/"},
                {"name": "HackerRank DSA", "type": "practice", "url": "https://www.hackerrank.com/domains/data-structures"}
            ],
            "java": [
                {"name": "Java Tutorial", "type": "tutorial", "url": "https://docs.oracle.com/javase/tutorial/"},
                {"name": "Java Practice", "type": "interactive", "url": "https://www.hackerrank.com/domains/java"}
            ],
            "javascript": [
                {"name": "MDN Web Docs", "type": "documentation", "url": "https://developer.mozilla.org/en-US/docs/Web/JavaScript"},
                {"name": "JavaScript.info", "type": "tutorial", "url": "https://javascript.info/"}
            ],
            "general": [
                {"name": "Interview Preparation", "type": "guide", "url": "https://www.indeed.com/career-advice/interviewing"},
                {"name": "Common Interview Questions", "type": "practice", "url": "https://www.themuse.com/advice/interview-questions-and-answers"}
            ]
        }
        
        # Add resources for weak topics
        added_topics = set()
        for weakness in weaknesses[:3]:
            topic = weakness["topic"].lower()
            if topic in resource_db and topic not in added_topics:
                resources.extend(resource_db[topic])
                added_topics.add(topic)
        
        # Add general resources if none found
        if not resources:
            resources = resource_db["general"]
        
        return resources[:5]  # Limit to 5 resources