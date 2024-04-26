import base64
import requests
from sqlite_operation import MusicListOperation

# with MusicListOperation.DatabaseManager() as manager:
#     result = manager.insert_data(
#         music_name = "i walk this earth all by myself.mp3",
#         music_data = open("D:\\HTML_MX\\MyFreeMusicPlayer\\MyFreeMusicPlayer\\audio\\i walk this earth all by myself.mp3", "rb").read()
#     )
#     print(result)

post_data = {
    "user_name": "admin",
    "key": "1949_10_1",
    "music_name": "test",
    "base64_data": base64.b64encode(open("E:\\音乐\\MAMUSUONA - Slow Down (0.8X版).flac", "rb").read()).decode('utf-8')
}
with requests.post("http://127.0.0.1:1949/upload_music", json=post_data) as post:
    print(post.json())

with requests.post("http://127.0.0.1:1949/get_my_music", json={"user_name": "admin", "key": "1949_10_1"}) as post:
    print(post.json())