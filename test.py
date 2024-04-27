import base64
import requests
from sqlite_operation import MusicListOperation

# with MusicListOperation.DatabaseManager() as manager:
#     result = manager.insert_data(
#         music_name = "i walk this earth all by myself.mp3",
#         music_data = open("D:\\HTML_MX\\MyFreeMusicPlayer\\MyFreeMusicPlayer\\audio\\i walk this earth all by myself.mp3", "rb").read()
#     )~
#     print(result)

host = "http://127.0.0.1:1949"
# host = "http://www.pymili-blog.icu:1949"
post_data = {
    "user_name": "admin",
    "key": "1949_10_1",
    "music_name": "Slow Down",
    "music_url": "https://m804.music.126.net/20240427102611/e45c58f800b9438763d8c01c72d6c31c/jdyyaac/obj/w5rDlsOJwrLDjj7CmsOj/19849510232/cf10/7836/c2c8/52ab93a5aa7e8966e63a07796589882f.m4a?authSecret=0000018f1d48f47909af0aa4638119de"
}
# files = {'upload_file': ('MAMUSUONA - Slow Down (0.8X版).flac', open("E:\\音乐\\MAMUSUONA - Slow Down (0.8X版).flac", "rb"))}
with requests.post(f"{host}/upload_music", data=post_data) as post:
    print(post.json())

with requests.post(f"{host}/get_my_music", json={"user_name": "admin", "key": "1949_10_1"}) as post:
    print(post.json())