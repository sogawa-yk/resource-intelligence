"""OCI Generative AI Inference クライアントラッパー。"""

import json
import time

import oci
import structlog
from oci.generative_ai_inference import GenerativeAiInferenceClient
from oci.generative_ai_inference.models import (
    ChatDetails,
    CohereChatRequest,
    GenericChatRequest,
    OnDemandServingMode,
    SystemMessage,
    UserMessage,
)

from ri_agent.config import Settings
from ri_agent.oci_client.base import create_signer

log = structlog.get_logger(__name__)

SYSTEM_PROMPT = """\
あなたはOCI Resource Intelligence Agentです。
ユーザーの自然言語入力を解析し、以下のいずれかのアクションをJSON形式で返してください。

## アクション一覧

### 1. resource_search（リソース検索）
ユーザーがOCIリソースの一覧・検索・表示を要求した場合。
```json
{
  "action": "resource_search",
  "params": {
    "resource_types": ["Instance", "Vcn"],
    "regions": ["ap-tokyo-1"],
    "lifecycle_states": ["RUNNING"],
    "tag_filters": {"project": "alpha"},
    "compartment_ocid": "ocid1.compartment..."
  }
}
```
paramsの各フィールドは省略可能。未指定は全件検索を意味する。

### 2. dependency_map（依存関係マップ）
ユーザーがリソースの依存関係・接続関係・マップを要求した場合。
```json
{
  "action": "dependency_map",
  "params": {
    "root_ocid": "ocid1.instance...",
    "depth": 3
  }
}
```
root_ocidは必須。depthは省略時3。

### 3. help（ヘルプ）
ユーザーが使い方を聞いた場合や、上記に該当しない場合。
```json
{
  "action": "help",
  "message": "ユーザーへの回答メッセージ"
}
```

## ルール
- 必ずJSON形式のみで応答すること（説明文不要）
- OCIDが含まれていればそのまま使用する
- リソースタイプ名はOCI標準名（Instance, Vcn, Subnet, LoadBalancer, DbSystem, Cluster等）を使用する
- リージョン名はOCI識別子（ap-tokyo-1, us-ashburn-1等）を使用する
- 「全リソース」「一覧」等の曖昧な指示はresource_searchでparams空で返す
"""


class GenAIClient:
    """OCI GenAI Service を使った自然言語理解クライアント。"""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        oci_config, signer = create_signer()

        if signer:
            self.client = GenerativeAiInferenceClient(
                config={},
                signer=signer,
                service_endpoint=settings.genai_endpoint,
            )
        else:
            self.client = GenerativeAiInferenceClient(
                config=oci_config,
                service_endpoint=settings.genai_endpoint,
            )

        self._is_cohere = settings.genai_model_id.startswith("cohere.")

    def parse_user_intent(self, user_input: str) -> dict:
        """ユーザー入力をGenAIで解析し、アクションとパラメータを返す。"""
        start = time.monotonic()

        if self._is_cohere:
            chat_request = CohereChatRequest(
                api_format="COHERE",
                message=user_input,
                preamble_override=SYSTEM_PROMPT,
                max_tokens=500,
                temperature=0.1,
                is_stream=False,
            )
        else:
            chat_request = GenericChatRequest(
                api_format="GENERIC",
                messages=[
                    SystemMessage(content=[{"type": "TEXT", "text": SYSTEM_PROMPT}]),
                    UserMessage(content=[{"type": "TEXT", "text": user_input}]),
                ],
                max_tokens=500,
                temperature=0.1,
                is_stream=False,
            )

        response = self.client.chat(
            chat_details=ChatDetails(
                compartment_id=self.settings.oci_compartment_ocid,
                serving_mode=OnDemandServingMode(
                    model_id=self.settings.genai_model_id,
                ),
                chat_request=chat_request,
            )
        )

        elapsed = time.monotonic() - start

        # Cohere と Generic でレスポンス構造が異なる
        if self._is_cohere:
            raw_text = response.data.chat_response.text
        else:
            raw_text = response.data.chat_response.choices[0].message.content[0].text

        log.info("genai_parse_intent", latency_seconds=round(elapsed, 2), raw_response=raw_text[:200])

        return self._extract_json(raw_text)

    @staticmethod
    def _extract_json(text: str) -> dict:
        """レスポンスからJSONを抽出する。"""
        text = text.strip()
        # ```json ... ``` ブロックの抽出
        if "```" in text:
            start = text.find("```")
            end = text.rfind("```")
            if start != end:
                inner = text[start:end]
                inner = inner.lstrip("`").lstrip("json").strip()
                text = inner

        try:
            return json.loads(text)
        except json.JSONDecodeError:
            # JSONっぽい部分を探す
            brace_start = text.find("{")
            brace_end = text.rfind("}")
            if brace_start != -1 and brace_end != -1:
                try:
                    return json.loads(text[brace_start : brace_end + 1])
                except json.JSONDecodeError:
                    pass
            return {"action": "help", "message": "入力を理解できませんでした。もう一度お試しください。"}
