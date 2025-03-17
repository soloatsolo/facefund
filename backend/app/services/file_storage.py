import os
import shutil
from datetime import datetime
from werkzeug.utils import secure_filename
import hashlib
from typing import Optional, Tuple

class SecureFileStorage:
    def __init__(self, base_path: str, allowed_extensions: set):
        self.base_path = base_path
        self.allowed_extensions = allowed_extensions
        self._ensure_directories()

    def _ensure_directories(self):
        """Ensure the base directory exists"""
        os.makedirs(self.base_path, exist_ok=True)

    def _allowed_file(self, filename: str) -> bool:
        """Check if the file extension is allowed"""
        return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in self.allowed_extensions

    def _generate_secure_filename(self, original_filename: str) -> str:
        """Generate a secure filename with timestamp and hash"""
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        filename = secure_filename(original_filename)
        name, ext = os.path.splitext(filename)
        
        # Create a hash of the original filename and timestamp
        hash_input = f"{original_filename}{timestamp}".encode('utf-8')
        file_hash = hashlib.sha256(hash_input).hexdigest()[:8]
        
        return f"{name}_{timestamp}_{file_hash}{ext}"

    def save_file(self, file, original_filename: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Save a file securely
        Returns: (filename, filepath) or (None, None) if failed
        """
        if not self._allowed_file(original_filename):
            return None, None
        
        filename = self._generate_secure_filename(original_filename)
        filepath = os.path.join(self.base_path, filename)
        
        try:
            file.save(filepath)
            return filename, filepath
        except Exception as e:
            print(f"Error saving file: {str(e)}")
            return None, None

    def delete_file(self, filename: str) -> bool:
        """Delete a file from storage"""
        filepath = self.get_file_path(filename)
        if not filepath or not os.path.exists(filepath):
            return False
        
        try:
            os.remove(filepath)
            return True
        except Exception as e:
            print(f"Error deleting file: {str(e)}")
            return False

    def get_file_path(self, filename: str) -> Optional[str]:
        """Get the full path of a file if it exists"""
        if not filename:
            return None
        
        filepath = os.path.join(self.base_path, filename)
        return filepath if os.path.exists(filepath) else None

    def move_file(self, src_filename: str, dest_dir: str) -> Optional[str]:
        """
        Move a file to a different directory
        Returns: New filepath if successful, None otherwise
        """
        src_path = self.get_file_path(src_filename)
        if not src_path:
            return None
        
        try:
            os.makedirs(dest_dir, exist_ok=True)
            dest_path = os.path.join(dest_dir, src_filename)
            shutil.move(src_path, dest_path)
            return dest_path
        except Exception as e:
            print(f"Error moving file: {str(e)}")
            return None