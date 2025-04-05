import os
import openai
from dotenv import load_dotenv, find_dotenv

# 读取本地/项目的环境变量。
# 如果没有找到.env文件，则会报错。
def get_chatanywhere_api_key():
    # find_dotenv()寻找并定位.env文件的路径
    # load_dotenv()读取该.env文件，并将其中的环境变量加载到当前的运行环境中
    # 如果你设置的是全局的环境变量，这行代码则没有任何作用。
    _ = load_dotenv(find_dotenv())
    return os.environ['CHATANYWHERE_API_KEY']
# 获取环境变量 OPENAI_API_KEY
#openai.api_key = get_openai_key()
def get_chatanywhere_url():
    # find_dotenv()寻找并定位.env文件的路径
    # load_dotenv()读取该.env文件，并将其中的环境变量加载到当前的运行环境中
    # 如果你设置的是全局的环境变量，这行代码则没有任何作用。
    _ = load_dotenv(find_dotenv())
    return os.environ['CHATANYWHERE_BASE_URL']
