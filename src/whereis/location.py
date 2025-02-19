import requests
import time
import json

API_KEY = "1923ba548c0ec48949b9f865c2037652"  # 替换为实际Key


def get_commercial_residences():
    """综合解决方案（区域+类型细分）"""
    print("⌛ 开始获取武汉住宅数据...")
    districts = ["江岸区", "江汉区", "硚口区", "汉阳区", "武昌区", 
                "青山区", "洪山区", "东西湖区", "蔡甸区", "江夏区", 
                "黄陂区", "新洲区"]
    type_groups = ["080400|080401|080402", 
                   "10000|100100|100101|100102|100103|100104|100105|100200|100201", 
                   "120304"]
    url = "https://restapi.amap.com/v3/place/text"
    
    residences = []
    for district in districts:
        for types in type_groups:
            page = 1
            while True:
                params = {
                    "key": API_KEY,
                    "city": "武汉",
                    "district": district,
                    "types": types,
                    "offset": 50,
                    "page": page,
                    "extensions": "base"
                }
                
                try:
                    response = requests.get(url, params=params)
                    data = response.json()
                    
                    if data.get("status") == "1":
                        current_pois = data.get("pois", [])

                        current_count = len(current_pois)
                        if current_count == 0:
                            print(f" ■ 第{page}页无数据，终止采集")
                            break
                        residences.extend(current_pois)
                        
                        print(f"{district}-{types} 第{page}页 获取{len(current_pois)}条")
                        
                        if page >= 25:# 遵守API最大页数限制
                            print("▲已达API最大25页限制")
                            break
                        # if len(current_pois) < 50:
                        #     break
                        page += 1
                        time.sleep(0.2)
                    else:
                        break
                
                except Exception as e:
                    print(f"请求失败：{str(e)}")
                    break
    
    print(f"\n🏁 数据获取完成！共获取 {len(residences)} 条商务住宅数据")
    return residences


def check_surrounding(lng, lat, radius, types):
    """检查周边设施存在性"""
    url = "https://restapi.amap.com/v5/place/around"
    params = {
        "key": API_KEY,
        "location": f"{lng},{lat}",
        "radius": radius,
        "types": types,
        "offset": 1,
        "page": 1
    }
    
    try:
        res = requests.get(url, params=params).json()
        return int(res.get("count", 0)) > 0
    except:
        return False

def validate_residences():
    """主验证流程"""
    residences = get_commercial_residences()
    qualified = []
    total = len(residences)
    start_time = time.time()
    
    print(f"\n🔍 开始验证周边设施，共需验证 {total} 个住宅")
    print("-" * 60)

    for index, res in enumerate(residences, 1):
        # 进度计算
        progress = index / total * 100
        elapsed = time.time() - start_time
        eta = (elapsed / index) * (total - index) if index > 0 else 0
        
        # 打印当前进度
        print(f"[{index:04d}/{total:04d}] {progress:5.1f}% | 🕒 已用 {elapsed:.0f}s | ⏳ 剩余 {eta:.0f}s | 正在验证：{res['name'][:20]}...")
        
        lng, lat = res["location"].split(",")
        
        # 并行检查四个条件
        conditions = {
            "medical": check_surrounding(lng, lat, 5000, "090101"),
            "transportation": check_surrounding(lng, lat, 3000, "150500|150700"),
            "environment": check_surrounding(lng, lat, 3000, "110100|110000|110105|110106"),
            "commerce": check_surrounding(lng, lat, 3000, "060100|060101|060102|060103|060400")
        }
        
        if all(conditions.values()):
            qualified.append({
                "住宅信息": res,
                "配套详情": {
                    "5km三甲医院": conditions["medical"],
                    "3km交通设施": conditions["transportation"],
                    "3km公园绿地": conditions["environment"],
                    "3km商业配套": conditions["commerce"]
                }
            })
        
        # 每10%打印进度条
        if index % max(1, total//10) == 0 or index == total:
            filled = int(40 * index/total)
            bar = '█' * filled + '-' * (40 - filled)
            percent = (index/total)*100
            print(f"\n📊 整体进度 [{bar}] {percent:.1f}%")
            print(f"🏠 已检查 {index} 个 | ✅ 合格 {len(qualified)} 个 | 🚀 效率 {index/elapsed:.1f}个/秒\n" if index > 0 else "")
        
        time.sleep(0.2)

    print("=" * 60)
    print(f"🎉 验证完成！总耗时 {time.time()-start_time:.1f} 秒")
    print(f"🏆 最终合格数量：{len(qualified)} 个住宅项目")
    
    return json.dumps({
        "status": "success",
        "qualified_count": len(qualified),
        "qualified_residences": qualified
    }, ensure_ascii=False, indent=2)

# 执行验证并打印结果
print(validate_residences())
