from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select,delete

from models.history_model import History
from models.news_model import News

#添加浏览记录 ： 
# 查询记录 -- 存在：更新访问时间； 不存在：添加浏览记录
async def add_history(
        db: AsyncSession,
        user_id: int,
        news_id: int
):
    query = select(History).where(user_id == History.user_id, news_id == History.news_id)
    result = await db.execute(query)
    existing_history = result.scalar_one_or_none()
    if existing_history:
        existing_history.view_time = datetime.now()
        await db.commit()
        await db.refresh(existing_history)
        return existing_history
    else:
        history = History(user_id = user_id, news_id = news_id)
        db.add(history)
        await db.commit()
        await db.refresh(History)
        return history
    
#获取浏览列表
# 得到用户的浏览总量 -- 定义offset -- 联表查询
async def get_history_list(
        db: AsyncSession,
        user_id: int,
        page: int = 1,
        page_size: int = 10
):
    # 根据用户查询浏览总量
    count_query = select(func.count(History.id)).where(user_id == History.user_id)
    count_result = await db.execute(count_query)
    total = count_result.scalar_one()
    # 收取查询列表：联表查询+查询时间排序+分页
    offset = (page - 1) * page_size
    query = (select(News, History.view_time.label("view_time"), History.id.label("history_id"))
             .join(History, History.news_id == News.id)
             .where(History.user_id == user_id)
             .order_by(History.view_time.desc())
             .offset(offset).limit(page_size)
             )
    result = await db.execute(query)
    rows = result.all()
    return rows,total

#删除单条浏览记录
# 验证用户 -- 删除当前用户浏览记录 --  检查命中数量 -- 响应结果
async def delete_history(
        db: AsyncSession,
        user_id: int,
        news_id:int
):
    query = delete(History).where(History.user_id == user_id, History.news_id == news_id)
    result = await db.execute(query)
    await db.commit()

    return result.rowcount > 0

#删除浏览列表
# 验证用户 -- 清空当前用户的浏览记录 -- 返回结果
async def clear_history(
        db: AsyncSession,
        user_id = int
):
    stmt = delete(History).where(History.user_id == user_id)
    result = await db.execute(stmt)
    await db.commit()

    return result.rowcount or 0