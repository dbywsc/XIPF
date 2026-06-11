"""Generate initial organizations.json from unmatched orgs with auto-detected province/city."""

import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent

# City name → province mapping (auto-detected from org name prefix)
CITY_PROVINCE = {
    "北京": ("北京", "北京"),
    "上海": ("上海", "上海"),
    "天津": ("天津", "天津"),
    "重庆": ("重庆", "重庆"),
    "广州": ("广东", "广州"),
    "深圳": ("广东", "深圳"),
    "武汉": ("湖北", "武汉"),
    "杭州": ("浙江", "杭州"),
    "南京": ("江苏", "南京"),
    "西安": ("陕西", "西安"),
    "成都": ("四川", "成都"),
    "长沙": ("湖南", "长沙"),
    "济南": ("山东", "济南"),
    "青岛": ("山东", "青岛"),
    "郑州": ("河南", "郑州"),
    "合肥": ("安徽", "合肥"),
    "福州": ("福建", "福州"),
    "厦门": ("福建", "厦门"),
    "南昌": ("江西", "南昌"),
    "沈阳": ("辽宁", "沈阳"),
    "大连": ("辽宁", "大连"),
    "哈尔滨": ("黑龙江", "哈尔滨"),
    "长春": ("吉林", "长春"),
    "太原": ("山西", "太原"),
    "昆明": ("云南", "昆明"),
    "南宁": ("广西", "南宁"),
    "贵阳": ("贵州", "贵阳"),
    "兰州": ("甘肃", "兰州"),
    "乌鲁木齐": ("新疆", "乌鲁木齐"),
    "石家庄": ("河北", "石家庄"),
    "苏州": ("江苏", "苏州"),
    "徐州": ("江苏", "徐州"),
    "无锡": ("江苏", "无锡"),
    "扬州": ("江苏", "扬州"),
    "镇江": ("江苏", "镇江"),
    "常州": ("江苏", "常州"),
    "宁波": ("浙江", "宁波"),
    "温州": ("浙江", "温州"),
    "绍兴": ("浙江", "绍兴"),
    "湘潭": ("湖南", "湘潭"),
    "衡阳": ("湖南", "衡阳"),
    "株洲": ("湖南", "株洲"),
    "洛阳": ("河南", "洛阳"),
    "新乡": ("河南", "新乡"),
    "开封": ("河南", "开封"),
    "芜湖": ("安徽", "芜湖"),
    "蚌埠": ("安徽", "蚌埠"),
    "桂林": ("广西", "桂林"),
    "秦皇岛": ("河北", "秦皇岛"),
    "保定": ("河北", "保定"),
    "烟台": ("山东", "烟台"),
    "威海": ("山东", "威海"),
    "绵阳": ("四川", "绵阳"),
    "咸阳": ("陕西", "咸阳"),
    "泉州": ("福建", "泉州"),
    "珠海": ("广东", "珠海"),
    "东莞": ("广东", "东莞"),
    "佛山": ("广东", "佛山"),
    "汕头": ("广东", "汕头"),
    "临沂": ("山东", "临沂"),
    "乐山": ("四川", "乐山"),
    "九江": ("江西", "九江"),
    "井冈山": ("江西", "井冈山"),
    "南阳": ("河南", "南阳"),
    "台州": ("浙江", "台州"),
    "宁德": ("福建", "宁德"),
    "宜春": ("江西", "宜春"),
    "怀化": ("湖南", "怀化"),
    "景德镇": ("江西", "景德镇"),
    "曲阜": ("山东", "曲阜"),
    "信阳": ("河南", "信阳"),
    "商丘": ("河南", "商丘"),
    "吉首": ("湖南", "吉首"),
    "黄冈": ("湖北", "黄冈"),
    "赣州": ("江西", "赣州"),
    "萍乡": ("江西", "萍乡"),
    "盐城": ("江苏", "盐城"),
    "阜阳": ("安徽", "阜阳"),
    "湖州": ("浙江", "湖州"),
    "潍坊": ("山东", "潍坊"),
    "渭南": ("陕西", "渭南"),
    "韶关": ("广东", "韶关"),
    "集美": ("福建", "厦门"),
    "韩山": ("广东", "潮州"),
    "武夷山": ("福建", "武夷山"),
    "阿坝": ("四川", "阿坝"),
    "闽南": ("福建", "漳州"),
    "赣东": ("江西", "抚州"),
    "五邑": ("广东", "江门"),
    "鲁东": ("山东", "烟台"),
    "齐鲁": ("山东", "济南"),
    "武昌": ("湖北", "武汉"),
    "江汉": ("湖北", "武汉"),
}

# Province codes for general matching
PROVINCE_MAP = {
    "北京": "北京", "上海": "上海", "天津": "天津", "重庆": "重庆",
    "河北": "河北", "山西": "山西", "辽宁": "辽宁", "吉林": "吉林",
    "黑龙江": "黑龙江", "江苏": "江苏", "浙江": "浙江", "安徽": "安徽",
    "福建": "福建", "江西": "江西", "山东": "山东", "河南": "河南",
    "湖北": "湖北", "湖南": "湖南", "广东": "广东", "广西": "广西",
    "海南": "海南", "四川": "四川", "贵州": "贵州", "云南": "云南",
    "陕西": "陕西", "甘肃": "甘肃", "青海": "青海", "内蒙古": "内蒙古",
    "西藏": "西藏", "宁夏": "宁夏", "新疆": "新疆",
}


# Hardcoded mapping for universities whose names don't start with a city
KNOWN_UNIVERSITIES = {
    # Directional universities
    "东北大学": ("辽宁", "沈阳"),
    "东北大学秦皇岛分校": ("河北", "秦皇岛"),
    "东南大学": ("江苏", "南京"),
    "中南大学": ("湖南", "长沙"),
    "中南林业科技大学": ("湖南", "长沙"),
    "中南民族大学": ("湖北", "武汉"),
    "中南财经政法大学": ("湖北", "武汉"),
    "中北大学": ("山西", "太原"),
    "西北大学": ("陕西", "西安"),
    "西北工业大学": ("陕西", "西安"),
    "西北农林科技大学": ("陕西", "杨凌"),
    "西南大学": ("重庆", "重庆"),
    "西南交通大学": ("四川", "成都"),
    "西南财经大学": ("四川", "成都"),
    "西南科技大学": ("四川", "绵阳"),
    "西南石油大学": ("四川", "成都"),
    "西南政法大学": ("重庆", "重庆"),
    "华东师范大学": ("上海", "上海"),
    "华东理工大学": ("上海", "上海"),
    "华东政法大学": ("上海", "上海"),
    "华中科技大学": ("湖北", "武汉"),
    "华中师范大学": ("湖北", "武汉"),
    "华中农业大学": ("湖北", "武汉"),
    "华南理工大学": ("广东", "广州"),
    "华南师范大学": ("广东", "广州"),
    "华南农业大学": ("广东", "广州"),
    "华北电力大学": ("北京", "北京"),
    "华北理工大学": ("河北", "唐山"),
    # China-prefix universities
    "中国科学技术大学": ("安徽", "合肥"),
    "中国科学院大学": ("北京", "北京"),
    "中国社会科学院大学": ("北京", "北京"),
    "中国传媒大学": ("北京", "北京"),
    "中国地质大学（北京）": ("北京", "北京"),
    "中国地质大学(北京)": ("北京", "北京"),
    "中国地质大学": ("湖北", "武汉"),
    "中国海洋大学": ("山东", "青岛"),
    "中国石油大学": ("山东", "青岛"),
    "中国石油大学（北京）": ("北京", "北京"),
    "中国石油大学(华东)": ("山东", "青岛"),
    "中国矿业大学": ("江苏", "徐州"),
    "中国矿业大学（北京）": ("北京", "北京"),
    "中国矿业大学徐海学院": ("江苏", "徐州"),
    "中国农业大学": ("北京", "北京"),
    "中国人民大学": ("北京", "北京"),
    "中国政法大学": ("北京", "北京"),
    "中国民航大学": ("天津", "天津"),
    "中国药科大学": ("江苏", "南京"),
    "中国医科大学": ("辽宁", "沈阳"),
    "中国计量大学": ("浙江", "杭州"),
    "中国美术学院": ("浙江", "杭州"),
    "中国劳动关系学院": ("北京", "北京"),
    # Other common patterns
    "中央民族大学": ("北京", "北京"),
    "中央财经大学": ("北京", "北京"),
    "中央戏剧学院": ("北京", "北京"),
    "中央音乐学院": ("北京", "北京"),
    "中央美术学院": ("北京", "北京"),
    "国防科技大学": ("湖南", "长沙"),
    "国防大学": ("北京", "北京"),
    "河海大学": ("江苏", "南京"),
    "江南大学": ("江苏", "无锡"),
    "长安大学": ("陕西", "西安"),
    "暨南大学": ("广东", "广州"),
    "华侨大学": ("福建", "厦门"),
    "燕山大学": ("河北", "秦皇岛"),
    "东华大学": ("上海", "上海"),
    "东华理工大学": ("江西", "南昌"),
    "西华大学": ("四川", "成都"),
    "南华大学": ("湖南", "衡阳"),
    "北华大学": ("吉林", "吉林"),
    "三峡大学": ("湖北", "宜昌"),
    "石河子大学": ("新疆", "石河子"),
    "塔里木大学": ("新疆", "阿拉尔"),
    # Common company/organization entries in contests
    "华为技术有限公司": ("广东", "深圳"),
    "上海楷登电子科技有限公司": ("上海", "上海"),
    "桃李未来": ("广东", "深圳"),
    "腾讯": ("广东", "深圳"),
    "百度": ("北京", "北京"),
    "阿里巴巴": ("浙江", "杭州"),
    "字节跳动": ("北京", "北京"),
    "三三信奥": ("北京", "北京"),
    "洛谷科技": ("上海", "上海"),
    "睿钯科技": ("广东", "深圳"),
    # Specific universities
    "同济大学": ("上海", "上海"),
    "电子科技大学": ("四川", "成都"),
    "电子科技大学中山学院": ("广东", "中山"),
    "江汉大学": ("湖北", "武汉"),
    "长江大学": ("湖北", "荆州"),
    "武警工程大学": ("陕西", "西安"),
    "空军工程大学": ("陕西", "西安"),
    "信息工程大学": ("河南", "郑州"),
    "浙大城市学院": ("浙江", "杭州"),
    "浙大宁波理工学院": ("浙江", "宁波"),
    "北师香港浸会大学": ("广东", "珠海"),
    "延安大学西安创新学院": ("陕西", "西安"),
    "国科英才科创学院": ("北京", "北京"),
    "清华大学附属中学": ("北京", "北京"),
    "焦作市第一中学": ("河南", "焦作"),
    "吉利学院": ("四川", "成都"),
    "阳光学院": ("福建", "福州"),
    "中原工学院": ("河南", "郑州"),
    "西华师范大学": ("四川", "南充"),
}

# Directional prefixes that map to provinces
DIRECTIONAL_PROVINCE = {
    "东北": "辽宁",
    "东南": "江苏",
    "中南": "湖南",
    "西北": "陕西",
    "西南": "重庆",
    "华东": "上海",
    "华中": "湖北",
    "华南": "广东",
    "华北": "北京",
}

def detect_location(name: str) -> tuple[str, str]:
    """Try to detect province and city from an organization name."""
    name = name.strip()

    # 1. Check hardcoded known universities
    if name in KNOWN_UNIVERSITIES:
        return KNOWN_UNIVERSITIES[name]

    # 2. Try exact city match
    for city, (province, city_name) in CITY_PROVINCE.items():
        if name.startswith(city):
            return province, city_name

    # 3. Try directional prefix
    for direction, province in DIRECTIONAL_PROVINCE.items():
        if name.startswith(direction):
            return province, ""

    # 4. Try province-level match
    for prov_short, prov_full in PROVINCE_MAP.items():
        if name.startswith(prov_short):
            return prov_full, ""

    # 5. "中国" prefix universities (default to Beijing)
    if name.startswith("中国"):
        return "北京", ""

    return "", ""


def generate_slug(name: str) -> str:
    """Generate a URL-friendly slug from a Chinese org name."""
    import re
    # Very basic: just strip non-alpha and lowercase
    slug = re.sub(r'[^a-zA-Z0-9一-鿿]', '-', name)
    if not any(c.isascii() and c.isalpha() for c in slug):
        # Pure Chinese name, use a hash-based approach
        import hashlib
        h = hashlib.md5(name.encode()).hexdigest()[:8]
        return f"org-{h}"
    return slug.lower()[:50]


def main():
    # Load unmatched orgs from build output
    unmatched_file = ROOT / "dist" / "unmatched_orgs.json"
    if not unmatched_file.exists():
        print("Run build.py first to generate unmatched_orgs.json")
        sys.exit(1)

    with open(unmatched_file, encoding="utf-8") as f:
        unmatched = json.load(f)

    orgs = []
    for name in sorted(unmatched):
        province, city = detect_location(name)
        slug = generate_slug(name)
        orgs.append({
            "id": slug,
            "canonical": name,
            "aliases": [],
            "province": province,
            "city": city,
        })

    # Merge with existing if present
    existing_file = ROOT / "organizations.json"
    if existing_file.exists():
        with open(existing_file, encoding="utf-8") as f:
            existing = json.load(f)
        existing_ids = {o["id"] for o in existing.get("organizations", [])}
        existing_names = {o["canonical"] for o in existing.get("organizations", [])}
        for name in sorted(unmatched):
            if name not in existing_names:
                province, city = detect_location(name)
                slug = generate_slug(name)
                # Avoid ID collision
                while slug in existing_ids:
                    slug += "-1"
                existing["organizations"].append({
                    "id": slug,
                    "canonical": name,
                    "aliases": [],
                    "province": province,
                    "city": city,
                })
                existing_ids.add(slug)
        output = existing
    else:
        output = {"organizations": orgs}

    with open(existing_file, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    filled = sum(1 for o in output["organizations"] if o["province"])
    print(f"Generated organizations.json with {len(output['organizations'])} entries")
    print(f"  {filled} with auto-detected province/city")
    print(f"  {len(output['organizations']) - filled} need manual fill")


if __name__ == "__main__":
    main()
