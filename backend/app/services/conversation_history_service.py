import os
from datetime import datetime
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class ConversationHistoryService:
    """Service to save conversation history to a text file."""
    
    def __init__(self, data_dir: str = None):
        # Use absolute path based on this file's location
        if data_dir is None:
            base_dir = Path(__file__).parent.parent.parent  # Go up to backend/
            data_dir = base_dir / "data"
        else:
            data_dir = Path(data_dir)
        
        self.data_dir = data_dir
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.history_file = self.data_dir / "history.txt"
        self.last_modified = None
        self._check_file_modified()
    
    def _check_file_modified(self) -> bool:
        """Check if history file has been modified since last check."""
        if not self.history_file.exists():
            self.last_modified = None
            return False
        
        current_mtime = os.path.getmtime(self.history_file)
        if self.last_modified is None or current_mtime > self.last_modified:
            old_mtime = self.last_modified
            self.last_modified = current_mtime
            return old_mtime is not None  # Return True only if this is an actual update
        return False
    
    def has_file_been_updated(self) -> bool:
        """Check if the history file has been updated since last check."""
        return self._check_file_modified()
    
    def save_conversation(self, user_message: str, assistant_response: str, model: str):
        """
        Save a conversation exchange to the history file.
        
        Content is sanitized to ensure file format integrity while preserving
        the original message content including emojis and special characters.
        """
        try:
            timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
            
            # Sanitize inputs: preserve content but ensure no corruption of file format
            # Remove or escape any separator patterns that could break parsing
            separator = '=' * 80
            user_message_safe = user_message.replace(separator, '-' * 80)
            assistant_response_safe = assistant_response.replace(separator, '-' * 80)
            model_safe = model.replace('\n', ' ').replace('\r', ' ')
            
            # Format the conversation entry
            entry = f"""
{separator}
Timestamp: {timestamp}
Model: {model_safe}

[User]:
{user_message_safe}

[Isabella]:
{assistant_response_safe}
{separator}

"""
            
            # Append to history file
            with open(self.history_file, 'a', encoding='utf-8') as f:
                f.write(entry)
            
            # Update last modified time
            self._check_file_modified()
            
            logger.info(f"Conversation saved to history.txt (model: {model})")
            
        except Exception as e:
            logger.error(f"Failed to save conversation to history: {str(e)}")
    
    def get_history_file_path(self) -> Path:
        """Get the path to the history file."""
        return self.history_file


# Global instance
conversation_history_service = ConversationHistoryService()
