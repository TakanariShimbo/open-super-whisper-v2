# スレッドマネージメント移行タスク

## スレッドマネージメントディレクトリをGUIディレクトリ内に移動
- [x] 現在の構造とファイル間の依存関係を分析
- [ ] スレッドマネージメントディレクトリをGUIディレクトリ内に移動
- [ ] インポートパスの更新
- [ ] 移行後の動作確認
- [ ] ドキュメント（READMEなど）の更新

## 依存関係分析結果
- 外部からの依存関係:
  - `gui/windows/main_window.py`で`thread_management.thread_manager`と`thread_management.ui_updater`をインポート
  - `gui/dialogs/hotkey_dialog.py`で`thread_management.hotkey_bridge`をインポート
  - `gui/dialogs/instruction_sets_dialog.py`で`thread_management.hotkey_bridge`をインポート

- 内部での依存関係:
  - `thread_management/thread_manager.py`内で`thread_management.workers.task_worker`と`thread_management.hotkey_bridge`をインポート
  - `workers/task_worker.py`はスレッドの実行に使用
  - `hotkey_bridge.py`はホットキー処理のブリッジとして使用
  - `ui_updater.py`はUIの更新を管理

## 移動計画
1. `thread_management`ディレクトリを`gui`ディレクトリ内に移動
2. 参照しているすべてのファイルのインポートパスを更新
   - `gui/windows/main_window.py`
   - `gui/dialogs/hotkey_dialog.py`
   - `gui/dialogs/instruction_sets_dialog.py`
   - 新しい場所の`gui/thread_management/thread_manager.py`内部のインポート
3. ドキュメントの更新（READMEなど）
