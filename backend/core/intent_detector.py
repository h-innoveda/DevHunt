import re

class IntentDetector:
    ADD_PATTERNS = [
        # Pattern 1: Match add/put/create/save/new followed by the task, optionally ending with "to my todo/list/tasks/etc"
        r"\b(?:add|put|create|save|new)\s+(?:a\s+)?(.+?)(?:\s+(?:to|on)\s+(?:my\s+)?(?:todo|list|tasks|board|quests))?$",
        # Pattern 2a: Match with explicit prefix anywhere in message
        r"\b(?:remind\s+me\s+to|don't\s+forget\s+to|i\s+want\s+to|i\s+need\s+to|i\s+should|want\s+to|need\s+to|should|forget\s+to)\s+(learn|study|practice|read|check|review|master|understand|look\s+into)\s+(.+)$",
        # Pattern 2b: Match starting directly with the verb at the beginning of the message
        r"^(?:hey\s+|hi\s+|please\s+)?(?:learn|study|practice|read|check|review|master|understand|look\s+into)\s+(.+)$",
    ]

    COMPLETE_PATTERNS = [
        r"(?:done\s+with|finished|completed|i've\s+finished|i\s+learned)\s+(.+)",
    ]

    @classmethod
    def detect_todo_intent(cls, message: str) -> dict:
        """
        Parses a user message to check if they intend to add or complete a task.
        Returns:
            dict: {"intent": "add"|"complete"|"none", "task_title": str, "priority": str}
        """
        text = message.strip()
        
        # Check add patterns
        for pattern in cls.ADD_PATTERNS:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                # If we captured a verb and a topic (Pattern 2a has 2 groups)
                if len(match.groups()) >= 2 and match.group(1) and match.group(2):
                    verb = match.group(1).strip().capitalize()
                    topic = match.group(2).strip()
                    task = f"{verb} {topic}"
                elif pattern.startswith("^(?:hey"):
                    # Pattern 2b captures the topic, but we know the verb from search.
                    # Let's extract the actual matched verb from the text.
                    matched_verb = "Learn"
                    for v in ["learn", "study", "practice", "read", "check", "review", "master", "understand", "look into"]:
                        if re.search(r"\b" + v + r"\b", text, re.IGNORECASE):
                            matched_verb = v.capitalize()
                            break
                    topic = match.group(1).strip()
                    task = f"{matched_verb} {topic}"
                else:
                    task = match.group(1).strip()
                
                # Clean up punctuation at the end
                task = re.sub(r"[.!?]+$", "", task)
                
                # Check for priority hints
                priority = "medium"
                if any(word in task.lower() for word in ["urgent", "asap", "high priority", "immediately"]):
                    priority = "high"
                elif any(word in task.lower() for word in ["later", "whenever", "low priority"]):
                    priority = "low"
                    
                # Clean up priority text from title
                task = re.sub(r"\b(asap|urgently|immediately|today|tomorrow)\b", "", task, flags=re.IGNORECASE).strip()
                task = re.sub(r"\s+", " ", task)
                
                # Capitalize first letter
                if task:
                    task = task[0].upper() + task[1:]
                    return {
                        "intent": "add",
                        "task_title": task,
                        "priority": priority
                    }

        # Check complete patterns
        for pattern in cls.COMPLETE_PATTERNS:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                task = match.group(1).strip()
                task = re.sub(r"[.!?]+$", "", task)
                task = re.sub(r"\b(today|yesterday|finally)\b", "", task, flags=re.IGNORECASE).strip()
                task = re.sub(r"\s+", " ", task)
                
                if task:
                    task = task[0].upper() + task[1:]
                    return {
                        "intent": "complete",
                        "task_title": task
                    }

        return {
            "intent": "none",
            "task_title": None
        }

