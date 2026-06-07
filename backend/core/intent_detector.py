import re

class IntentDetector:
    ADD_PATTERNS = [
        r"(?:add|put)\s+(.+?)\s+(?:to|on)\s+(?:my\s+)?(?:todo|list|tasks)",
        r"(?:remind\s+me\s+to|don't\s+forget\s+to|i\s+need\s+to\s+study|i\s+should\s+learn|i\s+want\s+to\s+learn|need\s+to\s+practice)\s+(.+)",
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
