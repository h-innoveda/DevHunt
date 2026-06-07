import json
from datetime import datetime, timedelta
from core.db import get_db_connection
from core.profile_manager import ProfileManager

class Analytics:
    @staticmethod
    def get_overview() -> dict:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 1. Total questions asked
        cursor.execute("SELECT COUNT(*) FROM messages WHERE role = 'user'")
        questions_count = cursor.fetchone()[0]
        
        # 2. Todos statistics
        cursor.execute("SELECT COUNT(*) FROM todos WHERE status = 'done'")
        completed_todos = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM todos WHERE status != 'done'")
        pending_todos = cursor.fetchone()[0]
        
        # 3. Total study hours (estimated from completed todos or estimated days completed)
        # We can assume each completed todo represents its estimated time or a default of 45 mins.
        # Let's check completed learning path days as well
        from core.learning_path import LearningPath
        path_mgr = LearningPath(None)
        path = path_mgr.get_path()
        completed_days = 0
        total_time_mins = 0
        
        for phase in path.get('phases', []):
            for day in phase.get('days', []):
                if day['status'] == 'completed':
                    completed_days += 1
                    total_time_mins += day.get('estimated_time', 60)
        
        # Add 45 minutes for each completed manual todo
        total_time_mins += completed_todos * 45
        study_hours = round(total_time_mins / 60, 1)

        # 4. Streak & consistency score
        profile = ProfileManager.get_profile()
        streak = profile.get("streak_counter", 0)
        
        # Consistency score (based on active days in last 14 days)
        # Count unique dates in messages + completed todos + path updates
        two_weeks_ago = (datetime.now() - timedelta(days=14)).isoformat()
        cursor.execute(
            """SELECT COUNT(DISTINCT DATE(timestamp)) FROM messages 
               WHERE role = 'user' AND timestamp >= ?""",
            (two_weeks_ago,)
        )
        active_days = cursor.fetchone()[0]
        
        consistency_score = int((active_days / 14) * 100) if active_days > 0 else 0
        if consistency_score > 100:
            consistency_score = 100

        conn.close()

        return {
            "questions_asked": questions_count,
            "completed_todos": completed_todos,
            "pending_todos": pending_todos,
            "study_hours": study_hours,
            "completed_days": completed_days,
            "streak": streak,
            "consistency_score": max(5, consistency_score)
        }

    @staticmethod
    def get_skills_matrix() -> list:
        """
        Dynamically analyzes chat messages to evaluate user skill competency levels.
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT content FROM messages WHERE role = 'user'")
        messages = [r['content'].lower() for r in cursor.fetchall()]
        conn.close()
        
        # Define core skills and their associated keywords
        skills_def = {
            "Linux & Scripting": ["linux", "bash", "script", "cron", "grep", "ssh", "permissions", "chmod"],
            "Git & Workflows": ["git", "branch", "merge", "rebase", "github", "commit", "conflict", "hook"],
            "Containerization (Docker)": ["docker", "container", "dockerfile", "compose", "volume", "image"],
            "Container Orchestration (K8s)": ["kubernetes", "k8s", "pod", "deployment", "kubectl", "minikube", "service"],
            "CI/CD Pipelines": ["jenkins", "pipeline", "ci/cd", "github actions", "gitlab", "build", "deploy"],
            "Infrastructure as Code": ["terraform", "iac", "ansible", "playbook", "cloudformation", "hcl", "tfstate"]
        }
        
        matrix = []
        for skill_name, keywords in skills_def.items():
            # Count keyword occurrences
            hits = sum(1 for msg in messages if any(kw in msg for kw in keywords))
            
            # Formulate proficiency based on usage
            if hits == 0:
                level = "Not Started"
                progress = 0
            elif hits <= 2:
                level = "Beginner"
                progress = 25 + min(15, hits * 5)
            elif hits <= 6:
                level = "Intermediate"
                progress = 50 + min(20, (hits - 2) * 5)
            else:
                level = "Advanced"
                progress = 80 + min(15, (hits - 6) * 2)
                
            matrix.append({
                "skill": skill_name,
                "level": level,
                "progress": progress
            })
            
        return matrix

    @staticmethod
    def get_weekly_progress() -> dict:
        """
        Returns data for a 7-day progress chart.
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        chart_data = []
        today = datetime.now().date()
        
        for i in range(6, -1, -1):
            day = today - timedelta(days=i)
            day_str = day.strftime('%Y-%m-%d')
            day_label = day.strftime('%a') # Mon, Tue...
            
            # Count questions asked on this day
            cursor.execute(
                "SELECT COUNT(*) FROM messages WHERE role = 'user' AND DATE(timestamp) = ?",
                (day_str,)
            )
            q_count = cursor.fetchone()[0]
            
            # Count todos completed on this day
            cursor.execute(
                "SELECT COUNT(*) FROM todos WHERE status = 'done' AND DATE(completed_at) = ?",
                (day_str,)
            )
            t_count = cursor.fetchone()[0]
            
            chart_data.append({
                "day": day_label,
                "date": day_str,
                "questions": q_count,
                "tasks_completed": t_count
            })
            
        conn.close()
        return chart_data
