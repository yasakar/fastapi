from fastapi import APIRouter
from fastapi import Response, Request, HTTPException, Depends
from fastapi.encoders import jsonable_encoder
from schemas import Todo, TodoBody, SuccessMsg
from database import db_create_todo, db_get_todos, db_get_single_todo, db_update_todo, db_delete_todo
from starlette.status import HTTP_201_CREATED
from typing import List
from fastapi_csrf_protect import CsrfProtect
from auth_utils import AuthJwtCsrt

router = APIRouter()
auth = AuthJwtCsrt()

@router.post("/api/todo", response_model=Todo)  # Todo の形 (Json)でクライアントからデータが渡される
async def create_todo(request: Request, response: Response, data: TodoBody, csrf_protect: CsrfProtect = Depends()):
    new_token = auth.verify_csrf_update_jwt(
        request, csrf_protect, request.headers)
    # database のdb_create_todo関数はディクショナリー型なのでJSON->dict に
    todo = jsonable_encoder(data) #dict型になる
    res = await db_create_todo(todo)
    response.status_code = HTTP_201_CREATED
    response.set_cookie(
        key="access_token", value=f"Bearer {new_token}", httponly=True, samesite="none", secure=True)
    if res:
        return res
    raise HTTPException(
        status_code = 404, detail="Create task failed")

@router.get("/api/todo", response_model=List[Todo])
async def get_todos(request: Request):
    # auth.verify_jwt(request)
    res = await db_get_todos()
    return res

@router.get("/api/todo/{id}", response_model=Todo) #1つのtodoが返ってくるので、response_modelはTodo
async def get_single_todo(request: Request, response: Response, id: str):
    new_token, _ = auth.verify_update_jwt(request) #payloadは使用しないので、アンダースコア
    res = await db_get_single_todo(id)
    response.set_cookie(
        key="access_token", value=f"Bearer {new_token}", httponly=True, samesite="none", secure=True)
    if res:
        return res
    raise HTTPException(
        status_code=404, detail=f"Task of ID:{id} doesn't exist")

@router.put("/api/todo/{id}", response_model=Todo)
async def update_todo(request: Request, response: Response, id: str, data: TodoBody, csrf_protect: CsrfProtect = Depends()):
    new_token = auth.verify_csrf_update_jwt(
        request, csrf_protect, request.headers)
    todo = jsonable_encoder(data)
    res = await db_update_todo(id, todo)
    response.set_cookie(
        key="access_token", value=f"Bearer {new_token}", httponly=True, samesite="none", secure=True)
    if res:
        return res
    raise HTTPException(
        status_code=404, detail="Update task failed")

@router.delete("/api/todo/{id}", response_model=SuccessMsg)
async def delete_todo(request: Request, response: Response, id: str, csrf_protect: CsrfProtect=Depends()):
    new_token = auth.verify_csrf_update_jwt(
        request, csrf_protect, request.headers)
    res = await db_delete_todo(id)
    response.set_cookie(
        key="access_token", value=f"Bearer {new_token}", httponly=True, samesite="none", secure=True)
    if res:
        return {'message': 'Successfully deleted'}
    raise HTTPException(
        status_code=404, detail="Delete task failed")

