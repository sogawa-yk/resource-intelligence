"""ストレージ抽象インターフェース。"""

from abc import ABC, abstractmethod
from datetime import date
from typing import Any


class StorageBase(ABC):
    """ストレージの抽象基底クラス。"""

    @abstractmethod
    def save_artifact(self, artifact_type: str, artifact: dict[str, Any]) -> None:
        """アーティファクトを保存する。"""

    @abstractmethod
    def load_artifact(self, artifact_type: str, target_date: date) -> dict[str, Any] | None:
        """指定日のアーティファクトを読み込む。"""
