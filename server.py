import os
import json
from typing import *
from fastapi import FastAPI, Response, Request
from fastapi.responses import FileResponse
from loguru import logger
import sqlite_operation

app = FastAPI()


@app.post("/get_my_music")
async def get_my_music(request: Request) -> Response:
    """
    通过用户的信息获取到音乐列表
    :param request: Request 请求对象
    """
    result = {"code": 404, "content": "null"}

    # 获取请求体内容
    body = await request.body()

    # 检查请求体是否为空
    if not body:
        result["content"] = "主体错误！"
        return Response(
            content=json.dumps(result),
            media_type="application/json"
        )

    # 解析请求体中的JSON数据
    try:
        params = json.loads(body)
    except json.JSONDecodeError:
        result["content"] = "参数缺少！"
        return Response(
            content=json.dumps(result),
            media_type="application/json"
        )

    # 获取请求参数
    user_id = params.get("user_id")
    user_name = params.get("user_name")
    key = params.get("key")
    end = params.get("range")

    # 检查参数是否完整
    if not all([user_name, key]):
        result["content"] = "参数错误！"
        return Response(
            content=json.dumps(result),
            media_type="application/json"
        )

    # 读取sqlite数据库
    with sqlite_operation.DatabaseManager() as DBmanager:
        identifier = user_id if user_id else user_name
        user_data = DBmanager.get_records_by_user(identifier, end=end)
        if not user_data:
            return Response(
                content=json.dumps(result),
                media_type="application/json"
            )
        
        user_key = user_data[0].get("key")
        if not user_key:
            return Response(
                content=json.dumps(result),
                media_type="application/json"
            )
        
        if user_key == key:
            music_list = await handle_music_list(user_data)
            result["content"] = music_list

    result['code'] = 200
    return Response(
        content=json.dumps(result),
        media_type="application/json"
    )


async def handle_music_list(music_list: List[Dict]) -> List:
    """
    处理通过的音乐列表，并填入临时音乐链接
    :param music_list: List[Dict] 音乐数据列表
    :return str
    """
    result = []
    temp_dir = os.path.join(os.getcwd(), "music_temp")
    if os.path.isdir(temp_dir) is False:
        try:
            os.makedirs(temp_dir)
        except Exception as e:
            logger.error(e)
            return result
        
    for music in music_list:
        temp_file = os.path.join(temp_dir, music['music_name'])
        with open(temp_file, "wb") as wfp:
            wfp.write(music['music_data'])

        if os.path.isfile(temp_file) is False:
            logger.error(f"未检测到文件：{temp_file}")
            continue

        result.append({
            "name": music['music_name'],
            "img": music['music_img'],
            "url": f"/music_temp/{music['music_name']}"
        })
    
    return result


@app.get("/music_temp/{filename}")
async def download_temp_file(filename: str):
    """
    返回临时文件
    """ 
    temp_file = os.path.join(os.getcwd(), "music_temp", filename)
    if os.path.isfile(temp_file) is False:
        return 500

    return FileResponse(temp_file)