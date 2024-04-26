import os
import json
import base64
from typing import *
from fastapi import FastAPI, Response, Request
from fastapi.responses import FileResponse
from loguru import logger
from sqlite_operation import MusicListOperation, UserOperation

app = FastAPI()
MUSIC_TEMP_DIR = os.path.join(os.getcwd(), "music_temp")


async def getParams(request: Request) -> dict:
    """
    根据通过的Request对象获取json数据
    :param request: Request
    :return dict
    """
    # 获取请求体内容
    body = await request.body()

    # 检查请求体是否为空
    if not body:
        return {}

    # 解析请求体中的JSON数据
    try:
        params = json.loads(body)
    except json.JSONDecodeError:
        return {}
    
    return params


async def inspect_user_info(
        user_name: str,
        key: str,
        pwd: Union[str, None] = None
    ) -> bool:
    """
    检查用户信息是否匹配
    :param user_name: str 用户的名称
    :param key: str 用户的KEY值
    :param pwd: Union[str, None] = None 用户密码（非必填）
    :return bool
    """
    with UserOperation.DatabaseManager() as user_manager:
        current_user_info = user_manager.get_current_user_info()
        if not current_user_info:
            logger.error("数据库错误！")
            return False
        
    if user_name != current_user_info['user_name']:
        return False
    if key != current_user_info['key']:
        return False
    
    if not pwd:
        return True
    if pwd != current_user_info['password']:
        return False


@app.post("/get_my_music")
async def get_my_music(request: Request) -> Response:
    """
    通过用户的信息获取到音乐列表
    :param request: Request 请求对象
    """
    result = {"code": 404, "content": "null"}

    # 获取请求参数并检查
    params = await getParams(request)
    if not params:
        result["content"] = "参数缺少！"
        return Response(
            content=json.dumps(result),
            media_type="application/json"
        )

    # 获取请求参数
    user_name = params.get("user_name")
    key = params.get("key")
    end = params.get("end")
    # 检查参数是否完整
    if not all([user_name, key]):
        result["content"] = "参数错误！"
        return Response(
            content=json.dumps(result),
            media_type="application/json"
        )
    
    # 检查用户的信息是否真实
    inspect_result = await inspect_user_info(user_name, key)
    if inspect_result is False:
        logger.error("用户信息错误！")
        result["content"] = "用户信息错误！"
        return Response(
            content=json.dumps(result),
            media_type="application/json"
        )
    logger.info("用户信息准确。")
        
    # 读取sqlite数据库
    with MusicListOperation.DatabaseManager() as DBmanager:
        list_data = DBmanager.get_records_by_range(end=end)
        if not list_data:
            return Response(
                content=json.dumps(result),
                media_type="application/json"
            )
        
        music_list = await handle_music_list(list_data)
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
    # 查看缓存文件夹是否存在，如果不存在进行创建
    if os.path.isdir(MUSIC_TEMP_DIR) is False:
        try:
            os.makedirs(MUSIC_TEMP_DIR)
        except Exception as e:
            logger.error(e)
            return result
        
    # 开始处理音乐列表
    for music in music_list:
        temp_file = os.path.join(MUSIC_TEMP_DIR, music['music_name'])
        if os.path.isfile(temp_file) is False:
            with open(temp_file, "wb") as wfp:
                wfp.write(music['music_data'])

        result.append({
            "music_name": music['music_name'],
            "music_img": music['music_img'],
            "music_url": f"/music_temp/{music['music_name']}"
        })
    
    return result


@app.get("/music_temp/{filename}")
async def download_temp_file(filename: str) -> FileResponse:
    """
    返回临时的音乐文件
    :param filename: str 文件名
    :return Union[FileResponse, int]
    """ 
    temp_file = os.path.join(MUSIC_TEMP_DIR, filename)
    if os.path.isfile(temp_file) is False:
        return 500

    return FileResponse(temp_file)


@app.post("/upload_music")
async def upload_music(request: Request) -> Response:
    """
    上传音乐至数据库
    :return dict
    """
    result = {"code": 404, "content": "null"}

    # 获取请求参数并检查
    params = await getParams(request)
    if not params:
        result["content"] = "参数缺少！"
        return Response(
            content=json.dumps(result),
            media_type="application/json"
        )
    
    # 用户信息请求参数
    user_name = params.get("user_name")
    key = params.get("key")
    if not all([user_name, key]):
        result["content"] = "用户名或key缺少！"
        return Response(
            content=json.dumps(result),
            media_type="application/json"
        )
    inspect_result = inspect_user_info(user_name, key)
    if inspect_result is False:
        result["content"] = "用户信息错误！"
        return Response(
            content=json.dumps(result),
            media_type="application/json"
        )
    
    # 音乐数据
    music_name = params.get("music_name")
    music_img = params.get("music_img")
    base64_data = params.get("base64_data")
    if not all([music_name, base64_data]):
        result["content"] = "音乐名称和base64数据为必填项。"
        return Response(
            content=json.dumps(result),
            media_type="application/json"
        )
    # 对base64数据解码
    decode_byte = base64.b64decode(base64_data)

    # 将新数据插入数据库
    with MusicListOperation.DatabaseManager() as db_manager:
        insert_result = db_manager.insert_data(
            music_name = music_name,
            music_data = decode_byte,
            music_img = music_img
        )
        if insert_result is False:
            result['code'] = 500
            result["content"] = "添加音乐失败！"
            return Response(
                content=json.dumps(result),
                media_type="application/app"
            )
    
    result['code'] = 200
    result["content"] = "添加成功！"
    return Response(
        content=json.dumps(result),
        media_type="application/app"
    )
