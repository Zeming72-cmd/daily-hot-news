import requests
import json
import datetime
import time
import os  # 新增：用于读取系统环境变量

# --- 配置区 ---
# B站接口
bilibili_url = "https://api.bilibili.com/x/web-interface/ranking/v2?rid=0&type=all"
# PushPlus 接口
pushplus_url = "http://www.pushplus.plus/send"

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://www.bilibili.com/v/popular/all",
    "Cookie": "buvid3=infoc;", 
    "Accept": "application/json, text/plain, */*"
}

def get_bilibili_hot():
    print("正在连接 Bilibili 服务器...")
    try:
        time.sleep(1)
        response = requests.get(bilibili_url, headers=headers)
        json_data = response.json()
        
        if json_data['code'] != 0:
            print(f"❌ B站拒绝了访问: {json_data['message']}")
            return None
            
        video_list = json_data['data']['list']
        my_hot_data = []
        update_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 准备发给微信的简报（只看前 3 名）
        msg_content = f"【B站热榜 Top 3】\n更新时间: {update_time}\n\n"
        
        print(f"✅ 获取成功！更新时间: {update_time}")
        
        for index, item in enumerate(video_list[:10]):
            title = item['title']
            author = item['owner']['name']
            link = item.get('short_link_v2', f"https://www.bilibili.com/video/{item['bvid']}")
            
            video = {
                "rank": index + 1,
                "title": title,
                "author": author,
                "play_count": item['stat']['view'],
                "link": link
            }
            my_hot_data.append(video)
            
            # 拼凑微信消息内容 (只拼前3名)
            if index < 3:
                msg_content += f"No.{index+1} {title}\nUP主: {author}\n{link}\n\n"
        
        # 保存数据
        final_output = {
            "source": "Bilibili热门",
            "updated_at": update_time,
            "news": my_hot_data
        }
        with open('data.json', 'w', encoding='utf-8') as f:
            json.dump(final_output, f, ensure_ascii=False, indent=2)
            
        return msg_content

    except Exception as e:
        print("❌ 抓取出错啦：", e)
        return None

def send_wechat_push(content):
    # 从系统变量里读取 Token (这就是“暗号”)
    token = os.environ.get('PUSHPLUS_TOKEN')
    
    if not token:
        print("⚠️ 没有找到 PUSHPLUS_TOKEN，跳过推送。")
        return
        
    print("正在发送微信推送...")
    data = {
        "token": token,
        "title": "今日 B站热榜吃瓜",
        "content": content
    }
    # 发送请求
    resp = requests.post(pushplus_url, json=data)
    print("推送结果:", resp.text)

# --- 主程序 ---
if __name__ == "__main__":
    # 1. 抓数据
    message = get_bilibili_hot()
    
    # 2. 如果抓到了数据，就发推送
    if message:
        send_wechat_push(message)