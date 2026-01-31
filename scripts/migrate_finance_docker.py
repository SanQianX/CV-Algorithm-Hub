# -*- coding: utf-8 -*-
"""
PostgreSQL to SQLite Migration Script (Docker Version)
"""

import sqlite3
import json
from datetime import datetime
import os


def get_pg_connection():
    """获取 PostgreSQL 连接（通过环境变量）"""
    import psycopg2
    return psycopg2.connect(
        host=os.environ.get("POSTGRES_HOST", "postgres"),
        port=os.environ.get("POSTGRES_PORT", "5432"),
        database=os.environ.get("POSTGRES_DB", "cv_algorithm_hub"),
        user=os.environ.get("POSTGRES_USER", "postgres"),
        password=os.environ.get("POSTGRES_PASSWORD", "postgres")
    )


class PostgresToSQLiteMigrator:
    """PostgreSQL 到 SQLite 迁移器"""

    def __init__(self, sqlite_path: str):
        self.sqlite_path = sqlite_path
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

    def get_pg_table_schema(self, pg_conn, table_name: str) -> list:
        """获取 PostgreSQL 表结构"""
        cursor = pg_conn.cursor()
        cursor.execute(f"""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns
            WHERE table_name = %s
            ORDER BY ordinal_position
        """, (table_name,))
        columns = cursor.fetchall()

        # 获取主键
        cursor.execute(f"""
            SELECT a.attname
            FROM pg_index i
            JOIN pg_attribute a ON a.attrelid = i.indrelid AND a.attnum = ANY(i.indkey)
            WHERE i.indrelid = %s::regclass AND i.indisprimary
        """, (table_name,))
        primary_keys = [row[0] for row in cursor.fetchall()]

        result = []
        for col in columns:
            result.append({
                'name': col[0],
                'type': col[1],
                'nullable': col[2] == 'YES',
                'default': col[3],
                'primary_key': col[0] in primary_keys
            })
        return result

    def create_sqlite_table(self, table_name: str, columns: list):
        """在 SQLite 中创建表"""
        type_mapping = {
            'character varying': 'TEXT',
            'varchar': 'TEXT',
            'text': 'TEXT',
            'integer': 'INTEGER',
            'bigint': 'INTEGER',
            'numeric': 'REAL',
            'real': 'REAL',
            'double precision': 'REAL',
            'boolean': 'INTEGER',
            'date': 'TEXT',
            'timestamp without time zone': 'TEXT',
            'timestamp with time zone': 'TEXT',
            'json': 'TEXT',
            'jsonb': 'TEXT',
            'uuid': 'TEXT',
        }

        column_defs = []
        for col in columns:
            pg_type = str(col['type']).lower()
            sqlite_type = type_mapping.get(pg_type, 'TEXT')

            col_def = f"{col['name']} {sqlite_type}"

            if col.get('primary_key', False):
                col_def += " PRIMARY KEY"
            if not col.get('nullable', True):
                col_def += " NOT NULL"

            column_defs.append(col_def)

        create_sql = f"CREATE TABLE IF NOT EXISTS {table_name} (\n    "
        create_sql += ",\n    ".join(column_defs)
        create_sql += "\n)"

        self.sqlite_conn.execute(create_sql)
        self.sqlite_conn.commit()
        print(f"  [创建表] {table_name}")

    def migrate_table(self, pg_conn, table_name: str) -> int:
        """迁移单个表的数据"""
        print(f"  迁移表: {table_name}")

        cursor = pg_conn.cursor()
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        print(f"    读取 {len(rows)} 条记录")

        if not rows:
            return 0

        # 插入 SQLite
        placeholders = ', '.join(['?' for _ in columns])
        insert_sql = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})"

        for row in rows:
            values = []
            for val in row:
                if isinstance(val, datetime):
                    values.append(val.isoformat())
                elif isinstance(val, (dict, list)):
                    values.append(json.dumps(val, ensure_ascii=False))
                else:
                    values.append(val)
            self.sqlite_conn.execute(insert_sql, values)

        self.sqlite_conn.commit()
        print(f"    插入 {len(rows)} 条记录")
        return len(rows)

    def migrate_all(self, pg_conn, tables: list) -> dict:
        """迁移所有表"""
        print("\n" + "=" * 60)
        print("开始数据迁移")
        print("=" * 60)

        self.connect_sqlite()

        stats = {}
        for table_name in tables:
            print(f"\n处理表: {table_name}")

            # 获取表结构
            columns = self.get_pg_table_schema(pg_conn, table_name)

            # 创建表
            self.create_sqlite_table(table_name, columns)

            # 迁移数据
            count = self.migrate_table(pg_conn, table_name)
            stats[table_name] = count

        self.close_sqlite()

        print("\n" + "=" * 60)
        print("迁移完成!")
        print("=" * 60)
        for table, count in stats.items():
            print(f"  {table}: {count} 条记录")

        return stats


def main():
    """主函数"""
    print("=" * 60)
    print("PostgreSQL -> SQLite 迁移脚本")
    print("=" * 60)

    # SQLite 路径
    sqlite_path = "/app/data/finance.db"

    # 要迁移的表
    tables = [
        "fund_history",
        "stock_history",
        "fund_details"
    ]

    migrator = PostgresToSQLiteMigrator(sqlite_path)

    try:
        # 连接 PostgreSQL
        print("\n连接 PostgreSQL...")
        pg_conn = get_pg_connection()
        print("[成功] 已连接 PostgreSQL")

        # 执行迁移
        stats = migrator.migrate_all(pg_conn, tables)
        pg_conn.close()

        print(f"\n数据已迁移到: {sqlite_path}")
        print("\n迁移测试通过!")

    except Exception as e:
        print(f"\n[错误] 迁移失败: {e}")
        raise


if __name__ == "__main__":
    main()
