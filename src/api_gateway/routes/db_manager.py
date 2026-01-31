# -*- coding: utf-8 -*-
"""
Database Management API routes - 数据库管理系统API
功能：统一管理所有数据库连接、连接池、健康检查、自动重连
"""
import uuid
import yaml
import json
import logging
import asyncio
import threading
import time
from datetime import datetime, timedelta
from typing import List, Optional, Any, Dict
from pathlib import Path as PathLib
from contextlib import contextmanager
from pydantic import BaseModel
from enum import Enum

from fastapi import APIRouter, HTTPException, Header, Query
from fastapi.params import Path as PathParam
from sqlalchemy.orm import Session
from sqlalchemy import inspect, text, create_engine, pool
from sqlalchemy.pool import QueuePool, NullPool
from sqlalchemy.exc import SQLAlchemyError

from src.api_gateway.db.database import get_db, engine

# ========== Pydantic Models ==========

class ConnectionStatus(str, Enum):
    """连接状态枚举"""
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    ERROR = "error"
    CHECKING = "checking"
    RECONNECTING = "reconnecting"


class PoolConfig(BaseModel):
    """连接池配置"""
    min_size: int = 2
    max_size: int = 10
    max_overflow: int = 20
    pool_timeout: int = 30
    pool_recycle: int = 3600


class HealthCheckConfig(BaseModel):
    """健康检查配置"""
    enabled: bool = True
    interval: int = 30  # 秒
    timeout: int = 5
    retries: int = 3


class ConnectionConfig(BaseModel):
    """数据库连接配置"""
    id: str
    name: str
    type: str  # postgresql, sqlite
    host: Optional[str] = None
    port: Optional[int] = None
    database: Optional[str] = None
    path: Optional[str] = None
    table_type: Optional[str] = None
    enabled: bool = True
    pool_config: Optional[PoolConfig] = None
    health_check: Optional[HealthCheckConfig] = None


class ConnectionInfo(BaseModel):
    """连接信息（返回给API）"""
    id: str
    name: str
    type: str
    host: Optional[str] = None
    port: Optional[int] = None
    database: Optional[str] = None
    path: Optional[str] = None
    table_type: Optional[str] = None
    status: str
    pool_size: Optional[int] = None
    checked_out: Optional[int] = None
    last_check: Optional[str] = None
    error: Optional[str] = None
    created_at: Optional[str] = None


class TestConnectionResponse(BaseModel):
    """测试连接响应"""
    connection_id: str
    status: str
    latency_ms: Optional[float] = None
    error: Optional[str] = None
    timestamp: str


class UpdateConnectionRequest(BaseModel):
    """更新连接配置请求"""
    name: Optional[str] = None
    host: Optional[str] = None
    port: Optional[int] = None
    database: Optional[str] = None
    path: Optional[str] = None
    enabled: Optional[bool] = None
    pool_min_size: Optional[int] = None
    pool_max_size: Optional[int] = None
    health_check_enabled: Optional[bool] = None


class RegisterTableMetadataRequest(BaseModel):
    """注册表元数据请求"""
    db_id: str
    table_name: str
    table_type: str
    schema: Dict[str, Any]
    custom_tags: Optional[Dict[str, Any]] = None


class UpdateConfigRequest(BaseModel):
    """更新配置请求"""
    config: Dict[str, Any]


# ========== 配置路径 ==========
import os

IN_DOCKER = os.environ.get("IN_DOCKER", "").lower() == "true"

if IN_DOCKER:
    CONFIG_PATH = "/app/config"
    METADATA_PATH = "/app/metadata"
    DATA_PATH = "/app/data"
else:
    CONFIG_PATH = "K:/data/database_manager/config"
    METADATA_PATH = "K:/data/database_manager/metadata"
    DATA_PATH = "K:/data/databases"

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/connections", tags=["connections"])


# ========== 配置加载器 ==========

def load_config(filename: str) -> Dict[str, Any]:
    """加载配置文件"""
    config_file = PathLib(CONFIG_PATH) / filename
    if config_file.exists():
        with open(config_file, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    return {}


def save_config(filename: str, config: Dict[str, Any]) -> bool:
    """保存配置文件"""
    config_file = PathLib(CONFIG_PATH) / filename
    try:
        with open(config_file, "w", encoding="utf-8") as f:
            yaml.dump(config, f, allow_unicode=True, default_flow_style=False)
        return True
    except Exception as e:
        logger.error(f"保存配置文件失败: {e}")
        return False


# ========== 连接池管理器 ==========

class ConnectionPoolManager:
    """
    数据库连接池管理器

    功能：
    - 统一管理所有数据库连接
    - 动态加载 K:/data 下的所有数据库
    - 连接池管理（支持并发）
    - 连接健康检查
    - 自动重连机制
    """

    _instance: Optional['ConnectionPoolManager'] = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True

        self.connections: Dict[str, Dict[str, Any]] = {}  # 连接配置
        self.pools: Dict[str, Any] = {}  # SQLAlchemy 连接池
        self.engines: Dict[str, Any] = {}  # SQLAlchemy 引擎
        self.health_check_task: Optional[asyncio.Task] = None
        self._running = False
        self._health_thread: Optional[threading.Thread] = None

        # 加载配置
        self._load_config()
        self._start_health_check_thread()

    def _load_config(self):
        """从配置文件加载所有数据库连接配置"""
        config = load_config("database_manager.yaml")
        databases = config.get("databases", {})

        for db_id, db_config in databases.items():
            if db_config.get("enabled", True):
                conn_info = {
                    "id": db_id,
                    "name": db_config.get("name", db_id),
                    "type": db_config.get("type", "postgresql"),
                    "host": db_config.get("host", ""),
                    "port": db_config.get("port", 0),
                    "database": db_config.get("database", ""),
                    "path": db_config.get("path", ""),
                    "table_type": db_config.get("table_type", ""),
                    "status": ConnectionStatus.DISCONNECTED.value,
                    "last_check": None,
                    "error": None,
                    "created_at": datetime.now().isoformat()
                }

                # 连接池配置
                pool_cfg = db_config.get("connection_pool", {})
                conn_info["pool_config"] = {
                    "min_size": pool_cfg.get("min_size", 2),
                    "max_size": pool_cfg.get("max_size", 10),
                    "max_overflow": pool_cfg.get("max_overflow", 20),
                    "pool_timeout": pool_cfg.get("pool_timeout", 30),
                    "pool_recycle": pool_cfg.get("pool_recycle", 3600)
                }

                # 健康检查配置
                health_cfg = db_config.get("health_check", {})
                conn_info["health_check"] = {
                    "enabled": health_cfg.get("enabled", True),
                    "interval": health_cfg.get("interval", 30),
                    "timeout": health_cfg.get("timeout", 5),
                    "retries": health_cfg.get("retries", 3)
                }

                self.connections[db_id] = conn_info

                # 创建连接池
                self._create_pool(db_id, conn_info)

        logger.info(f"已加载 {len(self.connections)} 个数据库连接配置")

    def _discover_databases(self):
        """动态发现 K:/data/databases 下的所有数据库"""
        data_path = PathLib(DATA_PATH)
        if not data_path.exists():
            return

        # 发现的数据库类型
        discovered = {
            "postgresql": [],  # 包含 postgres 目录的
            "sqlite": []       # .db 文件
        }

        for item in data_path.iterdir():
            if item.is_dir():
                # 检查是否为 PostgreSQL 数据目录
                if (item / "PG_VERSION").exists() or (item / "postgresql.conf").exists():
                    db_id = f"db_{item.name}"
                    discovered["postgresql"].append({
                        "id": db_id,
                        "name": f"{item.name} 数据库",
                        "path": str(item)
                    })

                # 检查是否有 SQLite 数据库
                db_files = list(item.glob("*.db"))
                for db_file in db_files:
                    db_id = f"db_{item.name}"
                    discovered["sqlite"].append({
                        "id": db_id,
                        "name": f"{item.name} ({db_file.stem})",
                        "path": str(db_file)
                    })

        return discovered

    def _create_pool(self, conn_id: str, conn_info: Dict[str, Any]):
        """为指定连接创建连接池"""
        try:
            # 如果已有池，先关闭
            if conn_id in self.pools:
                self._close_pool(conn_id)

            db_type = conn_info.get("type", "postgresql")
            pool_config = conn_info.get("pool_config", {})

            min_size = pool_config.get("min_size", 2)
            max_size = pool_config.get("max_size", 10)
            max_overflow = pool_config.get("max_overflow", 20)
            pool_timeout = pool_config.get("pool_timeout", 30)
            pool_recycle = pool_config.get("pool_recycle", 3600)

            if db_type == "postgresql":
                # PostgreSQL 连接
                host = conn_info.get("host", "localhost")
                port = conn_info.get("port", 5432)
                database = conn_info.get("database", "")

                if host and database:
                    connection_string = f"postgresql://postgres:postgres@{host}:{port}/{database}"
                    engine = create_engine(
                        connection_string,
                        poolclass=QueuePool,
                        pool_size=min_size,
                        max_overflow=max_overflow,
                        pool_timeout=pool_timeout,
                        pool_recycle=pool_recycle,
                        pool_pre_ping=True  # 连接前检查
                    )
                    self.engines[conn_id] = engine
                    logger.info(f"已为 {conn_id} 创建 PostgreSQL 连接池")

            elif db_type == "sqlite":
                # SQLite 连接
                db_path = conn_info.get("path", "")
                if db_path and PathLib(db_path).exists():
                    engine = create_engine(
                        f"sqlite:///{db_path}",
                        poolclass=QueuePool,
                        pool_size=min_size,
                        max_overflow=max_overflow,
                        pool_timeout=pool_timeout,
                        pool_recycle=pool_recycle,
                        pool_pre_ping=True
                    )
                    self.engines[conn_id] = engine
                    logger.info(f"已为 {conn_id} 创建 SQLite 连接池")

        except Exception as e:
            logger.error(f"为 {conn_id} 创建连接池失败: {e}")
            self.connections[conn_id]["status"] = ConnectionStatus.ERROR.value
            self.connections[conn_id]["error"] = str(e)

    def _close_pool(self, conn_id: str):
        """关闭指定连接池"""
        try:
            if conn_id in self.engines:
                self.engines[conn_id].dispose()
                del self.engines[conn_id]
            if conn_id in self.pools:
                del self.pools[conn_id]
            logger.info(f"已关闭 {conn_id} 的连接池")
        except Exception as e:
            logger.error(f"关闭 {conn_id} 连接池失败: {e}")

    def get_connection(self, conn_id: str) -> Optional[Dict[str, Any]]:
        """获取指定连接的配置信息"""
        return self.connections.get(conn_id)

    def get_all_connections(self) -> List[ConnectionInfo]:
        """获取所有连接信息"""
        result = []
        for conn_id, conn_info in self.connections.items():
            pool_info = self._get_pool_info(conn_id)
            result.append(ConnectionInfo(
                id=conn_id,
                name=conn_info.get("name", conn_id),
                type=conn_info.get("type", ""),
                host=conn_info.get("host"),
                port=conn_info.get("port"),
                database=conn_info.get("database"),
                path=conn_info.get("path"),
                table_type=conn_info.get("table_type"),
                status=conn_info.get("status", ConnectionStatus.DISCONNECTED.value),
                pool_size=pool_info.get("size"),
                checked_out=pool_info.get("checked_out"),
                last_check=conn_info.get("last_check"),
                error=conn_info.get("error")
            ))
        return result

    def _get_pool_info(self, conn_id: str) -> Dict[str, int]:
        """获取连接池信息"""
        try:
            if conn_id in self.engines:
                engine = self.engines[conn_id]
                pool = engine.pool
                return {
                    "size": pool.size() if hasattr(pool, 'size') else 0,
                    "checked_out": pool.checkedin() if hasattr(pool, 'checkedin') else 0
                }
        except Exception as e:
            logger.error(f"获取 {conn_id} 连接池信息失败: {e}")
        return {"size": 0, "checked_out": 0}

    async def test_connection(self, conn_id: str) -> TestConnectionResponse:
        """测试数据库连接"""
        if conn_id not in self.connections:
            raise HTTPException(status_code=404, detail=f"连接 {conn_id} 不存在")

        conn_info = self.connections[conn_id]
        conn_info["status"] = ConnectionStatus.CHECKING.value

        start_time = time.time()
        error = None
        status = ConnectionStatus.CONNECTED.value

        try:
            db_type = conn_info.get("type", "postgresql")

            if db_type == "postgresql":
                host = conn_info.get("host", "")
                port = conn_info.get("port", 5432)
                database = conn_info.get("database", "")

                if host and database:
                    connection_string = f"postgresql://postgres:postgres@{host}:{port}/{database}"
                    test_engine = create_engine(connection_string, poolclass=NullPool)
                    with test_engine.connect() as conn:
                        conn.execute(text("SELECT 1"))
                    test_engine.dispose()
                else:
                    raise ValueError("缺少主机或数据库配置")

            elif db_type == "sqlite":
                db_path = conn_info.get("path", "")
                if db_path and PathLib(db_path).exists():
                    import sqlite3
                    conn_sqlite = sqlite3.connect(db_path)
                    conn_sqlite.execute("SELECT 1")
                    conn_sqlite.close()
                else:
                    raise ValueError("数据库文件不存在")

            else:
                raise ValueError(f"不支持的数据库类型: {db_type}")

        except Exception as e:
            status = ConnectionStatus.ERROR.value
            error = str(e)
            logger.error(f"测试连接 {conn_id} 失败: {e}")

        latency_ms = (time.time() - start_time) * 1000

        # 更新状态
        conn_info["status"] = status
        conn_info["last_check"] = datetime.now().isoformat()
        conn_info["error"] = error

        return TestConnectionResponse(
            connection_id=conn_id,
            status=status,
            latency_ms=round(latency_ms, 2) if status == ConnectionStatus.CONNECTED.value else None,
            error=error,
            timestamp=conn_info["last_check"]
        )

    async def update_connection(self, conn_id: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """更新连接配置"""
        if conn_id not in self.connections:
            raise HTTPException(status_code=404, detail=f"连接 {conn_id} 不存在")

        conn_info = self.connections[conn_id]

        # 更新配置
        if "name" in config:
            conn_info["name"] = config["name"]
        if "host" in config:
            conn_info["host"] = config["host"]
        if "port" in config:
            conn_info["port"] = config["port"]
        if "database" in config:
            conn_info["database"] = config["database"]
        if "path" in config:
            conn_info["path"] = config["path"]
        if "enabled" in config:
            conn_info["enabled"] = config["enabled"]

        # 更新连接池配置
        if "pool_min_size" in config or "pool_max_size" in config:
            pool_config = conn_info.get("pool_config", {})
            if "pool_min_size" in config:
                pool_config["min_size"] = config["pool_min_size"]
            if "pool_max_size" in config:
                pool_config["max_size"] = config["pool_max_size"]
            conn_info["pool_config"] = pool_config

        # 更新健康检查配置
        if "health_check_enabled" in config:
            health_check = conn_info.get("health_check", {})
            health_check["enabled"] = config["health_check_enabled"]
            conn_info["health_check"] = health_check

        # 保存到配置文件
        full_config = load_config("database_manager.yaml")
        if "databases" not in full_config:
            full_config["databases"] = {}

        if conn_id not in full_config["databases"]:
            full_config["databases"][conn_id] = {}

        # 映射配置
        update_mapping = {
            "name": "name",
            "host": "host",
            "port": "port",
            "database": "database",
            "path": "path",
            "enabled": "enabled"
        }
        for key, config_key in update_mapping.items():
            if key in config:
                full_config["databases"][conn_id][config_key] = config[key]

        if save_config("database_manager.yaml", full_config):
            # 重新创建连接池
            self._create_pool(conn_id, conn_info)
            return {
                "success": True,
                "message": "配置更新成功",
                "connection": conn_info
            }
        else:
            raise HTTPException(status_code=500, detail="保存配置失败")

    def _start_health_check_thread(self):
        """启动健康检查线程"""
        if self._health_thread and self._health_thread.is_alive():
            return

        def health_check_loop():
            while self._running:
                try:
                    for conn_id, conn_info in self.connections.items():
                        if not conn_info.get("enabled", True):
                            continue

                        health_check = conn_info.get("health_check", {})
                        if not health_check.get("enabled", True):
                            continue

                        # 检查是否需要健康检查
                        last_check = conn_info.get("last_check")
                        interval = health_check.get("interval", 30)

                        if last_check:
                            last_check_time = datetime.fromisoformat(last_check)
                            if datetime.now() - last_check_time < timedelta(seconds=interval):
                                continue

                        # 执行健康检查
                        self._health_check_connection(conn_id)

                except Exception as e:
                    logger.error(f"健康检查循环错误: {e}")

                time.sleep(5)

        self._running = True
        self._health_thread = threading.Thread(target=health_check_loop, daemon=True)
        self._health_thread.start()
        logger.info("健康检查线程已启动")

    def _health_check_connection(self, conn_id: str):
        """对指定连接执行健康检查"""
        try:
            conn_info = self.connections.get(conn_id)
            if not conn_info:
                return

            db_type = conn_info.get("type", "")
            health_check = conn_info.get("health_check", {})
            timeout = health_check.get("timeout", 5)
            retries = health_check.get("retries", 3)

            for attempt in range(retries):
                try:
                    if db_type == "postgresql":
                        host = conn_info.get("host", "")
                        port = conn_info.get("port", 5432)
                        database = conn_info.get("database", "")

                        if host and database:
                            connection_string = f"postgresql://postgres:postgres@{host}:{port}/{database}"
                            test_engine = create_engine(
                                connection_string,
                                poolclass=NullPool,
                                connect_args={"connect_timeout": timeout}
                            )
                            with test_engine.connect() as conn:
                                conn.execute(text("SELECT 1"))
                            test_engine.dispose()
                            conn_info["status"] = ConnectionStatus.CONNECTED.value
                            conn_info["error"] = None
                            return

                    elif db_type == "sqlite":
                        db_path = conn_info.get("path", "")
                        if db_path and PathLib(db_path).exists():
                            import sqlite3
                            conn_sqlite = sqlite3.connect(db_path, timeout=timeout)
                            conn_sqlite.execute("PRAGMA integrity_check")
                            conn_sqlite.close()
                            conn_info["status"] = ConnectionStatus.CONNECTED.value
                            conn_info["error"] = None
                            return

                except Exception as e:
                    if attempt < retries - 1:
                        time.sleep(1)
                        continue
                    # 所有重试都失败
                    conn_info["status"] = ConnectionStatus.ERROR.value
                    conn_info["error"] = str(e)
                    logger.warning(f"连接 {conn_id} 健康检查失败: {e}")
                    # 尝试重连
                    self._reconnect(conn_id)

        except Exception as e:
            logger.error(f"健康检查 {conn_id} 时出错: {e}")

    def _reconnect(self, conn_id: str):
        """尝试重连"""
        conn_info = self.connections.get(conn_id)
        if not conn_info:
            return

        logger.info(f"尝试重连 {conn_id}...")
        conn_info["status"] = ConnectionStatus.RECONNECTING.value

        try:
            # 关闭旧连接池
            self._close_pool(conn_id)
            # 重新创建连接池
            self._create_pool(conn_id, conn_info)
            # 测试连接
            asyncio.run(self.test_connection(conn_id))
        except Exception as e:
            logger.error(f"重连 {conn_id} 失败: {e}")

    def get_engine(self, conn_id: str):
        """获取数据库引擎（用于创建会话）"""
        if conn_id in self.engines:
            return self.engines[conn_id]
        return None

    def get_session(self, conn_id: str) -> Optional[Session]:
        """获取数据库会话"""
        engine = self.get_engine(conn_id)
        if engine:
            Session = sessionmaker(bind=engine)
            return Session()
        return None

    def shutdown(self):
        """关闭所有连接池"""
        self._running = False
        for conn_id in list(self.engines.keys()):
            self._close_pool(conn_id)
        logger.info("所有连接池已关闭")


# 导入 sessionmaker
from sqlalchemy.orm import sessionmaker


# ========== 全局连接池管理器 ==========
connection_pool_manager = ConnectionPoolManager()


# ========== 元数据注册表 ==========

class MetadataRegistry:
    """表结构元数据注册表"""

    def __init__(self):
        self.metadata_file = PathLib(METADATA_PATH) / "metadata_registry.json"
        self.registry: Dict[str, Any] = self._load_registry()

    def _load_registry(self) -> Dict[str, Any]:
        """加载注册表"""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"加载元数据注册表失败: {e}")
        return {"version": "1.0", "tables": {}}

    def _save_registry(self):
        """保存注册表"""
        self.metadata_file.parent.mkdir(parents=True, exist_ok=True)
        try:
            with open(self.metadata_file, "w", encoding="utf-8") as f:
                json.dump(self.registry, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存元数据注册表失败: {e}")

    def register_table(self, db_id: str, table_name: str, table_type: str,
                       schema: Dict[str, Any], custom_tags: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """注册表结构"""
        table_key = f"{db_id}.{table_name}"

        table_info = {
            "table_id": str(uuid.uuid4()),
            "database_name": db_id,
            "table_name": table_name,
            "table_type": table_type,
            "schema_version": "1.0",
            "registered_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
            "schema": schema,
            "custom_tags": custom_tags or {}
        }

        self.registry["tables"][table_key] = table_info
        self._save_registry()

        return table_info

    def get_table(self, db_id: str, table_name: str) -> Optional[Dict[str, Any]]:
        """获取表元数据"""
        table_key = f"{db_id}.{table_name}"
        return self.registry["tables"].get(table_key)

    def get_all_tables(self, table_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """获取所有表元数据"""
        tables = list(self.registry["tables"].values())
        if table_type:
            tables = [t for t in tables if t["table_type"] == table_type]
        return tables


metadata_registry = MetadataRegistry()


# ========== API 端点 ==========

@router.get("", response_model=List[ConnectionInfo])
def list_connections(authorization: str = Header(None)):
    """获取所有可用数据库连接"""
    try:
        connections = connection_pool_manager.get_all_connections()
        return connections
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取连接列表失败: {str(e)}")


# 子路径端点（使用路径前缀避免与 {connection_id} 冲突）
@router.get("/all", response_model=List[ConnectionInfo])
def list_all_connections(authorization: str = Header(None)):
    """获取所有可用数据库连接（详细信息）"""
    return connection_pool_manager.get_all_connections()


@router.post("/test", response_model=TestConnectionResponse)
async def test_connection(connection_id: str = Query(..., description="连接ID"), authorization: str = Header(None)):
    """测试数据库连接"""
    return await connection_pool_manager.test_connection(connection_id)


# 动态路径参数路由（connection_id 不能是以下保留名称）
@router.get("/{connection_id}", response_model=ConnectionInfo)
def get_connection(connection_id: str, authorization: str = Header(None)):
    """获取指定连接信息"""
    # 保留路径保护
    if connection_id in ("all", "test"):
        raise HTTPException(status_code=404, detail=f"连接 {connection_id} 不存在")
    conn_info = connection_pool_manager.get_connection(connection_id)
    if not conn_info:
        raise HTTPException(status_code=404, detail=f"连接 {connection_id} 不存在")
    return ConnectionInfo(**conn_info)


@router.put("/{connection_id}")
async def update_connection(connection_id: str, request: UpdateConnectionRequest, authorization: str = Header(None)):
    """更新连接配置"""
    if connection_id in ("all", "test"):
        raise HTTPException(status_code=404, detail=f"连接 {connection_id} 不存在")
    config = {k: v for k, v in request.model_dump().items() if v is not None}
    return await connection_pool_manager.update_connection(connection_id, config)


@router.post("/{connection_id}/reconnect")
async def reconnect_connection(connection_id: str, authorization: str = Header(None)):
    """手动触发重连"""
    if connection_id in ("all", "test"):
        raise HTTPException(status_code=404, detail=f"连接 {connection_id} 不存在")
    conn_info = connection_pool_manager.get_connection(connection_id)
    if not conn_info:
        raise HTTPException(status_code=404, detail=f"连接 {connection_id} 不存在")

    connection_pool_manager._reconnect(conn_id)
    updated_info = connection_pool_manager.get_connection(connection_id)

    return {
        "success": True,
        "message": "重连操作已执行",
        "connection": updated_info
    }


@router.get("/{connection_id}/stats")
def get_pool_stats(connection_id: str, authorization: str = Header(None)):
    """获取连接池统计信息"""
    if connection_id in ("all", "test"):
        raise HTTPException(status_code=404, detail=f"连接 {connection_id} 不存在")
    pool_info = connection_pool_manager._get_pool_info(connection_id)
    if not pool_info:
        raise HTTPException(status_code=404, detail=f"连接 {connection_id} 不存在")

    return {
        "connection_id": connection_id,
        "pool_size": pool_info["size"],
        "checked_out": pool_info["checked_out"],
        "available": pool_info["size"] - pool_info["checked_out"]
    }


# ========== 元数据端点 ==========

@router.get("/{connection_id}/metadata")
def list_table_metadata(connection_id: str, authorization: str = Header(None)):
    """获取指定数据库的所有表元数据"""
    if connection_id in ("all", "test"):
        raise HTTPException(status_code=404, detail=f"连接 {connection_id} 不存在")
    tables = metadata_registry.get_all_tables()
    filtered_tables = [t for t in tables if t["database_name"] == connection_id]
    return {
        "connection_id": connection_id,
        "tables": filtered_tables,
        "total": len(filtered_tables)
    }


@router.post("/{connection_id}/metadata/discover")
async def discover_table_metadata(connection_id: str, authorization: str = Header(None)):
    """自动发现指定数据库的表结构"""
    if connection_id in ("all", "test"):
        raise HTTPException(status_code=404, detail=f"连接 {connection_id} 不存在")
    conn_info = connection_pool_manager.get_connection(connection_id)
    if not conn_info:
        raise HTTPException(status_code=404, detail=f"连接 {connection_id} 不存在")

    db_type = conn_info.get("type", "")
    discovered = []

    try:
        if db_type == "postgresql":
            host = conn_info.get("host", "")
            port = conn_info.get("port", 5432)
            database = conn_info.get("database", "")

            if host and database:
                connection_string = f"postgresql://postgres:postgres@{host}:{port}/{database}"
                discover_engine = create_engine(connection_string)
                inspector = inspect(discover_engine)
                table_names = inspector.get_table_names()

                for table_name in table_names:
                    columns = []
                    for col in inspector.get_columns(table_name):
                        columns.append({
                            "name": col["name"],
                            "type": str(col["type"]),
                            "nullable": col["nullable"],
                            "primary_key": col.get("primary_key", False)
                        })

                    schema = {"columns": columns}
                    table_info = metadata_registry.register_table(
                        db_id=connection_id,
                        table_name=table_name,
                        table_type=conn_info.get("table_type", "custom"),
                        schema=schema
                    )
                    discovered.append(table_info)

                discover_engine.dispose()

        elif db_type == "sqlite":
            db_path = conn_info.get("path", "")
            if db_path and PathLib(db_path).exists():
                import sqlite3
                conn_sqlite = sqlite3.connect(db_path)
                cursor = conn_sqlite.cursor()

                cursor.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
                )
                tables = cursor.fetchall()

                for (table_name,) in tables:
                    cursor.execute(f"PRAGMA table_info({table_name})")
                    columns_info = cursor.fetchall()

                    columns = []
                    for col_info in columns_info:
                        columns.append({
                            "name": col_info[1],
                            "type": col_info[2],
                            "nullable": not col_info[3],
                            "primary_key": col_info[5] == 1
                        })

                    schema = {"columns": columns}
                    table_info = metadata_registry.register_table(
                        db_id=connection_id,
                        table_name=table_name,
                        table_type=conn_info.get("table_type", "custom"),
                        schema=schema
                    )
                    discovered.append(table_info)

                conn_sqlite.close()

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"发现表结构失败: {str(e)}")

    return {
        "connection_id": connection_id,
        "tables_discovered": len(discovered),
        "tables": [{"name": t["table_name"], "type": t["table_type"]} for t in discovered]
    }


# ========== 应用启动和关闭事件 ==========

@router.on_event("shutdown")
def shutdown_event():
    """应用关闭时清理连接池"""
    connection_pool_manager.shutdown()
    logger.info("数据库连接池已关闭")
