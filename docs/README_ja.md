[English](README.md) | [日本語](README_ja.md) | **README**  
[English](MANUAL.md) | [日本語](MANUAL_ja.md) | **説明書**

# Open Super Whisper V2 - README

<div align="center">
  <img src="../assets/icon.png" alt="Open Super Whisper V2 Icon" width="128" height="128">
</div>

**会話型 AI エージェント - あなたの声を行動に変える**

話すだけで、AI エージェントがあなたの意図を理解し、自律的にタスクを実行します。PyQt6 ベースの強力なデスクトップアプリケーションで、OpenAI の最先端音声認識と高度な大規模言語モデルをシームレスに統合。音声による指示から、文書作成、情報検索、Web 操作まで、あなたの日常業務を革新的に効率化します。

## 機能

### 処理フロー

Open Super Whisper V2 は以下の 4 つのステップで動作します：

```
🎤 音声入力 → 📝 文字起こし → 🤖 エージェント処理 → 📋 結果出力
```

### 🎤 **音声入力**

- **グローバルホットキー** - どのアプリケーションからでも即座に起動
- **ワンクリック録音** - UI ボタンでの簡単な録音開始/停止
- **バックグラウンド動作** - システムトレイで常駐し、いつでも利用可能

### 📝 **文字起こし**

- **OpenAI Whisper 搭載** - 業界最高水準の音声認識精度
- **多言語対応** - 自動言語検出と 125 言語以上のサポート
- **カスタム語彙** - 専門用語や固有名詞の認識精度を向上

### 🤖 **エージェント処理**

- **インストラクションセット** - 用途別に特化した AI エージェントを事前定義
- **外部ツール連携** - MCP（Model Context Protocol）による拡張性
- **マルチコンテキスト** - クリップボードのテキストや画像、ウェブ検索を組み合わせた処理

### 📋 **結果出力**

- **Markdown レンダリング** - LaTeX 数式を含むリッチテキスト表示
- **自動クリップボード** - 処理完了と同時に結果をクリップボードに自動コピー
- **即座に活用** - 他のアプリケーションで結果をすぐに利用可能

## プロジェクト構造

```
.
├── run_open_super_whisper.py                      # アプリケーションエントリーポイント
├── pyproject.toml                                 # プロジェクト設定とuv用の依存関係
├── uv.lock                                        # プロジェクト設定とuv用の依存関係
├── assets/                                        # アセット（アイコン、音声ファイルなど）
│   ├── cancel_processing.wav                      # 処理完了時に再生される音
│   ├── complete_processing.wav                    # 処理中止時に再生される音
│   ├── icon.icns                                  # アプリケーションアイコン（macOS）
│   ├── icon.ico                                   # アプリケーションアイコン（Windows）
│   ├── icon.png                                   # アプリケーションアイコン（クロスプラットフォーム）
│   ├── start_recording.wav                        # 録音開始時に再生される音
│   └── stop_recording.wav                         # 録音停止時に再生される音
├── ffmpeg/                                        # FFmpeg実行ファイルとライブラリ
│   ├── bin/                                       # FFmpegバイナリファイル（実行ファイル、DLL）
│   ├── lib/                                       # ライブラリファイル
│   ├── include/                                   # インクルードファイル
│   └── doc/                                       # ドキュメント
├── docs/                                          # ドキュメントとサンプルファイル
│   ├── README.md                                  # プロジェクトドキュメント（英語版）
│   ├── README_ja.md                               # プロジェクトドキュメント（日本語版）
│   ├── settings_sample_en.json                    # サンプル設定ファイル（英語版）
│   └── settings_sample_ja.json                    # サンプル設定ファイル（日本語版）
├── core/                                          # コア機能（GUI非依存、完全実装済み）
│   ├── __init__.py
│   ├── api/                                       # APIクライアントファクトリーとユーティリティ
│   │   ├── __init__.py
│   │   └── api_client_factory.py
│   ├── key/                                       # キーボードとホットキー管理
│   │   ├── __init__.py
│   │   ├── hotkey_manager.py                      # グローバルホットキー管理
│   │   ├── key_formatter.py                       # キーフォーマットユーティリティ
│   │   └── key_state_tracker.py                   # キー状態追跡
│   ├── llm/                                       # 大規模言語モデル処理
│   │   ├── __init__.py
│   │   ├── llm_model.py                           # LLMモデルデータ構造
│   │   ├── llm_model_manager.py                   # LLMモデル管理
│   │   └── llm_processor.py                       # LLM処理実装
│   ├── pipelines/                                 # パイプラインとインストラクションセット
│   │   ├── __init__.py
│   │   ├── instruction_set.py                     # インストラクションセットデータモデル
│   │   ├── instruction_sets_manager.py            # インストラクションセット管理
│   │   ├── pipeline.py                            # 統合処理パイプライン
│   │   └── pipeline_result.py                     # パイプライン結果データモデル
│   ├── recorder/                                  # 音声録音機能
│   │   ├── __init__.py
│   │   └── audio_recorder.py                      # 音声録音実装
│   └── stt/                                       # 音声テキスト変換機能
│       ├── __init__.py
│       ├── audio_chunker.py                       # 大容量ファイル用音声チャンキング
│       ├── stt_lang_model.py                      # 言語モデルデータ構造
│       ├── stt_lang_model_manager.py              # 言語モデル管理
│       ├── stt_model.py                           # STTモデルデータ構造
│       ├── stt_model_manager.py                   # STTモデル管理
│       └── stt_processor.py                       # 音声テキスト変換処理実装
└── gui/                                           # GUI関連機能（Qt依存）
    ├── __init__.py
    ├── main.py                                    # GUIエントリーポイント
    └── app/                                       # メインアプリケーションコンポーネント
        ├── __init__.py
        ├── controllers/                           # MVCコントローラー
        │   ├── __init__.py
        │   ├── main_controller.py                 # メインアプリケーションコントローラー
        │   ├── dialogs/                           # ダイアログコントローラー
        │   │   ├── __init__.py
        │   │   ├── api_key_dialog_controller.py
        │   │   ├── hotkey_dialog_controller.py
        │   │   ├── instruction_dialog_controller.py
        │   │   └── settings_dialog_controller.py
        │   └── widgets/                           # ウィジェットコントローラー
        │       ├── __init__.py
        │       └── status_indicator_controller.py
        ├── managers/                              # アプリケーションマネージャー
        │   ├── __init__.py
        │   ├── audio_manager.py                   # 音声通知管理
        │   ├── icon_manager.py                    # アプリケーションアイコン管理
        │   ├── instruction_sets_manager.py        # GUIインストラクションセット管理
        │   ├── keyboard_manager.py                # GUIキーボード管理
        │   └── settings_manager.py                # アプリケーション設定管理
        ├── models/                                # MVCモデル
        │   ├── __init__.py
        │   ├── main_model.py                      # メインアプリケーションモデル
        │   ├── dialogs/                           # ダイアログモデル
        │   │   ├── __init__.py
        │   │   ├── api_key_dialog_model.py
        │   │   ├── hotkey_dialog_model.py
        │   │   ├── instruction_dialog_model.py
        │   │   └── settings_dialog_model.py
        │   └── widgets/                           # ウィジェットモデル
        │       ├── __init__.py
        │       └── status_indicator_model.py
        ├── utils/                                 # GUIユーティリティ関数
        │   ├── __init__.py
        │   ├── clipboard_utils.py                 # クリップボード操作
        │   └── pyinstaller_utils.py               # リソースパス解決
        └── views/                                 # MVCビュー
            ├── __init__.py
            ├── main_window.py                     # メインアプリケーションウィンドウ
            ├── dialogs/                           # ダイアログウィンドウ
            │   ├── __init__.py
            │   ├── api_key_dialog.py
            │   ├── hotkey_dialog.py
            │   ├── instruction_dialog.py
            │   └── settings_dialog.py
            ├── factories/                         # ビューファクトリー
            │   ├── __init__.py
            │   ├── api_key_dialog_factory.py
            │   ├── hotkey_dialog_factory.py
            │   ├── instruction_dialog_factory.py
            │   ├── main_window_factory.py
            │   ├── settings_dialog_factory.py
            │   └── status_indicator_factory.py
            ├── tray/                              # システムトレイ機能
            │   ├── __init__.py
            │   └── system_tray.py
            └── widgets/                           # カスタムウィジェット
                ├── __init__.py
                ├── markdown_text_browser.py       # Markdownレンダリングウィジェット
                └── status_indicator.py            # ステータスインジケーターウィンドウ
```

## インストール

1. リポジトリをクローンします：

   ```bash
   git clone https://github.com/TakanariShimbo/open-super-whisper-v2.git
   cd open-super-whisper-v2
   ```

   注：システムに Git がインストールされている必要があります。

2. 依存関係をインストールします：

   ```bash
   uv sync
   ```

   注：システムに UV がインストールされている必要があります。

3. FFmpeg をセットアップします：

   このアプリケーションには FFmpeg が必要です。

   **Windows 版：**

   プロジェクトルートに`ffmpeg`ディレクトリを作成し、その中に`bin`サブディレクトリを作成して、FFmpeg 実行ファイルを配置する必要があります。

   ```bash
   # 1. https://ffmpeg.org/download.html からFFmpegをダウンロード
   #    - 推奨："ffmpeg-release-essentials.zip"（Windows版）

   # 2. ダウンロードしたZIPファイルを展開

   # 3. 展開したフォルダ全体をプロジェクトルートのffmpegディレクトリにコピー
   #    例：展開した"ffmpeg-x.x.x-win64-static/" → プロジェクトの"ffmpeg/"
   ```

   アプリケーションは起動時に`ffmpeg/bin`ディレクトリを自動的に PATH に追加します。

## 設定

### サンプル設定の利用

`docs/`ディレクトリにサンプル設定ファイルが提供されています：

- `settings_sample_en.json` - 事前設定されたインストラクションセット付きの英語版
- `settings_sample_ja.json` - 同じ機能の日本語版

サンプルファイルを使用するには：

1. ユーザーホームディレクトリに設定ディレクトリを作成：

   ```bash
   mkdir ~/.open_super_whisper
   ```

2. 使用したいサンプルファイルを設定ディレクトリにコピー：

   ```bash
   cp docs/settings_sample/settings_ja.json ~/.open_super_whisper/settings.json
   ```

**注意:** アプリケーションは設定ファイルが`~/.open_super_whisper/settings.json`に配置されることを期待しています（`~`はユーザーホームディレクトリを表します）。

### サンプル設定の内容

両方のサンプルファイルには以下のインストラクションセットが含まれています：

- **文字起こしエージェント** (Ctrl+Shift+1) - 基本的な音声テキスト変換
- **文章作成エージェント** (Ctrl+Shift+2) - 音声を正式な書面に自動変換
- **検索キーワードエージェント** (Ctrl+Shift+3) - 音声から最適な検索キーワードを自動生成
- **テキスト Q&A エージェント** (Ctrl+Shift+4) - クリップボードテキストを分析して質問に回答（Web 検索対応）
- **画像 Q&A エージェント** (Ctrl+Shift+5) - クリップボード画像を解析して質問に回答（Web 検索対応）
- **Web 自動操作エージェント** (Ctrl+Shift+6) - Playwright を使用した自律的 Web 操作

## 実行方法

アプリケーションを起動するには、以下を実行します：

```bash
python run_open_super_whisper.py
```

コマンドラインオプション：

- `--minimized` または `-m`：アプリケーションをシステムトレイに最小化して起動

## パッケージング

アプリケーションをスタンドアロン実行ファイルにパッケージするには：

```bash
# Windows
python -m PyInstaller --onefile --icon assets/icon.ico --name "OpenSuperWhisper" --add-data "assets;assets" --add-data "ffmpeg;ffmpeg" run_open_super_whisper.py

# macOS用
# python -m PyInstaller --onefile --icon assets/icon.icns --name "OpenSuperWhisper" --add-data "assets:assets" run_open_super_whisper.py

# Linux用
# python -m PyInstaller --onefile --icon assets/icon.png --name "OpenSuperWhisper" --add-data "assets:assets" run_open_super_whisper.py
```

Windows コマンドは以下を実行します：

- `--onefile`：単一の実行可能ファイルを作成
- `--icon assets/icon.ico`：アプリケーションアイコンを設定
- `--name "OpenSuperWhisper"`：出力ファイル名を指定
- `--add-data "assets;assets"`：実行ファイルに assets ディレクトリ全体を含める
- `--add-data "ffmpeg;ffmpeg"`：実行ファイルに ffmpeg ディレクトリ全体を含める

ビルドが完了すると、Windows では`dist`フォルダに`OpenSuperWhisper.exe`が、macOS では`dist`フォルダに`OpenSuperWhisper.app`が、Linux では`dist`フォルダに`OpenSuperWhisper`が作成されます。

## ライセンス

このプロジェクトは MIT ライセンスの下でライセンスされています。
