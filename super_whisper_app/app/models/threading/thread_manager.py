"""
スレッドマネージャー実装

このモジュールはQtアプリケーションでスレッド間の安全な通信のための
中央スレッド管理システムを提供します。
"""

from PyQt6.QtCore import QObject, pyqtSignal, QMetaObject, Qt, QTimer
from typing import Callable, Any, Dict, Optional
import time
import uuid

from .task_worker import TaskWorker

class ThreadManager(QObject):
    """
    スレッド間の安全な通信と操作を管理するクラス
    
    このクラスはQtのスレッドモデルに基づいて、安全なスレッド間通信と操作を提供します。
    """
    
    # シグナル定義
    taskCompleted = pyqtSignal(str, object)  # task_id, result
    taskFailed = pyqtSignal(str, str)        # task_id, error_message
    statusUpdate = pyqtSignal(str, int)      # status_message, timeout_ms
    processingComplete = pyqtSignal(object)  # processing_result
    timerUpdate = pyqtSignal(str)            # time_string
    streamUpdate = pyqtSignal(str)           # stream_chunk
    
    # 内部シグナル
    _execute_in_main_thread = pyqtSignal(object, tuple, dict)  # func, args, kwargs
    
    def __init__(self):
        """
        ThreadManagerを初期化
        """
        super().__init__()
        
        # タイマー関連
        self._recording_timer = None
        self._recording_start_time = 0
        
        # タスク関連
        self._current_tasks = {}
        
        # 内部シグナル接続
        self._setup_internal_connections()
    
    def _setup_internal_connections(self):
        """
        内部シグナル/スロット接続を設定
        """
        # タスク完了/エラー処理
        self.taskCompleted.connect(self._handle_task_completed, Qt.ConnectionType.QueuedConnection)
        self.taskFailed.connect(self._handle_task_failed, Qt.ConnectionType.QueuedConnection)
        
        # メインスレッド実行シグナルを接続
        self._execute_in_main_thread.connect(self._execute_function, Qt.ConnectionType.QueuedConnection)
    
    def _execute_function(self, func: Callable, args: tuple, kwargs: dict) -> None:
        """
        与えられた引数で関数をメインスレッドで実行します。
        
        Parameters
        ----------
        func : Callable
            実行する関数
        args : tuple
            位置引数
        kwargs : dict
            キーワード引数
        """
        try:
            func(*args, **kwargs)
        except Exception as e:
            print(f"Error in main thread execution: {e}")
    
    def run_in_main_thread(self, func: Callable, *args, delay_ms=0, **kwargs) -> None:
        """
        関数をメインスレッドで実行
        
        Parameters
        ----------
        func : Callable
            実行する関数
        *args
            関数に渡す位置引数
        delay_ms : int, optional
            関数を実行する前の遅延（ミリ秒）
        **kwargs
            関数に渡すキーワード引数
        """
        if delay_ms > 0:
            # QTimerを使用して遅延実行
            timer = QTimer(self)
            timer.setSingleShot(True)
            timer.timeout.connect(lambda: self._execute_in_main_thread.emit(func, args, kwargs))
            timer.start(delay_ms)
        else:
            # 即時実行（スレッドの安全性のためにシグナル経由）
            self._execute_in_main_thread.emit(func, args, kwargs)
    
    def run_in_worker_thread(self, task_id: str, func: Callable, *args, callback=None, **kwargs) -> str:
        """
        関数をワーカースレッドで実行
        
        Parameters
        ----------
        task_id : str
            タスク識別子
        func : Callable
            実行する関数
        *args
            関数に渡す位置引数
        callback : Optional[Callable], optional
            タスクが完了したときに結果で呼び出す関数
        **kwargs
            関数に渡すキーワード引数
            
        Returns
        -------
        str
            タスクID
        """
        # タスクIDが指定されていなければ生成
        if not task_id:
            task_id = f"task_{uuid.uuid4().hex[:8]}"
        
        # TaskWorkerを作成して実行
        worker = TaskWorker(task_id, func, args, kwargs)
        
        # シグナルを接続
        def handle_task_completed(tid, result):
            self.taskCompleted.emit(tid, result)
            if callback and tid == task_id:
                # スレッドの安全性のためにコールバックをメインスレッドで実行
                self.run_in_main_thread(callback, result)
        
        worker.taskCompleted.connect(
            handle_task_completed,
            Qt.ConnectionType.QueuedConnection
        )
        worker.taskFailed.connect(
            lambda tid, error: self.taskFailed.emit(tid, error),
            Qt.ConnectionType.QueuedConnection
        )
        
        # 現在のタスクに追加
        self._current_tasks[task_id] = worker
        
        # タスクを開始
        worker.start()
        
        return task_id
    
    def _handle_task_completed(self, task_id: str, result: Any) -> None:
        """
        タスク完了のハンドラ
        
        Parameters
        ----------
        task_id : str
            タスクID
        result : Any
            タスク結果
        """
        # タスクのクリーンアップ
        if task_id in self._current_tasks:
            self._current_tasks[task_id].deleteLater()
            del self._current_tasks[task_id]
    
    def _handle_task_failed(self, task_id: str, error: str) -> None:
        """
        タスクエラーのハンドラ
        
        Parameters
        ----------
        task_id : str
            タスクID
        error : str
            エラーメッセージ
        """
        # タスクのクリーンアップ
        if task_id in self._current_tasks:
            self._current_tasks[task_id].deleteLater()
            del self._current_tasks[task_id]
    
    def update_status(self, message: str, timeout: int = 0) -> None:
        """
        ステータスバーを安全に更新
        
        Parameters
        ----------
        message : str
            表示するメッセージ
        timeout : int, optional
            表示時間（ミリ秒）、0で永続表示
        """
        # ステータス更新シグナルを発行
        self.statusUpdate.emit(message, timeout)
    
    def start_recording_timer(self) -> None:
        """
        録音タイマーを開始
        """
        self._recording_start_time = time.time()
        
        # タイマーが存在しなければ作成
        if not self._recording_timer:
            self._recording_timer = QTimer(self)
            self._recording_timer.timeout.connect(self._update_recording_time)
        
        # タイマーを開始
        self._recording_timer.start(1000)  # 1秒ごとに更新

    def stop_recording_timer(self) -> None:
        """
        録音タイマーを停止
        """
        if self._recording_timer and self._recording_timer.isActive():
            self._recording_timer.stop()
    
    def _update_recording_time(self) -> None:
        """
        録音時間を更新
        """
        # 経過時間を計算して表示
        elapsed = int(time.time() - self._recording_start_time)
        minutes = elapsed // 60
        seconds = elapsed % 60
        time_str = f"{minutes:02d}:{seconds:02d}"
        
        # タイマー更新シグナルを発行
        self.timerUpdate.emit(time_str)
        
    def update_stream(self, chunk: str) -> None:
        """
        LLMストリーミング更新を送信
        
        Parameters
        ----------
        chunk : str
            LLMストリーミングレスポンスからのテキストチャンク
        """
        self.streamUpdate.emit(chunk)
