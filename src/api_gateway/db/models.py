"""Database models"""
from sqlalchemy import Column, String, DateTime, Text, Boolean, Integer, ForeignKey, JSON, Float
from .database import Base
from datetime import datetime


class User(Base):
    """User model for database storage"""
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, index=True)
    username = Column(String(20), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}, email={self.email})>"


# 必须在 User 之后定义，以便 relationship 可以解析
from sqlalchemy.orm import relationship


class MonitorList(Base):
    """监控列表模型"""
    __tablename__ = "monitor_lists"

    id = Column(String(36), primary_key=True, index=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    list_type = Column(String(20), default="stock")  # stock 或 fund
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关联的监控标的
    items = relationship("MonitorItem", back_populates="monitor_list", cascade="all, delete-orphan")


class MonitorItem(Base):
    """监控标的模型（股票或基金）"""
    __tablename__ = "monitor_items"

    id = Column(String(36), primary_key=True, index=True)
    list_id = Column(String(36), ForeignKey("monitor_lists.id"), nullable=False, index=True)
    code = Column(String(20), nullable=False)
    name = Column(String(200), nullable=False)
    item_type = Column(String(20), nullable=False)  # stock 或 fund
    market = Column(String(10), nullable=True)  # sh, sz

    # 同步配置
    sync_frequency = Column(String(20), default="daily")
    sync_history = Column(Boolean, default=True)
    history_range = Column(String(20), default="90")

    # 技术指标配置
    indicators = Column(JSON, default=list)  # MA5, MA10, RSI, MACD 等

    # 预警规则
    alerts = Column(JSON, default=list)

    # 自定义标签
    tags = Column(JSON, default=list)

    # 扩展数据（基金净值等）
    extra_data = Column(JSON, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关联
    monitor_list = relationship("MonitorList", back_populates="items")


class FundHistory(Base):
    """基金历史数据模型 - 保存到 K:/data 目录的数据库"""
    __tablename__ = "fund_history"

    id = Column(String(36), primary_key=True, index=True)
    code = Column(String(20), nullable=False, index=True)  # 基金代码
    date = Column(DateTime, nullable=False, index=True)
    nav = Column(Float, nullable=False)  # 净值
    nav_change = Column(Float, default=0)  # 涨跌
    nav_change_percent = Column(Float, default=0)  # 涨跌幅
    created_at = Column(DateTime, default=datetime.utcnow)

    # 复合唯一索引：基金代码 + 日期
    __table_args__ = (
        {"sqlite_autoincrement": True},
    )


class StockHistory(Base):
    """股票历史数据模型 - 保存到 K:/data 目录的数据库"""
    __tablename__ = "stock_history"

    id = Column(String(36), primary_key=True, index=True)
    code = Column(String(20), nullable=False, index=True)  # 股票代码
    date = Column(DateTime, nullable=False, index=True)
    open = Column(Float, nullable=False)  # 开盘价
    high = Column(Float, nullable=False)  # 最高价
    low = Column(Float, nullable=False)  # 最低价
    close = Column(Float, nullable=False)  # 收盘价
    volume = Column(Integer, default=0)  # 成交量
    amount = Column(Float, default=0)  # 成交额
    created_at = Column(DateTime, default=datetime.utcnow)


class FundDetail(Base):
    """基金详情模型 - 保存基金基础信息和最新数据"""
    __tablename__ = "fund_details"

    id = Column(String(36), primary_key=True, index=True)
    code = Column(String(20), nullable=False, unique=True, index=True)  # 基金代码

    # 基本信息
    name = Column(String(200), nullable=True)  # 基金简称
    full_name = Column(String(500), nullable=True)  # 基金全称
    fund_type = Column(String(100), nullable=True)  # 基金类型
    establishment_date = Column(DateTime, nullable=True)  # 成立日期
    asset_scale = Column(String(100), nullable=True)  # 资产规模
    tracking_target = Column(String(500), nullable=True)  # 跟踪标的

    # 净值数据
    nav = Column(Float, nullable=True)  # 单位净值
    nav_date = Column(DateTime, nullable=True)  # 净值日期
    acc_nav = Column(Float, nullable=True)  # 累计净值
    acc_nav_date = Column(DateTime, nullable=True)  # 累计净值日期
    estimated_nav = Column(Float, nullable=True)  # 估算净值
    estimated_nav_change_percent = Column(Float, nullable=True)  # 估算净值涨跌幅

    # 费率信息
    subscription_fee = Column(Float, nullable=True)  # 申购费
    redemption_fee = Column(Float, nullable=True)  # 赎回费
    management_fee = Column(Float, nullable=True)  # 管理费
    custodian_fee = Column(Float, nullable=True)  # 托管费
    service_fee = Column(Float, nullable=True)  # 销售服务费

    # 机构信息
    company = Column(String(200), nullable=True)  # 基金公司
    manager = Column(String(100), nullable=True)  # 基金经理
    custodian = Column(String(100), nullable=True)  # 托管机构

    # 状态信息
    purchase_status = Column(String(20), nullable=True)  # 申购状态
    redemption_status = Column(String(20), nullable=True)  # 赎回状态
    risk_level = Column(String(20), nullable=True)  # 风险等级

    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
