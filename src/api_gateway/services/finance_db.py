# -*- coding: utf-8 -*-
"""
SQLite Finance Database Service
金融数据 SQLite 服务模块
"""

import sqlite3
import json
import uuid
import logging
from datetime import datetime
from typing import List, Optional, Dict, Any
from pathlib import Path
import os

logger = logging.getLogger(__name__)


class FinanceDatabaseService:
    """金融数据 SQLite 服务"""

    def __init__(self, db_path: str = None):
        if db_path is None:
            if os.environ.get("IN_DOCKER", "").lower() == "true":
                db_path = "/app/data/finance.db"
            else:
                db_path = "K:/data/databases/finance/finance.db"
        self.db_path = db_path
        self._ensure_database()

    def _ensure_database(self):
        """确保数据库存在"""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self._get_connection()

    def _get_connection(self) -> sqlite3.Connection:
        """获取数据库连接"""
        if not hasattr(self, '_conn') or self._conn is None:
            self._conn = sqlite3.connect(self.db_path)
            self._conn.row_factory = sqlite3.Row
            self._conn.execute("PRAGMA foreign_keys = ON")
        return self._conn

    def close(self):
        """关闭数据库连接"""
        if hasattr(self, '_conn') and self._conn:
            self._conn.close()
            self._conn = None

    def execute(self, query: str, params: tuple = None) -> sqlite3.Cursor:
        """执行 SQL 查询"""
        conn = self._get_connection()
        if params:
            return conn.execute(query, params)
        return conn.execute(query)

    def commit(self):
        """提交事务"""
        self._get_connection().commit()

    def fetch_one(self, query: str, params: tuple = None) -> Optional[sqlite3.Row]:
        """查询单条记录"""
        cursor = self.execute(query, params)
        result = cursor.fetchone()
        return result

    def fetch_all(self, query: str, params: tuple = None) -> List[sqlite3.Row]:
        """查询多条记录"""
        cursor = self.execute(query, params)
        return cursor.fetchall()

    # ========== Fund History Operations ==========
    # 列名: id, code, date, nav, nav_change, nav_change_percent, created_at

    def get_fund_history(self, fund_code: str = None, limit: int = 100) -> List[Dict[str, Any]]:
        """获取基金历史数据"""
        if fund_code:
            query = "SELECT * FROM fund_history WHERE code = ? ORDER BY date DESC LIMIT ?"
            rows = self.fetch_all(query, (fund_code, limit))
        else:
            query = "SELECT * FROM fund_history ORDER BY date DESC LIMIT ?"
            rows = self.fetch_all(query, (limit,))

        return [self._fund_row_to_dict(row) for row in rows]

    def add_fund_history(self, fund_code: str, nav: float, record_date: str,
                         nav_change: float = None, nav_change_percent: float = None,
                         fund_name: str = None, **extra) -> str:
        """添加基金历史记录"""
        record_id = str(uuid.uuid4())
        query = """
            INSERT INTO fund_history
            (id, code, date, nav, nav_change, nav_change_percent, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        now = datetime.now().isoformat()

        self.execute(query, (
            record_id, fund_code, record_date, nav,
            nav_change, nav_change_percent, now
        ))
        self.commit()
        return record_id

    def update_fund_history(self, record_id: str, **kwargs) -> bool:
        """更新基金历史记录"""
        if not kwargs:
            return False

        allowed_fields = ['nav', 'nav_change', 'nav_change_percent']
        updates = {k: v for k, v in kwargs.items() if k in allowed_fields}
        if not updates:
            return False

        set_clause = ', '.join([f"{k} = ?" for k in updates.keys()])
        values = list(updates.values()) + [record_id]

        query = f"UPDATE fund_history SET {set_clause} WHERE id = ?"
        self.execute(query, tuple(values))
        self.commit()
        return self.execute("SELECT changes()").fetchone()[0] > 0

    def delete_fund_history(self, record_id: str) -> bool:
        """删除基金历史记录"""
        query = "DELETE FROM fund_history WHERE id = ?"
        self.execute(query, (record_id,))
        self.commit()
        return self.execute("SELECT changes()").fetchone()[0] > 0

    # ========== Stock History Operations ==========
    # 列名: id, code, date, open, high, low, close, volume, amount, created_at

    def get_stock_history(self, stock_code: str = None, limit: int = 100) -> List[Dict[str, Any]]:
        """获取股票历史数据"""
        if stock_code:
            query = "SELECT * FROM stock_history WHERE code = ? ORDER BY date DESC LIMIT ?"
            rows = self.fetch_all(query, (stock_code, limit))
        else:
            query = "SELECT * FROM stock_history ORDER BY date DESC LIMIT ?"
            rows = self.fetch_all(query, (limit,))

        return [self._stock_row_to_dict(row) for row in rows]

    def add_stock_history(self, stock_code: str, close_price: float, record_date: str,
                          open_price: float = None, high_price: float = None,
                          low_price: float = None, volume: int = None,
                          amount: float = None, **extra) -> str:
        """添加股票历史记录"""
        record_id = str(uuid.uuid4())
        query = """
            INSERT INTO stock_history
            (id, code, date, open, high, low, close, volume, amount, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        now = datetime.now().isoformat()

        self.execute(query, (
            record_id, stock_code, record_date, open_price, high_price,
            low_price, close_price, volume, amount, now
        ))
        self.commit()
        return record_id

    def update_stock_history(self, record_id: str, **kwargs) -> bool:
        """更新股票历史记录"""
        if not kwargs:
            return False

        allowed_fields = ['open', 'high', 'low', 'close', 'volume', 'amount']
        updates = {k: v for k, v in kwargs.items() if k in allowed_fields}
        if not updates:
            return False

        set_clause = ', '.join([f"{k} = ?" for k in updates.keys()])
        values = list(updates.values()) + [record_id]

        query = f"UPDATE stock_history SET {set_clause} WHERE id = ?"
        self.execute(query, tuple(values))
        self.commit()
        return self.execute("SELECT changes()").fetchone()[0] > 0

    def delete_stock_history(self, record_id: str) -> bool:
        """删除股票历史记录"""
        query = "DELETE FROM stock_history WHERE id = ?"
        self.execute(query, (record_id,))
        self.commit()
        return self.execute("SELECT changes()").fetchone()[0] > 0

    # ========== Fund Details Operations ==========
    # 列名: id, code, name, full_name, fund_type, establishment_date, asset_scale, tracking_target,
    #       nav, nav_date, acc_nav, acc_nav_date, estimated_nav, estimated_nav_change_percent,
    #       subscription_fee, redemption_fee, management_fee, custodian_fee, service_fee,
    #       company, manager, custodian, purchase_status, redemption_status, risk_level,
    #       created_at, updated_at

    def get_fund_details(self, fund_code: str = None) -> List[Dict[str, Any]]:
        """获取基金详情"""
        if fund_code:
            query = "SELECT * FROM fund_details WHERE code = ?"
            rows = self.fetch_all(query, (fund_code,))
        else:
            query = "SELECT * FROM fund_details"
            rows = self.fetch_all(query)

        return [self._fund_detail_row_to_dict(row) for row in rows]

    def add_fund_detail(self, fund_code: str, fund_name: str = None,
                        fund_type: str = None, manager: str = None,
                        establish_date: str = None, nav: float = None, **extra) -> str:
        """添加基金详情"""
        record_id = str(uuid.uuid4())
        query = """
            INSERT INTO fund_details
            (id, code, name, fund_type, manager, establishment_date, nav, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        now = datetime.now().isoformat()

        self.execute(query, (
            record_id, fund_code, fund_name, fund_type, manager,
            establish_date, nav, now
        ))
        self.commit()
        return record_id

    def update_fund_detail(self, record_id: str, **kwargs) -> bool:
        """更新基金详情"""
        if not kwargs:
            return False

        allowed_fields = ['name', 'fund_type', 'manager', 'establishment_date', 'nav']
        updates = {k: v for k, v in kwargs.items() if k in allowed_fields}
        if not updates:
            return False

        set_clause = ', '.join([f"{k} = ?" for k in updates.keys()])
        values = list(updates.values()) + [record_id]

        query = f"UPDATE fund_details SET {set_clause} WHERE id = ?"
        self.execute(query, tuple(values))
        self.commit()
        return self.execute("SELECT changes()").fetchone()[0] > 0

    def delete_fund_detail(self, record_id: str) -> bool:
        """删除基金详情"""
        query = "DELETE FROM fund_details WHERE id = ?"
        self.execute(query, (record_id,))
        self.commit()
        return self.execute("SELECT changes()").fetchone()[0] > 0

    # ========== Statistics ==========

    def get_stats(self) -> Dict[str, int]:
        """获取统计数据"""
        stats = {}
        for table in ['fund_history', 'stock_history', 'fund_details']:
            try:
                result = self.fetch_one(f"SELECT COUNT(*) as count FROM {table}")
                stats[table] = result['count'] if result else 0
            except:
                stats[table] = 0
        return stats

    # ========== Row Converters ==========

    def _fund_row_to_dict(self, row: sqlite3.Row) -> Dict[str, Any]:
        """将基金历史 Row 转换为字典"""
        if row is None:
            return None
        return {
            'id': row['id'],
            'fund_code': row['code'],
            'record_date': row['date'],
            'nav': row['nav'],
            'nav_change': row['nav_change'],
            'nav_change_percent': row['nav_change_percent'],
            'created_at': row['created_at']
        }

    def _stock_row_to_dict(self, row: sqlite3.Row) -> Dict[str, Any]:
        """将股票历史 Row 转换为字典"""
        if row is None:
            return None
        return {
            'id': row['id'],
            'stock_code': row['code'],
            'record_date': row['date'],
            'open_price': row['open'],
            'high_price': row['high'],
            'low_price': row['low'],
            'close_price': row['close'],
            'volume': row['volume'],
            'amount': row['amount'],
            'change_percent': None,
            'created_at': row['created_at']
        }

    def _fund_detail_row_to_dict(self, row: sqlite3.Row) -> Dict[str, Any]:
        """将基金详情 Row 转换为字典"""
        if row is None:
            return None
        return {
            'id': row['id'],
            'fund_code': row['code'],
            'fund_name': row['name'],
            'full_name': row['full_name'],
            'fund_type': row['fund_type'],
            'establish_date': row['establishment_date'],
            'asset_scale': row['asset_scale'],
            'tracking_target': row['tracking_target'],
            'nav': row['nav'],
            'nav_date': row['nav_date'],
            'acc_nav': row['acc_nav'],
            'acc_nav_date': row['acc_nav_date'],
            'estimated_nav': row['estimated_nav'],
            'estimated_nav_change_percent': row['estimated_nav_change_percent'],
            'subscription_fee': row['subscription_fee'],
            'redemption_fee': row['redemption_fee'],
            'management_fee': row['management_fee'],
            'custodian_fee': row['custodian_fee'],
            'service_fee': row['service_fee'],
            'company': row['company'],
            'manager': row['manager'],
            'custodian': row['custodian'],
            'purchase_status': row['purchase_status'],
            'redemption_status': row['redemption_status'],
            'risk_level': row['risk_level'],
            'created_at': row['created_at'],
            'updated_at': row['updated_at']
        }


# 全局服务实例
_finance_service: Optional[FinanceDatabaseService] = None


def get_finance_service() -> FinanceDatabaseService:
    """获取金融数据库服务单例"""
    global _finance_service
    if _finance_service is None:
        if os.environ.get("IN_DOCKER", "").lower() == "true":
            db_path = "/app/data/finance.db"
        else:
            db_path = "K:/data/databases/finance/finance.db"
        _finance_service = FinanceDatabaseService(db_path)
    return _finance_service
