import requests
import sqlite_operation

with requests.post("http://127.0.0.1:1949/get_my_music", json={"user_name": "PYmili", "key": "key1"}) as post:
    print(post.json())


# with sqlite_operation.DatabaseManager() as manager:
#     result = manager.insert_data(
#         user_name = "PYmili",
#         key = "key1",
#         music_name = "i walk this earth all by myself.mp3",
#         music_data = open("D:\\HTML_MX\\MyFreeMusicPlayer\\MyFreeMusicPlayer\\audio\\i walk this earth all by myself.mp3", "rb").read()
#     )
#     print(result)