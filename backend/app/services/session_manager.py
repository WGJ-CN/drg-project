from typing import Dict, Optional, List
import time

class Session:
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.main_diag: Optional[str] = None
        self.other_diags: list[str] = []
        self.main_proc: Optional[str] = None
        self.other_procs: list[str] = []
        self.age_days: Optional[int] = None
        self.status = "COLLECTING"  # COLLECTING / AWAITING_CONFIRMATION / DONE
        self.last_updated = time.time()
        self.confirmed_slots: Optional[dict] = None

    def update_slots(self, **kwargs):
        """更新槽位，并返回是否所有必填字段已填。只有非空值才会更新。"""
        if "main_diag" in kwargs and kwargs["main_diag"]:
            self.main_diag = kwargs["main_diag"]
        if "other_diags" in kwargs and kwargs["other_diags"]:
            self.other_diags = kwargs["other_diags"]
        if "main_proc" in kwargs and kwargs["main_proc"]:
            self.main_proc = kwargs["main_proc"]
        if "other_procs" in kwargs and kwargs["other_procs"]:
            self.other_procs = kwargs["other_procs"]
        if "age_days" in kwargs and kwargs["age_days"]:
            self.age_days = kwargs["age_days"]
        self.last_updated = time.time()
        return self.is_complete()

    def is_complete(self) -> bool:
        """检查是否所有必填字段都已填（主诊断和年龄必填，手术可选）"""
        return self.main_diag is not None and self.age_days is not None

    def clear_slots(self, fields: List[str] = None):
        """清除指定字段，如果不指定则清除所有字段"""
        if fields is None:
            self.main_diag = None
            self.other_diags = []
            self.main_proc = None
            self.other_procs = []
            self.age_days = None
        else:
            if "main_diag" in fields:
                self.main_diag = None
            if "other_diags" in fields:
                self.other_diags = []
            if "main_proc" in fields:
                self.main_proc = None
            if "other_procs" in fields:
                self.other_procs = []
            if "age_days" in fields:
                self.age_days = None
        self.last_updated = time.time()

    def get_slots_summary(self) -> dict:
        """获取当前槽位摘要"""
        return {
            "main_diag": self.main_diag,
            "other_diags": self.other_diags,
            "main_proc": self.main_proc,
            "other_procs": self.other_procs,
            "age_days": self.age_days,
        }

    def to_dict(self) -> dict:
        return {
            "main_diag": self.main_diag,
            "other_diags": self.other_diags,
            "main_proc": self.main_proc,
            "other_procs": self.other_procs,
            "age_days": self.age_days,
        }

class SessionManager:
    def __init__(self):
        self._sessions: Dict[str, Session] = {}

    def get_session(self, session_id: str) -> Session:
        if session_id not in self._sessions:
            self._sessions[session_id] = Session(session_id)
        return self._sessions[session_id]

    def delete_session(self, session_id: str):
        self._sessions.pop(session_id, None)

session_manager = SessionManager()
