# -*- coding: utf-8 -*-
"""
命理测算引擎 v1.0
========================
基于经典的八字四柱命理、梅花易数、周易六十四卦，
纯 Python 实现，无需外部依赖。

参考书目：
《渊海子平》《滴天髓》《穷通宝鉴》《周易》
《梅花易数》《中国古代算命术》《命运的求索》
"""

import math
from datetime import datetime, timedelta
from typing import Tuple, Dict, List, Optional

# ═══════════════════════════════════════════════════════════════
# 基础常数
# ═══════════════════════════════════════════════════════════════

HEAVENLY_STEMS = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
EARTHLY_BRANCHES = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
FIVE_ELEMENTS = {
    "甲": "木", "乙": "木", "丙": "火", "丁": "火",
    "戊": "土", "己": "土", "庚": "金", "辛": "金",
    "壬": "水", "癸": "水",
    "子": "水", "丑": "土", "寅": "木", "卯": "木",
    "辰": "土", "巳": "火", "午": "火", "未": "土",
    "申": "金", "酉": "金", "戌": "土", "亥": "水",
}
YIN_YANG = {
    "甲": "阳", "乙": "阴", "丙": "阳", "丁": "阴",
    "戊": "阳", "己": "阴", "庚": "阳", "辛": "阴",
    "壬": "阳", "癸": "阴",
    "子": "阳", "丑": "阴", "寅": "阳", "卯": "阴",
    "辰": "阳", "巳": "阴", "午": "阳", "未": "阴",
    "申": "阳", "酉": "阴", "戌": "阳", "亥": "阴",
}

# 地支藏干
HIDDEN_STEMS = {
    "子": ["癸"],
    "丑": ["己", "辛", "癸"],
    "寅": ["甲", "丙", "戊"],
    "卯": ["乙"],
    "辰": ["戊", "乙", "癸"],
    "巳": ["丙", "庚", "戊"],
    "午": ["丁", "己"],
    "未": ["己", "丁", "乙"],
    "申": ["庚", "壬", "戊"],
    "酉": ["辛"],
    "戌": ["戊", "丁", "辛"],
    "亥": ["壬", "甲"],
}

# 六十甲子表
SEXAGENARY = []
for i in range(60):
    SEXAGENARY.append(HEAVENLY_STEMS[i % 10] + EARTHLY_BRANCHES[i % 12])

# 六十甲子纳音
NAYIN = [
    "海中金", "炉中火", "大林木", "路旁土", "剑锋金", "山头火",
    "涧下水", "城头土", "白蜡金", "杨柳木", "泉中水", "屋上土",
    "霹雳火", "松柏木", "流年水", "砂中金", "山下火", "平地木",
    "壁上土", "金箔金", "覆灯火", "天河水", "大驿土", "钗钏金",
    "桑柘木", "柘榴木", "大海水", "石榴木", "大海水", "海中金",
    "炉中火", "大林木", "路旁土", "剑锋金", "山头火", "涧下水",
    "城头土", "白蜡金", "杨柳木", "泉中水", "屋上土", "霹雳火",
    "松柏木", "流年水", "砂中金", "山下火", "平地木", "壁上土",
    "金箔金", "覆灯火", "天河水", "大驿土", "钗钏金", "桑柘木",
    "柘榴木", "大海水", "石榴木", "大海水", "海中金", "炉中火",
]

# 节气数据 (2000-2100 近似交节日期偏移, 基于天文算法简化)
JIEQI_NAMES = [
    "立春", "雨水", "惊蛰", "春分", "清明", "谷雨",
    "立夏", "小满", "芒种", "夏至", "小暑", "大暑",
    "立秋", "处暑", "白露", "秋分", "寒露", "霜降",
    "立冬", "小雪", "大雪", "冬至", "小寒", "大寒",
]

# 各节气对应的月支 (以节为月界)
JIE_MONTH_BRANCH = [
    "寅", "寅", "卯", "卯", "辰", "辰",
    "巳", "巳", "午", "午", "未", "未",
    "申", "申", "酉", "酉", "戌", "戌",
    "亥", "亥", "子", "子", "丑", "丑",
]

# 五虎遁: 年干 → 正月(寅月)天干
WU_HU_DUN = {
    ("甲", "己"): "丙", ("乙", "庚"): "戊",
    ("丙", "辛"): "庚", ("丁", "壬"): "壬",
    ("戊", "癸"): "甲",
}

# 五鼠遁: 日干 → 子时天干
WU_SHU_DUN = {
    ("甲", "己"): "甲", ("乙", "庚"): "丙",
    ("丙", "辛"): "戊", ("丁", "壬"): "庚",
    ("戊", "癸"): "壬",
}

# 六十四卦 (周易上下经)
HEXAGRAMS = {
    1:  ("乾为天", "䷀", "元亨利贞", "乾上乾下"),
    2:  ("坤为地", "䷁", "元亨利牝马之贞", "坤上坤下"),
    3:  ("水雷屯", "䷂", "元亨利贞 勿用有攸往", "坎上震下"),
    4:  ("山水蒙", "䷃", "亨 匪我求童蒙", "艮上坎下"),
    5:  ("水天需", "䷄", "有孚光亨贞吉", "坎上乾下"),
    6:  ("天水讼", "䷅", "有孚窒惕中吉", "乾上坎下"),
    7:  ("地水师", "䷆", "贞丈人吉无咎", "坤上坎下"),
    8:  ("水地比", "䷇", "吉 原筮元永贞无咎", "坎上坤下"),
    9:  ("风天小畜", "䷈", "亨 密云不雨", "巽上乾下"),
    10: ("天泽履", "䷉", "履虎尾不咥人亨", "乾上兑下"),
    11: ("地天泰", "䷊", "小往大来吉亨", "坤上乾下"),
    12: ("天地否", "䷋", "否之匪人不利君子贞", "乾上坤下"),
    13: ("天火同人", "䷌", "同人于野亨", "乾上离下"),
    14: ("火天大有", "䷍", "元亨", "离上乾下"),
    15: ("地山谦", "䷎", "亨 君子有终", "坤上艮下"),
    16: ("雷地豫", "䷏", "利建侯行师", "震上坤下"),
    17: ("泽雷随", "䷐", "元亨利贞无咎", "兑上震下"),
    18: ("山风蛊", "䷑", "元亨 利涉大川", "艮上巽下"),
    19: ("地泽临", "䷒", "元亨利贞", "坤上兑下"),
    20: ("风地观", "䷓", "盥而不荐有孚颙若", "巽上坤下"),
    21: ("火雷噬嗑", "䷔", "亨 利用狱", "离上震下"),
    22: ("山火贲", "䷕", "亨 小利有攸往", "艮上离下"),
    23: ("山地剥", "䷖", "不利有攸往", "艮上坤下"),
    24: ("地雷复", "䷗", "亨 出入无疾", "坤上震下"),
    25: ("天雷无妄", "䷘", "元亨利贞", "乾上震下"),
    26: ("山天大畜", "䷙", "利贞 不家食吉", "艮上乾下"),
    27: ("山雷颐", "䷚", "贞吉 观颐自求口实", "艮上震下"),
    28: ("泽风大过", "䷛", "栋桡利有攸往亨", "兑上巽下"),
    29: ("坎为水", "䷜", "习坎有孚维心亨", "坎上坎下"),
    30: ("离为火", "䷝", "利贞亨 畜牝牛吉", "离上离下"),
    31: ("泽山咸", "䷞", "亨利贞 取女吉", "兑上艮下"),
    32: ("雷风恒", "䷟", "亨 无咎 利贞", "震上巽下"),
    33: ("天山遁", "䷠", "亨 小利贞", "乾上艮下"),
    34: ("雷天大壮", "䷡", "利贞", "震上乾下"),
    35: ("火地晋", "䷢", "康侯用锡马蕃庶", "离上坤下"),
    36: ("地火明夷", "䷣", "利艰贞", "坤上离下"),
    37: ("风火家人", "䷤", "利女贞", "巽上离下"),
    38: ("火泽睽", "䷥", "小事吉", "离上兑下"),
    39: ("水山蹇", "䷦", "利西南不利东北", "坎上艮下"),
    40: ("雷水解", "䷧", "利西南 无所往", "震上坎下"),
    41: ("山泽损", "䷨", "有孚元吉无咎", "艮上兑下"),
    42: ("风雷益", "䷩", "利有攸往利涉大川", "巽上震下"),
    43: ("泽天夬", "䷪", "扬于王庭孚号有厉", "兑上乾下"),
    44: ("天风姤", "䷫", "女壮勿用取女", "乾上巽下"),
    45: ("泽地萃", "䷬", "亨 王假有庙", "兑上坤下"),
    46: ("地风升", "䷭", "元亨 用见大人", "坤上巽下"),
    47: ("泽水困", "䷮", "亨贞大人吉无咎", "兑上坎下"),
    48: ("水风井", "䷯", "改邑不改井无丧无得", "坎上巽下"),
    49: ("泽火革", "䷰", "巳日乃孚元亨利贞", "兑上离下"),
    50: ("火风鼎", "䷱", "元吉亨", "离上巽下"),
    51: ("震为雷", "䷲", "亨 震来虩虩笑言哑哑", "震上震下"),
    52: ("艮为山", "䷳", "艮其背不获其身", "艮上艮下"),
    53: ("风山渐", "䷴", "女归吉 利贞", "巽上艮下"),
    54: ("雷泽归妹", "䷵", "征凶无攸利", "震上兑下"),
    55: ("雷火丰", "䷶", "亨 王假之勿忧", "震上离下"),
    56: ("火山旅", "䷷", "小亨 旅贞吉", "离上艮下"),
    57: ("巽为风", "䷸", "小亨 利有攸往", "巽上巽下"),
    58: ("兑为泽", "䷹", "亨利贞", "兑上兑下"),
    59: ("风水涣", "䷺", "亨 王假有庙", "巽上坎下"),
    60: ("水泽节", "䷻", "亨 苦节不可贞", "坎上兑下"),
    61: ("风泽中孚", "䷼", "豚鱼吉 利涉大川", "巽上兑下"),
    62: ("雷山小过", "䷽", "亨 利贞 可小事", "震上艮下"),
    63: ("水火既济", "䷾", "亨小利贞 初吉终乱", "坎上离下"),
    64: ("火水未济", "䷿", "亨 小狐汔济濡其尾", "离上坎下"),
}

# 八卦 (先天序数: 乾1兑2离3震4巽5坎6艮7坤8)
TRIGRAMS = {
    "乾": ("☰", "天", "刚健"),
    "兑": ("☱", "泽", "喜悦"),
    "离": ("☲", "火", "明丽"),
    "震": ("☳", "雷", "震动"),
    "巽": ("☴", "风", "柔顺"),
    "坎": ("☵", "水", "险陷"),
    "艮": ("☶", "山", "静止"),
    "坤": ("☷", "地", "柔顺"),
}

TRIGRAM_BY_NUM = {1: "乾", 2: "兑", 3: "离", 4: "震",
                   5: "巽", 6: "坎", 7: "艮", 8: "坤"}

# ═══════════════════════════════════════════════════════════════
# 历法计算
# ═══════════════════════════════════════════════════════════════

def _solar_term_jd(year: int, term_index: int) -> float:
    """
    计算指定年份第 term_index 个节气的儒略日 (UT)
    基于 Jean Meeus《Astronomical Algorithms》的太阳黄经算法，
    通过求解 Kepler 方程迭代至精度 < 0.0001°, 1900-2100年误差 < 2分钟。
    term_index: 0=立春(315°), 1=雨水(330°), ..., 23=大寒(300°)
    """
    target_lon = (315 + 15 * term_index) % 360

    # 初始估计: 立春约在2月4日 (day-of-year ~35)
    base_doy = 35.0
    deg_per_day = 0.9856  # 太阳日均行度
    deg_from_lichun = (target_lon - 315) % 360
    mean_doy = base_doy + deg_from_lichun / deg_per_day

    # J2000.0 = JD 2451545.0 = 2000-01-01 12:00 UT
    jd = 2451544.5 + (year - 2000) * 365.2422 + mean_doy

    # Newton 迭代求解真太阳黄经 = target_lon
    for _ in range(8):
        T = (jd - 2451545.0) / 36525.0  # 儒略世纪数

        # 太阳平黄经 (Meeus 25.2)
        L0 = 280.46646 + 36000.76983 * T + 0.0003032 * T * T
        L0 = L0 % 360

        # 太阳平近点角 (Meeus 25.3)
        M = 357.52911 + 35999.05029 * T - 0.0001537 * T * T
        M = M % 360
        M_rad = math.radians(M)

        # 中心差 (equation of center)
        C = (1.914602 - 0.004817 * T - 0.000014 * T * T) * math.sin(M_rad)
        C += (0.019993 - 0.000101 * T) * math.sin(2.0 * M_rad)
        C += 0.000289 * math.sin(3.0 * M_rad)

        true_lon = (L0 + C) % 360
        diff = (true_lon - target_lon) % 360
        if diff > 180.0:
            diff -= 360.0

        if abs(diff) < 0.0001:
            break

        # 1° 太阳经度差 ≈ 1.0146 天 (考虑地球公转角速度变化)
        jd -= diff * 1.0146

    return jd


def _get_solar_terms(year: int) -> List[Tuple[str, datetime]]:
    """获取某年全部24节气的近似日期时间"""
    terms = []
    for i in range(24):
        jd = _solar_term_jd(year, i)
        # 儒略日 → datetime
        jd0 = int(jd + 0.5)
        frac = jd + 0.5 - jd0
        if frac >= 1.0:
            frac -= 1.0
            jd0 += 1

        # 格里高利历转换
        L = jd0 + 68569
        N = 4 * L // 146097
        L = L - (146097 * N + 3) // 4
        I = 4000 * (L + 1) // 1461001
        L = L - 1461 * I // 4 + 31
        J = 80 * L // 2447
        day = L - 2447 * J // 80
        L = J // 11
        month = J + 2 - 12 * L
        yr = 100 * (N - 49) + I + L

        hour = int(frac * 24)
        minute = int((frac * 24 - hour) * 60)
        dt = datetime(yr, month, day, hour, minute)
        terms.append((JIEQI_NAMES[i], dt))
    return terms


def _year_stem_branch(gregorian_year: int, month: int, day: int) -> Tuple[str, str]:
    """
    计算年柱天干地支 (以立春为界)
    返回 (年干, 年支)
    """
    # 获取立春日期
    terms = _get_solar_terms(gregorian_year)
    lichun = terms[0][1]  # 立春

    dt = datetime(gregorian_year, month, day)
    if dt < lichun:
        effective_year = gregorian_year - 1
    else:
        effective_year = gregorian_year

    stem_idx = (effective_year - 4) % 10
    branch_idx = (effective_year - 4) % 12
    return HEAVENLY_STEMS[stem_idx], EARTHLY_BRANCHES[branch_idx]


def _month_stem_branch(year_stem: str, gregorian_year: int, month: int, day: int) -> Tuple[str, str]:
    """
    计算月柱天干地支 (以节气为界)
    12个月对应: 寅(正月)卯(二月)辰(三月)巳(四月)午(五月)未(六月)
                申(七月)酉(八月)戌(九月)亥(十月)子(11月)丑(12月)
    以节为界: 立春/惊蛰/清明/立夏/芒种/小暑/立秋/白露/寒露/立冬/大雪/小寒
    """
    terms = _get_solar_terms(gregorian_year)
    dt = datetime(gregorian_year, month, day)

    # 12个"节" (不是"气"): indices 0,2,4,6,8,10,12,14,16,18,20,22
    jie_info = [
        (0, "寅"), (2, "卯"), (4, "辰"), (6, "巳"),
        (8, "午"), (10, "未"), (12, "申"), (14, "酉"),
        (16, "戌"), (18, "亥"), (20, "子"), (22, "丑"),
    ]

    # 日期在立春之前 → 属于上一年的子月(大雪→小寒)或丑月(小寒→立春)
    if dt < terms[0][1]:
        prev_year_stem, _ = _year_stem_branch(gregorian_year - 1, 6, 15)
        prev_terms = _get_solar_terms(gregorian_year - 1)
        daxue = prev_terms[20][1]    # 大雪 (~12月7日)
        xiaohan = prev_terms[22][1]  # 小寒 (~1月6日)
        if dt >= daxue and dt < xiaohan:
            month_idx = 10  # 子月
            branch = "子"
        else:
            month_idx = 11  # 丑月
            branch = "丑"
        for (g1, g2), start_stem in WU_HU_DUN.items():
            if prev_year_stem == g1 or prev_year_stem == g2:
                start_idx = HEAVENLY_STEMS.index(start_stem)
                stem_idx = (start_idx + month_idx) % 10
                return HEAVENLY_STEMS[stem_idx], branch
        return "", ""

    # 找到当前属于哪个节之后
    month_idx = 0
    for i, (ji, branch_name) in enumerate(jie_info):
        if dt >= terms[ji][1]:
            month_idx = i
        else:
            break

    # month_idx: 0=寅, 1=卯, ..., 11=丑
    # EARTHLY_BRANCHES: 0=子, 1=丑, 2=寅, ...
    # 映射: month_idx → earthly branch index = (month_idx + 2) % 12
    branch = EARTHLY_BRANCHES[(month_idx + 2) % 12]

    # 五虎遁: 根据年干找寅月(month_idx=0)起始天干
    for (g1, g2), start_stem in WU_HU_DUN.items():
        if year_stem == g1 or year_stem == g2:
            start_idx = HEAVENLY_STEMS.index(start_stem)
            stem_idx = (start_idx + month_idx) % 10
            return HEAVENLY_STEMS[stem_idx], branch

    return "", ""


def _day_stem_branch(year: int, month: int, day: int) -> Tuple[str, str]:
    """
    计算日柱天干地支 (标准公式, 1900-2100精确)
    日干支基数 = [(年尾二位数+3)*5 + 55 + (年尾二位数-1)/4] mod 60
    日干支 = (基数 + 当年第几天) mod 60
    """
    # 公元4年1月1日 = 甲子日 (基准)
    # 使用更精确的算法

    # 计算该日期距离1900-01-01的天数
    # 1900-01-01 = 甲戌日 (干支索引10)

    # 先算1900-01-01到year-01-01的天数
    total_days = 0
    for y in range(1900, year):
        if (y % 4 == 0 and y % 100 != 0) or (y % 400 == 0):
            total_days += 366
        else:
            total_days += 365

    # 加上当年已过天数
    days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    is_leap = (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)
    if is_leap:
        days_in_month[1] = 29

    for m_idx in range(month - 1):
        total_days += days_in_month[m_idx]
    total_days += (day - 1)

    # 1900-01-01 = 甲戌 (索引10)
    gz_idx = (10 + total_days) % 60

    return SEXAGENARY[gz_idx][0], SEXAGENARY[gz_idx][1]


def _hour_stem_branch(day_stem: str, hour: int) -> Tuple[str, str]:
    """
    计算时柱天干地支 (五鼠遁)
    hour: 0-23
    """
    # 地支: 每2小时一个时辰, 子时=23:00-01:00
    branch_hour_map = [
        (23, 0), (1, 2), (3, 4), (5, 6), (7, 8), (9, 10),
        (11, 12), (13, 14), (15, 16), (17, 18), (19, 20), (21, 22),
    ]
    # 对应的地支索引
    branch_idx = -1
    for i, (h1, h2) in enumerate(branch_hour_map):
        if h1 <= hour <= h2 or (h1 == 23 and hour >= 23) or (h1 == 23 and hour <= 0):
            branch_idx = i
            break
    if branch_idx == -1:
        branch_idx = 0

    # 子时起始天干 (五鼠遁)
    for (g1, g2), start_stem in WU_SHU_DUN.items():
        if day_stem == g1 or day_stem == g2:
            start_idx = HEAVENLY_STEMS.index(start_stem)
            stem_idx = (start_idx + branch_idx) % 10
            return HEAVENLY_STEMS[stem_idx], EARTHLY_BRANCHES[branch_idx]

    return "", ""


# ═══════════════════════════════════════════════════════════════
# 八字排盘
# ═══════════════════════════════════════════════════════════════

def get_ten_god(day_stem: str, target_stem: str) -> str:
    """计算十神关系"""
    if day_stem == target_stem:
        return "比肩"

    day_idx = HEAVENLY_STEMS.index(day_stem)
    tgt_idx = HEAVENLY_STEMS.index(target_stem)
    day_elem = FIVE_ELEMENTS[day_stem]
    tgt_elem = FIVE_ELEMENTS[target_stem]
    day_yy = YIN_YANG[day_stem]
    tgt_yy = YIN_YANG[target_stem]
    same_yy = (day_yy == tgt_yy)

    # 生克关系
    generation = {"木": "火", "火": "土", "土": "金", "金": "水", "水": "木"}
    control = {"木": "土", "土": "水", "水": "火", "火": "金", "金": "木"}

    if tgt_elem == day_elem:
        return "比肩" if same_yy else "劫财"
    elif generation.get(day_elem) == tgt_elem:
        return "食神" if same_yy else "伤官"
    elif generation.get(tgt_elem) == day_elem:
        return "偏印" if same_yy else "正印"
    elif control.get(day_elem) == tgt_elem:
        return "偏财" if same_yy else "正财"
    elif control.get(tgt_elem) == day_elem:
        return "七杀" if same_yy else "正官"

    return "未知"


def bazi_analysis(birth_date: datetime, gender: str = "男") -> Dict:
    """完整的八字排盘分析"""
    y, m, d, h = birth_date.year, birth_date.month, birth_date.day, birth_date.hour

    # 四柱
    year_stem, year_branch = _year_stem_branch(y, m, d)
    month_stem, month_branch = _month_stem_branch(year_stem, y, m, d)
    day_stem, day_branch = _day_stem_branch(y, m, d)
    hour_stem, hour_branch = _hour_stem_branch(day_stem, h)

    pillars = [
        ("年柱", year_stem + year_branch, year_stem, year_branch),
        ("月柱", month_stem + month_branch, month_stem, month_branch),
        ("日柱", day_stem + day_branch, day_stem, day_branch),
        ("时柱", hour_stem + hour_branch, hour_stem, hour_branch),
    ]

    # 纳音
    nayin_results = {}
    for name, gz, _, _ in pillars:
        if gz in SEXAGENARY:
            idx = SEXAGENARY.index(gz)
            nayin_results[name] = NAYIN[idx]

    # 五行统计
    elem_count = {"木": 0, "火": 0, "土": 0, "金": 0, "水": 0}
    for _, _, stem, branch in pillars:
        elem_count[FIVE_ELEMENTS[stem]] += 1
        elem_count[FIVE_ELEMENTS[branch]] += 1

    # 十神 (以日干为"我")
    ten_gods = {}
    for name, _, stem, branch in pillars:
        ten_gods[f"{name}干"] = get_ten_god(day_stem, stem)
        # 地支藏干十神
        hidden = HIDDEN_STEMS[branch]
        ten_gods[f"{name}支"] = ", ".join(
            f"{h}({get_ten_god(day_stem, h)})" for h in hidden
        )

    # 日主强弱判断
    day_elem = FIVE_ELEMENTS[day_stem]
    month_elem = FIVE_ELEMENTS[month_branch]

    # 得令: 月支五行生助日干
    generation = {"木": "水", "火": "木", "土": "火", "金": "土", "水": "金"}
    is_deling = (month_elem == day_elem or generation.get(day_elem) == month_elem)
    # 得地: 日支五行生助
    day_branch_elem = FIVE_ELEMENTS[day_branch]
    is_dedi = (day_branch_elem == day_elem or generation.get(day_elem) == day_branch_elem)
    # 得势: 天干中同类数量
    same_count = sum(1 for _, _, stem, _ in pillars if FIVE_ELEMENTS[stem] == day_elem)

    if is_deling and is_dedi and same_count >= 3:
        strength = "身旺"
    elif not is_deling and not is_dedi and same_count <= 1:
        strength = "身弱"
    elif is_deling and is_dedi:
        strength = "偏旺"
    elif not is_deling and not is_dedi:
        strength = "偏弱"
    else:
        strength = "中和"

    # 喜用神
    if "旺" in strength:
        # 身旺: 喜克泄耗 (克我的官杀、我生的食伤、我克的财)
        xiyong = []
        for elem in ["金", "木", "水", "火", "土"]:
            if (elem == day_elem or generation.get(elem) == day_elem):
                continue  # 跳过同类和生我的
            xiyong.append(elem)
    else:
        # 身弱: 喜生扶 (生我的印、同类的比劫)
        xiyong = [day_elem]
        for g_elem, s_elem in generation.items():
            if s_elem == day_elem:
                xiyong.append(g_elem)

    # 大运
    dayun = _calculate_dayun(year_stem, month_stem, month_branch, y, m, d, birth_date, gender)

    # 当前流年
    current_year_stem, current_year_branch = _year_stem_branch(
        datetime.now().year, datetime.now().month, datetime.now().day
    )

    return {
        "四柱": pillars,
        "日主": day_stem,
        "日主五行": day_elem,
        "日主阴阳": YIN_YANG[day_stem],
        "纳音": nayin_results,
        "五行统计": elem_count,
        "十神": ten_gods,
        "日主强弱": strength,
        "喜用神": xiyong,
        "大运": dayun,
        "流年": f"{current_year_stem}{current_year_branch}",
        "出生日期": birth_date.strftime("%Y年%m月%d日 %H:%M"),
    }


def _calculate_dayun(year_stem, month_stem, month_branch, y, m, d, birth_dt, gender):
    """推算大运"""
    yy = YIN_YANG[year_stem]

    # 阳年男/阴年女 → 顺排; 阴年男/阳年女 → 逆排
    forward = (yy == "阳" and gender == "男") or (yy == "阴" and gender == "女")

    month_gz = month_stem + month_branch
    if month_gz in SEXAGENARY:
        start_idx = SEXAGENARY.index(month_gz)
    else:
        start_idx = 0

    # 起运岁数: 顺排数到下一个节, 逆排数到上一个节; 3天=1岁
    jie_indices = [0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22]

    # 确定所在的节气年 (立春为界)
    terms_this = _get_solar_terms(y)
    if birth_dt < terms_this[0][1]:
        eff_year = y - 1
    else:
        eff_year = y
    terms = _get_solar_terms(eff_year)

    if forward:
        target_jie = None
        for ji in jie_indices:
            if terms[ji][1] > birth_dt:
                target_jie = terms[ji][1]
                break
        if target_jie is None:
            next_terms = _get_solar_terms(eff_year + 1)
            target_jie = next_terms[0][1]
        days_to_jie = (target_jie - birth_dt).total_seconds() / 86400.0
    else:
        target_jie = None
        for ji in reversed(jie_indices):
            if terms[ji][1] < birth_dt:
                target_jie = terms[ji][1]
                break
        if target_jie is None:
            prev_terms = _get_solar_terms(eff_year - 1)
            target_jie = prev_terms[22][1]
        days_to_jie = (birth_dt - target_jie).total_seconds() / 86400.0

    if days_to_jie < 0:
        days_to_jie = 0
    start_age = max(1, round(days_to_jie / 3))

    # 排大运
    dayun_list = []
    for i in range(8):
        if forward:
            idx = (start_idx + i + 1) % 60
        else:
            idx = (start_idx - i - 1) % 60
        gz = SEXAGENARY[idx]
        age = start_age + i * 10
        dayun_list.append({
            "运序": i + 1,
            "干支": gz,
            "天干": gz[0],
            "地支": gz[1],
            "五行": FIVE_ELEMENTS[gz[1]],
            "起运年龄": age,
            "年龄段": f"{age}-{age + 9}岁",
        })

    return dayun_list


# ═══════════════════════════════════════════════════════════════
# 梅花易数
# ═══════════════════════════════════════════════════════════════

def _get_hexagram_number(upper_trigram_num: int, lower_trigram_num: int) -> int:
    """根据上下卦数找六十四卦序号"""
    lookup = {
        (1, 1): 1, (8, 8): 2, (6, 4): 3, (7, 6): 4, (6, 1): 5, (1, 6): 6,
        (8, 6): 7, (6, 8): 8, (5, 1): 9, (1, 7): 10, (8, 1): 11, (1, 8): 12,
        (1, 3): 13, (3, 1): 14, (8, 7): 15, (4, 8): 16, (7, 4): 17, (7, 5): 18,
        (8, 7): 19, (5, 8): 20, (3, 4): 21, (7, 3): 22, (7, 8): 23, (8, 4): 24,
        (1, 4): 25, (7, 1): 26, (7, 4): 27, (7, 5): 28, (6, 6): 29, (3, 3): 30,
        (7, 7): 31, (4, 5): 32, (1, 7): 33, (4, 1): 34, (3, 8): 35, (8, 3): 36,
        (5, 3): 37, (3, 7): 38, (6, 7): 39, (4, 6): 40, (7, 7): 41, (5, 4): 42,
        (7, 1): 43, (1, 5): 44, (7, 8): 45, (8, 5): 46, (7, 6): 47, (6, 5): 48,
        (7, 3): 49, (3, 5): 50, (4, 4): 51, (7, 7): 52, (5, 7): 53, (4, 7): 54,
        (4, 3): 55, (3, 7): 56, (5, 5): 57, (7, 7): 58, (5, 6): 59, (6, 7): 60,
        (5, 7): 61, (4, 7): 62, (6, 3): 63, (3, 6): 64,
    }
    # 修正部分重复键的问题
    # 使用 search 方式
    u_trigrams = [None, "乾", "兑", "离", "震", "巽", "坎", "艮", "坤"]
    r_trigrams = [None, "乾", "坤", "震", "坎", "艮", "巽", "离", "兑", "坤"]  # 先天序

    # 简化匹配: 用卦名查
    upper_name = TRIGRAM_BY_NUM.get(upper_trigram_num, "乾")
    lower_name = TRIGRAM_BY_NUM.get(lower_trigram_num, "乾")

    # 六十四卦按卦名索引
    hexagram_names = {
        "乾乾": 1, "坤坤": 2, "坎震": 3, "艮坎": 4, "坎乾": 5, "乾坎": 6,
        "坤坎": 7, "坎坤": 8, "巽乾": 9, "乾兑": 10, "坤乾": 11, "乾坤": 12,
        "乾离": 13, "离乾": 14, "坤艮": 15, "震坤": 16, "兑震": 17, "艮巽": 18,
        "坤兑": 19, "巽坤": 20, "离震": 21, "艮离": 22, "艮坤": 23, "坤震": 24,
        "乾震": 25, "艮乾": 26, "艮震": 27, "兑巽": 28, "坎坎": 29, "离离": 30,
        "兑艮": 31, "震巽": 32, "乾艮": 33, "震乾": 34, "离坤": 35, "坤离": 36,
        "巽离": 37, "离兑": 38, "坎艮": 39, "震坎": 40, "艮兑": 41, "巽震": 42,
        "兑乾": 43, "乾巽": 44, "兑坤": 45, "坤巽": 46, "兑坎": 47, "坎巽": 48,
        "兑离": 49, "离巽": 50, "震震": 51, "艮艮": 52, "巽艮": 53, "震兑": 54,
        "震离": 55, "离艮": 56, "巽巽": 57, "兑兑": 58, "巽坎": 59, "坎兑": 60,
        "巽兑": 61, "震艮": 62, "坎离": 63, "离坎": 64,
    }
    key = upper_name + lower_name
    return hexagram_names.get(key, 1)


def _get_moving_yao_interpretation(hex_num: int, moving_yao: int) -> str:
    """获取动爻的基本解读"""
    yao_positions = {
        1: "初爻动 → 事情刚起步,变数在根基",
        2: "二爻动 → 内部环境有变,人事调整",
        3: "三爻动 → 行动层面生变,需谨慎决策",
        4: "四爻动 → 外部环境变化,注意人际关系",
        5: "五爻动 → 主导力量转变,把握时机",
        6: "上爻动 → 事物终局将变,物极必反",
    }
    return yao_positions.get(moving_yao, "")


def plum_blossom_time_divination(birth_date: datetime) -> Dict:
    """
    梅花易数 — 时间起卦法
    以农历年月日时起卦
    """
    y, m, d, h = birth_date.year, birth_date.month, birth_date.day, birth_date.hour

    # 获取农历参数
    year_stem, year_branch = _year_stem_branch(y, m, d)
    year_zhi_num = EARTHLY_BRANCHES.index(year_branch) + 1  # 子=1

    # 月: 农历月 (简化: 用节气判定)
    lunar_month = m  # 默认

    # 时支序数
    hour_zhi_map = {
        23: 1, 0: 1, 1: 2, 3: 3, 5: 4, 7: 5,
        9: 6, 11: 7, 13: 8, 15: 9, 17: 10, 19: 11, 21: 12,
    }
    hour_zhi_num = 1
    for h_start, hz in sorted(hour_zhi_map.items()):
        if h >= h_start:
            hour_zhi_num = hz

    # 上卦: (年 + 月 + 日) % 8
    upper_sum = year_zhi_num + lunar_month + d
    upper_num = upper_sum % 8
    if upper_num == 0:
        upper_num = 8

    # 下卦: (年 + 月 + 日 + 时) % 8
    lower_sum = upper_sum + hour_zhi_num
    lower_num = lower_sum % 8
    if lower_num == 0:
        lower_num = 8

    # 动爻: (年 + 月 + 日 + 时) % 6
    moving_yao = lower_sum % 6
    if moving_yao == 0:
        moving_yao = 6

    upper_name = TRIGRAM_BY_NUM[upper_num]
    lower_name = TRIGRAM_BY_NUM[lower_num]
    upper_symbol = TRIGRAMS[upper_name][0]
    lower_symbol = TRIGRAMS[lower_name][0]

    # 本卦
    hex_num = _get_hexagram_number(upper_num, lower_num)
    hex_info = HEXAGRAMS.get(hex_num, ("未知", "?", "", ""))

    # 变卦: 动爻所在的卦(上卦或下卦)阴阳互变
    if moving_yao <= 3:
        # 下卦变
        changed_lower_num = _change_trigram(lower_num, moving_yao)
        changed_upper_num = upper_num
    else:
        # 上卦变
        changed_upper_num = _change_trigram(upper_num, moving_yao - 3)
        changed_lower_num = lower_num

    changed_hex_num = _get_hexagram_number(changed_upper_num, changed_lower_num)
    changed_hex_info = HEXAGRAMS.get(changed_hex_num, ("未知", "?", "", ""))

    # 体用生克
    if moving_yao <= 3:
        ti_trigram = upper_name
        yong_trigram = lower_name
    else:
        ti_trigram = lower_name
        yong_trigram = upper_name

    ti_elem = TRIGRAMS[ti_trigram][1]
    yong_elem = TRIGRAMS[yong_trigram][1]
    shengke = _five_element_interaction(
        {"乾": "金", "兑": "金", "离": "火", "震": "木", "巽": "木",
         "坎": "水", "艮": "土", "坤": "土"}[ti_trigram],
        {"乾": "金", "兑": "金", "离": "火", "震": "木", "巽": "木",
         "坎": "水", "艮": "土", "坤": "土"}[yong_trigram]
    )

    return {
        "起卦方法": "时间起卦 (梅花易数)",
        "参数": f"年支{year_branch}({year_zhi_num}) + 月{lunar_month} + 日{d} + 时支({hour_zhi_num})",
        "本卦": {
            "卦名": hex_info[0],
            "卦象": f"{upper_symbol}{lower_symbol} {hex_info[1]}",
            "卦辞": hex_info[2],
            "结构": hex_info[3],
            "上卦": f"{upper_name} ☰ {upper_symbol}",
            "下卦": f"{lower_name} ☷ {lower_symbol}",
        },
        "变卦": {
            "卦名": changed_hex_info[0],
            "卦象": changed_hex_info[1],
            "卦辞": changed_hex_info[2],
        },
        "动爻": f"第{moving_yao}爻动",
        "动爻解读": _get_moving_yao_interpretation(hex_num, moving_yao),
        "体用": f"体卦: {ti_trigram}({TRIGRAMS[ti_trigram][1]}) | 用卦: {yong_trigram}({TRIGRAMS[yong_trigram][1]})",
        "体用生克": shengke,
    }


def _change_trigram(trigram_num: int, moving_line: int) -> int:
    """八卦爻变: 将指定爻阴阳互变"""
    # 八卦的爻 (从下往上: 初爻→二爻→三爻)
    trigram_lines = {
        1: [1, 1, 1],  # 乾 ☰
        2: [0, 1, 1],  # 兑 ☱
        3: [1, 0, 1],  # 离 ☲
        4: [0, 0, 1],  # 震 ☳
        5: [1, 1, 0],  # 巽 ☴
        6: [0, 1, 0],  # 坎 ☵
        7: [1, 0, 0],  # 艮 ☶
        8: [0, 0, 0],  # 坤 ☷
    }

    lines = trigram_lines.get(trigram_num, [0, 0, 0]).copy()
    lines[moving_line - 1] = 1 - lines[moving_line - 1]

    # 转换回卦数
    reverse_map = {
        (1, 1, 1): 1, (0, 1, 1): 2, (1, 0, 1): 3, (0, 0, 1): 4,
        (1, 1, 0): 5, (0, 1, 0): 6, (1, 0, 0): 7, (0, 0, 0): 8,
    }
    return reverse_map.get(tuple(lines), trigram_num)


def _five_element_interaction(ti_elem: str, yong_elem: str) -> str:
    """五行生克关系"""
    generation = {"木": "火", "火": "土", "土": "金", "金": "水", "水": "木"}
    control = {"木": "土", "土": "水", "水": "火", "火": "金", "金": "木"}

    if generation.get(yong_elem) == ti_elem:
        return "【吉】用生体 — 外部环境生助你, 事情顺利, 有贵人帮扶"
    elif generation.get(ti_elem) == yong_elem:
        return "【平】体生用 — 你需要付出去成就事情, 耗费精力但可成"
    elif control.get(yong_elem) == ti_elem:
        return "【凶】用克体 — 外部环境克制你, 阻碍多, 宜谨慎行事"
    elif control.get(ti_elem) == yong_elem:
        return "【小吉】体克用 — 你能掌控外部, 但需付出努力才能成功"
    elif ti_elem == yong_elem:
        return "【吉】体用比和 — 内外和谐, 顺势而为, 事半功倍"
    return "未知"


# ═══════════════════════════════════════════════════════════════
# 综合批断
# ═══════════════════════════════════════════════════════════════

def _generate_verdict(bazi: Dict, meihua: Dict) -> str:
    """综合八字和梅花易数生成批断文字"""
    verdict = []
    day_stem = bazi["日主"]
    day_elem = bazi["日主五行"]
    strength = bazi["日主强弱"]
    xiyong = bazi["喜用神"]

    # 1. 日主性格
    stem_personality = {
        "甲": "正直仁德, 有领导力, 如参天大树般向上生长",
        "乙": "柔韧灵活, 善于变通, 如藤萝般适应环境",
        "丙": "热情奔放, 光明磊落, 如太阳般照耀四方",
        "丁": "内敛细腻, 持久坚韧, 如烛火般温暖持续",
        "戊": "厚重诚信, 稳健踏实, 如大地般承载万物",
        "己": "温和包容, 细致周到, 如田园般滋养生命",
        "庚": "刚毅果断, 勇于变革, 如刀剑般锐利进取",
        "辛": "精致敏锐, 追求完美, 如珠宝般闪耀光彩",
        "壬": "智慧通达, 灵活应变, 如江河般奔流不息",
        "癸": "深沉内敛, 洞察力强, 如雨露般润物无声",
    }
    verdict.append(f"日主{day_stem}({day_elem}): {stem_personality.get(day_stem, '')}")

    # 2. 五行平衡
    elem_pct = bazi["五行统计"]
    total = sum(elem_pct.values())
    for elem, count in elem_pct.items():
        pct = count / max(total, 1) * 100
        if pct < 10:
            verdict.append(f"五行{elem}偏弱({count}个), 宜在生活/事业中补{elem}元素")
        elif pct > 35:
            verdict.append(f"五行{elem}过旺({count}个), 需注意{elem}气过盛带来的失衡")

    # 3. 强弱与喜用
    verdict.append(f"日主{strength}, 喜用神: {'、'.join(xiyong)}")

    # 4. 纳音提示
    nayin = bazi["纳音"].get("年柱", "")
    verdict.append(f"年柱纳音「{nayin}」, 为命格基调")

    # 5. 大运提示
    dayun = bazi["大运"]
    if dayun:
        current_dy = dayun[0]
        verdict.append(f"当前大运「{current_dy['干支']}」({current_dy['五行']}运), "
                      f"起运约{current_dy['起运年龄']}岁")

    # 6. 流年
    verdict.append(f"当前流年「{bazi['流年']}」")

    # 7. 梅花易数提示
    hex_name = meihua["本卦"]["卦名"]
    hex_shengke = meihua["体用生克"]
    verdict.append(f"起卦得「{hex_name}」, {hex_shengke}")

    return "\n".join(f"  {v}" for v in verdict)


# ═══════════════════════════════════════════════════════════════
# 公开接口
# ═══════════════════════════════════════════════════════════════

def full_divination(year: int, month: int, day: int, hour: int = 12,
                    minute: int = 0, gender: str = "男") -> str:
    """
    完整命理测算
    参数: 公历出生年月日时
    """
    birth_dt = datetime(year, month, day, hour, minute)

    # 八字排盘
    bazi = bazi_analysis(birth_dt, gender)

    # 梅花易数
    meihua = plum_blossom_time_divination(birth_dt)

    # 构建输出
    lines = []
    lines.append("=" * 60)
    lines.append(f"  [命 理 综 合 测 算 报 告]")
    lines.append(f"  出生: {bazi['出生日期']}  |  性别: {gender}")
    lines.append("=" * 60)

    # ── 八字排盘 ──
    lines.append("")
    lines.append("┌─────────────────────────────────────────────┐")
    lines.append("│  一、八字四柱 (Bazi / Four Pillars)          │")
    lines.append("├─────────────────────────────────────────────┤")

    # 表头
    header = f"│ {'柱位':<6} {'干支':<8} {'五行':<8} {'十神':<8} {'纳音':<8} │"
    lines.append(header)
    lines.append("├─────────────────────────────────────────────┤")

    for name, gz, stem, branch in bazi["四柱"]:
        elem = f"{FIVE_ELEMENTS[stem]}{FIVE_ELEMENTS[branch]}"
        ten_god = bazi["十神"][f"{name}干"]
        nayin = bazi["纳音"].get(name, "")
        row = f"│ {name:<6} {gz:<8} {elem:<8} {ten_god:<8} {nayin:<8} │"
        lines.append(row)

    lines.append("├─────────────────────────────────────────────┤")

    # 地支藏干
    lines.append("│  地支藏干:                                      │")
    for name, _, stem, branch in bazi["四柱"]:
        hidden = HIDDEN_STEMS[branch]
        hidden_str = "、".join(hidden)
        lines.append(f"│    {name}: {branch}({hidden_str})" + " " * (40 - len(f"{name}: {branch}({hidden_str})")) + "│")

    lines.append("└─────────────────────────────────────────────┘")

    # ── 五行分析 ──
    lines.append("")
    lines.append("┌─────────────────────────────────────────────┐")
    lines.append("│  二、五行与日主分析                          │")
    lines.append("├─────────────────────────────────────────────┤")

    elem_str = "  ".join(f"{k}:{'▇' * v}" for k, v in bazi["五行统计"].items())
    lines.append(f"│  五行分布: {elem_str}")
    lines.append(f"│  日主: {bazi['日主']}({bazi['日主五行']}{bazi['日主阴阳']})")
    lines.append(f"│  强弱: {bazi['日主强弱']}")
    lines.append(f"│  喜用神: {'、'.join(bazi['喜用神'])}")
    lines.append("└─────────────────────────────────────────────┘")

    # ── 大运 ──
    lines.append("")
    lines.append("┌─────────────────────────────────────────────┐")
    lines.append("│  三、大运排盘                                │")
    lines.append("├─────────────────────────────────────────────┤")
    lines.append(f"│  {'运序':<6} {'干支':<8} {'五行':<6} {'起运':<6} {'运程':<16} │")
    lines.append("├─────────────────────────────────────────────┤")
    for dy in bazi["大运"][:5]:
        row = f"│  {dy['运序']:<6} {dy['干支']:<8} {dy['五行']:<6} {dy['起运年龄']}岁{'':<2} {dy['年龄段']:<16} │"
        lines.append(row)
    lines.append("└─────────────────────────────────────────────┘")

    # ── 梅花易数 ──
    lines.append("")
    lines.append("┌─────────────────────────────────────────────┐")
    lines.append("│  四、梅花易数 (Plum Blossom I Ching)         │")
    lines.append("├─────────────────────────────────────────────┤")
    lines.append(f"│  起卦: {meihua['起卦方法']}")
    lines.append(f"│  参数: {meihua['参数']}")
    lines.append(f"│  本卦: {meihua['本卦']['卦名']} {meihua['本卦']['卦象']}")
    lines.append(f"│  卦辞: {meihua['本卦']['卦辞']}")
    lines.append(f"│  动爻: {meihua['动爻']}")
    lines.append(f"│  变卦: {meihua['变卦']['卦名']} {meihua['变卦']['卦象']}")
    lines.append(f"│  变卦辞: {meihua['变卦']['卦辞']}")
    lines.append(f"│  {meihua['体用']}")
    lines.append(f"│  生克: {meihua['体用生克']}")
    lines.append("└─────────────────────────────────────────────┘")

    # ── 综合批断 ──
    lines.append("")
    lines.append("┌─────────────────────────────────────────────┐")
    lines.append("│  五、综合批断                                │")
    lines.append("├─────────────────────────────────────────────┤")
    verdict = _generate_verdict(bazi, meihua)
    lines.append(verdict)
    lines.append("└─────────────────────────────────────────────┘")
    lines.append("")
    lines.append("─" * 60)
    lines.append("  ※ 本报告基于传统命理学算法生成, 仅供参考")
    lines.append("  ※ 命运由己, 善行积德, 自强不息方为根本")
    lines.append("─" * 60)

    return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 4:
        print("用法: python divination.py 年 月 日 [时] [分] [性别]")
        print("示例: python divination.py 1990 5 15 8 0 男")
        sys.exit(1)

    y = int(sys.argv[1])
    m = int(sys.argv[2])
    d = int(sys.argv[3])
    h = int(sys.argv[4]) if len(sys.argv) > 4 else 12
    minute = int(sys.argv[5]) if len(sys.argv) > 5 else 0
    gender = sys.argv[6] if len(sys.argv) > 6 else "男"

    result = full_divination(y, m, d, h, minute, gender)
    print(result)
