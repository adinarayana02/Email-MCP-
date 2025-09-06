import csv
import threading
from datetime import datetime
from hashlib import md5
from typing import Dict, List, Optional

from app.config import settings
from app.utils.email_utils import EmailUtils


class DatasetService:
    """In-memory dataset loader and cache for CSV/Excel emails.

    Thread-safe cache with lazy load and refresh support.
    """

    def __init__(self, dataset_path: Optional[str] = None):
        self._dataset_path = dataset_path or settings.dataset_path or "./Support_Emails_Dataset.csv"
        self._lock = threading.Lock()
        self._cache: List[Dict] = []
        self._last_loaded_at: Optional[datetime] = None

    @property
    def dataset_path(self) -> str:
        return self._dataset_path

    def set_dataset_path(self, path: str) -> None:
        with self._lock:
            self._dataset_path = path
            self._cache = []
            self._last_loaded_at = None

    def load(self, force: bool = False) -> List[Dict]:
        """Load dataset into memory. Uses cache unless forced."""
        with self._lock:
            if self._cache and not force:
                return list(self._cache)
            self._cache = self._read_csv(self._dataset_path)
            self._last_loaded_at = datetime.now()
            return list(self._cache)

    def refresh(self) -> List[Dict]:
        """Force reload dataset from disk."""
        return self.load(force=True)

    def get_emails(self, skip: int = 0, limit: Optional[int] = None) -> List[Dict]:
        data = self.load()
        if limit is None:
            return data[skip:]
        return data[skip: skip + limit]

    def _read_csv(self, path: str) -> List[Dict]:
        rows: List[Dict] = []
        try:
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    sender = row.get('sender') or row.get('from') or row.get('email')
                    subject = row.get('subject')
                    body = row.get('body')
                    date_val = row.get('sent_date') or row.get('date') or row.get('received_date')
                    if not sender or not subject:
                        continue
                    if not self._contains_support_keywords(str(subject).lower()):
                        continue
                    received_date = self._parse_date(date_val)
                    key = f"{sender}|{subject}|{received_date.isoformat()}"
                    email_id = md5(key.encode('utf-8')).hexdigest()
                    rows.append({
                        'email_id': email_id,
                        'sender': str(sender),
                        'subject': str(subject),
                        'body': EmailUtils.clean_email_text(str(body or "")),
                        'received_date': received_date,
                        'processed': True
                    })
        except Exception:
            # Return best-effort partial data
            return rows
        return rows

    def _parse_date(self, date_val) -> datetime:
        if not date_val:
            return datetime.now()
        # Try common formats; fallback to now
        for fmt in (
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d",
            "%d/%m/%Y %H:%M",
            "%m/%d/%Y %H:%M",
            "%d-%b-%Y",
            "%d/%m/%Y",
            "%m/%d/%Y",
        ):
            try:
                return datetime.strptime(str(date_val), fmt)
            except Exception:
                continue
        try:
            return datetime.fromisoformat(str(date_val))
        except Exception:
            return datetime.now()

    def _contains_support_keywords(self, text: str) -> bool:
        return any(keyword in text for keyword in settings.support_keywords)


