# research.md — 実装調査まとめ

設計資料をもとに、実装に必要な情報を整理したドキュメント。

---

## 1. アプリケーション設計

### 1.1 アーキテクチャ決定

| 設計観点 | 採用方針 |
|----------|----------|
| コンポーネント組織 | UI・API・データ層の3層分離 (UI-focused) |
| ペルソナ管理 | 独立した `PersonaManager` コンポーネント |
| ディスカッションフロー | 単一 `DiscussionEngine` による逐次実行 |
| ストリーミング | 各コンポーネントにビルトイン（専用コンポーネントなし） |
| サービス層 | ドメインサービス3本 (`PersonaService`, `DiscussionService`, `ExportService`) |
| Claude API統合 | `DiscussionEngine` 内で直接統合 |
| 設定管理 | グローバル `ConfigurationManager`（全コンポーネントから参照） |
| ファイル永続化 | 集中型 `FileManager`（全I/Oを一元管理） |

### 1.2 コンポーネント構成

```
UI Layer
  StreamlitUI       — メインUI調整、ページレンダリング
  PersonaUI         — ペルソナ管理専用UI

Service Layer
  PersonaService    — ペルソナのライフサイクル管理
  DiscussionService — ディスカッションワークフロー管理
  ExportService     — エクスポート・議事録生成

Component Layer
  DiscussionEngine  — Claude API直接統合・会話ロジック
  PersonaManager    — ペルソナCRUD・バリデーション
  FileManager       — 全ファイルI/O

Config Layer
  ConfigurationManager — 設定読込・APIキー管理
```

### 1.3 ユニット分割

| ユニット | 担当ストーリー数 | 主要コンポーネント |
|----------|-----------------|------------------|
| Unit 1: Core Application | 11/12 | StreamlitUI, PersonaService, DiscussionService, FileManager, ConfigurationManager |
| Unit 2: AI Integration Service | 1 (US-6.1) + 補助機能 | DiscussionEngine, Claude API client |
| Unit 3: Export Service | 補助機能 | ExportService, フォーマッタ |

### 1.4 ユニット間依存関係

```
Core Application ──→ AI Integration Service   (APIコール・ストリーミング受信)
Core Application ──→ Export Service           (エクスポート要求)
AI Integration Service ──→ Core Application  (コールバック・ストリーム返却)
Export Service ──→ Core Application          (ディスカッションデータ参照)
```

### 1.5 開発フェーズ順序

1. Core Application基盤 (US-1.1, US-2.1, US-2.4, US-2.5)
2. ペルソナ管理 (US-2.2, US-2.3)
3. AI統合サービス (US-6.1, レスポンス生成)
4. ディスカッション実行 (US-3.1, US-3.2, US-3.3)
5. 永続化・履歴 (US-4.2, US-5.1, US-5.2)
6. エクスポートサービス (US-4.1)

---

## 2. 機能設計

### 2.1 ドメインエンティティ

#### Persona
```python
@dataclass
class Persona:
    id: str           # ユニークスラッグ
    name: str         # 最大100文字
    description: str  # 最大500文字
    type: str         # "predefined" | "custom"
    created_at: datetime
```

#### Message
```python
@dataclass
class Message:
    id: str
    persona_id: str
    persona_name: str   # 非正規化（表示用）
    content: str
    turn_number: int    # 1以上
    timestamp: datetime
```

#### Discussion（メイン集約）
```python
@dataclass
class Discussion:
    id: str                         # UUID
    topic: str                      # 最大500文字
    personas: list[Persona]         # 2〜6名
    messages: list[Message]         # 線形順序
    parameters: DiscussionParameters
    materials_context: str | None   # 前処理済み資料テキスト
    state: str                      # ワークフロー状態
    resume_point: dict | None       # APIエラー時の再開ポイント
    created_at: datetime
    updated_at: datetime
```

#### DiscussionParameters
```python
@dataclass
class DiscussionParameters:
    max_turns: int          # デフォルト3、範囲1〜20
    language: str           # デフォルト"en"
    discussion_style: str   # "formal" | "casual" | "debate"
    extended_turns: int     # デフォルト1、延長ターン数
```

#### DiscussionSummary（履歴一覧用軽量モデル）
```python
@dataclass
class DiscussionSummary:
    id: str
    topic: str
    persona_names: list[str]
    turn_count: int
    state: str
    created_at: datetime
    updated_at: datetime
```

### 2.2 ワークフロー状態機械

```
setup → configuring → executing → completed → exported
                         ↑               |
                         └───────────────┘ (new_discussion)
```

| 状態 | 遷移元 | 遷移条件 |
|------|--------|---------|
| `setup` | 初回起動 | APIキーが有効 |
| `configuring` | `setup` / `exported` | ユーザーがDiscussionページへ遷移 |
| `executing` | `configuring` | ユーザーが開始ボタンを押す |
| `completed` | `executing` | ターン上限到達 or ユーザー停止 |
| `exported` | `completed` | エクスポート完了 |

- 状態は `st.session_state['workflow_state']` に保持
- 不正遷移は `WorkflowStateError` を送出

### 2.3 ビジネスルール

#### トピックバリデーション
| ルール | 制約 | エラーメッセージ |
|--------|------|----------------|
| 必須 | 空不可 | "Discussion topic is required" |
| 長さ | 1〜500文字 | "Topic must be between 1 and 500 characters" |

#### ペルソナ選択
**ハードルール（ブロック）**:
- 2〜6名を選択必須
- 同一ペルソナの重複選択禁止
- 各ペルソナに name・description が必要

**ソフトルール（警告のみ・上書き可）**:
- 全ペルソナが同一専門領域 → 多様性を推奨
- 批判的思考役がいない → バランス改善を提案

#### ターン制限
| 条件 | 動作 |
|------|------|
| `current_turn == max_turns - 1` | 非ブロッキングバナー表示 |
| `current_turn == max_turns` | モーダル表示「続けるか終了するか」 |
| 「続ける」 | `max_turns += extended_turns` |
| 「終了」 | `completed` 状態へ遷移 |

#### ファイル操作
| 対象 | ルール |
|------|--------|
| ディスカッション保存 | エージェント発言完了ごとにオートセーブ |
| ファイル名 | `{discussion_id}.json` (UUID) |
| エラー時 | ログ記録・非ブロッキング警告・処理継続 |
| カスタムペルソナ | `{slug}.json`、重複時は `{slug}-2` |
| 資料ファイル | `.txt/.md/.pdf/.docx`、最大10MB |

#### エクスポートルール
- `state == 'completed'` または `'exported'` 時のみ実行可能
- 最低1メッセージが必要
- ファイル名: `{topic_slug}_{date}.md`

### 2.4 ディスカッション実行ループ

```
For turn in 1..max_turns:
  For persona in selected_personas:
    1. プロンプト構築（トピック + 資料コンテキスト + 会話履歴 + ペルソナ指示）
    2. AI Integration Service に非同期リクエスト
    3. ストリーミングレスポンスを受信・UI表示
    4. message を discussion.messages に追記
    5. ディスカッション状態をオートセーブ
  ターン上限チェック（ソフトリミット）
```

### 2.5 資料処理フロー（AI前処理）

```
ファイルアップロード
  → ファイルタイプ検出 (.txt/.md/.pdf/.docx)
  → rawテキスト抽出
  → AI前処理（要約・主要トピック抽出・コンテキスト整形）
  → session_state に保存
  → プロンプトにコンテキストとして注入
```

前処理出力構造:
```python
{
    "original_filename": str,
    "raw_text": str,
    "summary": str,
    "key_topics": list[str],
    "context_for_discussion": str
}
```

### 2.6 UIページ構成（Streamlit Multi-page）

| ページ | ファイル | 役割 |
|--------|---------|------|
| 1_Setup | `pages/1_Setup.py` | APIキー確認・初期設定 |
| 2_Discussion | `pages/2_Discussion.py` | トピック入力・ペルソナ選択・実行 |
| 3_Results | `pages/3_Results.py` | 結果表示・エクスポート |
| 4_History | `pages/4_History.py` | 過去ディスカッション一覧・読込 |

---

## 3. 非機能要件設計

### 3.1 パフォーマンス

| 要件 | 仕様 |
|------|------|
| ストリーミング応答 | APIが返すそのままの速度でUI表示（遅延付加なし） |
| UI応答性 | ストリーミング中はスクロール可、Start/Exportボタンは無効化 |

### 3.2 信頼性

#### APIエラー時の挙動
1. APIエラー発生
2. `ResumeManager.set_resume_point(turn, persona_index, error)` で再開ポイント保存
3. `FileManager.save_discussion()` で強制セーブ（`resume_point` フィールド含む）
4. UI にエラーメッセージと「Resume Discussion」ボタンを表示

#### 再開フロー
```
ユーザーが「Resume」をクリック
  → DiscussionService.resume_discussion()
  → ResumeManager.get_resume_point()
  → 完了済みメッセージをスキップ
  → チェックポイントから再試行
  → 成功時: ResumeManager.clear_resume_point()
  → FileManager.save_discussion() (resume_point = None)
```

#### APIキー検証
- 起動時に `client.models.list()` で軽量検証
- 無効時: Setupページにエラー表示・Discussionページへの遷移をブロック
- 検証結果を `st.session_state['api_key_valid']` に保持

### 3.3 セキュリティ

| 要件 | 仕様 |
|------|------|
| APIキー保管 | `config.yaml` の `anthropic.api_key` キーのみ（環境変数フォールバックなし） |
| .gitignore | 起動時に自動生成・`config.yaml` を追記 |
| 入力バリデーション | 全ユーザー入力を `business-rules.md` に従って検証 |
| API通信 | 公式 `anthropic` Python SDK経由（HTTPS強制） |

### 3.4 ロギング

| 項目 | 設定 |
|------|------|
| ハンドラ | `RotatingFileHandler` |
| ファイル | `logs/agent_discussion.log` |
| ローテーション | 最大1MB × 3バックアップ |
| ログレベル | ERROR（障害）/ WARNING（設定異常）/ INFO（状態遷移）/ DEBUG（APIデータ、デフォルトOFF） |

### 3.5 論理コンポーネント（NFR追加分）

#### ApiValidator（新規）
```python
class ApiValidator:
    def validate(self, api_key: str) -> ApiValidationResult: ...

@dataclass
class ApiValidationResult:
    valid: bool
    error_type: str | None   # "auth" | "connection" | None
    error_message: str | None
```

#### ResumeManager（新規）
```python
class ResumeManager:
    def set_resume_point(self, turn: int, persona_index: int, error: str) -> None: ...
    def clear_resume_point(self) -> None: ...
    def has_resume_point(self) -> bool: ...
    def get_resume_point(self) -> dict | None: ...
```
保存先: `st.session_state['resume_point']` + ディスカッションJSON

#### LoggingConfig（新規）
```python
def setup_logging(level: str = "INFO") -> None: ...
```
`main.py` の最初に1回だけ呼び出す。

### 3.6 起動シーケンス

```
main.py
  → setup_logging()                    [LoggingConfig]
  → ensure_gitignore()                 [ConfigurationManager]
  → load_config()                      [ConfigurationManager]
  → validate_api_key_with_api()        [ConfigurationManager → ApiValidator]
  → render Setup page (valid/invalid)  [StreamlitUI]
```

---

## 4. データ永続化構造

```
data/
  discussions/
    {uuid}.json                # Discussion全体（resume_point含む）
  personas/
    predefined.json            # 組み込みペルソナリスト
    custom/
      {slug}.json              # カスタムペルソナ個別ファイル

exports/
  {topic_slug}_{date}.md       # エクスポートされた議事録

logs/
  agent_discussion.log         # ローテーティングログ

config.yaml                    # APIキー・設定（gitignore対象）
```

---

## 5. スコープ外（実装しない機能）

- マルチユーザー・認証
- クラウドデプロイ・データベース
- 複数ユーザーのリアルタイムコラボレーション
- 高度な分析・インサイト
- 外部ツール統合
- モバイルアプリ・音声・動画
- エージェントのクロスディスカッション学習・記憶
