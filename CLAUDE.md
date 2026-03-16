# CLAUDE.md

> 詳細設計仕様は [docs/spec/feature-auth.md](docs/spec/feature-auth.md) を参照すること。

---

## アプリケーション概要

**AI Agent Discussion** — 複数のAIエージェント（ペルソナ）が特定のトピックについて自律的にディスカッションするローカル動作のWebアプリ。個人利用・シングルユーザー前提。

### 主要機能
- ペルソナ管理（組み込み4種 + カスタム作成）
- 2〜6エージェントによるターン制ディスカッション（ストリーミング表示）
- 資料参照（PDF・Word等をAI前処理してコンテキスト注入）
- 議事録エクスポート（Markdown）
- 履歴管理（保存・閲覧・再開）

### 技術スタック
| 項目 | 内容 |
|------|------|
| 言語 | Python 3.13+ |
| UI | Streamlit（マルチページ） |
| AI | Anthropic Claude API（公式SDKのみ） |
| 設定 | YAML (`config.yaml`) |
| 依存管理 | Poetry |
| 永続化 | ローカルファイル（JSON） |

**スコープ外**: マルチユーザー・認証・クラウドデプロイ・DB・外部ツール統合・モバイル・音声動画・エージェントの記憶継続。

---

## アーキテクチャ

```
UI Layer        : StreamlitUI, PersonaUI
Service Layer   : PersonaService, DiscussionService, ExportService
Component Layer : DiscussionEngine, PersonaManager, FileManager
Config Layer    : ConfigurationManager
+ NFR           : ApiValidator, ResumeManager, LoggingConfig
```

- 上位レイヤーは下位レイヤーにのみ依存（循環依存禁止）
- 全ファイルI/Oは `FileManager` 経由
- Claude API統合は `DiscussionEngine` 内で直接行う
- サービス・コンポーネントのDIは `main.py` の `_init()` に集約

### ディレクトリ構成

```
AgentDiscussion/
├── main.py
├── agent_discussion/
│   ├── core/          # ConfigurationManager, FileManager, ApiValidator,
│   │                  # ResumeManager, LoggingConfig, models（エンティティ）
│   ├── personas/      # PersonaService, PersonaManager
│   ├── discussions/   # DiscussionService, DiscussionEngine
│   ├── ui/            # UI共通コンポーネント
│   └── pages/         # 1_Setup, 2_Discussion, 3_Results, 4_History
├── tests/             # agent_discussion と同構成
├── data/              # discussions/{uuid}.json, personas/
├── exports/           # {topic_slug}_{date}.md
├── logs/              # agent_discussion.log（RotatingFileHandler）
├── docs/spec/         # 詳細設計仕様
├── config.yaml        # APIキー等（gitignore対象）
└── pyproject.toml
```

---

## 技術制約・コーディング規約

### 技術制約
1. **シングルユーザー設計** — 認証・マルチユーザー対応なし
2. **ローカル実行のみ** — DB不使用、永続化はローカルファイルのみ
3. **APIキーはコードに書かない** — `config.yaml` の `anthropic.api_key` のみ（環境変数フォールバックなし）
4. **Claude API必須** — インターネット接続・有効なAPIキーが必要

### コーディング規約

#### 全般
- 型ヒントを全関数・メソッドに付与する
- パブリックAPIにはdocstringを記述する
- 1ファイル1クラスを基本（小さなdataclassは例外）

#### 命名規則
| 対象 | 規則 | 例 |
|------|------|----|
| クラス | PascalCase | `DiscussionEngine` |
| 関数・メソッド | snake_case | `start_discussion()` |
| 定数 | UPPER_SNAKE_CASE | `MAX_AGENTS = 6` |
| プライベートメンバー | `_` プレフィックス | `_load_config()` |

#### エラーハンドリング
- API呼び出しは必ず `try/except` でラップし、ユーザーに分かりやすいメッセージを表示する
- 例外は握り潰さず、ログ記録後に伝播・表示する
- カスタム例外クラスは `core/` に定義する（例: `ConfigError`, `WorkflowStateError`）

#### セキュリティ
- ユーザー入力は全てバリデーションする（長さ・型・内容）
- ファイルパスは `pathlib.Path` で正規化する
- APIキーはログ・例外メッセージに含めない

#### テスト
- `tests/` 以下に `agent_discussion/` と同じ構造で配置する
- テストライブラリ: `pytest`, `pytest-asyncio`
- 外部API（Claude API）はモックする

#### Streamlit固有
- セッション状態のキーは文字列定数で管理する（マジックストリング禁止）
- UIロジックとビジネスロジックを分離する（ページファイルにはUIのみ記述）
- ストリーミング中は Start/Export ボタンを無効化する（`workflow_state == 'executing'`）
- ストリーミング表示は `st.empty()` を使いページ全体の再レンダリングを避ける

---

## エージェント役割分担

### メインエージェント（コーディング担当）
- 機能コード・設定・ドキュメントの作成・修正
- `PLAN.md` を作成し、実装タスクを管理・追跡する（実装前に必ず確認）
- `tests/` ディレクトリへの変更は原則禁止

### サブエージェント（テスト・品質担当）
- `tests/` 以下のテストコード作成・修正・実行
- `poetry run pytest` によるテスト実行と結果の報告
- 不具合検出時は `PLAN.md` に記録し、修正はメインエージェントに委ねる
- メインエージェントのコードを直接変更しない

### 連携ルール
- 両エージェントは独立して動作し、互いのタスクに干渉しない
- 実装完了 → テスト実施 → 不具合報告（`PLAN.md`経由）→ 修正、の順序で進める
