import base64
import hashlib
import json
import random
import requests
from Crypto import Random  # pycryptodome
from Crypto.Cipher import DES3
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5
from Crypto.Util.Padding import pad


# 内蒙古工业大学完美校园健康打卡
# @li14300 鹏宇的昵称已被占用
# des3加密
def des_3_encrypt(string, key, iv):
    cipher = DES3.new(key, DES3.MODE_CBC, iv.encode("utf-8"))
    ct_bytes = cipher.encrypt(pad(string.encode('utf8'), DES3.block_size))
    ct = base64.b64encode(ct_bytes).decode('utf8')
    return ct


# des3解密
def object_encrypt(object_to_encrypt, key, iv="66666666"):
    return des_3_encrypt(json.dumps(object_to_encrypt), key, iv)


# rsa解密，用私钥解密session和appKey
def rsa_decrypt(input_string, private_key):
    input_bytes = base64.b64decode(input_string)
    rsa_key = RSA.importKey("-----BEGIN RSA PRIVATE KEY-----\n" + private_key + "\n-----END RSA PRIVATE KEY-----")
    cipher = PKCS1_v1_5.new(rsa_key)
    # noinspection PyArgumentList
    return str(cipher.decrypt(input_bytes, Random.new().read), 'utf-8')


# 创建密钥对
def create_key_pair(size):
    rsa = RSA.generate(size, Random.new().read)
    private_key = str(rsa.export_key(), 'utf8')
    private_key = private_key.split('-\n')[1].split('\n-')[0]
    public_key = str(rsa.publickey().export_key(), 'utf8')
    public_key = public_key.split('-\n')[1].split('\n-')[0]
    return public_key, private_key


# 第一步，创建空白信息，私钥，公钥
def create_info():
    rsa_keys = create_key_pair(1024)
    deviceId = str(random.randint(999999999999999, 9999999999999999))
    public_key = rsa_keys[0]
    private_key = rsa_keys[1]
    return deviceId, public_key, private_key


# 第二步，与服务器交换公钥，获取对应的sessionId，和appKey
def exchange_secret(public_key, private_key):
    resp_exch = requests.post(
        "https://server.17wanxiao.com/campus/cam_iface46/exchangeSecretkey.action",
        headers={
            "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 10; MI 9 MIUI/20.11.5)",
        },
        json={
            "key": public_key
        }
    )
    session_info = json.loads(
        rsa_decrypt(resp_exch.text.encode(resp_exch.apparent_encoding), private_key)
    )
    sessionId = session_info["session"]
    appKey = session_info["key"][:24]
    return sessionId, appKey


# 第三步，正式登录，使sessionId可用
def login(phone, password, deviceId, sessionId, appKey):
    password_list = []
    for i in password:
        password_list.append(des_3_encrypt(i, appKey, "66666666"))
    login_args = {
        "appCode": "M002",
        "deviceId": deviceId,
        "netWork": "wifi",
        "password": password_list,
        "qudao": "guanwang",
        "requestMethod": "cam_iface46/loginnew.action",
        "shebeixinghao": "MI 9",
        "systemType": "android",
        "telephoneInfo": "10.0",
        "telephoneModel": "MI 9",
        "type": "1",
        "userName": phone,
        "wanxiaoVersion": 10462101,
        "yunyingshang": "07"
    }
    upload_args = {
        "session": sessionId,
        "data": object_encrypt(login_args, appKey)
    }
    resp_login = requests.post(
        "https://server.17wanxiao.com/campus/cam_iface46/loginnew.action",
        headers={"campusSign": hashlib.sha256(json.dumps(upload_args).encode('utf-8')).hexdigest()},
        json=upload_args
    ).json()
    return resp_login


# 第四步，获取用户信息
def get_main_info(sessionId):
    token = {'token': sessionId}
    resp_user = requests.post(
        "https://reportedh5.17wanxiao.com/api/clock/school/getUserInfo",
        data=token
    ).json()
    return resp_user


# 函数排序，对return数据拆分，方便调用
def campus_start(phone, password, mz, daoshi, place):
    # 第一步
    create_info_result = create_info()
    deviceId = create_info_result[0]
    public_key = create_info_result[1]
    private_key = create_info_result[2]
    # 第二步
    exchange_secret_result = exchange_secret(public_key, private_key)
    sessionId = exchange_secret_result[0]
    appKey = exchange_secret_result[1]
    login(phone, password, deviceId, sessionId, appKey)
    # 第三步
    data = get_main_info(sessionId)
    deptid = data["userInfo"]["classId"]
    classDescription = data["userInfo"]["classDescription"]
    stuNo = data["userInfo"]["stuNo"]
    username = data["userInfo"]["username"]
    userid = data["userInfo"]["userId"]
    # 返回结果
    return appKey, sessionId, deptid, classDescription, stuNo, username, userid, mz, phone, daoshi, place


# 函数启动入口，便于调用与云函数挂载
def campus_main():
    with open('./userinfo.json', 'r', encoding='utf8')as fp:
        json_data = json.load(fp)
    phone = json_data["single"]["phone"]
    password = json_data["single"]["password"]
    mz = json_data["single"]["mz"]
    daoshi = json_data["single"]["daoshi"]
    place = json_data["single"]["place"]
    data_campus = campus_start(phone, password, mz, daoshi, place)
    return data_campus


campus_main()
