# 録音状態表示改善タスク

## 1. 現状調査と要件の詳細化
- [x] UIUpdaterの現在の実装を確認
- [x] labelsの管理方法を確認
- [x] 関連するUI部分の実装を確認
- [x] 外部から注入する仕組みの検討
  - `resources/labels.py`に録音状態と停止状態のラベルを追加
  - `UIUpdater`クラスの`update_recording_indicator`メソッドを修正して、ハードコードされたテキストをラベルからのテキストに置き換える
  - 色の指定はユーザー要件通りに削除する

## 2. 録音状態表示修正の実装
- [x] `resources/labels.py`のAppLabelsクラスに録音状態と停止状態のラベルを追加
  - 既存の`STATUS_RECORDING_INDICATOR`の代わりに、録音時と停止時のラベルを分けて定義する
- [x] `UIUpdater`クラスの`update_recording_indicator`メソッドを修正
  - ~~色の設定を削除~~
  - ~~ハードコードされたテキストをAppLabelsから取得するように変更~~
  - メソッドシグネチャを変更して、ブール値ではなく表示テキストを直接受け取るように変更
- [x] `main_window.py`の`update_recording_status`メソッドを修正
  - 条件に応じて適切なラベルを引数として渡すように変更
- [x] テスト実施と動作確認（コードレビューによる確認）

## 3. 最終確認とまとめ
- [x] 変更箇所の最終レビュー
- [x] 変更内容のまとめ

## 実装概要

本タスクでは以下の改善を行いました：

1. 録音状態表示をタイマーと同様に外部から注入可能な仕組みに変更
   - これまでの実装：
     - `update_recording_indicator`メソッドに渡すのは`is_recording`というブール値だけ
     - メソッド内部で条件に応じてハードコードされた文字列を表示
   - 変更後：
     - `update_recording_indicator`メソッドに表示したいテキストを直接渡す
     - 呼び出し側で条件に応じて`AppLabels`から適切なラベルを選択して渡す

2. 主な変更箇所：
   - `labels.py`: ラベル定数の追加
     - `STATUS_RECORDING_INDICATOR_RECORDING = "●REC"`
     - `STATUS_RECORDING_INDICATOR_STOPPED = "■STOP"`
   - `ui_updater.py`: メソッドシグネチャの変更
     - `update_recording_indicator(self, is_recording: bool)` → `update_recording_indicator(self, text: str)`
   - `main_window.py`: メソッド呼び出し部分の変更
     - `ui_updater.update_recording_indicator(is_recording)` → `ui_updater.update_recording_indicator(AppLabels.STATUS_RECORDING_INDICATOR_XXX)`

3. 色の設定の削除
   - 要件に従い、色の設定（赤と灰色）を削除

これにより、タイマーと同様に録音ステータスの表示テキストも外部から注入可能になりました。将来的にテキストを変更したい場合は、`labels.py`のラベル定数を編集するだけで対応できます。
