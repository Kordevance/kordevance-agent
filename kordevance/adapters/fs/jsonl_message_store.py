import asyncio
import json
from datetime import UTC, datetime
from pathlib import Path
from uuid import UUID

from kordevance.domain.ports.message_store import MessageStore
from kordevance.domain.ports.profile_workspace import ProfileWorkspace


class JsonlMessageStore(MessageStore):
    def __init__(self, workspace: ProfileWorkspace) -> None:
        self._workspace: ProfileWorkspace = workspace

    async def _conversation_file(self, profile_id: UUID, conversation_id: UUID) -> Path:
        profile_dir = await self._workspace.load_profile(profile_id)
        conversations_dir = profile_dir.joinpath("conversations")
        conversations_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
        return conversations_dir.joinpath(f"{conversation_id}.jsonl")

    async def append(
        self, profile_id: UUID, conversation_id: UUID, message_json: str, timestamp: datetime
    ) -> None:
        path = await self._conversation_file(profile_id, conversation_id)
        await asyncio.to_thread(self._append_line, path, message_json, timestamp)

    @staticmethod
    def _append_line(path: Path, message_json: str, timestamp: datetime) -> None:
        record = {
            "timestamp": timestamp.astimezone(UTC).isoformat(),
            "message": message_json.replace("\n", " ").strip(),
        }
        with path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")

    async def load_history(self, profile_id: UUID, conversation_id: UUID) -> list[tuple[str, datetime]]:
        path = await self._conversation_file(profile_id, conversation_id)
        if not path.exists():
            return []
        return await asyncio.to_thread(self._read_lines, path)

    @staticmethod
    def _read_lines(path: Path) -> list[tuple[str, datetime]]:
        records: list[tuple[str, datetime]] = []
        with path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                record = json.loads(line)
                records.append((record["message"], datetime.fromisoformat(record["timestamp"])))
        return records

    async def list_conversations(self, profile_id: UUID) -> list[UUID]:
        profile_dir = await self._workspace.load_profile(profile_id)
        conversations_dir = profile_dir.joinpath("conversations")
        if not conversations_dir.exists():
            return []
        return await asyncio.to_thread(self._list_conversation_ids, conversations_dir)

    @staticmethod
    def _list_conversation_ids(conversations_dir: Path) -> list[UUID]:
        conversation_ids = []
        for path in conversations_dir.glob("*.jsonl"):
            try:
                conversation_ids.append(UUID(path.stem))
            except ValueError:
                continue
        return conversation_ids
