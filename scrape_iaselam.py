import urllib.request
import json
import re

def get_channel_videos(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
    with urllib.request.urlopen(req) as resp:
        html = resp.read().decode("utf-8", errors="ignore")
    
    m = re.search(r"var ytInitialData = ({.*?});</script>", html)
    if not m:
        m = re.search(r"ytInitialData\s*=\s*({.*?});", html)
    
    if not m:
        return []
    
    data = json.loads(m.group(1))
    
    vids = []
    def find_videos(obj):
        if isinstance(obj, dict):
            if "videoRenderer" in obj:
                vr = obj["videoRenderer"]
                vid_id = vr.get("videoId")
                title = vr.get("title", {}).get("runs", [{}])[0].get("text", "")
                length = vr.get("lengthText", {}).get("simpleText", "")
                view_count = vr.get("viewCountText", {}).get("simpleText", "")
                published = vr.get("publishedTimeText", {}).get("simpleText", "")
                vids.append({
                    "id": vid_id,
                    "title": title,
                    "length": length,
                    "viewCount": view_count,
                    "published": published,
                    "type": "video"
                })
            elif "reelItemRenderer" in obj:
                rr = obj["reelItemRenderer"]
                vid_id = rr.get("videoId")
                headline = rr.get("headline", {}).get("simpleText", "")
                vids.append({
                    "id": vid_id,
                    "title": headline,
                    "length": "Short",
                    "type": "short"
                })
            for k, v in obj.items():
                find_videos(v)
        elif isinstance(obj, list):
            for item in obj:
                find_videos(item)
                
    find_videos(data)
    
    seen = set()
    unique = []
    for v in vids:
        if v["id"] and v["id"] not in seen:
            seen.add(v["id"])
            unique.append(v)
    return unique

videos = get_channel_videos("https://www.youtube.com/@iaselam/videos")
shorts = get_channel_videos("https://www.youtube.com/@iaselam/shorts")

all_items = {
    "videos": videos,
    "shorts": shorts
}

with open("C:/Users/CASPER/Desktop/serkanduman-portal/data/iaselam_raw.json", "w", encoding="utf-8") as f:
    json.dump(all_items, f, ensure_ascii=False, indent=2)

print(f"Total videos found: {len(videos)}")
for v in videos:
    print(f"- [{v['id']}] {v['title']} ({v['length']})")

print(f"\nTotal shorts found: {len(shorts)}")
for s in shorts[:10]:
    print(f"- [{s['id']}] {s['title']}")
