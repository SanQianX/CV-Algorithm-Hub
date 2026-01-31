# -*- coding: utf-8 -*-
"""
Finance Data API Routes - 金融数据 API
"""

import uuid
import logging
from typing import Optional

from fastapi import APIRouter, HTTPException, Query, Header
from pydantic import BaseModel

from src.api_gateway.services.finance_db import get_finance_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/finance", tags=["finance"])


# ========== Pydantic Models ==========

class FundHistoryCreate(BaseModel):
    """创建基金历史记录"""
    fund_code: str
    nav: float
    record_date: str
    nav_change: Optional[float] = None
    nav_change_percent: Optional[float] = None


class FundHistoryUpdate(BaseModel):
    """更新基金历史记录"""
    nav: Optional[float] = None
    nav_change: Optional[float] = None
    nav_change_percent: Optional[float] = None


class StockHistoryCreate(BaseModel):
    """创建股票历史记录"""
    stock_code: str
    close_price: float
    record_date: str
    open_price: Optional[float] = None
    high_price: Optional[float] = None
    low_price: Optional[float] = None
    volume: Optional[int] = None
    amount: Optional[float] = None


class StockHistoryUpdate(BaseModel):
    """更新股票历史记录"""
    open_price: Optional[float] = None
    high_price: Optional[float] = None
    low_price: Optional[float] = None
    close_price: Optional[float] = None
    volume: Optional[int] = None
    amount: Optional[float] = None


class FundDetailCreate(BaseModel):
    """创建基金详情"""
    fund_code: str
    fund_name: Optional[str] = None
    fund_type: Optional[str] = None
    manager: Optional[str] = None
    establish_date: Optional[str] = None
    nav: Optional[float] = None


class FundDetailUpdate(BaseModel):
    """更新基金详情"""
    fund_name: Optional[str] = None
    fund_type: Optional[str] = None
    manager: Optional[str] = None
    establish_date: Optional[str] = None
    nav: Optional[float] = None


# ========== Fund History Endpoints ==========

@router.get("/funds/history")
def get_fund_history(
    fund_code: Optional[str] = None,
    limit: int = Query(100, ge=1, le=1000),
    authorization: str = Header(None)
):
    """获取基金历史数据"""
    try:
        service = get_finance_service()
        data = service.get_fund_history(fund_code, limit)
        return {
            "success": True,
            "data": data,
            "total": len(data)
        }
    except Exception as e:
        logger.error(f"获取基金历史数据失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取数据失败: {str(e)}")


@router.get("/funds/history/{record_id}")
def get_fund_history_by_id(
    record_id: str,
    authorization: str = Header(None)
):
    """获取单条基金历史记录"""
    try:
        service = get_finance_service()
        data = service.get_fund_history()
        for item in data:
            if item.get('id') == record_id:
                return {"success": True, "data": item}
        raise HTTPException(status_code=404, detail="记录不存在")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取基金历史记录失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取数据失败: {str(e)}")


@router.post("/funds/history")
def create_fund_history(
    request: FundHistoryCreate,
    authorization: str = Header(None)
):
    """创建基金历史记录"""
    try:
        service = get_finance_service()
        record_id = service.add_fund_history(
            fund_code=request.fund_code,
            nav=request.nav,
            record_date=request.record_date,
            nav_change=request.nav_change,
            nav_change_percent=request.nav_change_percent
        )
        return {
            "success": True,
            "message": "创建成功",
            "id": record_id
        }
    except Exception as e:
        logger.error(f"创建基金历史记录失败: {e}")
        raise HTTPException(status_code=500, detail=f"创建失败: {str(e)}")


@router.put("/funds/history/{record_id}")
def update_fund_history(
    record_id: str,
    request: FundHistoryUpdate,
    authorization: str = Header(None)
):
    """更新基金历史记录"""
    try:
        service = get_finance_service()
        success = service.update_fund_history(
            record_id,
            nav=request.nav,
            nav_change=request.nav_change,
            nav_change_percent=request.nav_change_percent
        )
        if success:
            return {"success": True, "message": "更新成功"}
        raise HTTPException(status_code=404, detail="记录不存在")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新基金历史记录失败: {e}")
        raise HTTPException(status_code=500, detail=f"更新失败: {str(e)}")


@router.delete("/funds/history/{record_id}")
def delete_fund_history(
    record_id: str,
    authorization: str = Header(None)
):
    """删除基金历史记录"""
    try:
        service = get_finance_service()
        success = service.delete_fund_history(record_id)
        if success:
            return {"success": True, "message": "删除成功"}
        raise HTTPException(status_code=404, detail="记录不存在")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除基金历史记录失败: {e}")
        raise HTTPException(status_code=500, detail=f"删除失败: {str(e)}")


# ========== Stock History Endpoints ==========

@router.get("/stocks/history")
def get_stock_history(
    stock_code: Optional[str] = None,
    limit: int = Query(100, ge=1, le=1000),
    authorization: str = Header(None)
):
    """获取股票历史数据"""
    try:
        service = get_finance_service()
        data = service.get_stock_history(stock_code, limit)
        return {
            "success": True,
            "data": data,
            "total": len(data)
        }
    except Exception as e:
        logger.error(f"获取股票历史数据失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取数据失败: {str(e)}")


@router.get("/stocks/history/{record_id}")
def get_stock_history_by_id(
    record_id: str,
    authorization: str = Header(None)
):
    """获取单条股票历史记录"""
    try:
        service = get_finance_service()
        data = service.get_stock_history()
        for item in data:
            if item.get('id') == record_id:
                return {"success": True, "data": item}
        raise HTTPException(status_code=404, detail="记录不存在")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取股票历史记录失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取数据失败: {str(e)}")


@router.post("/stocks/history")
def create_stock_history(
    request: StockHistoryCreate,
    authorization: str = Header(None)
):
    """创建股票历史记录"""
    try:
        service = get_finance_service()
        record_id = service.add_stock_history(
            stock_code=request.stock_code,
            close_price=request.close_price,
            record_date=request.record_date,
            open_price=request.open_price,
            high_price=request.high_price,
            low_price=request.low_price,
            volume=request.volume,
            amount=request.amount
        )
        return {
            "success": True,
            "message": "创建成功",
            "id": record_id
        }
    except Exception as e:
        logger.error(f"创建股票历史记录失败: {e}")
        raise HTTPException(status_code=500, detail=f"创建失败: {str(e)}")


@router.put("/stocks/history/{record_id}")
def update_stock_history(
    record_id: str,
    request: StockHistoryUpdate,
    authorization: str = Header(None)
):
    """更新股票历史记录"""
    try:
        service = get_finance_service()
        success = service.update_stock_history(
            record_id,
            open_price=request.open_price,
            high_price=request.high_price,
            low_price=request.low_price,
            close_price=request.close_price,
            volume=request.volume,
            amount=request.amount
        )
        if success:
            return {"success": True, "message": "更新成功"}
        raise HTTPException(status_code=404, detail="记录不存在")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新股票历史记录失败: {e}")
        raise HTTPException(status_code=500, detail=f"更新失败: {str(e)}")


@router.delete("/stocks/history/{record_id}")
def delete_stock_history(
    record_id: str,
    authorization: str = Header(None)
):
    """删除股票历史记录"""
    try:
        service = get_finance_service()
        success = service.delete_stock_history(record_id)
        if success:
            return {"success": True, "message": "删除成功"}
        raise HTTPException(status_code=404, detail="记录不存在")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除股票历史记录失败: {e}")
        raise HTTPException(status_code=500, detail=f"删除失败: {str(e)}")


# ========== Fund Details Endpoints ==========

@router.get("/funds/details")
def get_fund_details(
    fund_code: Optional[str] = None,
    authorization: str = Header(None)
):
    """获取基金详情"""
    try:
        service = get_finance_service()
        data = service.get_fund_details(fund_code)
        return {
            "success": True,
            "data": data,
            "total": len(data)
        }
    except Exception as e:
        logger.error(f"获取基金详情失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取数据失败: {str(e)}")


@router.get("/funds/details/{record_id}")
def get_fund_detail_by_id(
    record_id: str,
    authorization: str = Header(None)
):
    """获取单条基金详情"""
    try:
        service = get_finance_service()
        data = service.get_fund_details()
        for item in data:
            if item.get('id') == record_id:
                return {"success": True, "data": item}
        raise HTTPException(status_code=404, detail="记录不存在")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取基金详情失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取数据失败: {str(e)}")


@router.post("/funds/details")
def create_fund_detail(
    request: FundDetailCreate,
    authorization: str = Header(None)
):
    """创建基金详情"""
    try:
        service = get_finance_service()
        record_id = service.add_fund_detail(
            fund_code=request.fund_code,
            fund_name=request.fund_name,
            fund_type=request.fund_type,
            manager=request.manager,
            establish_date=request.establish_date,
            nav=request.nav
        )
        return {
            "success": True,
            "message": "创建成功",
            "id": record_id
        }
    except Exception as e:
        logger.error(f"创建基金详情失败: {e}")
        raise HTTPException(status_code=500, detail=f"创建失败: {str(e)}")


@router.put("/funds/details/{record_id}")
def update_fund_detail(
    record_id: str,
    request: FundDetailUpdate,
    authorization: str = Header(None)
):
    """更新基金详情"""
    try:
        service = get_finance_service()
        success = service.update_fund_detail(
            record_id,
            fund_name=request.fund_name,
            fund_type=request.fund_type,
            manager=request.manager,
            establish_date=request.establish_date,
            nav=request.nav
        )
        if success:
            return {"success": True, "message": "更新成功"}
        raise HTTPException(status_code=404, detail="记录不存在")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新基金详情失败: {e}")
        raise HTTPException(status_code=500, detail=f"更新失败: {str(e)}")


@router.delete("/funds/details/{record_id}")
def delete_fund_detail(
    record_id: str,
    authorization: str = Header(None)
):
    """删除基金详情"""
    try:
        service = get_finance_service()
        success = service.delete_fund_detail(record_id)
        if success:
            return {"success": True, "message": "删除成功"}
        raise HTTPException(status_code=404, detail="记录不存在")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除基金详情失败: {e}")
        raise HTTPException(status_code=500, detail=f"删除失败: {str(e)}")


# ========== Statistics Endpoints ==========

@router.get("/stats")
def get_finance_stats(authorization: str = Header(None)):
    """获取金融数据统计"""
    try:
        service = get_finance_service()
        stats = service.get_stats()
        return {
            "success": True,
            "stats": stats
        }
    except Exception as e:
        logger.error(f"获取统计失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取统计失败: {str(e)}")
