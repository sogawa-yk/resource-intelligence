"""ローカルJSONファイルストレージ実装。"""

import json
from datetime import date
from pathlib import Path
from typing import Any

from ri_agent.storage.base import StorageBase


class LocalJsonStorage(StorageBase):
    """ローカルJSONファイルでアーティファクトを保存する。

    パス: {base_dir}/{artifact_type}/{YYYY-MM-DD}.json
    同日の重複実行は上書きする。
    """

    def __init__(self, base_dir: str = "/data/history") -> None:
        self.base_dir = Path(base_dir)

    def save_artifact(self, artifact_type: str, artifact: dict[str, Any]) -> None:
        dir_path = self.base_dir / artifact_type
        dir_path.mkdir(parents=True, exist_ok=True)

        today = date.today().isoformat()
        file_path = dir_path / f"{today}.json"
        file_path.write_text(json.dumps(artifact, ensure_ascii=False, default=str, indent=2))

    def load_artifact(self, artifact_type: str, target_date: date) -> dict[str, Any] | None:
        file_path = self.base_dir / artifact_type / f"{target_date.isoformat()}.json"
        if not file_path.exists():
            return None
        return json.loads(file_path.read_text())
