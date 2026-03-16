# PLAN.md — 実装タスク管理

## 実装フェーズ

### Phase 1: プロジェクト基盤
- [x] CLAUDE.md 作成
- [x] docs/spec/feature-auth.md 作成
- [x] research.md 作成
- [x] config.yaml 作成
- [ ] pyproject.toml 作成（Poetry設定）

### Phase 2: Core Layer
- [ ] `agent_discussion/core/models.py` — ドメインエンティティ (Persona, Message, Discussion, etc.)
- [ ] `agent_discussion/core/exceptions.py` — カスタム例外 (ConfigError, WorkflowStateError)
- [ ] `agent_discussion/core/logging_config.py` — RotatingFileHandler設定
- [ ] `agent_discussion/core/config.py` — ConfigurationManager, ensure_gitignore
- [ ] `agent_discussion/core/api_validator.py` — ApiValidator
- [ ] `agent_discussion/core/files.py` — FileManager（全I/O）
- [ ] `agent_discussion/core/resume_manager.py` — ResumeManager

### Phase 3: Persona Layer
- [ ] `agent_discussion/personas/manager.py` — PersonaManager（CRUD）
- [ ] `agent_discussion/personas/service.py` — PersonaService（バリデーション）

### Phase 4: Discussion Layer
- [ ] `agent_discussion/discussions/engine.py` — DiscussionEngine（Claude API統合）
- [ ] `agent_discussion/discussions/service.py` — DiscussionService（ワークフロー）

### Phase 5: UI Layer
- [ ] `agent_discussion/ui/components.py` — 共通UIコンポーネント
- [ ] `agent_discussion/pages/1_Setup.py` — APIキー確認
- [ ] `agent_discussion/pages/2_Discussion.py` — ディスカッション設定・実行
- [ ] `agent_discussion/pages/3_Results.py` — 結果表示・エクスポート
- [ ] `agent_discussion/pages/4_History.py` — 履歴管理

### Phase 6: エントリポイント・データ
- [ ] `main.py` — アプリエントリポイント
- [ ] `data/personas/predefined.json` — 組み込みペルソナ

## 不具合追跡（サブエージェントからの報告受付）

| ID | 発生箇所 | 内容 | 状態 |
|----|---------|------|------|
| - | - | - | - |

## メモ
- `tests/` ディレクトリはサブエージェントが担当
- 詳細設計は `docs/spec/feature-auth.md` を参照
