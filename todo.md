# ホットキーダイアログ修正タスク

## 問題分析と現状理解
- [x] ホットキーダイアログとインストラクションセットダイアログのホットキー無効化処理の確認
  - [x] `hotkey_dialog.py`の`showEvent`では`HotkeyBridge.instance().set_recording_mode(True, None)`を呼び出している
  - [x] `instruction_sets_dialog.py`も同様に`showEvent`でホットキーを無効化している
  - [x] これらのダイアログでは`closeEvent`や`accept`/`reject`時に`HotkeyBridge.instance().set_recording_mode(False)`でホットキーを再有効化している
- [x] システムログの動作不具合の分析
  - [x] ログでは「Disabled all hotkeys while hotkey dialog is open」と出力されているが、実際にはホットキーが反応している

## 修正計画
- [ ] デバッグ用のログ追加
  - [ ] `HotkeyBridge`の`set_recording_mode`メソッドにより詳細なログを追加
  - [ ] `HotkeyManager`の`start_listener`と`stop_listener`にデバッグ情報を追加
- [ ] ホットキー無効化の改善
  - [ ] `HotkeyBridge`の実装を再確認し、必要に応じて修正
  - [ ] `set_recording_mode`の処理フローで問題がないか確認
- [ ] テスト検証
  - [ ] 修正後の動作確認
  - [ ] ダイアログ表示中のホットキー動作検証
