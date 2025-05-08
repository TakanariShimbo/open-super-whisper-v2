"""
タスクワーカー実装

このモジュールは長時間実行タスクを別スレッドで実行するためのワーカークラスを提供し、
タスク完了と失敗の適切なシグナル処理を行います。
"""

from PyQt6.QtCore import QObject, QThread, pyqtSignal
from typing import Callable, Dict, Any, Tuple

class TaskWorker(QThread):
    """
    長時間実行タスクを処理するワーカークラス
    
    このクラスはQThreadを継承して、関数を別スレッドで実行し、
    結果をシグナルで通知します。
    """
    
    # シグナル定義
    taskCompleted = pyqtSignal(str, object)  # task_id, result
    taskFailed = pyqtSignal(str, str)       # task_id, error_message
    
    def __init__(self, task_id: str, func: Callable, args: Tuple, kwargs: Dict[str, Any]):
        """
        TaskWorkerを初期化
        
        Parameters
        ----------
        task_id : str
            タスク識別子
        func : Callable
            実行する関数
        args : Tuple
            関数の位置引数
        kwargs : Dict[str, Any]
            関数のキーワード引数
        """
        super().__init__()
        
        self.task_id = task_id
        self.func = func
        self.args = args
        self.kwargs = kwargs
    
    def run(self) -> None:
        """
        スレッド実行プロセス
        
        関数を実行し、結果またはエラーをシグナルで通知します。
        """
        try:
            # 関数を実行
            result = self.func(*self.args, **self.kwargs)
            
            # 完了シグナルを発行
            self.taskCompleted.emit(self.task_id, result)
            
        except Exception as e:
            # エラーシグナルを発行
            error_msg = f"Error in task {self.task_id}: {str(e)}"
            print(error_msg)
            self.taskFailed.emit(self.task_id, str(e))
