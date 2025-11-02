from __future__ import annotations

from typing import Optional
from typing_extensions import override
import asyncpg
from google.adk.artifacts import BaseArtifactService
import logging
from typing import Optional
from google.genai import types


logger = logging.getLogger("google_adk." + __name__)

class PostgresArtifactService(BaseArtifactService):
    """A PostgreSQL implementation of the artifact service.
    
    Provides persistent storage for artifacts using PostgreSQL as the backend.
    """

    def __init__(self, dsn: str):
        """Initialize the PostgreSQL artifact service.
        
        Args:
            dsn: PostgreSQL connection string (Data Source Name).
        """
        self.dsn = dsn
        self._pool: Optional[asyncpg.Pool] = None

    async def _get_pool(self) -> asyncpg.Pool:
        """Lazy initialization of the connection pool."""
        if self._pool is None:
            self._pool = await asyncpg.create_pool(dsn=self.dsn)
        return self._pool

    def _file_has_user_namespace(self, filename: str) -> bool:
        """Checks if the filename has a user namespace.

        Args:
            filename: The filename to check.

        Returns:
            True if the filename has a user namespace (starts with "user:"),
            False otherwise.
        """
        return filename.startswith("user:")

    def _artifact_path(
        self, app_name: str, user_id: str, session_id: str, filename: str
    ) -> str:
        """Constructs the artifact path.

        Args:
            app_name: The name of the application.
            user_id: The ID of the user.
            session_id: The ID of the session.
            filename: The name of the artifact file.

        Returns:
            The constructed artifact path.
        """
        if self._file_has_user_namespace(filename):
            return f"{app_name}/{user_id}/user/{filename}"
        return f"{app_name}/{user_id}/{session_id}/{filename}"

    @override
    async def save_artifact(
        self,
        *,
        app_name: str,
        user_id: str,
        session_id: str,
        filename: str,
        artifact: types.Part,
    ) -> int:
        """Saves an artifact and returns the assigned version number.
        
        Args:
            app_name: The name of the application.
            user_id: The ID of the user.
            session_id: The ID of the session.
            filename: The name of the artifact file.
            artifact: The artifact data as a Part object.
            
        Returns:
            The version number assigned to the saved artifact.
        """
        path = self._artifact_path(app_name, user_id, session_id, filename)
        
        pool = await self._get_pool()
        async with pool.acquire() as conn:
            async with conn.transaction():
                # Get the next version number (count of existing versions)
                version = await conn.fetchval(
                    """
                    SELECT COUNT(*) 
                    FROM artifacts_table
                    WHERE path = $1
                    """,
                    path
                )
                
                # Insert the new artifact data
                await conn.execute(
                    """
                    INSERT INTO artifacts_table (path, version, mime_type, data)
                    VALUES ($1, $2, $3, $4)
                    """,
                    path,
                    version,
                    artifact.inline_data.mime_type,
                    artifact.inline_data.data
                )
                
        return version

    @override
    async def load_artifact(
        self,
        *,
        app_name: str,
        user_id: str,
        session_id: str,
        filename: str,
        version: Optional[int] = None,
    ) -> Optional[types.Part]:
        """Loads an artifact. Returns None if not found.
        
        Args:
            app_name: The name of the application.
            user_id: The ID of the user.
            session_id: The ID of the session.
            filename: The name of the artifact file.
            version: The version to load. If None, loads the latest version.
            
        Returns:
            The artifact as a Part object, or None if not found.
        """
        path = self._artifact_path(app_name, user_id, session_id, filename)
        
        pool = await self._get_pool()
        async with pool.acquire() as conn:
            if version is None:
                # Load latest version (highest version number)
                record = await conn.fetchrow(
                    """
                    SELECT data, mime_type 
                    FROM artifacts_table 
                    WHERE path = $1
                    ORDER BY version DESC
                    LIMIT 1
                    """,
                    path
                )
            else:
                # Load specific version
                record = await conn.fetchrow(
                    """
                    SELECT data, mime_type 
                    FROM artifacts_table 
                    WHERE path = $1 AND version = $2
                    """,
                    path, version
                )

        if record:
            return types.Part.from_bytes(
                data=record['data'], 
                mime_type=record['mime_type']
            )
        return None

    @override
    async def list_artifact_keys(
        self, *, app_name: str, user_id: str, session_id: str
    ) -> list[str]:
        """Lists all artifact filenames within a session.
        
        Includes both session-scoped and user-scoped artifacts.
        
        Args:
            app_name: The name of the application.
            user_id: The ID of the user.
            session_id: The ID of the session.
            
        Returns:
            A sorted list of artifact filenames.
        """
        session_prefix = f"{app_name}/{user_id}/{session_id}/"
        usernamespace_prefix = f"{app_name}/{user_id}/user/"
        
        pool = await self._get_pool()
        async with pool.acquire() as conn:
            records = await conn.fetch(
                """
                SELECT DISTINCT path
                FROM artifacts_table
                WHERE path LIKE $1 OR path LIKE $2
                """,
                f"{session_prefix}%",
                f"{usernamespace_prefix}%"
            )
        
        filenames = []
        for record in records:
            path = record['path']
            if path.startswith(session_prefix):
                filename = path.removeprefix(session_prefix)
                filenames.append(filename)
            elif path.startswith(usernamespace_prefix):
                filename = path.removeprefix(usernamespace_prefix)
                filenames.append(filename)
        
        return sorted(filenames)

    @override
    async def delete_artifact(
        self, *, app_name: str, user_id: str, session_id: str, filename: str
    ) -> None:
        """Deletes all versions of an artifact.
        
        Args:
            app_name: The name of the application.
            user_id: The ID of the user.
            session_id: The ID of the session.
            filename: The name of the artifact file to delete.
        """
        path = self._artifact_path(app_name, user_id, session_id, filename)
        
        pool = await self._get_pool()
        async with pool.acquire() as conn:
            await conn.execute(
                """
                DELETE FROM artifacts_table
                WHERE path = $1
                """,
                path
            )

    @override
    async def list_versions(
        self, *, app_name: str, user_id: str, session_id: str, filename: str
    ) -> list[int]:
        """Lists all available versions for a specific artifact.
        
        Args:
            app_name: The name of the application.
            user_id: The ID of the user.
            session_id: The ID of the session.
            filename: The name of the artifact file.
            
        Returns:
            A list of version numbers in ascending order.
        """
        path = self._artifact_path(app_name, user_id, session_id, filename)
        
        pool = await self._get_pool()
        async with pool.acquire() as conn:
            records = await conn.fetch(
                """
                SELECT version
                FROM artifacts_table
                WHERE path = $1
                ORDER BY version
                """,
                path
            )
        
        return [record['version'] for record in records]

    async def close(self):
        """Close the connection pool."""
        if self._pool:
            await self._pool.close()
            self._pool = None