from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import Column, BigInteger, String, Text, TIMESTAMP, SmallInteger, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from datetime import datetime
from sqlalchemy import text

# 数据库连接配置
DATABASE_URL = "mysql+pymysql://root:wyx778899@localhost:3306/blogdb"

# 数据库引擎和会话
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# SQLAlchemy 基类
Base = declarative_base()

# 数据库模型
class Blog(Base):
    __tablename__ = "m_blog"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger)
    title = Column(String(255))
    description = Column(String(255))
    content = Column(Text)
    created = Column(TIMESTAMP, default=datetime.utcnow)
    status = Column(SmallInteger)

# 自动建表（首次运行时执行一次）
Base.metadata.create_all(bind=engine)

# FastAPI 实例
app = FastAPI()

# 数据入参模型
class BlogCreate(BaseModel):
    user_id: int
    title: str
    description: str
    content: str
    status: int

# 获取数据库会话
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 创建博客
@app.post("/blogs/")
def create_blog(blog: BlogCreate, db: Session = Depends(get_db)):
    db_blog = Blog(
        user_id=blog.user_id,
        title=blog.title,
        description=blog.description,
        content=blog.content,
        status=blog.status,
        created=datetime.utcnow()
    )
    db.add(db_blog)
    db.commit()
    db.refresh(db_blog)
    return db_blog

# 根据 ID 查询博客
@app.get("/blogs/{blog_id}")
def read_blog(blog_id: int, db: Session = Depends(get_db)):
    blog = db.query(Blog).filter(Blog.id == blog_id).first()
    if not blog:
        raise HTTPException(status_code=404, detail="Blog not found")
    return blog
from sqlalchemy import text

@app.get("/db-check/")
def db_check(db: Session = Depends(get_db)):
    try:
        result = db.execute(text("SELECT * FROM m_blog LIMIT 1"))
        row = result.fetchone()
        if row:
            # 将行数据转成字典返回
            data = dict(row._mapping)
            return {
                "status": "success",
                "message": "数据库连接正常，存在数据",
                "data": data
            }
        else:
            return {
                "status": "success",
                "message": "数据库连接正常，但表中暂无数据",
                "data": None
            }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "data": None
        }



if __name__ == "__main__":
    import uvicorn
    uvicorn.run("databasetsest:app", host="127.0.0.1", port=8000, reload=True)
