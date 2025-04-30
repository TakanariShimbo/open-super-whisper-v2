# new_core 実装

## 概要

本プロジェクトでは、新しい `new_core` ディレクトリ構造を実装しました。これは既存の `core` ディレクトリ構造を刷新し、モジュール間の責務をより明確に分離したものです。

## 実装内容

### ディレクトリ構造

```
new_core/
├── __init__.py
├── llm/                   # LLM (大規模言語モデル) 関連機能
│   ├── __init__.py
│   ├── llm_model.py
│   ├── llm_model_manager.py
│   └── llm_processor.py
├── pipelines/             # 複数の処理を連携させるパイプライン
│   ├── __init__.py
│   ├── pipeline_result.py
│   └── stt_llm_pipeline.py
├── recorder/              # 音声録音関連機能
│   ├── __init__.py
│   └── audio_recorder.py
├── stt/                   # Speech-to-Text (音声認識) 関連機能
│   ├── __init__.py
│   ├── audio_chunker.py
│   ├── process_tracker.py
│   ├── stt_model.py
│   ├── stt_model_manager.py
│   └── stt_processor.py
├── ui/                    # ユーザーインターフェース関連機能
│   ├── __init__.py
│   └── hot_key_manager.py
└── utils/                 # 汎用ユーティリティ
    ├── __init__.py
    └── instruction_manager.py
```

### 主要モジュール

#### recorder モジュール
- `audio_recorder.py`: マイクから音声を録音する機能を提供

#### stt モジュール
- `audio_chunker.py`: 大きな音声ファイルを適切なサイズに分割
- `process_tracker.py`: 処理したチャンクの進捗を追跡
- `stt_model.py`: 音声認識モデルの定義
- `stt_model_manager.py`: 利用可能な音声認識モデルの管理
- `stt_processor.py`: 音声認識の実行処理

#### llm モジュール
- `llm_model.py`: 大規模言語モデルの定義
- `llm_model_manager.py`: 利用可能な言語モデルの管理
- `llm_processor.py`: テキスト処理の実行

#### pipelines モジュール
- `pipeline_result.py`: パイプライン処理結果のコンテナ
- `stt_llm_pipeline.py`: 音声認識から言語処理までの一連の処理

#### ui モジュール
- `hot_key_manager.py`: グローバルホットキーの管理

#### utils モジュール
- `instruction_manager.py`: 処理指示セットの管理

## テスト

各モジュールの機能確認のために以下のテストを実装：

- `test_stt_model.py`: STTModelクラスの単体テスト
- `test_hot_key_manager.py`: HotKeyManagerクラスの単体テスト
- `test_instruction_manager.py`: InstructionManagerクラスの単体テスト
- `test_stt_llm_pipeline.py`: STTLLMPipelineクラスの統合テスト

## 主な改善点

1. **モジュールの明確な責務分離**:
   - 各機能が独立したモジュールとして分離され、メンテナンス性が向上

2. **一貫した命名規則**:
   - クラス名をベンダー非依存に変更 (例: OpenAIWhisperTranscriber → STTProcessor)
   - メソッド名を統一 (例: process_with_llm → process_text)

3. **パラメータの明確化**:
   - ベンダー固有の名前を排除 (例: openai_api_key → api_key)

4. **拡張性の向上**:
   - 将来的に他のAPIやモデルにも対応しやすい設計

## 使用方法

各モジュールは独立して使用できますが、通常は`pipelines`モジュールを通じて機能を組み合わせて使用します：

```python
from new_core.pipelines.stt_llm_pipeline import STTLLMPipeline

# パイプラインの作成
pipeline = STTLLMPipeline(api_key="YOUR_API_KEY")

# LLM処理を有効にする
pipeline.enable_llm_processing(True)

# 音声ファイルを処理
result = pipeline.process("audio_file.wav", language="en")

# 結果を取得
print(f"Transcription: {result.transcription}")
print(f"LLM Response: {result.llm_response}")
```

## 今後の展望

1. より多様なモデルのサポート追加
2. 非同期処理への対応
3. パフォーマンス最適化
4. より詳細なドキュメントの整備
