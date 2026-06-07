import os
import json
import time
from google import genai
from google.genai import types
from config import LEARNING_PATH_JSON
from core.key_manager import KeyManager

class LearningPath:
    def __init__(self, key_manager: KeyManager):
        self.key_manager = key_manager

    def _get_fallback_path(self, goal: str, target_skills: list) -> dict:
        """
        Creates a high-quality fallback DevOps roadmap.
        """
        return {
            "goal": goal,
            "current_day": 1,
            "phases": [
                {
                    "title": "Phase 1: Foundations",
                    "description": "Master the command line, version control, and core networking.",
                    "days": [
                        {
                            "day": 1,
                            "title": "Linux Commands & Scripting",
                            "topics": ["CLI navigation", "file permissions", "pipes & redirects", "basic bash scripts"],
                            "resources": [
                                {"title": "Linux Journey", "url": "https://linuxjourney.com/"},
                                {"title": "Bash Scripting Cheat Sheet", "url": "https://devhints.io/bash"}
                            ],
                            "tasks": ["Write a script to automate log compression", "Configure user groups and permissions"],
                            "estimated_time": 60,
                            "status": "pending"
                        },
                        {
                            "day": 2,
                            "title": "Git & Collaborative Workflows",
                            "topics": ["Git branching", "rebase vs merge", "resolving conflicts", "GitHub Actions basics"],
                            "resources": [
                                {"title": "Git Branching Game", "url": "https://learngitbranching.js.org/"}
                            ],
                            "tasks": ["Create a repo, create conflict, merge and resolve it", "Setup a simple pre-commit hook"],
                            "estimated_time": 60,
                            "status": "pending"
                        },
                        {
                            "day": 3,
                            "title": "DevOps Networking Essentials",
                            "topics": ["TCP/IP stack", "DNS resolution", "HTTP/HTTPS protocols", "Load Balancers"],
                            "resources": [
                                {"title": "DNS in One Picture", "url": "https://dnsimple.com/how-dns-works"}
                            ],
                            "tasks": ["Dig DNS records for a domain", "Run a local python server and map traffic"],
                            "estimated_time": 60,
                            "status": "pending"
                        }
                    ]
                },
                {
                    "title": "Phase 2: Containerization & Automation",
                    "description": "Learn to package applications and automate server setup.",
                    "days": [
                        {
                            "day": 4,
                            "title": "Docker Core Concepts",
                            "topics": ["Docker images vs containers", "Dockerfile optimization", "Docker volumes & networking"],
                            "resources": [
                                {"title": "Docker Documentation Guide", "url": "https://docs.docker.com/get-started/"}
                            ],
                            "tasks": ["Write a multi-stage Dockerfile for a Node/Python app", "Mount database volume locally"],
                            "estimated_time": 90,
                            "status": "pending"
                        },
                        {
                            "day": 5,
                            "title": "Docker Compose",
                            "topics": ["Multi-container orchestration", "compose environment files", "service dependencies"],
                            "resources": [
                                {"title": "Awesome Docker Compose Templates", "url": "https://github.com/docker/awesome-compose"}
                            ],
                            "tasks": ["Spin up a Wordpress + MySQL stack using Compose", "Define healthchecks in Compose file"],
                            "estimated_time": 90,
                            "status": "pending"
                        },
                        {
                            "day": 6,
                            "title": "CI/CD & Jenkins/GitHub Actions",
                            "topics": ["CI/CD pipelines", "build automation", "declarative syntax", "artifact storage"],
                            "resources": [
                                {"title": "GitHub Actions Docs", "url": "https://docs.github.com/en/actions"}
                            ],
                            "tasks": ["Setup GitHub Action to run linter on git push", "Build and push docker image to DockerHub automatically"],
                            "estimated_time": 120,
                            "status": "pending"
                        }
                    ]
                },
                {
                    "title": "Phase 3: Orchestration & Infrastructure",
                    "description": "Learn production grade systems scaling and IaC.",
                    "days": [
                        {
                            "day": 7,
                            "title": "Kubernetes Architecture & Pods",
                            "topics": ["Control plane components", "kubelet & kube-proxy", "Pods and namespaces"],
                            "resources": [
                                {"title": "Kubernetes Interactive Tutorial", "url": "https://kubernetes.io/docs/tutorials/"}
                            ],
                            "tasks": ["Install Minikube or Kind", "Deploy an Nginx Pod via YAML configuration"],
                            "estimated_time": 120,
                            "status": "pending"
                        },
                        {
                            "day": 8,
                            "title": "K8s Deployments & Services",
                            "topics": ["ReplicaSets", "rolling updates", "ClusterIP, NodePort, and LoadBalancer services"],
                            "resources": [
                                {"title": "Kubernetes Services Explained", "url": "https://kubernetes.io/docs/concepts/services-networking/service/"}
                            ],
                            "tasks": ["Create a Deployment with 3 replicas", "Expose deployment using ClusterIP and port-forward to test"],
                            "estimated_time": 120,
                            "status": "pending"
                        },
                        {
                            "day": 9,
                            "title": "Infrastructure as Code with Terraform",
                            "topics": ["Declarative infra", "Terraform providers & state", "HCL variables & outputs"],
                            "resources": [
                                {"title": "Terraform HashiCorp Learn", "url": "https://learn.hashicorp.com/terraform"}
                            ],
                            "tasks": ["Deploy a local Docker container using Terraform", "Configure state locking or local file backend"],
                            "estimated_time": 90,
                            "status": "pending"
                        }
                    ]
                },
                {
                    "title": "Phase 4: Interview & Production Readiness",
                    "description": "Refine architectures and practice common DevOps interview topics.",
                    "days": [
                        {
                            "day": 10,
                            "title": "DevOps Interview Q&A & System Design",
                            "topics": ["DevOps lifecycle", "troubleshooting exercises", "high availability designs"],
                            "resources": [
                                {"title": "DevOps Interview Questions Guide", "url": "https://github.com/bregman-arie/devops-exercises"}
                            ],
                            "tasks": ["Architect a resilient three-tier web application", "Review 15 common interview scenarios"],
                            "estimated_time": 120,
                            "status": "pending"
                        }
                    ]
                }
            ]
        }

    def generate_initial_path(self, name: str, goal: str, current_skills: list, target_skills: list, daily_study_time: int) -> dict:
        api_key, key_id = self.key_manager.get_active_key_string()
        
        # If no API key, build fallback
        if not api_key:
            path = self._get_fallback_path(goal, target_skills)
            self._save_path(path)
            return path
            
        # Call Gemini to generate a tailored learning path in JSON format
        prompt = (
            f"Generate a customized day-by-day learning roadmap.\n"
            f"User Profile:\n"
            f"- Name: {name}\n"
            f"- Career Goal: {goal}\n"
            f"- Current Skills: {', '.join(current_skills)}\n"
            f"- Target Skills: {', '.join(target_skills)}\n"
            f"- Daily Study Time: {daily_study_time} minutes\n\n"
            f"Structure the response strictly as a JSON object with this shape:\n"
            f"{{\n"
            f"  \"goal\": \"string representing the goal\",\n"
            f"  \"current_day\": 1,\n"
            f"  \"phases\": [\n"
            f"    {{\n"
            f"      \"title\": \"Phase Title (e.g. Phase 1: Foundations)\",\n"
            f"      \"description\": \"Brief summary of this phase\",\n"
            f"      \"days\": [\n"
            f"        {{\n"
            f"          \"day\": 1,\n"
            f"          \"title\": \"Daily topic title\",\n"
            f"          \"topics\": [\"topic 1\", \"topic 2\"],\n"
            f"          \"resources\": [{{\"title\": \"resource name\", \"url\": \"http... or type description\"}}],\n"
            f"          \"tasks\": [\"task 1\", \"task 2\"],\n"
            f"          \"estimated_time\": 60,\n"
            f"          \"status\": \"pending\"\n"
            f"        }}\n"
            f"      ]\n"
            f"    }}\n"
            f"  ]\n"
            f"}}\n"
            f"Keep it realistic, concise, and target around 10 to 15 days of content. Return ONLY the raw JSON output."
        )
        
        try:
            client = genai.Client(api_key=api_key)
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                )
            )
            self.key_manager.on_success(key_id)
            
            path = json.loads(response.text)
            self._save_path(path)
            return path
        except Exception as e:
            # Fallback on error
            path = self._get_fallback_path(goal, target_skills)
            self._save_path(path)
            return path

    def get_path(self) -> dict:
        if not os.path.exists(LEARNING_PATH_JSON):
            # Try to build from profile if profile exists
            from core.profile_manager import ProfileManager
            profile = ProfileManager.get_profile()
            return self.generate_initial_path(
                profile.get("name"),
                profile.get("goal"),
                profile.get("current_skills", []),
                profile.get("target_skills", []),
                profile.get("daily_study_time", 60)
            )
            
        try:
            with open(LEARNING_PATH_JSON, 'r') as f:
                return json.load(f)
        except Exception:
            return {}

    def _save_path(self, path: dict):
        with open(LEARNING_PATH_JSON, 'w') as f:
            json.dump(path, f, indent=4)

    def update_day_status(self, day_num: int, status: str) -> bool:
        """
        Updates the status of a specific day ('pending', 'completed', 'skipped')
        """
        path = self.get_path()
        changed = False
        
        for phase in path.get('phases', []):
            for d in phase.get('days', []):
                if d['day'] == day_num:
                    d['status'] = status
                    changed = True
                    break
            if changed:
                break
                
        if changed:
            # Auto increment current_day if completing current day
            if status == "completed" and path.get("current_day") == day_num:
                path["current_day"] = day_num + 1
            self._save_path(path)
            return True
        return False

    def auto_adjust_path(self, last_chat_text: str) -> bool:
        """
        Adapts the roadmap daily based on what the user discussed in chat.
        """
        path = self.get_path()
        api_key, key_id = self.key_manager.get_active_key_string()
        if not api_key:
            return False # skip if no key
            
        prompt = (
            f"Analyze the following conversation context and adjust/update the current roadmap path JSON.\n"
            f"Context: \"{last_chat_text[:1500]}\"\n\n"
            f"Current roadmap JSON:\n{json.dumps(path)}\n\n"
            f"Determine if the user successfully completed/understands any of the current day's topics, "
            f"or if they are struggling (in which case you might append a new day or insert extra practice tasks "
            f"or resource links to help them, or adjust upcoming days).\n"
            f"Return the adjusted roadmap strictly using the identical JSON schema. Do not return extra commentary."
        )
        
        try:
            client = genai.Client(api_key=api_key)
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                )
            )
            self.key_manager.on_success(key_id)
            
            adjusted_path = json.loads(response.text)
            self._save_path(adjusted_path)
            return True
        except Exception:
            return False

    def get_today_plan(self) -> dict:
        path = self.get_path()
        curr = path.get("current_day", 1)
        
        for phase in path.get("phases", []):
            for d in phase.get("days", []):
                if d["day"] == curr:
                    return d
                    
        # Return first pending day if current day is not matching
        for phase in path.get("phases", []):
            for d in phase.get("days", []):
                if d["status"] == "pending":
                    return d
        return {}
