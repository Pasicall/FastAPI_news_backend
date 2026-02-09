from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from models.user_model import User
from config.db_conf import get_db
from schemas.history import HistoryAddRequest, HistoryListResponse, HistoryNewsItemResponse
from crud import history
from utils.response import success_response
from utils.auth import get_current_user


router = APIRouter(prefix='/api/history', tags=["history"])

#添加浏览历史接口
@router.post("/add")
async def add_history(
    data: HistoryAddRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await history.add_history(db,user.id,data.news_id)
    return success_response(message="添加历史记录成功",data=result)

# 获取历史浏览记录列表
@router.get("/list")
async def get_history_list(
    page: int = Query(1,ge=1),
    page_size: int = Query(10, ge=1, le=100, alias="pageSize"),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    rows,total = await history.get_history_list(db,user.id,page,page_size)
    has_more =  total > (page-1) * page_size
    history_list = [HistoryNewsItemResponse.model_validate({
        **news.__dict__,
        "view_time": view_time,
        "history_id": history_id

    }) for news,view_time,history_id in rows ]

    data = HistoryListResponse(list=history_list, total=total, hasMore=has_more)
    return success_response(data=data)

# 删除单条浏览记录
@router.delete("/delete/{id}")
async def delete_history(
    news_id: int = Path(...,gt=0, alias="id"),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await history.delete_history(db, user.id, news_id)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="历史记录不存在")
    return success_response(message="删除浏览记录成功")

# 删除浏览列表
@router.delete("/clear")
async def clear_history(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await history.clear_history(db, user.id)
    return success_response(message=f"清空了{result}条历史记录")