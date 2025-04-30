#!/usr/bin/env python3
"""
Open Super Whisper V2 - テスト用コマンドラインプログラム

このプログラムは、Open Super Whisper V2の new_core モジュールの各機能を
コマンドラインからテストするためのツールです。各サブモジュール（recorder, stt, llm, pipelines, ui, utils）の
機能を個別にテストしたり、統合テストを行うことができます。
"""

import os
import sys
import time
import argparse
import json
from typing import List, Dict, Any, Optional, Union, Callable

# モジュールインポートのためのパスを設定
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# バージョン情報
__version__ = "0.1.0"


def setup_common_parser() -> argparse.ArgumentParser:
    """共通の引数パーサーをセットアップ"""
    parser = argparse.ArgumentParser(
        description="Open Super Whisper V2 テストツール",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # 共通オプション
    parser.add_argument("-v", "--verbose", action="store_true", help="詳細出力モード")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument("--api-key", help="OpenAI APIキー（環境変数 OPENAI_API_KEY でも設定可能）")
    
    return parser


def setup_subparsers(parser: argparse.ArgumentParser) -> Dict[str, argparse.ArgumentParser]:
    """サブコマンドパーサーをセットアップ"""
    subparsers = parser.add_subparsers(dest="command", help="サブコマンド")
    subparsers.required = True
    
    # サブコマンドパーサーを保持する辞書
    sub_parsers = {}
    
    # recorder サブコマンド
    recorder_parser = subparsers.add_parser("recorder", help="録音機能テスト")
    recorder_subparsers = recorder_parser.add_subparsers(dest="subcommand", help="recorder サブコマンド")
    recorder_subparsers.required = True
    
    # recorder check
    check_parser = recorder_subparsers.add_parser("check", help="マイク利用可能性確認")
    
    # recorder list
    list_parser = recorder_subparsers.add_parser("list", help="利用可能なマイク一覧表示")
    
    # recorder record
    record_parser = recorder_subparsers.add_parser("record", help="録音テスト")
    record_parser.add_argument("--duration", type=int, default=5, help="録音時間（秒）")
    record_parser.add_argument("--sample-rate", type=int, default=16000, help="サンプルレート")
    record_parser.add_argument("--channels", type=int, default=1, help="チャンネル数")
    
    sub_parsers["recorder"] = recorder_parser
    
    # stt サブコマンド
    stt_parser = subparsers.add_parser("stt", help="音声認識機能テスト")
    stt_subparsers = stt_parser.add_subparsers(dest="subcommand", help="stt サブコマンド")
    stt_subparsers.required = True
    
    # stt models
    models_parser = stt_subparsers.add_parser("models", help="利用可能なSTTモデル一覧表示")
    
    # stt transcribe
    transcribe_parser = stt_subparsers.add_parser("transcribe", help="音声ファイルの文字起こし")
    transcribe_parser.add_argument("file", help="音声ファイルのパス")
    transcribe_parser.add_argument("--language", help="言語コード（例: ja, en）")
    transcribe_parser.add_argument("--model", default="gpt-4o-transcribe", help="使用するモデル")
    transcribe_parser.add_argument("--vocabulary", help="カスタム語彙（カンマ区切り）")
    transcribe_parser.add_argument("--instructions", help="文字起こし指示")
    
    # stt chunk
    chunk_parser = stt_subparsers.add_parser("chunk", help="音声ファイルのチャンク分割テスト")
    chunk_parser.add_argument("file", help="音声ファイルのパス")
    
    sub_parsers["stt"] = stt_parser
    
    # llm サブコマンド
    llm_parser = subparsers.add_parser("llm", help="LLM機能テスト")
    llm_subparsers = llm_parser.add_subparsers(dest="subcommand", help="llm サブコマンド")
    llm_subparsers.required = True
    
    # llm models
    llm_models_parser = llm_subparsers.add_parser("models", help="利用可能なLLMモデル一覧表示")
    
    # llm process
    process_parser = llm_subparsers.add_parser("process", help="テキスト処理")
    process_parser.add_argument("text", help="処理するテキスト")
    process_parser.add_argument("--model", default="gpt-4o", help="使用するモデル")
    process_parser.add_argument("--instructions", help="処理指示")
    process_parser.add_argument("--image", help="画像ファイルのパス（マルチモーダル処理）")
    
    # llm stream
    stream_parser = llm_subparsers.add_parser("stream", help="ストリーミングレスポンステスト")
    stream_parser.add_argument("text", help="処理するテキスト")
    stream_parser.add_argument("--model", default="gpt-4o", help="使用するモデル")
    stream_parser.add_argument("--instructions", help="処理指示")
    
    sub_parsers["llm"] = llm_parser
    
    # pipelines サブコマンド
    pipelines_parser = subparsers.add_parser("pipelines", help="パイプライン機能テスト")
    pipelines_subparsers = pipelines_parser.add_subparsers(dest="subcommand", help="pipelines サブコマンド")
    pipelines_subparsers.required = True
    
    # pipelines process
    pipeline_process_parser = pipelines_subparsers.add_parser("process", help="音声ファイルのパイプライン処理")
    pipeline_process_parser.add_argument("file", help="音声ファイルのパス")
    pipeline_process_parser.add_argument("--language", help="言語コード（例: ja, en）")
    pipeline_process_parser.add_argument("--llm", action="store_true", help="LLM処理を有効化")
    pipeline_process_parser.add_argument("--llm-instructions", help="LLM処理指示")
    pipeline_process_parser.add_argument("--stt-model", default="gpt-4o-transcribe", help="STTモデル")
    pipeline_process_parser.add_argument("--llm-model", default="gpt-4o", help="LLMモデル")
    
    sub_parsers["pipelines"] = pipelines_parser
    
    # ui サブコマンド
    ui_parser = subparsers.add_parser("ui", help="UI関連機能テスト")
    ui_subparsers = ui_parser.add_subparsers(dest="subcommand", help="ui サブコマンド")
    ui_subparsers.required = True
    
    # ui hotkey
    hotkey_parser = ui_subparsers.add_parser("hotkey", help="ホットキー機能テスト")
    hotkey_subparsers = hotkey_parser.add_subparsers(dest="hotkey_command", help="hotkey サブコマンド")
    hotkey_subparsers.required = True
    
    # ui hotkey check
    hotkey_check_parser = hotkey_subparsers.add_parser("check", help="ホットキー有効性チェック")
    hotkey_check_parser.add_argument("hotkey", help="チェックするホットキー（例: ctrl+shift+r）")
    
    # ui hotkey listen
    hotkey_listen_parser = hotkey_subparsers.add_parser("listen", help="ホットキーリスニングテスト")
    hotkey_listen_parser.add_argument("--timeout", type=int, default=30, help="タイムアウト時間（秒）")
    hotkey_listen_parser.add_argument("--register", action="append", help="登録するホットキー（形式: KEY=ACTION）")
    
    sub_parsers["ui"] = ui_parser
    
    # utils サブコマンド
    utils_parser = subparsers.add_parser("utils", help="ユーティリティ機能テスト")
    utils_subparsers = utils_parser.add_subparsers(dest="subcommand", help="utils サブコマンド")
    utils_subparsers.required = True
    
    # utils instructions
    instructions_parser = utils_subparsers.add_parser("instructions", help="指示セット機能テスト")
    instructions_subparsers = instructions_parser.add_subparsers(dest="instructions_command", help="instructions サブコマンド")
    instructions_subparsers.required = True
    
    # utils instructions create
    instructions_create_parser = instructions_subparsers.add_parser("create", help="指示セット作成テスト")
    instructions_create_parser.add_argument("name", help="指示セット名")
    instructions_create_parser.add_argument("--vocabulary", help="カスタム語彙（カンマ区切り）")
    instructions_create_parser.add_argument("--instructions", help="指示")
    instructions_create_parser.add_argument("--language", help="言語コード（例: ja, en）")
    instructions_create_parser.add_argument("--llm-enabled", action="store_true", help="LLM処理を有効化")
    
    # utils instructions list
    instructions_list_parser = instructions_subparsers.add_parser("list", help="指示セット一覧表示")
    
    sub_parsers["utils"] = utils_parser
    
    # all サブコマンド（統合テスト）
    all_parser = subparsers.add_parser("all", help="統合テスト")
    all_parser.add_argument("file", help="テスト用音声ファイルのパス")
    all_parser.add_argument("--stt-only", action="store_true", help="STTのみテスト")
    all_parser.add_argument("--llm-only", action="store_true", help="LLMのみテスト")
    all_parser.add_argument("--language", default="ja", help="言語コード（例: ja, en）")
    
    sub_parsers["all"] = all_parser
    
    return sub_parsers


# モジュール別のハンドラー関数

def handle_recorder_command(args: argparse.Namespace) -> None:
    """recorder モジュールのコマンドハンドラー"""
    try:
        from new_core.recorder.audio_recorder import AudioRecorder
        
        if args.subcommand == "check":
            # マイク利用可能性確認
            available = AudioRecorder.check_microphone_availability()
            print(f"マイク利用可能: {'はい' if available else 'いいえ'}")
            
        elif args.subcommand == "list":
            # 利用可能なマイク一覧表示
            mics = AudioRecorder.get_available_microphones()
            if not mics:
                print("利用可能なマイクが見つかりませんでした")
            else:
                print(f"利用可能なマイク: {len(mics)}個")
                for i, mic in enumerate(mics):
                    print(f"[{i}] {mic.get('name', 'Unknown')}")
                    if args.verbose:
                        for key, value in mic.items():
                            if key != 'name':
                                print(f"    {key}: {value}")
            
        elif args.subcommand == "record":
            # 録音テスト
            recorder = AudioRecorder(sample_rate=args.sample_rate, channels=args.channels)
            
            if not recorder.check_microphone_availability():
                print("エラー: マイクが利用できません")
                return
            
            print(f"{args.duration}秒間の録音を開始します...")
            recorder.start_recording()
            
            # 進捗表示
            for i in range(args.duration):
                time.sleep(1)
                seconds_left = args.duration - i - 1
                print(f"残り {seconds_left}秒...", end="\r")
            
            print("\n録音を停止しています...")
            audio_path = recorder.stop_recording()
            
            if audio_path:
                print(f"録音完了: {audio_path}")
            else:
                print("録音に失敗しました")
    
    except ImportError as e:
        print(f"モジュール読み込みエラー: {e}")
    except Exception as e:
        print(f"エラー: {e}")


def handle_stt_command(args: argparse.Namespace) -> None:
    """stt モジュールのコマンドハンドラー"""
    try:
        if args.subcommand == "models":
            # 利用可能なSTTモデル一覧表示
            from new_core.stt.stt_model_manager import STTModelManager
            
            models = STTModelManager.get_available_models()
            print("利用可能なSTTモデル:")
            for model in models:
                print(f"- {model.name}: {model.description}")
        
        elif args.subcommand == "transcribe":
            # 音声ファイルの文字起こし
            from new_core.stt.stt_processor import STTProcessor
            
            # APIキーを取得
            api_key = args.api_key or os.getenv("OPENAI_API_KEY")
            if not api_key:
                print("エラー: APIキーが設定されていません。--api-key オプションまたは環境変数 OPENAI_API_KEY で設定してください。")
                return
            
            # ファイルの存在確認
            if not os.path.exists(args.file):
                print(f"エラー: ファイル {args.file} が見つかりません")
                return
            
            # STTProcessorの初期化
            processor = STTProcessor(api_key=api_key, model_id=args.model)
            
            # カスタム語彙の設定
            if args.vocabulary:
                vocabulary = [v.strip() for v in args.vocabulary.split(",")]
                processor.add_custom_vocabulary(vocabulary)
                if args.verbose:
                    print(f"カスタム語彙を設定: {vocabulary}")
            
            # 文字起こし指示の設定
            if args.instructions:
                processor.add_transcription_instruction(args.instructions)
                if args.verbose:
                    print(f"文字起こし指示を設定: {args.instructions}")
            
            # 文字起こし実行
            print(f"ファイル {args.file} の文字起こしを開始...")
            start_time = time.time()
            result = processor.transcribe(args.file, language=args.language)
            elapsed_time = time.time() - start_time
            
            # 結果表示
            print(f"\n=== 文字起こし結果 ({elapsed_time:.2f}秒) ===")
            print(result)
            print("===================================")
        
        elif args.subcommand == "chunk":
            # 音声ファイルのチャンク分割テスト
            from new_core.stt.audio_chunker import AudioChunker
            
            # ファイルの存在確認
            if not os.path.exists(args.file):
                print(f"エラー: ファイル {args.file} が見つかりません")
                return
            
            file_size_mb = os.path.getsize(args.file) / (1024 * 1024)
            print(f"ファイルサイズ: {file_size_mb:.2f}MB")
            
            # チャンク分割
            chunker = AudioChunker()
            print(f"ファイル {args.file} をチャンク分割しています...")
            chunks = chunker.chunk_audio_file(args.file)
            
            if not chunks:
                print("チャンク分割に失敗しました")
            else:
                print(f"チャンク分割成功: {len(chunks)}個のチャンクに分割")
                for i, chunk in enumerate(chunks):
                    chunk_size_mb = os.path.getsize(chunk) / (1024 * 1024)
                    print(f"チャンク {i+1}: {chunk} ({chunk_size_mb:.2f}MB)")
                
                # 一時ファイルの削除
                if args.verbose:
                    response = input("一時チャンクファイルを削除しますか？ (y/n): ")
                    if response.lower() == 'y':
                        chunker.remove_temp_chunks()
                        print("一時チャンクファイルを削除しました")
                else:
                    chunker.remove_temp_chunks()
                    print("一時チャンクファイルを削除しました")
    
    except ImportError as e:
        print(f"モジュール読み込みエラー: {e}")
    except Exception as e:
        print(f"エラー: {e}")


def handle_llm_command(args: argparse.Namespace) -> None:
    """llm モジュールのコマンドハンドラー"""
    try:
        if args.subcommand == "models":
            # 利用可能なLLMモデル一覧表示
            from new_core.llm.llm_model_manager import LLMModelManager
            
            models = LLMModelManager.get_available_models()
            print("利用可能なLLMモデル:")
            for model in models:
                print(f"- {model.name}: {model.description}")
        
        elif args.subcommand == "process":
            # テキスト処理
            from new_core.llm.llm_processor import LLMProcessor
            
            # APIキーを取得
            api_key = args.api_key or os.getenv("OPENAI_API_KEY")
            if not api_key:
                print("エラー: APIキーが設定されていません。--api-key オプションまたは環境変数 OPENAI_API_KEY で設定してください。")
                return
            
            # LLMProcessorの初期化
            processor = LLMProcessor(api_key=api_key, model_id=args.model)
            
            # 処理指示の設定
            if args.instructions:
                processor.add_system_instruction(args.instructions)
                if args.verbose:
                    print(f"処理指示を設定: {args.instructions}")
            
            # 画像データの読み込み
            image_data = None
            if args.image:
                if not os.path.exists(args.image):
                    print(f"エラー: 画像ファイル {args.image} が見つかりません")
                    return
                
                with open(args.image, "rb") as f:
                    image_data = f.read()
                    if args.verbose:
                        print(f"画像ファイル {args.image} を読み込みました")
            
            # テキスト処理実行
            print("テキスト処理を開始...")
            start_time = time.time()
            result = processor.process_text(args.text, image_data=image_data)
            elapsed_time = time.time() - start_time
            
            # 結果表示
            print(f"\n=== 処理結果 ({elapsed_time:.2f}秒) ===")
            print(result)
            print("===================================")
        
        elif args.subcommand == "stream":
            # ストリーミングレスポンステスト
            from new_core.llm.llm_processor import LLMProcessor
            
            # APIキーを取得
            api_key = args.api_key or os.getenv("OPENAI_API_KEY")
            if not api_key:
                print("エラー: APIキーが設定されていません。--api-key オプションまたは環境変数 OPENAI_API_KEY で設定してください。")
                return
            
            # LLMProcessorの初期化
            processor = LLMProcessor(api_key=api_key, model_id=args.model)
            
            # 処理指示の設定
            if args.instructions:
                processor.add_system_instruction(args.instructions)
                if args.verbose:
                    print(f"処理指示を設定: {args.instructions}")
            
            # ストリーミングコールバック
            def stream_callback(chunk: str) -> None:
                print(chunk, end="", flush=True)
            
            # ストリーミング処理実行
            print("ストリーミングレスポンスを開始...\n")
            start_time = time.time()
            processor.process_with_stream(args.text, callback=stream_callback)
            elapsed_time = time.time() - start_time
            
            # 完了表示
            print(f"\n\n=== ストリーミング完了 ({elapsed_time:.2f}秒) ===")
    
    except ImportError as e:
        print(f"モジュール読み込みエラー: {e}")
    except Exception as e:
        print(f"エラー: {e}")


def handle_pipelines_command(args: argparse.Namespace) -> None:
    """pipelines モジュールのコマンドハンドラー"""
    try:
        if args.subcommand == "process":
            # 音声ファイルのパイプライン処理
            from new_core.pipelines.stt_llm_pipeline import STTLLMPipeline
            
            # APIキーを取得
            api_key = args.api_key or os.getenv("OPENAI_API_KEY")
            if not api_key:
                print("エラー: APIキーが設定されていません。--api-key オプションまたは環境変数 OPENAI_API_KEY で設定してください。")
                return
            
            # ファイルの存在確認
            if not os.path.exists(args.file):
                print(f"エラー: ファイル {args.file} が見つかりません")
                return
            
            # パイプラインの初期化
            pipeline = STTLLMPipeline(
                api_key=api_key,
                stt_model_id=args.stt_model,
                llm_model_id=args.llm_model
            )
            
            # LLM処理の有効化設定
            pipeline.enable_llm_processing(args.llm)
            
            # LLM指示の設定
            if args.llm_instructions and args.llm:
                pipeline.add_llm_instruction(args.llm_instructions)
                if args.verbose:
                    print(f"LLM指示を設定: {args.llm_instructions}")
            
            # パイプライン処理実行
            print(f"ファイル {args.file} のパイプライン処理を開始...")
            start_time = time.time()
            result = pipeline.process(args.file, language=args.language)
            elapsed_time = time.time() - start_time
            
            # 結果表示
            print(f"\n=== パイプライン処理結果 ({elapsed_time:.2f}秒) ===")
            print("\n【文字起こし結果】")
            print(result.transcription)
            
            if result.llm_processed and result.llm_response:
                print("\n【LLM処理結果】")
                print(result.llm_response)
            
            print("===================================")
    
    except ImportError as e:
        print(f"モジュール読み込みエラー: {e}")
    except Exception as e:
        print(f"エラー: {e}")


def handle_ui_command(args: argparse.Namespace) -> None:
    """ui モジュールのコマンドハンドラー"""
    try:
        if args.subcommand == "hotkey":
            from new_core.ui.hot_key_manager import HotKeyManager
            
            if args.hotkey_command == "check":
                # ホットキー有効性チェック
                hotkey_manager = HotKeyManager()
                parsed_hotkey = hotkey_manager.parse_hotkey_string(args.hotkey)
                
                if parsed_hotkey:
                    print(f"ホットキー '{args.hotkey}' は有効です")
                    print(f"パース結果: {parsed_hotkey}")
                else:
                    print(f"ホットキー '{args.hotkey}' は無効です")
            
            elif args.hotkey_command == "listen":
                # ホットキーリスニングテスト
                hotkey_manager = HotKeyManager()
                
                # 登録するホットキー
                if args.register:
                    for reg in args.register:
                        parts = reg.split("=", 1)
                        if len(parts) == 2:
                            key, action_name = parts
                            # アクション名に応じたコールバック関数を定義
                            def create_callback(name):
                                return lambda: print(f"ホットキー '{name}' が押されました")
                            
                            callback = create_callback(action_name)
                            success = hotkey_manager.register_hotkey(key, callback)
                            
                            if success:
                                print(f"ホットキー '{key}' を '{action_name}' として登録しました")
                            else:
                                print(f"ホットキー '{key}' の登録に失敗しました")
                
                # 終了用のホットキー
                def exit_callback():
                    print("終了ホットキーが押されました")
                    global should_exit
                    should_exit = True
                
                global should_exit
                should_exit = False
                hotkey_manager.register_hotkey("ctrl+shift+q", exit_callback)
                print("終了するには Ctrl+Shift+Q を押してください")
                
                # リスニング開始
                print(f"ホットキーリスニングを {args.timeout} 秒間開始します...")
                start_time = time.time()
                
                while not should_exit and (time.time() - start_time < args.timeout):
                    time.sleep(0.1)
                
                # 終了処理
                hotkey_manager.stop_listening()
                print("ホットキーリスニングを終了しました")
    
    except ImportError as e:
        print(f"モジュール読み込みエラー: {e}")
    except Exception as e:
        print(f"エラー: {e}")


def handle_utils_command(args: argparse.Namespace) -> None:
    """utils モジュールのコマンドハンドラー"""
    try:
        if args.subcommand == "instructions":
            from new_core.utils.instruction_manager import InstructionManager
            
            if args.instructions_command == "create":
                # 指示セット作成テスト
                manager = InstructionManager()
                
                # 語彙リストの作成
                vocabulary = []
                if args.vocabulary:
                    vocabulary = [v.strip() for v in args.vocabulary.split(",")]
                
                # 指示の作成
                instructions = []
                if args.instructions:
                    instructions = [args.instructions]
                
                # 指示セットの作成
                success = manager.create_set(
                    name=args.name,
                    vocabulary=vocabulary,
                    instructions=instructions,
                    language=args.language,
                    llm_enabled=args.llm_enabled
                )
                
                if success:
                    print(f"指示セット '{args.name}' を作成しました")
                    print("内容:")
                    print(f"- 語彙: {vocabulary}")
                    print(f"- 指示: {instructions}")
                    print(f"- 言語: {args.language or '自動検出'}")
                    print(f"- LLM有効: {args.llm_enabled}")
                    
                    # 保存
                    if manager.save_instructions(args.name):
                        print(f"指示セット '{args.name}' を保存しました")
                    else:
                        print(f"指示セット '{args.name}' の保存に失敗しました")
                else:
                    print(f"指示セット '{args.name}' の作成に失敗しました")
            
            elif args.instructions_command == "list":
                # 指示セット一覧表示
                manager = InstructionManager()
                manager.load_instructions()
                
                sets = manager.get_available_instruction_sets()
                if not sets:
                    print("指示セットが見つかりませんでした")
                else:
                    print(f"利用可能な指示セット: {len(sets)}個")
                    for i, name in enumerate(sets):
                        instruction_set = manager.sets[name]
                        print(f"[{i+1}] {name}")
                        print(f"  - 語彙: {instruction_set.vocabulary}")
                        print(f"  - 指示: {instruction_set.instructions}")
                        print(f"  - 言語: {instruction_set.language or '自動検出'}")
                        print(f"  - LLM有効: {instruction_set.llm_enabled}")
                        if instruction_set.llm_enabled:
                            print(f"  - LLM指示: {instruction_set.llm_instructions}")
                            print(f"  - LLMモデル: {instruction_set.llm_model}")
    
    except ImportError as e:
        print(f"モジュール読み込みエラー: {e}")
    except Exception as e:
        print(f"エラー: {e}")


def handle_all_command(args: argparse.Namespace) -> None:
    """統合テストのコマンドハンドラー"""
    try:
        # ファイルの存在確認
        if not os.path.exists(args.file):
            print(f"エラー: ファイル {args.file} が見つかりません")
            return
        
        # APIキーを取得
        api_key = args.api_key or os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("エラー: APIキーが設定されていません。--api-key オプションまたは環境変数 OPENAI_API_KEY で設定してください。")
            return
        
        # 進捗追跡用カウンタ
        total_tests = 0
        passed_tests = 0
        
        # 結果記録用辞書
        results = {}
        
        print("=== Open Super Whisper V2 統合テスト開始 ===")
        
        # STTモデルのテスト
        if not args.llm_only:
            from new_core.stt.stt_processor import STTProcessor
            
            try:
                print("\n--- STT モジュールテスト ---")
                total_tests += 1
                
                # STTProcessorの初期化
                processor = STTProcessor(api_key=api_key)
                
                # 文字起こし実行
                print(f"ファイル {args.file} の文字起こしを開始...")
                start_time = time.time()
                transcription = processor.transcribe(args.file, language=args.language)
                elapsed_time = time.time() - start_time
                
                # 結果表示
                print(f"文字起こし完了 ({elapsed_time:.2f}秒)")
                results["stt"] = {
                    "success": True,
                    "elapsed_time": elapsed_time,
                    "transcription": transcription
                }
                passed_tests += 1
            
            except Exception as e:
                print(f"STTモジュールテスト失敗: {e}")
                results["stt"] = {
                    "success": False,
                    "error": str(e)
                }
        
        # LLMモデルのテスト
        if not args.stt_only:
            from new_core.llm.llm_processor import LLMProcessor
            
            try:
                print("\n--- LLM モジュールテスト ---")
                total_tests += 1
                
                # テスト用テキスト
                test_text = "次の長所と短所を3点ずつ箇条書きにしてください。「Pythonプログラミング言語」"
                if "stt" in results and results["stt"]["success"]:
                    # 文字起こし結果があれば、それを要約する指示にする
                    test_text = f"次のテキストを3点要約してください: {results['stt']['transcription']}"
                
                # LLMProcessorの初期化
                processor = LLMProcessor(api_key=api_key)
                
                # テキスト処理実行
                print("テキスト処理を開始...")
                start_time = time.time()
                llm_response = processor.process_text(test_text)
                elapsed_time = time.time() - start_time
                
                # 結果表示
                print(f"テキスト処理完了 ({elapsed_time:.2f}秒)")
                results["llm"] = {
                    "success": True,
                    "elapsed_time": elapsed_time,
                    "response": llm_response
                }
                passed_tests += 1
            
            except Exception as e:
                print(f"LLMモジュールテスト失敗: {e}")
                results["llm"] = {
                    "success": False,
                    "error": str(e)
                }
        
        # パイプラインのテスト
        if not args.stt_only and not args.llm_only:
            from new_core.pipelines.stt_llm_pipeline import STTLLMPipeline
            
            try:
                print("\n--- Pipeline モジュールテスト ---")
                total_tests += 1
                
                # パイプラインの初期化
                pipeline = STTLLMPipeline(api_key=api_key)
                
                # LLM処理の有効化
                pipeline.enable_llm_processing(True)
                pipeline.add_llm_instruction("テキストを3行程度で要約してください")
                
                # パイプライン処理実行
                print(f"ファイル {args.file} のパイプライン処理を開始...")
                start_time = time.time()
                result = pipeline.process(args.file, language=args.language)
                elapsed_time = time.time() - start_time
                
                # 結果表示
                print(f"パイプライン処理完了 ({elapsed_time:.2f}秒)")
                results["pipeline"] = {
                    "success": True,
                    "elapsed_time": elapsed_time,
                    "transcription": result.transcription,
                    "llm_processed": result.llm_processed,
                    "llm_response": result.llm_response
                }
                passed_tests += 1
            
            except Exception as e:
                print(f"パイプラインモジュールテスト失敗: {e}")
                results["pipeline"] = {
                    "success": False,
                    "error": str(e)
                }
        
        # テスト結果のまとめ
        print("\n=== テスト結果サマリー ===")
        print(f"実行テスト数: {total_tests}")
        print(f"成功: {passed_tests}")
        print(f"失敗: {total_tests - passed_tests}")
        
        # 詳細結果表示
        print("\n=== 詳細結果 ===")
        
        if "stt" in results:
            if results["stt"]["success"]:
                print("\n【STTモジュールテスト】: 成功")
                print(f"実行時間: {results['stt']['elapsed_time']:.2f}秒")
                if args.verbose:
                    print("文字起こし結果:")
                    print(results["stt"]["transcription"])
            else:
                print("\n【STTモジュールテスト】: 失敗")
                print(f"エラー: {results['stt']['error']}")
        
        if "llm" in results:
            if results["llm"]["success"]:
                print("\n【LLMモジュールテスト】: 成功")
                print(f"実行時間: {results['llm']['elapsed_time']:.2f}秒")
                if args.verbose:
                    print("LLM処理結果:")
                    print(results["llm"]["response"])
            else:
                print("\n【LLMモジュールテスト】: 失敗")
                print(f"エラー: {results['llm']['error']}")
        
        if "pipeline" in results:
            if results["pipeline"]["success"]:
                print("\n【パイプラインモジュールテスト】: 成功")
                print(f"実行時間: {results['pipeline']['elapsed_time']:.2f}秒")
                print(f"LLM処理: {'実行済み' if results['pipeline']['llm_processed'] else '未実行'}")
                if args.verbose:
                    print("文字起こし結果:")
                    print(results["pipeline"]["transcription"])
                    if results["pipeline"]["llm_processed"]:
                        print("\nLLM処理結果:")
                        print(results["pipeline"]["llm_response"])
            else:
                print("\n【パイプラインモジュールテスト】: 失敗")
                print(f"エラー: {results['pipeline']['error']}")
        
        print("\n===========================")
    
    except ImportError as e:
        print(f"モジュール読み込みエラー: {e}")
    except Exception as e:
        print(f"統合テストエラー: {e}")


def main():
    """メイン関数"""
    parser = setup_common_parser()
    sub_parsers = setup_subparsers(parser)
    
    # コマンドライン引数の解析
    args = parser.parse_args()
    
    # サブコマンドに応じたハンドラーの呼び出し
    if args.command == "recorder":
        handle_recorder_command(args)
    elif args.command == "stt":
        handle_stt_command(args)
    elif args.command == "llm":
        handle_llm_command(args)
    elif args.command == "pipelines":
        handle_pipelines_command(args)
    elif args.command == "ui":
        handle_ui_command(args)
    elif args.command == "utils":
        handle_utils_command(args)
    elif args.command == "all":
        handle_all_command(args)


if __name__ == "__main__":
    main()
