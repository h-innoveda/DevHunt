import os
import subprocess
from core import logger

class UpdateManager:
    @staticmethod
    def _run_git(args, timeout=15):
        """Helper to run a git command and return stdout. Raises exceptions on failure."""
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) # Local-AI/backend
        proj_dir = os.path.dirname(base_dir) # Local-AI
        
        # Ensure we run from the project root directory where .git lives
        try:
            res = subprocess.run(
                ["git"] + args,
                cwd=proj_dir,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            if res.returncode != 0:
                raise Exception(res.stderr.strip() or res.stdout.strip() or f"Exit code {res.returncode}")
            return res.stdout.strip()
        except FileNotFoundError:
            raise Exception("Git command not found on system path. Please install Git.")
        except subprocess.TimeoutExpired:
            raise Exception("Git command timed out.")

    @classmethod
    def check_for_updates(cls):
        """
        Checks if the local repository is behind its remote tracking branch.
        Returns:
            dict containing success status, update_available (bool), and list of new commits.
        """
        try:
            # 1. Verify it is a git repo
            cls._run_git(["rev-parse", "--is-inside-work-tree"])
            
            # 2. Get current branch and tracking branch
            current_branch = cls._run_git(["rev-parse", "--abbrev-ref", "HEAD"])
            
            # 3. Try to fetch from remote
            try:
                # Limit fetch to avoid long delays
                cls._run_git(["fetch", "origin"], timeout=10)
            except Exception as e:
                logger.warn("updates", f"Failed to fetch from remote: {e}")
                # We can continue and compare with whatever we have cached locally

            # 4. Resolve upstream tracking branch
            tracking_branch = None
            try:
                tracking_branch = cls._run_git(["rev-parse", "--abbrev-ref", "@{u}"])
            except Exception:
                # No upstream configured for current branch, look for origin/main or origin/master
                for fallback in ["origin/main", "origin/master"]:
                    try:
                        cls._run_git(["rev-parse", fallback])
                        tracking_branch = fallback
                        break
                    except Exception:
                        continue
            
            if not tracking_branch:
                return {
                    "success": False,
                    "error": "No remote tracking branch or origin fallback branch found to compare against."
                }
            
            # 5. Get local and remote commit hashes
            local_commit = cls._run_git(["rev-parse", "HEAD"])
            remote_commit = cls._run_git(["rev-parse", tracking_branch])
            
            # 6. Check if they are identical
            if local_commit == remote_commit:
                return {
                    "success": True,
                    "update_available": False,
                    "current_commit": local_commit[:7],
                    "latest_commit": remote_commit[:7],
                    "current_branch": current_branch,
                    "tracking_branch": tracking_branch,
                    "commits": []
                }
                
            # 7. Get commits that exist in remote but not locally
            commits_raw = cls._run_git(["log", f"HEAD..{tracking_branch}", "--pretty=format:%h|%an|%s"])
            commits = []
            
            if commits_raw:
                for line in commits_raw.split("\n"):
                    line = line.strip()
                    if not line:
                        continue
                    parts = line.split("|", 2)
                    if len(parts) == 3:
                        commits.append({
                            "hash": parts[0],
                            "author": parts[1],
                            "message": parts[2]
                        })
            
            # If commits is empty but hashes differ, we are either ahead or diverged.
            # We only prompt for updates if remote has commits we don't have.
            update_available = len(commits) > 0
            
            return {
                "success": True,
                "update_available": update_available,
                "current_commit": local_commit[:7],
                "latest_commit": remote_commit[:7],
                "current_branch": current_branch,
                "tracking_branch": tracking_branch,
                "commits": commits
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    @classmethod
    def apply_update(cls):
        """
        Applies the update by pulling the remote changes.
        Preserves local modifications to tracked files via git stash.
        Returns:
            dict containing success status and conflict flag.
        """
        try:
            # 1. Check if git repo
            cls._run_git(["rev-parse", "--is-inside-work-tree"])
            
            # 2. Check for local modifications to tracked files
            status = cls._run_git(["status", "--porcelain"])
            
            # We filter for files that are modified/added/deleted in tracking (i.e. not untracked files)
            # Untracked files start with '??'
            has_modifications = False
            if status:
                for line in status.split("\n"):
                    if line.strip() and not line.startswith("??"):
                        has_modifications = True
                        break
            
            # 3. Stash changes if modifications exist
            stashed = False
            if has_modifications:
                logger.info("updates", "Local modifications detected. Stashing changes before update...")
                cls._run_git(["stash", "save", "DevHunt Auto-Update Stash"])
                stashed = True
                
            # 4. Pull updates
            logger.info("updates", "Pulling updates from remote...")
            pull_error = None
            try:
                # Try pull
                cls._run_git(["pull"])
            except Exception as e:
                pull_error = str(e)
                # Fallback to origin/main if simple pull fails
                try:
                    current_branch = cls._run_git(["rev-parse", "--abbrev-ref", "HEAD"])
                    cls._run_git(["pull", "origin", current_branch])
                    pull_error = None
                except Exception as e2:
                    pull_error = f"Pull failed: {e}. Fallback pull failed: {e2}"
                    
            if pull_error:
                # If pull failed, restore stash if we created one
                if stashed:
                    try:
                        cls._run_git(["stash", "pop"])
                    except Exception:
                        pass
                raise Exception(pull_error)
                
            # 5. Restore stash if we stashed
            conflict = False
            if stashed:
                logger.info("updates", "Restoring local modifications from stash...")
                try:
                    cls._run_git(["stash", "pop"])
                except Exception as e:
                    logger.warn("updates", f"Conflict occurred during stash pop: {e}")
                    conflict = True
                    
            logger.success("updates", "System updated successfully.")
            return {
                "success": True,
                "conflict": conflict
            }
            
        except Exception as e:
            logger.error("updates", f"Failed to apply update: {e}")
            return {
                "success": False,
                "error": str(e)
            }
