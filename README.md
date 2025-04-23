# Open Super Whisper

A PyQt6-based GUI application for audio transcription using OpenAI's Whisper API. This application allows for recording audio, sending it to Whisper for transcription, and displaying the results.

## Features

- Complete PyQt6-based GUI implementation 
- Global hotkey support for starting/stopping recording
- Custom vocabulary and instruction sets management
- System tray integration
- Multiple language and model support
- Clipboard integration
- Status indicator window
- Settings management

## Project Structure

新しいディレクトリ構成:

```
.
├── main.py                      # アプリケーションのエントリーポイント
├── README.md                    # プロジェクトの説明ドキュメント
├── pyproject.toml               # プロジェクト設定と依存関係
├── assets/                      # アセット（アイコン、音声ファイルなど）
│   ├── complete_sound.wav       # 転写完了時のサウンド
│   ├── icon.ico                 # アプリケーションアイコン (Windows)
│   ├── icon.png                 # アプリケーションアイコン (クロスプラットフォーム)
│   ├── start_sound.wav          # 録音開始時のサウンド
│   └── stop_sound.wav           # 録音停止時のサウンド
├── whisper_core/                # コア機能（GUI非依存）
│   ├── __init__.py
│   ├── transcriber.py           # 音声転写インターフェース
│   ├── recorder.py              # 音声録音インターフェース
│   └── instructions.py          # カスタム語彙とインストラクション
└── whisper_gui/                 # GUI関連の機能（QtとGUI依存）
    ├── __init__.py
    ├── main.py                  # GUIのエントリーポイント
    ├── hotkeys.py               # グローバルホットキー管理
    ├── components/              # 再利用可能なUIコンポーネント
    │   ├── __init__.py
    │   └── widgets/             # カスタムウィジェット
    │       ├── __init__.py
    │       └── status_indicator.py
    ├── dialogs/                 # ダイアログウィンドウ
    │   ├── __init__.py
    │   ├── api_key_dialog.py
    │   ├── hotkey_dialog.py
    │   ├── instruction_sets_dialog.py
    │   └── simple_message_dialog.py
    ├── resources/               # アプリケーションリソース
    │   ├── __init__.py
    │   ├── config.py            # 設定
    │   └── labels.py            # UIテキストラベル
    ├── utils/                   # ユーティリティ関数
    │   ├── __init__.py
    │   └── resource_helper.py   # リソースパス解決
    └── windows/                 # メインアプリケーションウィンドウ
        ├── __init__.py
        └── main_window.py       # メインアプリケーションウィンドウ
```

### 特徴:

1. **明確な責任分離**:
   - `whisper_core`: GUIに依存しないコア機能
   - `whisper_gui`: Qt/GUIに依存するコード

2. **モジュール化**:
   - 各機能が論理的に整理されたディレクトリに配置
   - 共通機能の重複を削減

## How to Run

To run the application:

```bash
# With Python directly
python main.py

# Or, after installation
pip install .
open-super-whisper
```

## 開発

### 開発環境のセットアップ

```bash
# 仮想環境の作成
python -m venv venv
source venv/bin/activate  # Linuxの場合
venv\Scripts\activate     # Windowsの場合

# 依存関係のインストール（開発モード）
pip install -e ".[dev]"
```

### テスト

```bash
# テストの実行
pytest
```

### パッケージ化

```bash
# PyInstallerを使用してスタンドアロン実行ファイルを作成
pyinstaller --onefile --windowed --icon=assets/icon.ico --name=open-super-whisper main.py
```

### コア機能とGUI機能

コアモジュール（`whisper_core`）は、GUIに依存せず、他のプロジェクトからも再利用可能です。

GUIモジュール（`whisper_gui`）は、コアモジュールを使用してユーザーインターフェースを提供します。

## ライセンス

MITライセンスの下で公開されています。詳細はLICENSEファイルを参照してください。
