from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from models.news_model import Category,News

async def get_categories(db: AsyncSession,skip: int = 0, limit: int = 100):
    #分页查询
    stmt = select(Category).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()

async def get_news_list(db: AsyncSession, category_id: int, skip: int=0, limit: int=10):
    #查询指定分类下的所有新闻
    stmt = select(News).where(category_id == News.category_id).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()

async def get_news_acount(db: AsyncSession, category_id: int):
    stmt = select(func.count(News.id)).where(category_id == News.category_id)
    result = await db.execute(stmt)
    return result.scalar_one() #只能有一个结果

#根据id在数据库中搜索新闻
async def get_news_detail(db: AsyncSession, news_id: int):
    stmt = select(News).where(news_id == News.id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()

#增加浏览量
async def increase_news_views(db: AsyncSession, news_id: int):
    stmt = update(News).where(News.id == news_id).values(views=News.views + 1)
    result = await db.execute(stmt)
    await db.commit() 
    #新增浏览量的判断逻辑：是否执行了update函数所在行的函数
    return result.rowcount > 0

#相关新闻推荐逻辑
#实现流：根据当前新闻id按照浏览量降序排列出同一分类的新闻
async def get_related_news(db: AsyncSession, news_id: int, category_id: int, limit: int = 5):
    stmt = select(News).where(
        News.category_id == category_id,
        News.id != news_id
    ).order_by(
        News.views.desc(),
        News.publish_time.desc()
    ).limit(limit)
    result = await db.execute(stmt)
    related_news = result.scalars().all()
    return[{
        "id": news_detail.id,
        "title": news_detail.title,
        "content": news_detail.content,
        "image": news_detail.image,
        "author": news_detail.author,
        "publishTime": news_detail.publish_time,
        "categoryId": news_detail.category_id,
        "views": news_detail.views,
    } for news_detail in related_news]