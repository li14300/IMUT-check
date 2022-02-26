import random
import campus
import time
import requests
import json


# 内蒙古工业大学完美校园健康打卡（校外版）
# @li14300 鹏宇的昵称已被占用
def check_data(data):
    # 从campus中获取认证后的sessionId和用户信息
    token = data[1]
    deptid = data[2]
    text = data[3]
    stuNo = data[4]
    username = data[5]
    userid = data[6]
    with open('./userinfo.json', 'r', encoding='utf8')as fp:
        json_data = json.load(fp)
    phone = json_data["single"]["phone"]
    mz = json_data["single"]["mz"]
    daoshi = json_data["single"]["daoshi"]
    place = json_data["single"]["place"]
    lng0 = json_data["single"]["lng0"]
    lat0 = json_data["single"]["lat0"]
    district = json_data["single"]["district"]
    city = json_data["single"]["city"]
    province = json_data["single"]["province"]
    address = json_data["single"]["address"]
    if place == 1:
        area = "金川校区"
    elif place == 2:
        area = "新城校区"
    else:
        area = "准格尔校区"
    lng = str(lng0 + random.random() / 100000)
    lat = str(lat0 + random.random() / 100000)
    areaStr = '{\"streetNumber\":\"\",\"street\":\"\",\"district\":\"' + district + '\",\"city\":\"' + city + '\",' \
              '\"province\":\"' + province + '\",\"town\":\"\",\"pois\":\"' + address + '\",\"lng\":' + lng + ',' \
              '\"lat\":' + lat + ',\"address\":\"' + address + '\",\"text\":\"' + province + '-' + city + '\",' \
              '\"code\":\"\"} '
    temp = round(random.uniform(36.2, 36.8), 1)
    print(token)

    # 获取ver信息
    healthy_post_json = {
        "businessType": "epmpics",
        "jsonData": {"templateid": "pneumonia", "token": token},
        "method": "userComeApp",
    }
    ver_res = requests.post(
        url="https://reportedh5.17wanxiao.com/sass/api/epmpics",
        json=healthy_post_json
    ).json()
    ver_data = json.loads(ver_res["data"])

    # 组合打卡数据
    json_data = {
        "businessType": "epmpics",
        "method": "submitUpInfo",
        "jsonData": {
            "deptStr": {
                "deptid": deptid,
                "text": text
            },
            "areaStr": areaStr,
            "reportdate": int(round(time.time() * 1000)),
            "customerid": "533",
            "deptid": deptid,
            "source": "app",
            "templateid": "pneumonia",
            "stuNo": stuNo,
            "username": username,
            "phonenum": "",
            "userid": userid,
            "updatainfo": [{
                "propertyname": "temperature",
                "value": temp
            }, {
                "propertyname": "symptom",
                "value": "无症状"
            }, {
                "propertyname": "isTouch",
                "value": "否"
            }, {
			    "propertyname": "jkgkry",
			    "value": "否"
		    }, {
                "propertyname": "bodyzk",
                "value": "否"
            }, {
			    "propertyname": "qt",
			    "value": ""
		    }, {
                "propertyname": "xinqing",
                "value": "否"
            }, {
                "propertyname": "cxjh",
                "value": "无"
            }, {
                "propertyname": "isAlreadyInSchool",
                "value": "本专科生"
            }, {
                "propertyname": "area1",
                "value": area
            }, {
                "propertyname": "jtdz",
                "value": mz
            }, {
                "propertyname": "emergencyContact",
                "value": phone
            }, {
                "propertyname": "age",
                "value": daoshi
            }],
            "ver": ver_data["ver"],
            "gpsType": 1,
            "token": token
        }
    }
    return json_data


def check_post(json_data):
    # 发送，解析post数据
    url_check = "https://reportedh5.17wanxiao.com/sass/api/epmpics"
    headers = {'Content-Type': 'application/json'}
    resp = requests.post(url_check, headers=headers, json=json_data).text
    resp_json = json.loads(resp)
    return resp_json


def check_info(resp_json):
    # 判断是否打卡成功，发送推送数据
    if resp_json["msg"] == "成功":
        with open('./userinfo.json', 'r', encoding='utf8')as fp:
            json_data = json.load(fp)
        serverurl = json_data["single"]["serverurl"]
        apm = time.strftime("%Y-%m-%d, %H:%M:%S")
        try:
            requests.post(serverurl, data={"text": "打卡完成", "desp": "" + apm + "打卡完成"})
            print("打卡成功，推送成功")
        except:
            print("打卡成功，推送失败")
        return str("打卡成功")


def check_start(event, context):
    data = campus.campus_main()
    json_data = check_data(data)
    resp_json = check_post(json_data)
    result = check_info(resp_json)
    return result

