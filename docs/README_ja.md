[English](README.md) | [日本語](README_ja.md)

# Open Super Whisper V2

**究極の音声文字起こし＆AI 分析ツール**

音声をインテリジェントで実行可能なテキストに変換する、PyQt6 ベースの強力なデスクトップアプリケーションです。OpenAI の最先端 Whisper 音声認識と高度な大規模言語モデルをシームレスに組み合わせて、音声コンテンツを単に文字起こしするだけでなく、分析、要約、拡張します。

## 機能

### 🎯 **スマート録音＆文字起こし**

- **ワンクリック録音** - 即座に音声をキャプチャ
- **グローバルホットキー対応** - システムのどこからでも録音を開始/停止
- **多言語対応** - 自動言語検出機能付き
- **高品質な文字起こし** - OpenAI Whisper API を搭載
- **大容量ファイル処理** - インテリジェントな音声チャンキング機能

### 🧠 **AI 駆動のコンテンツ処理**

- **LLM 統合** - GPT-4、Claude などのモデルで文字起こしを処理
- **インテリジェント分析** - コンテンツの要約、翻訳、変換
- **カスタム AI 指示** - 特定のニーズに合わせて AI レスポンスを調整
- **ストリーミングレスポンス** - AI 分析をリアルタイムで表示
- **MCP サーバーサポート** - Model Context Protocol による外部ツールとデータソースへの接続

### ⚡ **高度なワークフロー管理**

- **指示セット** - 異なる処理プロファイルを作成して切り替え
- **カスタム語彙** - 専門用語や特殊なコンテンツの精度を向上
- **クリップボード統合** - AI 処理にクリップボードの内容を自動的に含める
- **プロファイルベースのホットキー** - 異なるワークフローにキーボードショートカットを割り当て

### 💼 **プロフェッショナルなユーザー体験**

- **クリーンでモダンなインターフェース** - PyQt6 で構築
- **システムトレイ統合** - アプリをバックグラウンドで実行し続ける
- **視覚的なステータスインジケーター** - 何が起きているかを常に把握
- **音声通知** - 録音状態の音声フィードバック
- **自動クリップボード** - 処理完了時に結果を自動的にコピー

### 🔧 **柔軟でカスタマイズ可能**

- **複数の AI モデル** - タスクに最適なモデルを選択
- **設定可能な設定** - アプリケーションのあらゆる側面をカスタマイズ
- **Markdown サポート** - LaTeX 数式をサポートしたリッチテキストレンダリング
- **クロスプラットフォーム対応** - Windows、macOS、Linux で動作

## プロジェクト構造

```
.
├── run_open_super_whisper.py                      # アプリケーションエントリーポイント
├── pyproject.toml                                 # プロジェクト設定とuv用の依存関係
├── uv.lock                                        # プロジェクト設定とuv用の依存関係
├── assets/                                        # アセット（アイコン、音声ファイルなど）
│   ├── cancel_processing.wav                      # 処理完了時に再生される音
│   ├── complete_processing.wav                    # 処理キャンセル時に再生される音
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
│   ├── pipelines/                                 # 処理パイプラインと指示セット
│   │   ├── __init__.py
│   │   ├── instruction_set.py                     # 指示セットデータモデル
│   │   ├── instruction_sets_manager.py            # 指示セット管理
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
        │   ├── instruction_sets_manager.py        # GUI指示セット管理
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
   git clone https://github.com/yourusername/open-super-whisper-v2.git
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

### サンプル設定

`docs/`ディレクトリにサンプル設定ファイルが提供されています：

- `settings_sample_en.json` - 事前設定された指示セット付きの英語版
- `settings_sample_ja.json` - 同じ機能の日本語版

サンプルファイルを使用するには：

1. ユーザーホームディレクトリに設定ディレクトリを作成：

   ```bash
   mkdir ~/.open_super_whisper
   ```

2. 使用したいサンプルファイルを設定ディレクトリにコピー：

   ```bash
   # 英語設定の場合
   cp docs/settings_sample_en.json ~/.open_super_whisper/settings.json

   # 日本語設定の場合
   cp docs/settings_sample_ja.json ~/.open_super_whisper/settings.json
   ```

**注意:** アプリケーションは設定ファイルが`~/.open_super_whisper/settings.json`に配置されることを期待しています（`~`はユーザーホームディレクトリを表します）。

### 事前設定された指示セット

両方のサンプルファイルには以下の指示セットが含まれています：

- **シンプル文字起こし** (Ctrl+Shift+1) - 基本的な音声テキスト変換
- **書き言葉に変換** (Ctrl+Shift+2) - 音声を正式な書面に変換
- **検索キーワード生成** (Ctrl+Shift+3) - 音声から検索キーワードを抽出
- **クリップボードテキスト Q&A** (Ctrl+Shift+4) - クリップボードテキストに関する質問応答（Web 検索対応）
- **クリップボード画像 Q&A** (Ctrl+Shift+5) - クリップボード画像に関する質問応答（Web 検索対応）
- **Web 自動操作エージェント** (Ctrl+Shift+6) - Playwright を使用した自動 Web 操作

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

このプロジェクトは MIT ライセンスの下でライセンスされています。詳細については LICENSE ファイルを参照してください。
