# 詳細設計仕様

アプリケーションの詳細設計をまとめたドキュメント。実装時はこのファイルを参照すること。

---

## 1. コンポーネント責務

| コンポーネント | 責務 |
|--------------|------|
| `StreamlitUI` | メインUI調整・ページレンダリング・ストリーミング表示 |
| `PersonaUI` | ペルソナ選択・カスタムペルソナ作成フォーム |
| `PersonaService` | ペルソナのライフサイクル管理・バリデーション |
| `DiscussionService` | ディスカッションワークフロー管理・APIエラー時の再開制御 |
| `ExportService` | 議事録生成・Markdownフォーマット |
| `DiscussionEngine` | Claude API直接統合・ターン制会話ロジック・ストリーミング |
| `PersonaManager` | ペルソナCRUD・定義済みペルソナ管理 |
| `FileManager` | 全ファイルI/O（ディスカッション保存・資料読込・エクスポート） |
| `ConfigurationManager` | 設定読込・APIキー管理・`.gitignore` 自動生成 |

### NFR追加論理コンポーネント

#### ApiValidator
```python
class ApiValidator:
    def validate(self, api_key: str) -> ApiValidationResult: ...

@dataclass
class ApiValidationResult:
    valid: bool
    error_type: str | None   # "auth" | "connection" | None
    error_message: str | None
```
`client.models.list()` で軽量検証。`ConfigurationManager` が起動時に使用する。

#### ResumeManager
```python
class ResumeManager:
    def set_resume_point(self, turn: int, persona_index: int, error: str) -> None: ...
    def clear_resume_point(self) -> None: ...
    def has_resume_point(self) -> bool: ...
    def get_resume_point(self) -> dict | None: ...
```
保存先: `st.session_state['resume_point']` + ディスカッションJSON両方。

#### LoggingConfig
```python
def setup_logging(level: str = "INFO") -> None: ...
```
`main.py` の最初に1回だけ呼び出す。`RotatingFileHandler`（最大1MB × 3バックアップ）。ログファイル: `logs/agent_discussion.log`。

---

## 2. ドメインモデル

```python
@dataclass
class Persona:
    id: str           # ユニークスラッグ
    name: str         # 最大100文字
    description: str  # 最大500文字
    type: str         # "predefined" | "custom"
    created_at: datetime

@dataclass
class Message:
    id: str
    persona_id: str
    persona_name: str   # 非正規化（表示用）
    content: str
    turn_number: int    # 1以上
    timestamp: datetime

@dataclass
class DiscussionParameters:
    max_turns: int          # デフォルト3、範囲1〜20
    language: str           # デフォルト"en"
    discussion_style: str   # "formal" | "casual" | "debate"
    extended_turns: int     # デフォルト1、延長ターン数

@dataclass
class Discussion:
    id: str                         # UUID
    topic: str                      # 最大500文字
    personas: list[Persona]         # 2〜6名
    messages: list[Message]         # 線形順序
    parameters: DiscussionParameters
    materials_context: str | None   # 前処理済み資料テキスト
    state: str                      # ワークフロー状態
    resume_point: dict | None       # APIエラー時の再開ポイント（通常はNone）
    created_at: datetime
    updated_at: datetime

@dataclass
class DiscussionSummary:            # 履歴一覧用軽量モデル
    id: str
    topic: str
    persona_names: list[str]
    turn_count: int
    state: str
    created_at: datetime
    updated_at: datetime
```

### データ整合性ルール
- `Discussion.personas`: 2〜6件、IDが一意であること
- `Message.turn_number`: 1以上
- `Discussion.topic`: 非空・最大500文字・有効UTF-8
- メッセージ順序: `(turn_number, personas リスト内インデックス)` で決定

---

## 3. ビジネスルール

### ワークフロー状態機械

```
setup → configuring → executing → completed → exported
                                      ↑           |
                                      └───────────┘ (new_discussion)
```

| 状態 | 遷移元 | 遷移条件 |
|------|--------|---------|
| `setup` | 初回起動 | APIキーが有効 |
| `configuring` | `setup` / `exported` | Discussionページへ遷移 |
| `executing` | `configuring` | 開始ボタン押下 |
| `completed` | `executing` | ターン上限到達 or ユーザー停止 |
| `exported` | `completed` | エクスポート完了 |

- 状態は `st.session_state['workflow_state']` に保持
- 不正遷移は `WorkflowStateError` を送出

### トピックバリデーション
- 空不可（"Discussion topic is required"）
- 1〜500文字（"Topic must be between 1 and 500 characters"）
- 施行ポイント: `DiscussionService.setup_discussion()` 内

### ペルソナ選択ルール

**ハードルール（ブロック）**:
- 2〜6名選択必須
- 重複IDは禁止（"Persona '{name}' is already selected"）
- name・description が必須

**ソフトルール（警告のみ・上書き可）**:
- 全ペルソナが同一専門領域 → 多様性を推奨
- 批判的思考役なし → バランス改善を提案

### ターン制限ルール
| 条件 | 動作 |
|------|------|
| `current_turn == max_turns - 1` | 非ブロッキングバナー表示 |
| `current_turn == max_turns` | モーダル「続けるか終了するか」 |
| 「続ける」選択 | `max_turns += extended_turns` |
| 「終了」選択 | `completed` 状態へ遷移 |

### ファイル操作ルール
| 対象 | ルール |
|------|--------|
| ディスカッション自動保存 | エージェント発言完了ごとに保存（エラー時は非ブロッキング警告） |
| ディスカッションファイル名 | `{uuid}.json` |
| カスタムペルソナ | `{slug}.json`、重複時は `{slug}-2` |
| 資料ファイル | `.txt/.md/.pdf/.docx`、最大10MB |

### エクスポートルール
- `state == 'completed'` または `'exported'` の時のみ実行可能
- 最低1メッセージが必要
- ファイル名: `{topic_slug}_{date}.md`

---

## 4. 主要フロー

### 起動シーケンス
```
main.py
  → setup_logging()                    [LoggingConfig]
  → ensure_gitignore()                 [ConfigurationManager]
  → load_config()                      [ConfigurationManager]
  → validate_api_key()                 [ConfigurationManager → ApiValidator]
  → st.switch_page("pages/1_Setup.py") [StreamlitUI]
```

### ディスカッション実行ループ
```
For turn in 1..max_turns:
  For persona in selected_personas:
    1. プロンプト構築（トピック + 資料コンテキスト + 会話履歴 + ペルソナ指示）
    2. DiscussionEngine に非同期リクエスト
    3. ストリーミングレスポンスを受信・UI表示
    4. message を discussion.messages に追記
    5. FileManager.save_discussion() でオートセーブ
  ターン上限チェック（ソフトリミット）
```

### APIエラー時の再開フロー
```
API エラー発生
  → ResumeManager.set_resume_point(turn, persona_index, error)
  → FileManager.save_discussion()（resume_point フィールド含む）
  → UI: エラーメッセージ + "Resume Discussion" ボタン表示

ユーザーが「Resume」クリック
  → DiscussionService.resume_discussion()
  → ResumeManager.get_resume_point()
  → 完了済みメッセージをスキップ
  → チェックポイントから再試行
  → 成功時: ResumeManager.clear_resume_point()
  → FileManager.save_discussion()（resume_point = None）
```

### 資料処理フロー（AI前処理）
```
ファイルアップロード
  → ファイルタイプ検出 (.txt/.md/.pdf/.docx)
  → rawテキスト抽出（PDF: PyMuPDF、DOCX: python-docx）
  → Claude API で前処理（要約・主要トピック抽出・コンテキスト整形）
  → session_state に保存
  → ディスカッションプロンプトにコンテキストとして注入
```

---

## 5. UIページ構成

| ページ | ファイル | 役割 |
|--------|---------|------|
| Setup | `pages/1_Setup.py` | APIキー確認・初期設定 |
| Discussion | `pages/2_Discussion.py` | トピック入力・ペルソナ選択・ディスカッション実行 |
| Results | `pages/3_Results.py` | 結果表示・エクスポート |
| History | `pages/4_History.py` | 過去ディスカッション一覧・読込 |

---

## 6. データ永続化構造

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
  agent_discussion.log         # RotatingFileHandler（1MB × 3）

config.yaml                    # APIキー等（gitignore対象）
```
