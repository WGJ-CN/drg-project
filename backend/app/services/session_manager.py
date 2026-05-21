from typing import Dict, Optional
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
        # 存储确认前的快照，用于比对
        self.confirmed_slots: Optional[dict] = None

    def update_slots(self, **kwargs):
        """更新槽位，并返回是否所有必填字段已填"""
        if "main_diag" in kwargs: self.main_diag = kwargs["main_diag"]
        if "other_diags" in kwargs: self.other_diags = kwargs["other_diags"]
        if "main_proc" in kwargs: self.main_proc = kwargs["main_proc"]
        if "other_procs" in kwargs: self.other_procs = kwargs["other_procs"]
        if "age_days" in kwargs: self.age_days = kwargs["age_days"]
        self.last_updated = time.time()
        return self.is_complete()

    def is_complete(self) -> bool:
        """检查是否所有必填字段都已填（主诊断和年龄必填，手术可选）"""
        return self.main_diag is not None and self.age_days is not None

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