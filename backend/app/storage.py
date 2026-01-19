"""Supabase Storage client for study guide file storage."""
from typing import Optional
from supabase import create_client, Client
from .config import settings


class StorageManager:
    """Manages file storage in Supabase Storage."""

    def __init__(self):
        self._client: Optional[Client] = None

    @property
    def client(self) -> Client:
        """Lazy initialization of Supabase client."""
        if self._client is None:
            self._client = create_client(settings.supabase_url, settings.supabase_service_key)
        return self._client

    @property
    def bucket(self) -> str:
        return settings.supabase_bucket

    def upload_file(self, user_id: int, filename: str, content: bytes) -> str:
        """
        Upload a file to Supabase Storage.

        Args:
            user_id: The user's ID
            filename: Original filename
            content: File content as bytes

        Returns:
            The storage path of the uploaded file
        """
        # Create a unique path for the user's file
        storage_path = f"{user_id}/{filename}"

        # Delete existing file if it exists
        try:
            self.client.storage.from_(self.bucket).remove([storage_path])
        except Exception:
            pass  # File doesn't exist, that's fine

        # Upload the new file
        self.client.storage.from_(self.bucket).upload(
            path=storage_path,
            file=content,
            file_options={"content-type": "text/plain", "upsert": "true"}
        )

        return storage_path

    def download_file(self, user_id: int, filename: str) -> bytes:
        """
        Download a file from Supabase Storage.

        Args:
            user_id: The user's ID
            filename: The filename to download

        Returns:
            File content as bytes
        """
        storage_path = f"{user_id}/{filename}"
        response = self.client.storage.from_(self.bucket).download(storage_path)
        return response

    def get_file_info(self, user_id: int) -> dict | None:
        """
        Get information about a user's study guide file.

        Args:
            user_id: The user's ID

        Returns:
            Dict with filename, file_size, word_count or None if no file exists
        """
        try:
            # List files in the user's directory
            files = self.client.storage.from_(self.bucket).list(path=str(user_id))

            if not files:
                return None

            # Get the first .txt file
            txt_files = [f for f in files if f['name'].endswith('.txt')]
            if not txt_files:
                return None

            file_info = txt_files[0]
            filename = file_info['name']

            # Download to get word count
            content = self.download_file(user_id, filename)
            text_content = content.decode('utf-8')
            word_count = len(text_content.split())

            return {
                "filename": filename,
                "file_size": len(content),
                "word_count": word_count
            }
        except Exception:
            return None

    def delete_user_files(self, user_id: int) -> None:
        """
        Delete all files for a user.

        Args:
            user_id: The user's ID
        """
        try:
            files = self.client.storage.from_(self.bucket).list(path=str(user_id))
            if files:
                paths = [f"{user_id}/{f['name']}" for f in files]
                self.client.storage.from_(self.bucket).remove(paths)
        except Exception:
            pass


# Create a singleton instance (client is lazily initialized)
storage_manager = StorageManager()
