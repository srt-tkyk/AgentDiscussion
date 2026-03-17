# AI Agent Discussion

複数のAIエージェント（ペルソナ）が特定のトピックについて自律的にディスカッションするローカル動作のWebアプリ。

---

## 目次

1. [必要環境](#必要環境)
2. [セットアップ](#セットアップ)
3. [アプリの起動](#アプリの起動)
4. [使い方](#使い方)
   - [1. Setup ページ](#1-setup-ページ)
   - [2. Discussion ページ](#2-discussion-ページ)
   - [3. Results ページ](#3-results-ページ)
   - [4. History ページ](#4-history-ページ)
5. [config.yaml リファレンス](#configyaml-リファレンス)
6. [カスタムペルソナの作成](#カスタムペルソナの作成)
7. [議事録のエクスポート](#議事録のエクスポート)
8. [トラブルシューティング](#トラブルシューティング)

---

## 必要環境

| 項目 | バージョン |
|------|-----------|
| Python | 3.13 以上 |
| Poetry | 1.8 以上（2.x 推奨） |
| Anthropic API キー | 有効なキーとクレジット残高 |
| インターネット接続 | Claude API 呼び出しに必要 |

---

## セットアップ

### 1. リポジトリのクローン（または展開）

```bash
git clone <repository-url>
cd AgentDiscussion
```

### 2. 依存ライブラリのインストール

```bash
poetry install
```

仮想環境は自動的に `.venv/` に作成されます。

### 3. `config.yaml` の作成・編集

プロジェクトルートに `config.yaml` を作成し、Anthropic API キーを設定します。

```yaml
anthropic:
  api_key: "sk-ant-api03-..."     # Anthropic APIキー（必須）
  model: "claude-haiku-4-5-20251001"  # 使用するモデル
  max_tokens: 4096                # APIレベルのトークン上限
  max_response_chars: 500         # エージェント1発言あたりの文字数目安

app:
  max_turns_default: 3            # ディスカッションのデフォルトターン数
  max_personas: 6                 # 最大エージェント数
  min_personas: 2                 # 最小エージェント数
  max_file_size_mb: 10            # 資料アップロードの上限サイズ (MB)
  language_default: "ja"          # デフォルト言語
  discussion_style_default: "formal"
  log_level: "INFO"

paths:
  discussions_dir: "data/discussions"
  personas_dir: "data/personas"
  materials_dir: "data/materials"
  exports_dir: "exports"
  logs_dir: "logs"
```

> **注意**: `config.yaml` には API キーが含まれるため `.gitignore` に自動追加されます。Git にコミットしないでください。

---

## アプリの起動

```bash
poetry run streamlit run main.py
```

起動後、ブラウザで `http://localhost:8501` が自動的に開きます。

---

## 使い方

### 1. Setup ページ

アプリ起動後に最初に表示されるページです。

- **✅ API key is valid** が表示されれば準備完了
- **❌ エラーが表示された場合**: `config.yaml` の `anthropic.api_key` を確認してアプリを再起動してください

「Go to Discussion →」ボタンでディスカッション設定画面に進みます。

---

### 2. Discussion ページ

ディスカッションの設定と実行を行います。

#### トピックの入力

- 最大 500 文字でディスカッションのテーマを入力します
- 例: `AIが教育に与える影響について議論してください`

#### ペルソナの選択

組み込みペルソナの中から 2〜6 名を選択します。

| ペルソナ | 特徴 |
|---------|------|
| 組み込み4種 | 事前定義済みのエージェント |
| カスタム | 任意の名前・説明で作成可能 |

チェックボックスで参加するエージェントを選択してください。

#### パラメータの設定

| 設定項目 | 内容 | 選択肢 |
|---------|------|--------|
| Max turns | 最大ターン数（1エージェント1回=1ターン） | 1〜20 |
| Discussion style | ディスカッションのトーン | `formal` / `casual` / `debate` |
| Language | 発言言語 | `ja` / `en` / `fr` / `de` / `es` |

#### 資料のアップロード（任意）

- 対応形式: `.txt`, `.md`, `.pdf`, `.docx`
- 最大サイズ: 10 MB
- アップロードした資料はAIが前処理し、全エージェントの文脈として注入されます

#### ディスカッションの開始

「▶ Start Discussion」ボタンを押すと実行が始まります。各エージェントの発言がリアルタイムにストリーミング表示されます。

**実行中の操作:**

| ボタン | 動作 |
|--------|------|
| ⏹ Stop Discussion | 現在のターン完了後に停止 |
| ターン上限到達時 | 「Continue」で延長 / 「Finish」で終了 |
| エラー発生時 | 「▶ Resume Discussion」で中断点から再開 |

---

### 3. Results ページ

完了したディスカッションの結果を確認します。

- **トランスクリプト**: 全発言をエージェントごとの色で表示
- **📥 Export Meeting Minutes**: 議事録を Markdown ファイルとして `exports/` に保存し、ダウンロードリンクを表示
- **➕ New Discussion**: 設定をリセットして新しいディスカッションを開始

---

### 4. History ページ

過去のディスカッションを一覧表示します。

- トピック・参加者・ターン数・日時・状態を確認できます
- 「Load」ボタンで過去のディスカッションを Results ページに読み込めます
- 中断したディスカッション（`is_resumable`）は Discussion ページから再開可能です

---

## config.yaml リファレンス

### `anthropic` セクション

| キー | 説明 | デフォルト |
|-----|------|-----------|
| `api_key` | Anthropic API キー（必須） | — |
| `model` | 使用する Claude モデル ID | `claude-3-5-sonnet-20241022` |
| `max_tokens` | APIレベルのトークン上限（打ち切り防止） | `4096` |
| `max_response_chars` | エージェントへの文字数指示（ソフト制約） | `500` |

**`max_response_chars` の調整指針:**

| 値 | 発言スタイル |
|----|------------|
| 200〜300 | 短く簡潔なやり取り |
| 400〜600 | 標準的なディスカッション |
| 800〜1200 | 詳細な論点展開 |

### `app` セクション

| キー | 説明 |
|-----|------|
| `max_turns_default` | ディスカッションのデフォルトターン数 |
| `max_turns_extension` | ターン上限到達時の延長ターン数 |
| `max_personas` | 最大エージェント数（上限 6） |
| `min_personas` | 最小エージェント数（下限 2） |
| `max_file_size_mb` | 資料アップロードの上限サイズ |
| `language_default` | デフォルト言語 |
| `discussion_style_default` | デフォルトのディスカッションスタイル |
| `log_level` | ログレベル（`DEBUG` / `INFO` / `WARNING`） |

---

## カスタムペルソナの作成

Discussion ページの「➕ Create Custom Persona」セクションから作成できます。

1. **Name**: ペルソナの名前（最大 100 文字）
2. **Description**: キャラクターの説明（最大 500 文字）
   例: `慎重派のエンジニア。リスクとコストを重視し、実現可能性を常に問う。`
3. 「Save Persona」ボタンで保存

作成したペルソナは `data/personas/` に JSON で保存され、以降のセッションでも利用できます。

---

## 議事録のエクスポート

Results ページの「📥 Export Meeting Minutes」で Markdown 形式の議事録を生成します。

**出力先**: `exports/{topic_slug}_{日時}.md`

**形式:**

```markdown
# Meeting Minutes

**Topic**: ...
**Date**: ...
**Participants**: ...
**Turns**: ...

---

## Transcript

### Turn 1 — エージェント名
発言内容...
```

---

## トラブルシューティング

### API キーが無効と表示される

- `config.yaml` の `anthropic.api_key` が正しいか確認してください
- アプリを再起動してください（Streamlit はセッション単位で初期化されます）

### クレジット残高不足エラー

```
Error code: 400 - credit balance is too low
```

Anthropic Console の Plans & Billing でクレジットを追加してください。

### モデルが見つからないエラー

```
Error code: 404 - model: xxx not found
```

`config.yaml` の `anthropic.model` を利用可能なモデル ID に変更してください。
例: `claude-haiku-4-5-20251001`

### エージェントの発言が途中で切れる

`config.yaml` の `max_tokens` を増やしてください（例: `8192`）。
また `max_response_chars` を小さくすることで、エージェントが上限内に収まるよう促せます。

### ディスカッションがエラーで中断した

「▶ Resume Discussion」ボタンで中断点から再開できます。
再開できない場合は History ページからも確認できます。

### ログの確認

```bash
cat logs/agent_discussion.log
```

ログはローテーション管理（最大 1MB × 3ファイル）されます。

---

## ディレクトリ構成

```
AgentDiscussion/
├── main.py                  # エントリポイント
├── config.yaml              # 設定ファイル（gitignore対象）
├── pyproject.toml           # Poetry 依存管理
├── pages/                   # Streamlit マルチページ
│   ├── 1_Setup.py
│   ├── 2_Discussion.py
│   ├── 3_Results.py
│   └── 4_History.py
├── agent_discussion/        # アプリケーションコード
├── data/                    # ローカルデータ（自動生成）
│   ├── discussions/         # ディスカッション履歴 (JSON)
│   └── personas/            # カスタムペルソナ (JSON)
├── exports/                 # エクスポートした議事録 (Markdown)
└── logs/                    # アプリログ
```
