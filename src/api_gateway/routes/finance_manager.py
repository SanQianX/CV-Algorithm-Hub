# -*- coding: utf-8 -*-
"""
Finance Data Manager API routes - 金融数据管理API
功能：获取股票和基金数据列表，包括时间范围、更新时间、内存占用等信息
"""
import logging
from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy import func, desc
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel

from src.api_gateway.db.database import get_db
from src.api_gateway.db.models import StockHistory, FundHistory, FundDetail

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/db-manager/finance", tags=["finance-manager"])


# ========== Pydantic Models ==========

class FinanceDataItem(BaseModel):
    """金融数据项"""
    id: str
    name: str
    code: str
    type: str  # 'stock' or 'fund'
    dateRange: str
    startDate: str
    endDate: str
    lastUpdate: str
    memorySize: str
    memorySizeBytes: int


class FinanceDataList(BaseModel):
    """金融数据列表响应"""
    items: List[FinanceDataItem]
    total: int
    stockCount: int
    fundCount: int


class FinanceStats(BaseModel):
    """金融数据统计"""
    total: int
    stockCount: int
    fundCount: int


# ========== 辅助函数 ==========

def calculate_memory_size(row_count: int, avg_row_size: int = 200) -> int:
    """
    估算数据占用的内存空间

    Args:
        row_count: 数据行数
        avg_row_size: 平均每行数据大小（字节）

    Returns:
        内存占用字节数
    """
    # 索引和表结构额外开销（约20%）
    overhead = 1.2
    return int(row_count * avg_row_size * overhead)


def format_memory_size(bytes_size: int) -> str:
    """格式化内存大小显示"""
    if bytes_size < 1024 * 1024:
        return f"{bytes_size / 1024:.2f} KB"
    elif bytes_size < 1024 * 1024 * 1024:
        return f"{bytes_size / (1024 * 1024):.2f} MB"
    else:
        return f"{bytes_size / (1024 * 1024 * 1024):.2f} GB"


def format_date_range(start_date: datetime, end_date: datetime) -> str:
    """格式化日期范围"""
    format_str = "%Y年%m月%d日"
    return f"{start_date.strftime(format_str)} - {end_date.strftime(format_str)}"


# ========== API 端点 ==========

@router.get("/stocks", response_model=List[FinanceDataItem])
async def get_stocks_data(
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    """
    获取所有股票数据列表

    返回每只股票的：
    - 名称（股票名称，如果有）
    - 编码（股票代码）
    - 数据时间范围
    - 最后更新时间
    - 内存占用大小
    """
    try:
        # 按股票代码分组，获取时间范围和记录数
        stock_stats = (
            db.query(
                StockHistory.code,
                func.min(StockHistory.date).label('min_date'),
                func.max(StockHistory.date).label('max_date'),
                func.max(StockHistory.created_at).label('last_update'),
                func.count(StockHistory.id).label('record_count')
            )
            .group_by(StockHistory.code)
            .all()
        )

        items = []
        for stat in stock_stats:
            code = stat.code
            min_date = stat.min_date
            max_date = stat.max_date
            last_update = stat.last_update
            record_count = stat.record_count

            # 计算内存占用
            memory_bytes = calculate_memory_size(record_count)

            # 查找股票名称（从 FundDetail 或其他来源，这里先用代码作为名称）
            # TODO: 可以从其他表获取股票名称
            name = f"股票{code}"

            items.append(FinanceDataItem(
                id=f"stock_{code}",
                name=name,
                code=code,
                type="stock",
                dateRange=format_date_range(min_date, max_date),
                startDate=min_date.strftime("%Y-%m-%d"),
                endDate=max_date.strftime("%Y-%m-%d"),
                lastUpdate=last_update.strftime("%Y-%m-%d %H:%M:%S") if last_update else "",
                memorySize=format_memory_size(memory_bytes),
                memorySizeBytes=memory_bytes
            ))

        # 按代码排序
        items.sort(key=lambda x: x.code)

        return items

    except Exception as e:
        logger.error(f"获取股票数据失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取股票数据失败: {str(e)}")


@router.get("/funds", response_model=List[FinanceDataItem])
async def get_funds_data(
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    """
    获取所有基金数据列表

    返回每只基金的：
    - 名称（基金名称）
    - 编码（基金代码）
    - 数据时间范围
    - 最后更新时间
    - 内存占用大小
    """
    try:
        # 获取基金详情，用于获取基金名称
        fund_details = db.query(FundDetail.code, FundDetail.name).all()
        fund_names = {code: name for code, name in fund_details}

        # 按基金代码分组，获取时间范围和记录数
        fund_stats = (
            db.query(
                FundHistory.code,
                func.min(FundHistory.date).label('min_date'),
                func.max(FundHistory.date).label('max_date'),
                func.max(FundHistory.created_at).label('last_update'),
                func.count(FundHistory.id).label('record_count')
            )
            .group_by(FundHistory.code)
            .all()
        )

        items = []
        for stat in fund_stats:
            code = stat.code
            min_date = stat.min_date
            max_date = stat.max_date
            last_update = stat.last_update
            record_count = stat.record_count

            # 计算内存占用
            memory_bytes = calculate_memory_size(record_count, avg_row_size=150)  # 基金数据稍小

            # 获取基金名称
            name = fund_names.get(code, f"基金{code}")

            items.append(FinanceDataItem(
                id=f"fund_{code}",
                name=name,
                code=code,
                type="fund",
                dateRange=format_date_range(min_date, max_date),
                startDate=min_date.strftime("%Y-%m-%d"),
                endDate=max_date.strftime("%Y-%m-%d"),
                lastUpdate=last_update.strftime("%Y-%m-%d %H:%M:%S") if last_update else "",
                memorySize=format_memory_size(memory_bytes),
                memorySizeBytes=memory_bytes
            ))

        # 按代码排序
        items.sort(key=lambda x: x.code)

        return items

    except Exception as e:
        logger.error(f"获取基金数据失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取基金数据失败: {str(e)}")


@router.get("/all", response_model=FinanceDataList)
async def get_all_finance_data(
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    """
    获取所有金融数据（股票+基金）

    返回包含股票和基金的完整列表，以及统计信息
    """
    try:
        # 并行获取股票和基金数据
        stocks = await get_stocks_data(authorization, db)
        funds = await get_funds_data(authorization, db)

        all_items = stocks + funds
        # 按类型和代码排序
        all_items.sort(key=lambda x: (x.type, x.code))

        return FinanceDataList(
            items=all_items,
            total=len(all_items),
            stockCount=len(stocks),
            fundCount=len(funds)
        )

    except Exception as e:
        logger.error(f"获取金融数据失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取金融数据失败: {str(e)}")


@router.get("/stats", response_model=FinanceStats)
async def get_finance_stats(
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    """
    获取金融数据统计信息

    返回：
    - 总数量
    - 股票数量
    - 基金数量
    """
    try:
        # 统计股票数量
        stock_count = (
            db.query(func.count(func.distinct(StockHistory.code)))
            .scalar() or 0
        )

        # 统计基金数量
        fund_count = (
            db.query(func.count(func.distinct(FundHistory.code)))
            .scalar() or 0
        )

        return FinanceStats(
            total=stock_count + fund_count,
            stockCount=stock_count,
            fundCount=fund_count
        )

    except Exception as e:
        logger.error(f"获取统计数据失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取统计数据失败: {str(e)}")
