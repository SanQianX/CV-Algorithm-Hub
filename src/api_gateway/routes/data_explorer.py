# -*- coding: utf-8 -*-
"""
Data Explorer API Routes - 数据目录浏览器API
功能：浏览K盘数据目录结构、文件预览、数据库内容查看
"""

import os
import sqlite3
import json
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime

from fastapi import APIRouter, HTTPException, Query, Header
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/explorer", tags=["explorer"])

# K盘数据根目录 - 根据环境选择正确的路径
import os
if os.environ.get("IN_DOCKER", "").lower() == "true":
    DATA_ROOT = "/app/data"
else:
    DATA_ROOT = "K:/data/databases"


# ========== Pydantic Models ==========

class DirectoryItem(BaseModel):
    """目录项"""
    name: str
    path: str
    type: str  # directory, file
    size: Optional[int] = None
    modified: Optional[str] = None
    children_count: Optional[int] = None


class DirectoryTreeNode(BaseModel):
    """目录树节点"""
    name: str
    path: str
    type: str
    size: Optional[int] = None
    children: Optional[List['DirectoryTreeNode']] = None
    expanded: bool = False


class DatabaseInfo(BaseModel):
    """数据库信息"""
    name: str
    path: str
    db_type: str  # postgresql, sqlite
    size: int
    table_count: int
    tables: List[Dict[str, Any]]


class TablePreview(BaseModel):
    """表预览"""
    table_name: str
    row_count: int
    columns: List[Dict[str, Any]]
    sample_data: List[Dict[str, Any]]
    date_range: Optional[Dict[str, str]] = None


class FinanceRecord(BaseModel):
    """金融数据记录（简化版）"""
    id: str
    code: str
    name: Optional[str] = None
    date: Optional[str] = None
    value: Optional[float] = None
    change_percent: Optional[float] = None


# ========== 辅助函数 ==========

def get_file_size(path: str) -> int:
    """获取文件大小"""
    try:
        if os.path.isfile(path):
            return os.path.getsize(path)
    except Exception:
        pass
    return 0


def get_file_modified(path: str) -> str:
    """获取文件修改时间"""
    try:
        if os.path.exists(path):
            return datetime.fromtimestamp(os.path.getmtime(path)).isoformat()
    except Exception:
        pass
    return None


def build_directory_tree(path: str, max_depth: int = 3, current_depth: int = 0) -> List[DirectoryTreeNode]:
    """递归获取目录树"""
    if current_depth >= max_depth:
        return []

    nodes = []
    try:
        items = sorted(os.listdir(path), key=str.lower)
        for item in items:
            item_path = os.path.join(path, item)
            if os.path.isdir(item_path):
                # 检查是否是数据库目录
                has_db = False
                children = []
                try:
                    sub_items = os.listdir(item_path)
                    for sub in sub_items:
                        sub_path = os.path.join(item_path, sub)
                        if os.path.isfile(sub_path) and sub.endswith('.db'):
                            has_db = True
                        elif os.path.isdir(sub_path):
                            # 检查是否是 postgres 目录
                            if (sub == 'postgresql' or
                                os.path.exists(os.path.join(sub_path, 'PG_VERSION'))):
                                has_db = True
                    if current_depth < max_depth - 1:
                        children = build_directory_tree(item_path, max_depth, current_depth + 1)
                except Exception:
                    pass

                node = DirectoryTreeNode(
                    name=item,
                    path=item_path,
                    type="directory",
                    children=children if children else None
                )
                nodes.append(node)
            elif os.path.isfile(item_path) and item.endswith('.db'):
                nodes.append(DirectoryTreeNode(
                    name=item,
                    path=item_path,
                    type="file",
                    size=get_file_size(item_path)
                ))
    except Exception as e:
        logger.error(f"获取目录树失败: {e}")
    return nodes


def get_sqlite_tables(db_path: str) -> List[Dict[str, Any]]:
    """获取SQLite数据库的所有表"""
    tables = []
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # 获取所有表
        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name NOT LIKE 'sqlite_%'
            ORDER BY name
        """)
        for row in cursor.fetchall():
            table_name = row['name']

            # 获取表记录数
            try:
                cursor.execute(f"SELECT COUNT(*) as count FROM {table_name}")
                count = cursor.fetchone()['count']
            except:
                count = 0

            # 获取列信息
            try:
                cursor.execute(f"PRAGMA table_info({table_name})")
                columns = []
                for col in cursor.fetchall():
                    columns.append({
                        'name': col[1],
                        'type': col[2],
                        'nullable': bool(col[3])
                    })
            except:
                columns = []

            tables.append({
                'name': table_name,
                'row_count': count,
                'columns': columns
            })

        conn.close()
    except Exception as e:
        logger.error(f"获取SQLite表失败: {e}")
    return tables


def get_table_sample_data(db_path: str, table_name: str, limit: int = 10) -> List[Dict[str, Any]]:
    """获取表样本数据"""
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute(f"SELECT * FROM {table_name} LIMIT ?", (limit,))
        rows = cursor.fetchall()

        result = []
        for row in rows:
            row_dict = {}
            for key in row.keys():
                val = row[key]
                if isinstance(val, bytes):
                    val = val.hex()
                row_dict[key] = val
            result.append(row_dict)

        conn.close()
        return result
    except Exception as e:
        logger.error(f"获取表样本数据失败: {e}")
        return []


def get_date_range(db_path: str, table_name: str, date_column: str = 'date') -> Optional[Dict[str, str]]:
    """获取表数据的日期范围"""
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute(f"SELECT MIN({date_column}) as min_date, MAX({date_column}) as max_date FROM {table_name}")
        row = cursor.fetchone()

        conn.close()

        if row['min_date']:
            return {
                'start': row['min_date'],
                'end': row['max_date']
            }
    except Exception:
        pass
    return None


def find_database_path(db_name: str) -> Optional[str]:
    """查找数据库文件路径"""
    search_paths = [
        os.path.join(DATA_ROOT, f"{db_name}.db"),  # finance.db
        os.path.join(DATA_ROOT, db_name, f"{db_name}.db"),  # finance/finance.db
        os.path.join(DATA_ROOT, db_name),  # finance (directory or file)
    ]

    for p in search_paths:
        if os.path.exists(p):
            return p
    return None


def get_finance_data_summary(db_path: str, table_type: str) -> Dict[str, Any]:
    """获取金融数据摘要"""
    summary = {
        'total_records': 0,
        'funds': [],
        'stocks': [],
        'date_range': None
    }

    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # 基金历史表
        if table_type == 'finance':
            cursor.execute("SELECT COUNT(*) as count FROM fund_history")
            summary['total_records'] = cursor.fetchone()['count']

            # 获取基金代码列表
            cursor.execute("SELECT DISTINCT code FROM fund_history LIMIT 20")
            for row in cursor.fetchall():
                summary['funds'].append({
                    'code': row['code'],
                    'records': 0
                })

            # 股票历史表
            cursor.execute("SELECT COUNT(*) as count FROM stock_history")
            stock_count = cursor.fetchone()['count']
            summary['total_records'] += stock_count

            cursor.execute("SELECT DISTINCT code FROM stock_history LIMIT 20")
            for row in cursor.fetchall():
                summary['stocks'].append({
                    'code': row['code'],
                    'records': 0
                })

            # 获取日期范围
            try:
                cursor.execute("SELECT MIN(date) as min_date, MAX(date) as max_date FROM fund_history")
                row = cursor.fetchone()
                if row['min_date']:
                    summary['date_range'] = {
                        'start': row['min_date'],
                        'end': row['max_date']
                    }
            except:
                pass

        conn.close()
    except Exception as e:
        logger.error(f"获取金融数据摘要失败: {e}")

    return summary


# ========== API 端点 ==========

@router.get("/tree")
def get_directory_tree(
    path: Optional[str] = Query(None, description="目录路径，默认K盘数据根目录"),
    depth: int = Query(3, ge=1, le=5, description="树深度"),
    authorization: str = Header(None)
):
    """获取目录树结构"""
    target_path = path or DATA_ROOT

    if not os.path.exists(target_path):
        raise HTTPException(status_code=404, detail=f"路径不存在: {target_path}")

    if not os.path.isdir(target_path):
        raise HTTPException(status_code=400, detail=f"不是目录: {target_path}")

    try:
        tree = build_directory_tree(target_path, max_depth=depth)
        return {
            "success": True,
            "path": target_path,
            "tree": tree
        }
    except Exception as e:
        logger.error(f"获取目录树失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取目录树失败: {str(e)}")


@router.get("/directories", response_model=List[DirectoryItem])
def list_directories(
    path: Optional[str] = Query(None, description="目录路径"),
    authorization: str = Header(None)
):
    """列出目录内容"""
    target_path = path or DATA_ROOT

    if not os.path.exists(target_path):
        raise HTTPException(status_code=404, detail=f"路径不存在: {target_path}")

    items = []
    try:
        for item in sorted(os.listdir(target_path), key=str.lower):
            item_path = os.path.join(target_path, item)
            if os.path.isdir(item_path):
                try:
                    children_count = len(os.listdir(item_path))
                except:
                    children_count = 0

                items.append(DirectoryItem(
                    name=item,
                    path=item_path,
                    type="directory",
                    children_count=children_count,
                    modified=get_file_modified(item_path)
                ))
            elif os.path.isfile(item_path):
                if item.endswith('.db'):
                    items.append(DirectoryItem(
                        name=item,
                        path=item_path,
                        type="file",
                        size=get_file_size(item_path),
                        modified=get_file_modified(item_path)
                    ))
    except Exception as e:
        logger.error(f"列出目录失败: {e}")
        raise HTTPException(status_code=500, detail=f"列出目录失败: {str(e)}")

    return items


@router.get("/database/{db_name}", response_model=DatabaseInfo)
def get_database_info(
    db_name: str,
    authorization: str = Header(None)
):
    """获取数据库信息"""
    db_path = find_database_path(db_name)

    if not db_path:
        raise HTTPException(status_code=404, detail=f"数据库不存在: {db_name}")

    if not os.path.isfile(db_path):
        raise HTTPException(status_code=400, detail=f"不是数据库文件: {db_path}")

    try:
        tables = get_sqlite_tables(db_path)
        size = get_file_size(db_path)

        return DatabaseInfo(
            name=db_name,
            path=db_path,
            db_type="sqlite",
            size=size,
            table_count=len(tables),
            tables=tables
        )
    except Exception as e:
        logger.error(f"获取数据库信息失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取数据库信息失败: {str(e)}")


@router.get("/database/{db_name}/tables/{table_name}/preview", response_model=TablePreview)
def preview_table(
    db_name: str,
    table_name: str,
    limit: int = Query(20, ge=1, le=100),
    authorization: str = Header(None)
):
    """预览表数据"""
    db_path = find_database_path(db_name)

    if not db_path:
        raise HTTPException(status_code=404, detail=f"数据库不存在: {db_name}")

    try:
        tables = get_sqlite_tables(db_path)
        table_info = None
        for t in tables:
            if t['name'] == table_name:
                table_info = t
                break

        if not table_info:
            raise HTTPException(status_code=404, detail=f"表不存在: {table_name}")

        sample_data = get_table_sample_data(db_path, table_name, limit)
        date_range = get_date_range(db_path, table_name, 'date')

        return TablePreview(
            table_name=table_name,
            row_count=table_info['row_count'],
            columns=table_info['columns'],
            sample_data=sample_data,
            date_range=date_range
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"预览表失败: {e}")
        raise HTTPException(status_code=500, detail=f"预览表失败: {str(e)}")


@router.get("/database/{db_name}/tables/{table_name}/data")
def get_table_data(
    db_name: str,
    table_name: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=500),
    authorization: str = Header(None)
):
    """分页获取表数据"""
    db_path = find_database_path(db_name)

    if not db_path:
        raise HTTPException(status_code=404, detail=f"数据库不存在: {db_name}")

    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # 获取总数
        cursor.execute(f"SELECT COUNT(*) as total FROM {table_name}")
        total = cursor.fetchone()['total']

        # 获取分页数据
        offset = (page - 1) * page_size
        cursor.execute(f"SELECT * FROM {table_name} LIMIT ? OFFSET ?", (page_size, offset))
        rows = cursor.fetchall()

        columns = []
        if rows:
            for key in rows[0].keys():
                columns.append(key)

        data = []
        for row in rows:
            row_dict = {}
            for key in columns:
                val = row[key]
                if isinstance(val, bytes):
                    val = val.hex()
                row_dict[key] = val
            data.append(row_dict)

        conn.close()

        return {
            "success": True,
            "table": table_name,
            "page": page,
            "page_size": page_size,
            "total": total,
            "total_pages": (total + page_size - 1) // page_size,
            "columns": columns,
            "data": data
        }
    except Exception as e:
        logger.error(f"获取表数据失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取表数据失败: {str(e)}")


@router.get("/database/{db_name}/finance-summary")
def get_finance_summary(
    db_name: str = "finance",
    authorization: str = Header(None)
):
    """获取金融数据摘要"""
    db_path = find_database_path(db_name)

    if not db_path:
        raise HTTPException(status_code=404, detail=f"金融数据库不存在: {db_name}")

    try:
        summary = get_finance_data_summary(db_path, 'finance')

        # 获取基金详情
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) as count FROM fund_details")
        fund_details_count = cursor.fetchone()['count']

        conn.close()

        return {
            "success": True,
            "database": db_name,
            "total_records": summary['total_records'],
            "fund_details_count": fund_details_count,
            "fund_codes": summary['funds'],
            "stock_codes": summary['stocks'],
            "date_range": summary['date_range']
        }
    except Exception as e:
        logger.error(f"获取金融摘要失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取金融摘要失败: {str(e)}")


@router.get("/database/{db_name}/finance-records")
def get_finance_records(
    db_name: str = "finance",
    record_type: str = Query("fund", description="记录类型: fund 或 stock"),
    code: Optional[str] = Query(None, description="基金/股票代码"),
    start_date: Optional[str] = Query(None, description="开始日期"),
    end_date: Optional[str] = Query(None, description="结束日期"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=500),
    authorization: str = Header(None)
):
    """获取金融数据记录"""
    db_path = find_database_path(db_name)

    if not db_path:
        raise HTTPException(status_code=404, detail=f"金融数据库不存在: {db_name}")

    table = "fund_history" if record_type == "fund" else "stock_history"
    code_column = "code"

    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # 构建查询条件
        conditions = []
        params = []

        if code:
            conditions.append(f"{code_column} = ?")
            params.append(code)

        if start_date:
            conditions.append("date >= ?")
            params.append(start_date)

        if end_date:
            conditions.append("date <= ?")
            params.append(end_date)

        where_clause = " AND ".join(conditions) if conditions else "1=1"

        # 获取总数
        cursor.execute(f"SELECT COUNT(*) as total FROM {table} WHERE {where_clause}", tuple(params))
        total = cursor.fetchone()['total']

        # 获取分页数据
        offset = (page - 1) * page_size
        query = f"SELECT * FROM {table} WHERE {where_clause} ORDER BY date DESC LIMIT ? OFFSET ?"
        cursor.execute(query, tuple(params + [page_size, offset]))
        rows = cursor.fetchall()

        # 构建响应
        data = []
        for row in rows:
            record = {
                "id": row['id'],
                "code": row['code'],
                "date": row['date']
            }

            if record_type == "fund":
                record["nav"] = row['nav']
                record["nav_change"] = row['nav_change']
                record["nav_change_percent"] = row['nav_change_percent']
            else:
                record["open"] = row['open']
                record["high"] = row['high']
                record["low"] = row['low']
                record["close"] = row['close']
                record["volume"] = row['volume']

            data.append(record)

        conn.close()

        return {
            "success": True,
            "type": record_type,
            "page": page,
            "page_size": page_size,
            "total": total,
            "total_pages": (total + page_size - 1) // page_size,
            "data": data
        }
    except Exception as e:
        logger.error(f"获取金融记录失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取金融记录失败: {str(e)}")


@router.get("/stats")
def get_explorer_stats(authorization: str = Header(None)):
    """获取数据目录统计信息"""
    stats = {
        "total_size": 0,
        "databases": [],
        "total_tables": 0,
        "total_records": 0
    }

    if not os.path.exists(DATA_ROOT):
        return {"success": True, **stats}

    try:
        for item in os.listdir(DATA_ROOT):
            item_path = os.path.join(DATA_ROOT, item)
            if os.path.isdir(item_path):
                db_file = os.path.join(item_path, f"{item}.db")
                if os.path.exists(db_file):
                    size = get_file_size(db_file)
                    tables = get_sqlite_tables(db_file)
                    record_count = sum(t['row_count'] for t in tables)

                    stats["total_size"] += size
                    stats["databases"].append({
                        "name": item,
                        "size": size,
                        "table_count": len(tables),
                        "record_count": record_count
                    })
                    stats["total_tables"] += len(tables)
                    stats["total_records"] += record_count

        return {
            "success": True,
            **stats
        }
    except Exception as e:
        logger.error(f"获取统计信息失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取统计信息失败: {str(e)}")


@router.get("/search")
def search_data(
    keyword: str = Query(..., description="搜索关键词"),
    db_type: Optional[str] = Query(None, description="数据库类型过滤"),
    authorization: str = Header(None)
):
    """搜索数据"""
    results = []
    keyword_lower = keyword.lower()

    if not os.path.exists(DATA_ROOT):
        return {"success": True, "results": results}

    try:
        for item in os.listdir(DATA_ROOT):
            item_path = os.path.join(DATA_ROOT, item)
            if os.path.isdir(item_path):
                db_file = os.path.join(item_path, f"{item}.db")
                if os.path.exists(db_file):
                    # 检查数据库名是否匹配
                    if keyword_lower in item.lower():
                        tables = get_sqlite_tables(db_file)
                        for table in tables:
                            if keyword_lower in table['name'].lower():
                                results.append({
                                    "type": "table",
                                    "database": item,
                                    "table": table['name'],
                                    "row_count": table['row_count'],
                                    "path": db_file
                                })

                    # 检查表名和列名
                    tables = get_sqlite_tables(db_file)
                    for table in tables:
                        if keyword_lower in table['name'].lower():
                            if not any(r['table'] == table['name'] and r['database'] == item for r in results):
                                results.append({
                                    "type": "table",
                                    "database": item,
                                    "table": table['name'],
                                    "row_count": table['row_count'],
                                    "path": db_file
                                })

                        for col in table['columns']:
                            if keyword_lower in col['name'].lower():
                                results.append({
                                    "type": "column",
                                    "database": item,
                                    "table": table['name'],
                                    "column": col['name'],
                                    "column_type": col['type'],
                                    "path": db_file
                                })

        return {
            "success": True,
            "keyword": keyword,
            "count": len(results),
            "results": results
        }
    except Exception as e:
        logger.error(f"搜索失败: {e}")
        raise HTTPException(status_code=500, detail=f"搜索失败: {str(e)}")
