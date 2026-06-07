import json
from datetime import datetime
from google import genai
from google.genai import types
from core.db import get_db_connection
from core.key_manager import KeyManager
from core.rag_pipeline import RAGPipeline
from core.model_selector import classify_query
from core.intent_detector import IntentDetector
from core.todo_manager import TodoManager
from core import logger
from config import SETTINGS_PATH

class ChatEngine:
    def __init__(self, key_manager: KeyManager, rag_pipeline: RAGPipeline):
        self.key_manager = key_manager
        self.rag_pipeline = rag_pipeline

    def _get_english_mode(self) -> bool:
        import os
        if os.path.exists(SETTINGS_PATH):
            try:
                with open(SETTINGS_PATH, 'r') as f:
                    settings = json.load(f)
                    return settings.get("english_correction", False)
            except Exception:
                pass
        return False

    def send_message(self, session_id: str, user_message: str, model_override: str = None) -> dict:
        # 1. Fetch relevant content from RAG
        rag_results = self.rag_pipeline.search_similarity(user_message, top_k=3)
        has_rag = len(rag_results) > 0 and any(r['similarity'] > 0.45 for r in rag_results)
        active_rag_docs = [r for r in rag_results if r['similarity'] > 0.45]

        # 2. Classify query / select model
        model_name = model_override
        if not model_name:
            model_name = classify_query(user_message, has_rag_docs=len(active_rag_docs) > 0)

        # 3. Retrieve session history from DB
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """SELECT role, content FROM messages
               WHERE session_id = ?
               ORDER BY timestamp DESC LIMIT 10""",
            (session_id,)
        )
        history_rows = cursor.fetchall()
        conn.close()
        history = list(reversed(history_rows))

        # 4. Construct System Instruction
        system_instruction = (
            "You are DevHunt AI, a smart personal assistant that helps with problem solving, debugging, learning, and answering questions on any topic.\n"
            "You provide clear, structured, and example-rich answers. Always use clear headings, "
            "bullet points, and code blocks where appropriate.\n"
            "If the user asks about a learning roadmap or topic, guide them step-by-step.\n"
        )

        if self._get_english_mode():
            system_instruction += (
                "\n[IMPORTANT: English Grammar Correction is ENABLED]\n"
                "At the very beginning of your response, check if the user's message had any grammar mistakes. "
                "If it did, output a brief, polite correction and suggested phrasing in a blockquote format, "
                "wrapped in italics. For example:\n"
                "> *Grammar Tip: 'I needs learn Docker' -> 'I need to learn Docker' (Suggested: 'I want to study Docker today')*\n"
                "Then proceed to answer their question normally. If there are no mistakes, do not include any grammar tip."
            )

        if active_rag_docs:
            system_instruction += (
                "\n[IMPORTANT: Contextual Knowledge Available]\n"
                "Use the following materials from the user's personal Knowledge Base to answer the question. "
                "You must cite the source name/type in your explanation.\n\nKnowledge Base Context:\n"
            )
            for doc in active_rag_docs:
                source_name = doc['metadata'].get('source_name', 'Unknown Source')
                source_type = doc['metadata'].get('source_type', 'Note')
                system_instruction += f"--- Source: {source_name} ({source_type}) ---\n{doc['content']}\n\n"

        # 5. Key rotation retry loop
        all_keys = self.key_manager.get_keys_list()
        max_attempts = max(3, len(all_keys))

        response_text = None
        used_key_id = None
        used_key_masked = "None"

        for attempt in range(max_attempts):
            api_key, key_id = self.key_manager.get_active_key_string()
            if not api_key:
                return {
                    "success": False,
                    "error": "No active API key available. Go to Key Manager in Settings to add a Gemini API Key."
                }

            used_key_id = key_id
            for k in all_keys:
                if k['id'] == key_id:
                    used_key_masked = k['masked_key']
                    break

            try:
                # New google-genai SDK (supports AQ. keys)
                client = genai.Client(api_key=api_key)

                # Build conversation history
                contents = []
                for msg in history:
                    role = "user" if msg['role'] == "user" else "model"
                    contents.append(types.Content(
                        role=role,
                        parts=[types.Part(text=msg['content'])]
                    ))
                # Add current message
                contents.append(types.Content(
                    role="user",
                    parts=[types.Part(text=user_message)]
                ))

                import time as _time
                t0 = _time.time()
                response = client.models.generate_content(
                    model=model_name,
                    contents=contents,
                    config=types.GenerateContentConfig(
                        system_instruction=system_instruction,
                        temperature=0.3,
                    )
                )

                response_text = response.text
                duration_ms = int((_time.time() - t0) * 1000)
                self.key_manager.on_success(key_id)
                logger.success("api_call", f"Chat response from {model_name}", {
                    "model": model_name, "key": used_key_masked,
                    "session_id": session_id, "duration_ms": duration_ms,
                    "prompt_len": len(user_message), "response_len": len(response_text)
                })
                break  # success

            except Exception as e:
                err_str = str(e)
                print(f"ChatEngine Exception: {type(e).__name__} - {err_str}")
                if "429" in err_str or "ResourceExhausted" in err_str or "RESOURCE_EXHAUSTED" in err_str:
                    self.key_manager.on_rate_limit_error(key_id)
                    logger.warn("key_event", f"Rate limit hit on key {used_key_masked}", {"key": used_key_masked, "model": model_name})
                else:
                    self.key_manager.on_other_error(key_id)
                    logger.error("api_call", f"API error: {err_str[:200]}", {"model": model_name, "key": used_key_masked, "error": err_str[:300]})
                    return {
                        "success": False,
                        "error": f"Gemini API Error: {err_str}"
                    }
        if not response_text:
            return {
                "success": False,
                "error": "All API keys are exhausted or on cooldown. Please try again in 60 seconds."
            }

        # 6. Intent Detection & Auto-Todo
        todo_detected = None
        intent = IntentDetector.detect_todo_intent(user_message)
        if intent['intent'] == 'add':
            new_todo = TodoManager.create_todo(
                title=intent['task_title'],
                priority=intent['priority'],
                source="ai_detected",
                description=f"Auto-added from chat session topic: {user_message[:50]}..."
            )
            todo_detected = {"action": "add", "todo": new_todo}
        elif intent['intent'] == 'complete':
            todos = TodoManager.get_todos(status_filter="pending")
            completed_todo = None
            for todo in todos:
                if intent['task_title'].lower() in todo['title'].lower() or todo['title'].lower() in intent['task_title'].lower():
                    TodoManager.complete_todo(todo['id'])
                    completed_todo = todo
                    break
            if completed_todo:
                todo_detected = {"action": "complete", "todo": completed_todo}

        # 7. Log to SQLite
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO messages (session_id, role, content, model_used, key_used) VALUES (?, ?, ?, ?, ?)",
            (session_id, 'user', user_message, model_name, used_key_id)
        )
        cursor.execute(
            "INSERT INTO messages (session_id, role, content, model_used, key_used) VALUES (?, ?, ?, ?, ?)",
            (session_id, 'assistant', response_text, model_name, used_key_id)
        )
        cursor.execute(
            "INSERT INTO analytics_events (event_type, topic, metadata) VALUES (?, ?, ?)",
            ('question_asked', 'General Q&A', json.dumps({"model": model_name, "has_rag": has_rag}))
        )
        conn.commit()
        conn.close()

        # 8. Citations
        citations = []
        for doc in active_rag_docs:
            citations.append({
                "source_name": doc['metadata'].get('source_name'),
                "source_type": doc['metadata'].get('source_type'),
                "similarity": doc['similarity']
            })

        return {
            "success": True,
            "response": response_text,
            "model_used": model_name,
            "key_used": used_key_masked,
            "citations": citations,
            "todo_detected": todo_detected
        }

    def stream_message(self, session_id: str, user_message: str, model_override: str = None):
        """
        Generator that yields SSE chunks as the model streams tokens.
        Yields dicts: {type: 'token', text: '...'} or {type: 'done', ...meta} or {type: 'error', error: '...'}
        """
        import json

        # RAG
        rag_results = self.rag_pipeline.search_similarity(user_message, top_k=3)
        active_rag_docs = [r for r in rag_results if r['similarity'] > 0.45]
        has_rag = len(active_rag_docs) > 0

        # Model
        model_name = model_override or classify_query(user_message, has_rag_docs=has_rag)

        # History
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT role, content FROM messages WHERE session_id = ? ORDER BY timestamp DESC LIMIT 10",
            (session_id,)
        )
        history = list(reversed(cursor.fetchall()))
        conn.close()

        # System prompt
        system_instruction = (
            "You are DevHunt AI, a smart personal assistant that helps with problem solving, debugging, learning, and answering questions on any topic.\n"
            "You provide clear, structured, and example-rich answers. Always use clear headings, "
            "bullet points, and code blocks where appropriate.\n"
        )
        if self._get_english_mode():
            system_instruction += (
                "\n[Grammar Correction ENABLED] Start with a grammar tip blockquote if the user made mistakes, "
                "then answer normally.\n"
            )
        if active_rag_docs:
            system_instruction += "\n[Knowledge Base Context]\n"
            for doc in active_rag_docs:
                system_instruction += f"--- {doc['metadata'].get('source_name')} ---\n{doc['content']}\n\n"

        # Get key
        api_key, key_id = self.key_manager.get_active_key_string()
        if not api_key:
            yield {"type": "error", "error": "No active API key. Add a Gemini key in Settings."}
            return

        all_keys = self.key_manager.get_keys_list()
        used_key_masked = next((k['masked_key'] for k in all_keys if k['id'] == key_id), "None")

        try:
            client = genai.Client(api_key=api_key)

            contents = []
            for msg in history:
                role = "user" if msg['role'] == "user" else "model"
                contents.append(types.Content(role=role, parts=[types.Part(text=msg['content'])]))
            contents.append(types.Content(role="user", parts=[types.Part(text=user_message)]))

            full_response = ""
            for chunk in client.models.generate_content_stream(
                model=model_name,
                contents=contents,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=0.3,
                )
            ):
                if chunk.text:
                    full_response += chunk.text
                    yield {"type": "token", "text": chunk.text}

            self.key_manager.on_success(key_id)

            # Save to DB
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO messages (session_id, role, content, model_used, key_used) VALUES (?, ?, ?, ?, ?)",
                (session_id, 'user', user_message, model_name, key_id)
            )
            cursor.execute(
                "INSERT INTO messages (session_id, role, content, model_used, key_used) VALUES (?, ?, ?, ?, ?)",
                (session_id, 'assistant', full_response, model_name, key_id)
            )
            cursor.execute(
                "INSERT INTO analytics_events (event_type, topic, metadata) VALUES (?, ?, ?)",
                ('question_asked', 'General Q&A', json.dumps({"model": model_name, "has_rag": has_rag}))
            )
            conn.commit()
            conn.close()

            # Citations
            citations = [
                {"source_name": d['metadata'].get('source_name'), "source_type": d['metadata'].get('source_type'), "similarity": d['similarity']}
                for d in active_rag_docs
            ]

            yield {"type": "done", "model_used": model_name, "key_used": used_key_masked, "citations": citations}

        except Exception as e:
            err_str = str(e)
            if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str:
                self.key_manager.on_rate_limit_error(key_id)
            else:
                self.key_manager.on_other_error(key_id)
            yield {"type": "error", "error": f"API Error: {err_str[:200]}"}

    def get_history(self, session_id: str) -> list:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, role, content, model_used, key_used, timestamp FROM messages WHERE session_id = ? ORDER BY timestamp ASC",
            (session_id,)
        )
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def clear_history(self, session_id: str) -> bool:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM messages WHERE session_id = ?", (session_id,))
        conn.commit()
        conn.close()
        return True
