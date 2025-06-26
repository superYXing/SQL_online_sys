from fastapi import FastAPI, APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import List, Optional

# 数据模型定义
class Item(BaseModel):
    id: int
    name: str
    price: float
    is_available: bool = True

# 模拟数据库
items_db = {
    1: Item(id=1, name="Apple", price=5.99),
    2: Item(id=2, name="Banana", price=3.99),
    3: Item(id=3, name="Cherry", price=8.99, is_available=False),
}

# 创建API路由器
api_router = APIRouter()

# 商品API接口
@api_router.get("/items/", response_model=List[Item], summary="获取商品列表")
async def get_items(available: Optional[bool] = None):
    """获取商品列表，支持筛选条件"""
    if available is not None:
        return [item for item in items_db.values() if item.is_available == available]
    return list(items_db.values())

@api_router.get("/items/{item_id}", response_model=Item, summary="获取单个商品")
async def get_item(item_id: int):
    """根据商品ID获取详情"""
    item = items_db.get(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="商品不存在")
    return item

@api_router.post("/items/", response_model=Item, status_code=201, summary="创建商品")
async def create_item(item: Item):
    """创建新商品（ID需唯一）"""
    if item.id in items_db:
        raise HTTPException(status_code=400, detail="商品ID已存在")
    items_db[item.id] = item
    return item

@api_router.put("/items/{item_id}", response_model=Item, summary="更新商品")
async def update_item(item_id: int, updated_item: Item):
    """更新现有商品信息"""
    if item_id not in items_db:
        raise HTTPException(status_code=404, detail="商品不存在")
    if updated_item.id != item_id:
        raise HTTPException(status_code=400, detail="商品ID不可修改")
    items_db[item_id] = updated_item
    return updated_item

@api_router.delete("/items/{item_id}", status_code=204, summary="删除商品")
async def delete_item(item_id: int):
    """删除指定ID的商品"""
    if item_id not in items_db:
        raise HTTPException(status_code=404, detail="商品不存在")
    del items_db[item_id]
    return None

# 创建Jinja2模板加载器
templates = Jinja2Templates(directory="templates")

# 创建Web界面路由器
web_router = APIRouter()

@web_router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """商品管理系统首页"""
    return templates.TemplateResponse("index.html", {"request": request})

@web_router.get("/items", response_class=HTMLResponse)
async def items_list(request: Request, available: Optional[bool] = None):
    """商品列表页面"""
    items = await get_items(available)
    return templates.TemplateResponse(
        "items_list.html",
        {"request": request, "items": items, "available": available}
    )

@web_router.get("/items/create", response_class=HTMLResponse)
async def create_item_form(request: Request):
    """创建商品表单页面"""
    return templates.TemplateResponse("item_form.html", {"request": request, "is_create": True})

@web_router.post("/items/create", response_class=HTMLResponse)
async def process_create_item(request: Request):
    """处理创建商品请求"""
    form_data = await request.form()
    try:
        new_item = Item(
            id=int(form_data["id"]),
            name=form_data["name"],
            price=float(form_data["price"]),
            is_available=form_data.get("is_available") == "on"
        )
        await create_item(new_item)
        return templates.TemplateResponse(
            "success.html",
            {"request": request, "message": "商品创建成功", "redirect_url": "/items"}
        )
    except Exception as e:
        return templates.TemplateResponse(
            "error.html",
            {"request": request, "error": str(e), "back_url": "/items/create"}
        )

@web_router.get("/items/{item_id}/edit", response_class=HTMLResponse)
async def edit_item_form(request: Request, item_id: int):
    """编辑商品表单页面"""
    item = await get_item(item_id)
    return templates.TemplateResponse(
        "item_form.html",
        {"request": request, "item": item, "is_create": False}
    )

@web_router.post("/items/{item_id}/edit", response_class=HTMLResponse)
async def process_edit_item(request: Request, item_id: int):
    """处理编辑商品请求"""
    form_data = await request.form()
    try:
        updated_item = Item(
            id=item_id,  # 确保ID不被修改
            name=form_data["name"],
            price=float(form_data["price"]),
            is_available=form_data.get("is_available") == "on"
        )
        await update_item(item_id, updated_item)
        return templates.TemplateResponse(
            "success.html",
            {"request": request, "message": "商品更新成功", "redirect_url": "/items"}
        )
    except Exception as e:
        return templates.TemplateResponse(
            "error.html",
            {"request": request, "error": str(e), "back_url": f"/items/{item_id}/edit"}
        )

@web_router.post("/items/{item_id}/delete", response_class=HTMLResponse)
async def process_delete_item(request: Request, item_id: int):
    """处理删除商品请求"""
    try:
        await delete_item(item_id)
        return templates.TemplateResponse(
            "success.html",
            {"request": request, "message": "商品删除成功", "redirect_url": "/items"}
        )
    except Exception as e:
        return templates.TemplateResponse(
            "error.html",
            {"request": request, "error": str(e), "back_url": "/items"}
        )

# 创建FastAPI应用
app = FastAPI(
    title="商品管理系统",
    description="一个带有Web界面的商品管理系统",
    version="1.0.0",
)
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],  # Vue 项目地址
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# 挂载API路由
app.include_router(api_router, prefix="/api")

# 挂载Web界面路由
app.include_router(web_router)

# 应用启动入口
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)