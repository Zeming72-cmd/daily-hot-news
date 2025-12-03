import requests
import json
import datetime
import time

url = "https://api.bilibili.com/x/web-interface/ranking/v2?rid=0&type=all"

headers = {
    # 1. 模拟浏览器身份
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    # 2. 告诉它是从官网首页点进去的 (防盗链)
    "Referer": "https://www.bilibili.com/v/popular/all",
    # 3. 加一个空的 Cookie，有时候 B 站会检查有没有这个字段
    "Cookie": "buvid3=infoc;", 
    # 4. 告诉它我们接受 JSON 格式
    "Accept": "application/json, text/plain, */*"
}

print("正在连接 Bilibili 服务器 (加强伪装版)...")

try:
    # 稍微停顿 1 秒，防止请求太快
    time.sleep(1)
    
    response = requests.get(url, headers=headers)
    json_data = response.json()
    
    if json_data['code'] != 0:
        print(f"❌ B站拒绝了访问 (代码 {json_data['code']}): {json_data['message']}")
    else:
        video_list = json_data['data']['list']
        my_hot_data = []
        update_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        print(f"✅ 获取成功！更新时间: {update_time}")
        
        for index, item in enumerate(video_list[:10]):
            video = {
                "rank": index + 1,
                "title": item['title'],
                "author": item['owner']['name'],
                "play_count": item['stat']['view'],
                # 处理链接：有的可能有 short_link_v2，有的要用 bvid 拼凑
                "link": item.get('short_link_v2', f"https://www.bilibili.com/video/{item['bvid']}")
            }
            my_hot_data.append(video)
            print(f"第 {index+1} 名: {video['title']}")

        final_output = {
            "source": "Bilibili热门",
            "updated_at": update_time,
            "news": my_hot_data
        }
        
        with open('data.json', 'w', encoding='utf-8') as f:
            json.dump(final_output, f, ensure_ascii=False, indent=2)
        
        print("💾 文件已保存为 data.json")

except Exception as e:
    print("❌ 代码出错啦：", e)