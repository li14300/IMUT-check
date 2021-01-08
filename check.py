import random
import campus
import time
import requests
import json


# 内蒙古工业大学完美校园健康打卡
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
    if place == 1:
        lng = str(111.557612 + random.random() / 1000)
        lat = str(40.798552 + random.random() / 1000)
        area = "金川校区"
        areaStr = '{\"streetNumber\":\"\",\"street\":\"\",\"district\":\"土默特左旗\",\"city\":\"呼和浩特市\",' \
                  '\"province\":\"内蒙古自治区\",\"town\":\"\",\"pois\":\"内蒙古工业大学金川校区\",\"lng\":' + lng + ',' \
                  '\"lat\":' + lat + ',\"address\":\"内蒙古工业大学金川校区\",\"text\":\"内蒙古自治区-呼和浩特市\",' \
                  '\"code\":\"\"}'
    elif place == 2:
        lng = str(111.557612 + random.random() / 1000)
        lat = str(40.853463 + random.random() / 1000)
        area = "新城校区"
        areaStr = '{\"streetNumber\":\"\",\"street\":\"\",\"district\":\"新城区\",\"city\":\"呼和浩特市\",' \
                  '\"province\":\"内蒙古自治区\",\"town\":\"\",\"pois\":\"内蒙古工业大学\",\"lng\":' + lng + ',' \
                  '\"lat\":' + lat + ',\"address\":\"内蒙古工业大学\",\"text\":\"内蒙古自治区-呼和浩特市\",' \
                  '\"code\":\"\"}'
    else:
        lng = str(111.293511 + random.random() / 1000)
        lat = str(40.086395 + random.random() / 1000)
        area = "准格尔校区"
        areaStr = '{\"streetNumber\":\"\",\"street\":\"\",\"district\":\"准格尔旗\",\"city\":\"鄂尔多斯市\",' \
                  '\"province\":\"内蒙古自治区\",\"town\":\"\",\"pois\":\"内蒙古工业大学准格尔校区\",\"lng\":' + lng + ',' \
                  '\"lat\":' + lat + ',\"address\":\"内蒙古工业大学准格尔校区\",\"text\":\"内蒙古自治区-鄂尔多斯市\",' \
                  '\"code\":\"\"}'
    temp = round(random.uniform(36.2, 36.8), 1)

    # 判断时间上午或下午
    apm = time.strftime("%p")
    if apm == "AM":
        json_data = {
            "businessType": "epmpics",
            "method": "submitUpInfoSchool",
            "jsonData": {
                "deptStr": {
                    "deptid": deptid,
                    "text": text
                },
                "areaStr": areaStr,
                "reportdate": int(round(time.time() * 1000)),
                "customerid": 533,
                "deptid": deptid,
                "source": "app",
                "templateid": "clockSign1",
                "stuNo": stuNo,
                "username": username,
                "userid": userid,
                "updatainfo": [
                    {
                        "propertyname": "temperature",
                        "value": temp
                    },
                    {
                        "propertyname": "symptom",
                        "value": "无症状"
                    },
                    {
                        "propertyname": "isTouch",
                        "value": "否"
                    },
                    {
                        "propertyname": "xueshenglx1",
                        "value": "本专科生"
                    },
                    {
                        "propertyname": "area",
                        "value": area
                    },
                    {
                        "propertyname": "mz",
                        "value": mz
                    },
                    {
                        "propertyname": "phone",
                        "value": phone
                    },
                    {
                        "propertyname": "daoshi",
                        "value": daoshi
                    },
                    {
                        "propertyname": "notice",
                        "value": "已知晓"
                    }
                ],
                "customerAppTypeRuleId": 199,
                "clockState": 0,
                "token": token
            },
            "token": token
        }
    else:
        json_data = {
            "businessType": "epmpics",
            "method": "submitUpInfoSchool",
            "jsonData": {
                "deptStr": {
                    "deptid": deptid,
                    "text": text
                },
                "areaStr": areaStr,
                "reportdate": int(round(time.time() * 1000)),
                "customerid": 533,
                "deptid": deptid,
                "source": "unknown",
                "templateid": "clockSign2",
                "stuNo": stuNo,
                "username": username,
                "userid": userid,
                "updatainfo": [
                    {
                        "propertyname": "temperature",
                        "value": temp
                    },
                    {
                        "propertyname": "symptom",
                        "value": "无症状"
                    }
                ],
                "customerAppTypeRuleId": 358,
                "clockState": 0,
                "token": token
            },
            "token": token
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
