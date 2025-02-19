import requests
import time
import json

API_KEY = "1923ba548c0ec48949b9f865c2037652"  # 替换为实际Key

def get_commercial_residences():
    """获取商务住宅数据（类型代码参考高德官方文档）"""
    print("⌛ 开始获取武汉商务住宅数据...")
    url = "https://restapi.amap.com/v3/place/text"
    residences = []
    page = 1
    total_count = 0
    
    while True:
        print(f"📄 正在获取第 {page} 页数据...", end="\r")
        params = {
            "key": API_KEY,
            "city": "武汉",
            "types": "120302",
            "offset": 50,
            "page": page,
            "extensions": "base"
        }
        
        try:
            response = requests.get(url, params=params)
            data = response.json()
            
            if data.get("status") == "1":
                current_count = len(data.get("pois", []))
                if current_count > 0:
                    total_count += current_count
                    print(f"✅ 第 {page:2d} 页获取成功 | 本页 {current_count:2d} 条 | 累计 {total_count:4d} 条")
                    
                    for poi in data["pois"]:
                        residence = {
                            "id": poi["id"],
                            "name": poi["name"],
                            "address": poi.get("address", ""),
                            "location": poi["location"],
                            "district": f"{poi['pname']}{poi['cityname']}{poi['adname']}"
                        }
                        residences.append(residence)
                    
                    if current_count < 50:
                        break
                    page += 1
                    time.sleep(0.1)
                else:
                    break
            else:
                print(f"❌ 第 {page} 页获取失败：{data.get('info', '未知错误')}")
                break
                
        except Exception as e:
            print(f"\n❌ 获取异常：{str(e)}")
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



# 在代码开头添加测试用例
def debug_single_case():
    test_location = "114.407143,30.474225"  # 武汉光谷广场坐标
    print("\n=== 测试用例调试 ===")
    print("医疗检查:", check_surrounding(114.407143, 30.474225, 5000, "090101"))
    print("交通检查:", check_surrounding(114.407143, 30.474225, 3000, "150500|150700"))
    print("环境检查:", check_surrounding(114.407143, 30.474225, 3000, "110100"))
    print("商业检查:", check_surrounding(114.407143, 30.474225, 3000, "060100|060400"))

debug_single_case()  # 在validate_residences()之前调用
