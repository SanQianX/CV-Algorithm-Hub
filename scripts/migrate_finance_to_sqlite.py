# -*- coding: utf-8 -*-
"""
PostgreSQL to SQLite Migration Script
将金融数据从 PostgreSQL 迁移到 SQLite
"""

import sqlite3
import yaml
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker
import json
from datetime import datetime
import os


class PostgresToSQLiteMigrator:
    """PostgreSQL 到 SQLite 迁移器"""

    def __init__(self, pg_url: str, sqlite_path: str):
        self.pg_url = pg_url
        self.sqlite_path = sqlite_path

        # PostgreSQL 连接
        self.pg_engine = create_engine(pg_url)
        self.pg_session = sessionmaker(bind=self.pg_engine)

        # SQLite 连接
        self.sqlite_conn = None

    def connect_sqlite(self):
        """连接 SQLite（自动创建数据库文件）"""
        os.makedirs(os.path.dirname(self.sqlite_path), exist_ok=True)
        self.sqlite_conn = sqlite3.connect(self.sqlite_path)
        self.sqlite_conn.row_factory = sqlite3.Row
        print(f"[成功] 连接到 SQLite: {self.sqlite_path}")

    def close_sqlite(self):
        """关闭 SQLite 连接"""
        if self.sqlite_conn:
            self.sqlite_conn.close()

    def get_pg_table_schema(self, table_name: str) -> list:
        """获取 PostgreSQL 表结构"""
        inspector = inspect(self.pg_engine)
        columns = inspector.get_columns(table_name)
        return columns

    def create_sqlite_table(self, table_name: str, columns: list):
        """在 SQLite 中创建表"""
        # 转换 PostgreSQL 类型到 SQLite 类型
        type_mapping = {
            'VARCHAR': 'TEXT',
            'CHARACTER VARYING': 'TEXT',
            'TEXT': 'TEXT',
            'INTEGER': 'INTEGER',
            'BIGINT': 'INTEGER',
            'SMALLINT': 'INTEGER',
            'NUMERIC': 'REAL',
            'DECIMAL': 'REAL',
            'REAL': 'REAL',
            'FLOAT': 'REAL',
            'DOUBLE PRECISION': 'REAL',
            'BOOLEAN': 'INTEGER',
            'DATE': 'TEXT',
            'TIMESTAMP': 'TEXT',
            'TIME': 'TEXT',
            'JSON': 'TEXT',
            'JSONB': 'TEXT',
            'UUID': 'TEXT',
        }

        column_defs = []
        for col in columns:
            pg_type = str(col['type']).upper().split('(')[0]
            sqlite_type = type_mapping.get(pg_type, 'TEXT')

            col_def = f"{col['name']} {sqlite_type}"

            # 处理主键
            if col.get('primary_key', False):
                col_def += " PRIMARY KEY"

            # 处理非空
            if not col.get('nullable', True):
                col_def += " NOT NULL"

            column_defs.append(col_def)

        create_sql = f"CREATE TABLE IF NOT EXISTS {table_name} (\n    "
        create_sql += ",\n    ".join(column_defs)
        create_sql += "\n)"

        self.sqlite_conn.execute(create_sql)
        self.sqlite_conn.commit()
        print(f"  [创建表] {table_name}")

    def migrate_table(self, table_name: str) -> int:
        """迁移单个表的数据"""
        print(f"  迁移表: {table_name}")

        # 读取 PostgreSQL 数据
        pg_session = self.pg_session()
        try:
            result = pg_session.execute(text(f"SELECT * FROM {table_name}"))
            rows = result.fetchall()
            columns = result.keys()
            print(f"    读取 {len(rows)} 条记录")

            if not rows:
                return 0

            # 转换数据
            sqlite_rows = []
            for row in rows:
                sqlite_row = {}
                for i, col in enumerate(columns):
                    value = row[i]
                    if isinstance(value, datetime):
                        value = value.isoformat()
                    elif isinstance(value, dict):
                        value = json.dumps(value, ensure_ascii=False)
                    elif isinstance(value, list):
                        value = json.dumps(value, ensure_ascii=False)
                    sqlite_row[col] = value
                sqlite_rows.append(sqlite_row)

            # 插入 SQLite
            placeholders = ', '.join(['?' for _ in columns])
            insert_sql = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})"

            for row in sqlite_rows:
                values = [row.get(col) for col in columns]
                self.sqlite_conn.execute(insert_sql, values)

            self.sqlite_conn.commit()
            print(f"    插入 {len(sqlite_rows)} 条记录")

            return len(sqlite_rows)

        finally:
            pg_session.close()

    def migrate_all(self, tables: list) -> dict:
        """迁移所有表"""
        print("\n" + "=" * 60)
        print("开始数据迁移")
        print("=" * 60)

        # 连接 SQLite
        self.connect_sqlite()

        stats = {}
        for table_name in tables:
            print(f"\n处理表: {table_name}")

            # 获取表结构
            columns = self.get_pg_table_schema(table_name)

            # 创建表
            self.create_sqlite_table(table_name, columns)

            # 迁移数据
            count = self.migrate_table(table_name)
            stats[table_name] = count

        # 创建元数据表
        self.create_metadata_table()

        self.close_sqlite()

        print("\n" + "=" * 60)
        print("迁移完成!")
        print("=" * 60)
        for table, count in stats.items():
            print(f"  {table}: {count} 条记录")

        return stats

    def create_metadata_table(self):
        """创建迁移元数据表"""
        self.sqlite_conn.execute("""
            CREATE TABLE IF NOT EXISTS _migration_log (
                table_name TEXT PRIMARY KEY,
                migrated_at TEXT,
                record_count INTEGER
            )
        """)
        self.sqlite_conn.commit()

    def log_migration(self, table_name: str, count: int):
        """记录迁移日志"""
        self.sqlite_conn.execute(
            "INSERT OR REPLACE INTO _migration_log VALUES (?, ?, ?)",
            (table_name, datetime.now().isoformat(), count)
        )
        self.sqlite_conn.commit()


def main():
    """主函数"""
    print("=" * 60)
    print("PostgreSQL -> SQLite 迁移脚本")
    print("=" * 60)

    # PostgreSQL 连接
    pg_url = "postgresql://postgres:postgres@postgres:5432/cv_algorithm_hub"

    # SQLite 路径
    sqlite_path = "K:/data/databases/finance/finance.db"

    # 要迁移的表
    tables = [
        "fund_history",
        "stock_history",
        "fund_details"
    ]

    # 创建迁移器
    migrator = PostgresToSQLiteMigrator(pg_url, sqlite_path)

    try:
        # 执行迁移
        stats = migrator.migrate_all(tables)

        print(f"\n数据已迁移到: {sqlite_path}")
        print("\n后续步骤:")
        print("1. 更新后端代码支持 SQLite 金融数据读写")
        print("2. 更新配置文件 database_manager.yaml")
        print("3. 测试 API 读写功能")

    except Exception as e:
        print(f"\n[错误] 迁移失败: {e}")
        raise


if __name__ == "__main__":
    main()
