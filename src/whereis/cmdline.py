# 使用高德API获取医院数据示例

import requests
import json

API_KEY = "1ce1ebd9f26476f66f50dcaab25479f5"

def get_hospitals_json():
    url = "https://restapi.amap.com/v3/place/text"
    hospitals = []
    page = 1
    
    while True:
        params = {
            "key": API_KEY,
            "keywords": "三甲医院",
            "city": "武汉",
            "types": "090101",
            "offset": 50,
            "page": page,
            "extensions": "base"
        }
        
        response = requests.get(url, params=params)
        data = response.json()
        
        if data["status"] == "1" and int(data["count"]) > 0:
            for poi in data["pois"]:
                hospital = {
                    "id": poi["id"],
                    "name": poi["name"],
                    "address": poi["address"],
                    "location": {
                        "lng": poi["location"].split(",")[0],
                        "lat": poi["location"].split(",")[1]
                    },
                    "tel": poi.get("tel", ""),
                    "district": poi["pname"] + poi["cityname"] + poi["adname"]
                }
                hospitals.append(hospital)
            
            if len(data["pois"]) < 50:
                break
            page += 1
        else:
            break
    
    return json.dumps({
        "status": "success",
        "count": len(hospitals),
        "hospitals": hospitals
    }, ensure_ascii=False, indent=2)

# 执行并打印
result = get_hospitals_json()
print(result)


def check_surrounding(lng, lat, radius, types):
    """检查指定坐标周边是否存在某类设施"""
    url = "https://restapi.amap.com/v3/place/around"
    params = {
        "key": API_KEY,
        "location": f"{lng},{lat}",
        "radius": radius,
        "types": types,
        "offset": 20,
        "page": 1
    }
    try:
        res = requests.get(url, params=params).json()
        return int(res.get('count',0)) > 0
    except:
        return False