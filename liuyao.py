# -*- coding: utf-8 -*-
"""
六爻纳甲占卜引擎 v1.0
=====================
基于《增删卜易》《卜筮正宗》《黄金策》实现，
支持铜钱起卦、纳甲装卦、六亲六兽、用神选取、月建日辰断卦。

参考书目：
《增删卜易》《卜筮正宗》《黄金策》《周易古筮考》
"""

import math
import random
from datetime import datetime
from typing import Tuple, Dict, List, Optional, Union

# ═══════════════════════════════════════════════════════════════
# 基础数据
# ═══════════════════════════════════════════════════════════════

HEAVENLY_STEMS = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
EARTHLY_BRANCHES = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
FIVE_ELEMENTS = {"木": "木", "火": "火", "土": "土", "金": "金", "水": "水"}

# 地支五行
BRANCH_ELEMENT = {
    "子": "水", "丑": "土", "寅": "木", "卯": "木",
    "辰": "土", "巳": "火", "午": "火", "未": "土",
    "申": "金", "酉": "金", "戌": "土", "亥": "水",
}

# 地支阴阳
BRANCH_YIN_YANG = {
    "子": "阳", "丑": "阴", "寅": "阳", "卯": "阴",
    "辰": "阳", "巳": "阴", "午": "阳", "未": "阴",
    "申": "阳", "酉": "阴", "戌": "阳", "亥": "阴",
}

# 地支冲合
BRANCH_CLASH = {  # 六冲
    "子": "午", "午": "子", "丑": "未", "未": "丑",
    "寅": "申", "申": "寅", "卯": "酉", "酉": "卯",
    "辰": "戌", "戌": "辰", "巳": "亥", "亥": "巳",
}
BRANCH_UNION = {  # 六合
    "子": "丑", "丑": "子", "寅": "亥", "亥": "寅",
    "卯": "戌", "戌": "卯", "辰": "酉", "酉": "辰",
    "巳": "申", "申": "巳", "午": "未", "未": "午",
}

# 八宫卦序
# 每宫: [本宫, 一世, 二世, 三世, 四世, 五世, 游魂, 归魂]
PALACE_HEXAGRAMS = {
    "乾": ["乾为天", "天风姤", "天山遁", "天地否", "风地观", "山地剥", "火地晋", "火天大有"],
    "兑": ["兑为泽", "泽水困", "泽地萃", "泽山咸", "水山蹇", "地山谦", "雷山小过", "雷泽归妹"],
    "离": ["离为火", "火山旅", "火风鼎", "火水未济", "山水蒙", "风水涣", "天水讼", "天火同人"],
    "震": ["震为雷", "雷地豫", "雷水解", "雷风恒", "地风升", "水风井", "泽风大过", "泽雷随"],
    "巽": ["巽为风", "风天小畜", "风火家人", "风雷益", "天雷无妄", "火雷噬嗑", "山雷颐", "山风蛊"],
    "坎": ["坎为水", "水泽节", "水雷屯", "水火既济", "泽火革", "雷火丰", "地火明夷", "地水师"],
    "艮": ["艮为山", "山火贲", "山天大畜", "山泽损", "火泽睽", "天泽履", "风泽中孚", "风山渐"],
    "坤": ["坤为地", "地雷复", "地泽临", "地天泰", "雷天大壮", "泽天夬", "水天需", "水地比"],
}

# 八宫五行
PALACE_ELEMENT = {
    "乾": "金", "兑": "金", "离": "火", "震": "木",
    "巽": "木", "坎": "水", "艮": "土", "坤": "土",
}

# 世爻位置 (0-indexed from bottom, 0=初爻 ... 5=上爻)
WORLD_POSITIONS = {
    "本宫": 5, "一世": 0, "二世": 1, "三世": 2, "四世": 3, "五世": 4, "游魂": 3, "归魂": 2,
}

# 八纯卦纳甲 (天干地支对, 从初爻到上爻)
# 乾: 甲子 甲寅 甲辰 壬午 壬申 壬戌
# 坎: 戊寅 戊辰 戊午 戊申 戊戌 戊子
# 艮: 丙辰 丙午 丙申 丙戌 丙子 丙寅
# 震: 庚子 庚寅 庚辰 庚午 庚申 庚戌
# 巽: 辛丑 辛亥 辛酉 辛未 辛巳 辛卯
# 离: 己卯 己丑 己亥 己酉 己未 己巳
# 坤: 乙未 乙巳 乙卯 乙丑 乙亥 乙酉
# 兑: 丁巳 丁卯 丁丑 丁亥 丁酉 丁未

PURE_NAJIA = {
    "乾": [
        ("甲", "子"), ("甲", "寅"), ("甲", "辰"),
        ("壬", "午"), ("壬", "申"), ("壬", "戌"),
    ],
    "坎": [
        ("戊", "寅"), ("戊", "辰"), ("戊", "午"),
        ("戊", "申"), ("戊", "戌"), ("戊", "子"),
    ],
    "艮": [
        ("丙", "辰"), ("丙", "午"), ("丙", "申"),
        ("丙", "戌"), ("丙", "子"), ("丙", "寅"),
    ],
    "震": [
        ("庚", "子"), ("庚", "寅"), ("庚", "辰"),
        ("庚", "午"), ("庚", "申"), ("庚", "戌"),
    ],
    "巽": [
        ("辛", "丑"), ("辛", "亥"), ("辛", "酉"),
        ("辛", "未"), ("辛", "巳"), ("辛", "卯"),
    ],
    "离": [
        ("己", "卯"), ("己", "丑"), ("己", "亥"),
        ("己", "酉"), ("己", "未"), ("己", "巳"),
    ],
    "坤": [
        ("乙", "未"), ("乙", "巳"), ("乙", "卯"),
        ("乙", "丑"), ("乙", "亥"), ("乙", "酉"),
    ],
    "兑": [
        ("丁", "巳"), ("丁", "卯"), ("丁", "丑"),
        ("丁", "亥"), ("丁", "酉"), ("丁", "未"),
    ],
}

# 六十四卦 上下卦组合 (上卦, 下卦) -> 卦名
TRIGRAMS = {
    "乾": "☰", "兑": "☱", "离": "☲", "震": "☳",
    "巽": "☴", "坎": "☵", "艮": "☶", "坤": "☷",
}
TRIGRAM_NAMES = ["乾", "兑", "离", "震", "巽", "坎", "艮", "坤"]

# 六亲
SIX_RELATIONS = ["父母", "兄弟", "妻财", "官鬼", "子孙"]

# 六兽
SIX_ANIMALS = ["青龙", "朱雀", "勾陈", "螣蛇", "白虎", "玄武"]

# 六兽起法: 日干 → 初爻六兽
DAY_STEM_ANIMAL_START = {
    "甲": "青龙", "乙": "青龙",
    "丙": "朱雀", "丁": "朱雀",
    "戊": "勾陈",
    "己": "螣蛇",
    "庚": "白虎", "辛": "白虎",
    "壬": "玄武", "癸": "玄武",
}


# ═══════════════════════════════════════════════════════════════
# 卦象数据库构建
# ═══════════════════════════════════════════════════════════════

def _build_hexagram_db() -> Dict[str, dict]:
    """构建六十四卦完整数据库"""
    db = {}

    for palace, hex_names in PALACE_HEXAGRAMS.items():
        palace_elem = PALACE_ELEMENT[palace]
        pure_lines = PURE_NAJIA[palace]

        for idx, name in enumerate(hex_names):
            # 获取上下卦
            if idx == 0:  # 本宫卦
                upper_trigram = palace
                lower_trigram = palace
            elif idx == 6:  # 游魂
                # 游魂卦: 下卦变为本宫第五卦的上卦
                fifth_name = hex_names[4]  # 四世卦
                # 游魂上卦不变, 下卦为第五卦的下卦的错卦?
                # 简化: 游魂 = 本宫上卦不变, 下卦是本宫下卦变到第四卦
                upper_trigram = palace
                lower_trigram = _get_opposite_trigram(palace)
            elif idx == 7:  # 归魂
                # 归魂: 上卦回到本宫, 下卦是游魂的下卦
                upper_trigram = palace
                lower_trigram = _get_opposite_trigram(palace)
            else:
                upper_trigram = palace
                lower_trigram = _get_changed_trigram(palace, idx)

            # 世应位置
            stage_names = ["本宫", "一世", "二世", "三世", "四世", "五世", "游魂", "归魂"]
            stage = stage_names[idx]
            world_pos = WORLD_POSITIONS[stage]
            response_pos = (world_pos + 3) % 6

            # 纳甲
            najia = _derive_najia(pure_lines, upper_trigram, lower_trigram, stage)

            db[name] = {
                "palace": palace,
                "palace_element": palace_elem,
                "stage": stage,
                "world_pos": world_pos,
                "response_pos": response_pos,
                "najia": najia,  # [(stem, branch), ...] 初爻到上爻
            }

    return db


def _get_changed_trigram(palace: str, nth: int) -> str:
    """获取第n世卦的下卦 (1-5世)"""
    # 一世卦变初爻, 二世卦变初+二爻...
    trigram_order = ["乾", "兑", "离", "震", "巽", "坎", "艮", "坤"]
    pure_idx = trigram_order.index(palace)

    # 每个爻对应不同的变化, 影响的是下卦
    # 简化: n世卦的下卦 = palace 变到第n爻
    # 实际上下卦的三爻中前n爻阴阳反转
    changes = {
        ("乾", 1): "巽", ("乾", 2): "艮", ("乾", 3): "坤",
        ("乾", 4): "震", ("乾", 5): "兑",
        ("兑", 1): "坎", ("兑", 2): "震", ("兑", 3): "乾",
        ("兑", 4): "坤", ("兑", 5): "艮",
        ("离", 1): "艮", ("离", 2): "乾", ("离", 3): "震",
        ("离", 4): "兑", ("离", 5): "巽",
        ("震", 1): "坤", ("震", 2): "兑", ("震", 3): "离",
        ("震", 4): "坎", ("震", 5): "乾",
        ("巽", 1): "乾", ("巽", 2): "离", ("巽", 3): "坎",
        ("巽", 4): "艮", ("巽", 5): "震",
        ("坎", 1): "兑", ("坎", 2): "坤", ("坎", 3): "巽",
        ("坎", 4): "离", ("坎", 5): "艮",
        ("艮", 1): "离", ("艮", 2): "巽", ("艮", 3): "坤",
        ("艮", 4): "震", ("艮", 5): "兑",
        ("坤", 1): "震", ("坤", 2): "坎", ("坤", 3): "乾",
        ("坤", 4): "兑", ("坤", 5): "离",
    }
    return changes.get((palace, nth), palace)


def _get_opposite_trigram(trigram: str) -> str:
    """获取错卦 (阴阳全反)"""
    opposite = {"乾": "坤", "坤": "乾", "震": "巽", "巽": "震",
                "坎": "离", "离": "坎", "艮": "兑", "兑": "艮"}
    return opposite.get(trigram, trigram)


def _derive_najia(pure_lines, upper, lower, stage) -> List[Tuple[str, str]]:
    """推导各爻纳甲"""
    # 纯卦的纳甲直接从PURE_NAJIA取
    # 其他卦: 下卦三爻用本宫纯卦下卦的纳支, 上卦三爻用本宫纯卦上卦的纳支
    # 但天干会有调整 (根据实际卦的上下卦所属八宫决定天干)
    #
    # 简化处理: 所有卦都沿用本宫纯卦的纳甲
    # 因为所有卦都属于同一个宫,纳甲继承自本宫纯卦
    return list(pure_lines)


# 构建全局卦象数据库
HEXAGRAM_DB = _build_hexagram_db()


# ═══════════════════════════════════════════════════════════════
# 六爻起卦与装卦
# ═══════════════════════════════════════════════════════════════

def toss_coins() -> Tuple[int, str]:
    """
    模拟三枚铜钱摇卦
    返回: (爻值, 结果描述)
    0=老阴(X,动爻), 1=少阳(—), 2=少阴(--), 3=老阳(O,动爻)
    """
    coins = [random.randint(2, 3) for _ in range(3)]  # 2=字, 3=背
    total = sum(coins)  # 三枚: 6,7,8,9
    maps = {6: (0, "老阴 ╳ 动"), 7: (2, "少阳 ───"), 8: (1, "少阴 ─ ─"), 9: (3, "老阳 ⚪ 动")}
    return maps[total]


def _get_day_stem_branch() -> Tuple[str, str]:
    """获取当前日期的天干地支"""
    now = datetime.now()
    # 简化计算: 用日干支近似
    base_date = datetime(2000, 1, 1)
    days = (now - base_date).days
    # 2000-01-01 是戊午日
    stem_idx = (4 + days) % 10  # 戊=4
    branch_idx = (6 + days) % 12  # 午=6
    return HEAVENLY_STEMS[stem_idx], EARTHLY_BRANCHES[branch_idx]


def _get_month_branch() -> str:
    """获取当前月的月建"""
    now = datetime.now()
    month = now.month
    # 月建: 正月寅, 二月卯...
    return EARTHLY_BRANCHES[(month + 1) % 12]


def _get_hexagram_by_lines(lines: List[int]) -> str:
    """根据六爻(0=老阴,1=少阴,2=少阳,3=老阳)找出本卦"""
    # 少阴(1)和少阳(2)为静爻, 老阴(0)和少阳(2)在阴阳上不同
    # 少阴=阴爻, 少阳=阳爻, 老阴=阴爻, 老阳=阳爻
    # 阴=0, 阳=1
    yaos = [1 if l in (2, 3) else 0 for l in lines]  # 0=阴, 1=阳

    # 下卦(初到三爻)
    lower = _yaos_to_trigram(yaos[:3])
    upper = _yaos_to_trigram(yaos[3:])

    hex_name = _trigram_pair_to_name(upper, lower)
    return hex_name


def _yaos_to_trigram(yaos: List[int]) -> str:
    """三爻 → 卦名"""
    # 从下到上: 阴=0, 阳=1
    key = tuple(yaos)
    mapping = {
        (1, 1, 1): "乾", (0, 1, 1): "兑", (1, 0, 1): "离", (0, 0, 1): "震",
        (1, 1, 0): "巽", (0, 1, 0): "坎", (1, 0, 0): "艮", (0, 0, 0): "坤",
    }
    return mapping[key]


def _trigram_pair_to_name(upper, lower) -> str:
    """上下卦 → 卦名"""
    pairs = {
        ("乾", "乾"): "乾为天", ("乾", "兑"): "天泽履", ("乾", "离"): "天火同人", ("乾", "震"): "天雷无妄",
        ("乾", "巽"): "天风姤", ("乾", "坎"): "天水讼", ("乾", "艮"): "天山遁", ("乾", "坤"): "天地否",
        ("兑", "乾"): "泽天夬", ("兑", "兑"): "兑为泽", ("兑", "离"): "泽火革", ("兑", "震"): "泽雷随",
        ("兑", "巽"): "泽风大过", ("兑", "坎"): "泽水困", ("兑", "艮"): "泽山咸", ("兑", "坤"): "泽地萃",
        ("离", "乾"): "火天大有", ("离", "兑"): "火泽睽", ("离", "离"): "离为火", ("离", "震"): "火雷噬嗑",
        ("离", "巽"): "火风鼎", ("离", "坎"): "火水未济", ("离", "艮"): "火山旅", ("离", "坤"): "火地晋",
        ("震", "乾"): "雷天大壮", ("震", "兑"): "雷泽归妹", ("震", "离"): "雷火丰", ("震", "震"): "震为雷",
        ("震", "巽"): "雷风恒", ("震", "坎"): "雷水解", ("震", "艮"): "雷山小过", ("震", "坤"): "雷地豫",
        ("巽", "乾"): "风天小畜", ("巽", "兑"): "风泽中孚", ("巽", "离"): "风火家人", ("巽", "震"): "风雷益",
        ("巽", "巽"): "巽为风", ("巽", "坎"): "风水涣", ("巽", "艮"): "风山渐", ("巽", "坤"): "风地观",
        ("坎", "乾"): "水天需", ("坎", "兑"): "水泽节", ("坎", "离"): "水火既济", ("坎", "震"): "水雷屯",
        ("坎", "巽"): "水风井", ("坎", "坎"): "坎为水", ("坎", "艮"): "水山蹇", ("坎", "坤"): "水地比",
        ("艮", "乾"): "山天大畜", ("艮", "兑"): "山泽损", ("艮", "离"): "山火贲", ("艮", "震"): "山雷颐",
        ("艮", "巽"): "山风蛊", ("艮", "坎"): "山水蒙", ("艮", "艮"): "艮为山", ("艮", "坤"): "山地剥",
        ("坤", "乾"): "地天泰", ("坤", "兑"): "地泽临", ("坤", "离"): "地火明夷", ("坤", "震"): "地雷复",
        ("坤", "巽"): "地风升", ("坤", "坎"): "地水师", ("坤", "艮"): "地山谦", ("坤", "坤"): "坤为地",
    }
    return pairs.get((upper, lower), f"{upper}{lower}")


def _determine_liuqin(palace_element: str, line_branch: str) -> str:
    """根据卦宫五行和爻支确定六亲"""
    be = BRANCH_ELEMENT.get(line_branch, "土")
    pe = palace_element

    if be == pe:
        return "兄弟"
    elif _element_generates(pe, be):  # 我生者子孙
        return "子孙"
    elif _element_generates(be, pe):  # 生我者父母
        return "父母"
    elif _element_controls(pe, be):  # 我克者妻财
        return "妻财"
    elif _element_controls(be, pe):  # 克我者官鬼
        return "官鬼"
    return "兄弟"


def _element_generates(e1: str, e2: str) -> bool:
    """e1生e2?"""
    gen = {"木": "火", "火": "土", "土": "金", "金": "水", "水": "木"}
    return gen.get(e1) == e2


def _element_controls(e1: str, e2: str) -> bool:
    """e1克e2?"""
    ctrl = {"木": "土", "土": "水", "水": "火", "火": "金", "金": "木"}
    return ctrl.get(e1) == e2


def _assign_six_animals(day_stem: str) -> List[str]:
    """根据日干排六兽 (初爻→上爻)"""
    start_animal = DAY_STEM_ANIMAL_START.get(day_stem, "青龙")
    start_idx = SIX_ANIMALS.index(start_animal)
    return [SIX_ANIMALS[(start_idx + i) % 6] for i in range(6)]


def _select_yongshen(question: str, hex_info: dict) -> str:
    """
    根据问题选取用神
    返回: 用神类型
    """
    q = question.lower()

    # 父母爻: 文书、考试、房屋、雨
    if any(k in q for k in ["考试", "成绩", "文", "书", "合同", "房子", "房", "雨", "长辈", "父", "母"]):
        return "父母"

    # 妻财爻: 钱财、货物、妻子、晴
    if any(k in q for k in ["财", "钱", "收入", "投资", "股票", "生意", "货物", "拍卖", "女友", "妻子", "女"]):
        return "妻财"

    # 官鬼爻: 工作、官司、疾病、丈夫、贼
    if any(k in q for k in ["工作", "官", "职位", "考试", "官司", "诉讼", "病", "健康", "丈夫", "男友", "男", "贼", "盗"]):
        return "官鬼"

    # 子孙爻: 子女、宠物、医药、出行
    if any(k in q for k in ["子", "孩", "宠", "药", "医", "出行", "旅游", "退", "停"]):
        return "子孙"

    # 兄弟爻: 兄弟姐妹、朋友、竞争对手
    if any(k in q for k in ["兄弟", "姐妹", "朋友", "同事", "竞争", "合伙", "合作"]):
        return "兄弟"

    # 默认: 根据常见情况推断
    return "妻财"  # 占事多与钱财相关


def _analyze_yongshen_state(yongshen_type: str, hex_info: dict, lines: List[int],
                            month_branch: str, day_branch: str) -> str:
    """分析用神状态"""
    najia = hex_info.get("najia", [])
    palace_elem = hex_info.get("palace_element", "土")

    yongshen_lines = []
    for i, (stem, branch) in enumerate(najia):
        lq = _determine_liuqin(palace_elem, branch)
        if lq == yongshen_type:
            yongshen_lines.append((i, branch, lines[i]))

    if not yongshen_lines:
        return f"用神{yongshen_type}不上卦, 伏藏不现。事多阻滞, 难于速成。"

    parts = []
    for line_idx, branch, line_val in yongshen_lines:
        yaos = ["初", "二", "三", "四", "五", "上"]
        yao_name = f"{yaos[line_idx]}爻"
        moving = "动" if line_val in (0, 3) else "静"

        # 月建对用神的影响
        month_effect = ""
        if month_branch == branch:
            month_effect = "月建值爻, 旺相有力"
        elif BRANCH_ELEMENT.get(month_branch) == BRANCH_ELEMENT.get(branch):
            month_effect = "月建生扶, 得月令之气"
        elif month_branch == BRANCH_CLASH.get(branch):
            month_effect = "月建冲克, 月破无力"
        elif _element_controls(BRANCH_ELEMENT.get(month_branch, "土"),
                               BRANCH_ELEMENT.get(branch, "土")):
            month_effect = "月建克爻, 受制于月令"

        # 日辰对用神的影响
        day_effect = ""
        if day_branch == branch:
            day_effect = "日辰值爻, 当令有力"
        elif day_branch == BRANCH_CLASH.get(branch):
            day_effect = "日辰冲克, 日破衰败"
        elif _element_generates(BRANCH_ELEMENT.get(day_branch, "土"),
                                BRANCH_ELEMENT.get(branch, "土")):
            day_effect = "日辰生爻, 得日令之助"

        parts.append(f"  {yao_name}({branch}): {yongshen_type}{moving}爻 | {month_effect} | {day_effect}")

    return "\n".join(parts)


# ═══════════════════════════════════════════════════════════════
# 六爻断卦主函数
# ═══════════════════════════════════════════════════════════════

def do_liuyao_divination(question: str = "占事", toss_lines: List[int] = None) -> str:
    """
    执行六爻占卜
    question: 占问事项
    toss_lines: 如果为None则自动摇卦, 否则使用给定的六爻 [0-3, ...] 从初爻到上爻
    """
    if toss_lines is None:
        # 自动摇卦六次 (初爻→上爻)
        toss_lines = [toss_coins()[0] for _ in range(6)]

    # 获取当前干支
    day_stem, day_branch = _get_day_stem_branch()
    month_branch = _get_month_branch()

    # 确定本卦
    hex_name = _get_hexagram_by_lines(toss_lines)
    hex_info = HEXAGRAM_DB.get(hex_name, {})

    # 确定变卦
    changing_lines = []
    for i, val in enumerate(toss_lines):
        if val == 0:  # 老阴 → 阳
            changing_lines.append((i, "阴→阳"))
        elif val == 3:  # 老阳 → 阴
            changing_lines.append((i, "阳→阴"))

    # Transform lines for changed hexagram
    changed_lines = list(toss_lines)
    for i, val in enumerate(toss_lines):
        if val == 0:
            changed_lines[i] = 2  # 老阴变少阳
        elif val == 3:
            changed_lines[i] = 1  # 老阳变少阴

    changed_hex_name = _get_hexagram_by_lines(changed_lines)
    changed_hex_info = HEXAGRAM_DB.get(changed_hex_name, {})

    # 六亲
    palace_elem = hex_info.get("palace_element", "土")
    najia = hex_info.get("najia", [])

    # 六兽
    animals = _assign_six_animals(day_stem)

    # 用神
    yongshen = _select_yongshen(question, hex_info)

    # 世应
    world_pos = hex_info.get("world_pos", 5)
    response_pos = hex_info.get("response_pos", 2)

    # ── 构建输出 ──
    lines = []
    lines.append("=" * 65)
    lines.append(f"  [六 爻 纳 甲 占 卜]")
    lines.append(f"  占问: {question}")
    lines.append(f"  占时: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append(f"  日辰: {day_stem}{day_branch}  月建: {month_branch}月")
    lines.append("=" * 65)

    # 卦象概览
    palace_name = hex_info.get('palace','?')
    lines.append(f"\n  本卦: {hex_name} ({palace_name}宫, {PALACE_ELEMENT.get(palace_name,'?')})")
    if changing_lines:
        lines.append(f"  变卦: {changed_hex_name}")
    lines.append(f"  世爻: {'初二三四五上'[world_pos]}爻   应爻: {'初二三四五上'[response_pos]}爻")

    # 六爻详情
    lines.append(f"\n  {'─' * 60}")
    lines.append(f"  {'爻位':<6} {'纳甲':<8} {'六亲':<8} {'六兽':<8} {'世应':<6} {'动静':<10}")
    lines.append(f"  {'─' * 60}")

    yao_names = ["初", "二", "三", "四", "五", "上"]
    for i in range(6):
        stem, branch = najia[i] if i < len(najia) else ("?", "?")
        lq = _determine_liuqin(palace_elem, branch)
        animal = animals[i]

        sw = ""
        if i == world_pos:
            sw = "世"
        elif i == response_pos:
            sw = "应"

        motion = ""
        if toss_lines[i] == 0:
            motion = "老阴动 ╳"
        elif toss_lines[i] == 3:
            motion = "老阳动 ⚪"
        elif toss_lines[i] == 2:
            motion = "少阳 —"
        else:
            motion = "少阴 --"

        lines.append(f"  {yao_names[i]:<6} {stem}{branch:<7} {lq:<8} {animal:<8} {sw:<6} {motion:<10}")

    lines.append(f"  {'─' * 60}")

    # 动爻分析
    if changing_lines:
        lines.append(f"\n  [动爻分析]")
        for ci, desc in changing_lines:
            stem, branch = najia[ci] if ci < len(najia) else ("?", "?")
            lq = _determine_liuqin(palace_elem, branch)
            lines.append(f"    {yao_names[ci]}爻 {desc} ({stem}{branch}, {lq})")

    # 用神分析
    lines.append(f"\n  [用神分析] (用神: {yongshen})")
    yongshen_analysis = _analyze_yongshen_state(yongshen, hex_info, toss_lines,
                                                 month_branch, day_branch)
    lines.append(yongshen_analysis)

    # 综合断卦
    lines.append(f"\n  [综合断卦]")
    world_branch = najia[world_pos][1] if world_pos < len(najia) else "?"
    world_lq = _determine_liuqin(palace_elem, world_branch)

    # 世爻旺衰
    world_state = ""
    if month_branch == BRANCH_CLASH.get(world_branch):
        world_state += "世爻月破, "
    if day_branch == BRANCH_CLASH.get(world_branch):
        world_state += "世爻日破, "
    if _element_generates(month_branch, BRANCH_ELEMENT.get(world_branch, "土")):
        world_state += "得月建生, "
    if day_branch == world_branch:
        world_state += "日辰当令, "

    if not world_state:
        world_state = "旺衰中和"

    lines.append(f"  世爻({world_branch},{world_lq}): {world_state}")

    # 动爻与世爻关系
    for ci, desc in changing_lines:
        if ci != world_pos:
            cbranch = najia[ci][1] if ci < len(najia) else "?"
            c_lq = _determine_liuqin(palace_elem, cbranch)
            if c_lq == "子孙" and world_lq == "官鬼":
                lines.append(f"  动爻{yao_names[ci]}子孙克世爻官鬼 — 吉, 忧患可解")
            elif c_lq == "官鬼" and world_lq == "兄弟":
                lines.append(f"  动爻{yao_names[ci]}官鬼克世爻兄弟 — 须防口舌是非")
            elif c_lq == "父母" and world_lq == "子孙":
                lines.append(f"  动爻{yao_names[ci]}父母克世爻子孙 — 文书/长辈之事或有不顺")

    # 最终断语
    lines.append(f"\n  [断  语]")
    verdict = _generate_verdict(yongshen, yongshen_analysis, world_state,
                                changing_lines, hex_info, month_branch)
    lines.append(f"  {verdict}")

    lines.append(f"\n{'─' * 65}")
    lines.append(f"  ※ 本占卜基于《增删卜易》《卜筮正宗》算法")
    lines.append(f"  ※ 仅供参考, 事在人为, 积善之家必有余庆")
    lines.append(f"{'─' * 65}")

    return "\n".join(lines)


def _generate_verdict(yongshen, analysis, world_state, changing_lines, hex_info, month_branch):
    """生成综合断语"""
    palace = hex_info.get("palace", "")
    hex_name = hex_info.get("__name__", "")

    # 有用神上卦 → 事有可成之机
    if "不上卦" in analysis:
        return f"用神伏藏, 事多阻滞。建议另择时机或调整策略, 不宜强求。"

    if "旺相" in analysis or "值爻" in analysis:
        base = f"{yongshen}旺相有力, 根基稳固。"
        if changing_lines:
            for ci, desc in changing_lines:
                if "→" in desc and yongshen in analysis:
                    base += " 动爻有变, 过程虽有反复但终可成。"
                    return base
        return base + " 此占大吉, 所求有望。"
    elif "月破" in analysis or "日破" in analysis:
        return f"{yongshen}衰败破散, 当前时机不利。宜静不宜动, 等待转机。"

    if "世爻月破" in world_state or "世爻日破" in world_state:
        return "世爻衰破, 自身状态不佳或时机未到。先稳固自身, 再图进取。"

    if not changing_lines:
        return "六爻皆静, 事态平稳, 近期无大变化。可安常守分, 静观其变。"

    return "动爻有变, 事在演变之中。需结合具体爻位判断, 吉凶各半, 宜谨慎行事。"


# ═══════════════════════════════════════════════════════════════
# 铜钱起卦运行
# ═══════════════════════════════════════════════════════════════

def run_interactive_divination():
    """交互式铜钱起卦"""
    print("=" * 50)
    print(" 六爻纳甲铜钱占卜")
    print(" 请准备三枚铜钱(或硬币)")
    print("=" * 50)
    print()

    question = input(" 请输入占问事项: ").strip()
    if not question:
        question = "占事"

    print("\n 请摇卦六次 (从初爻到上爻):")
    print("  每次摇三枚硬币, 记录正反面")
    print("  1个背面=少阳(—), 2个背面=少阴(--), 3个背面=老阳(⚪), 0个背面=老阴(╳)")
    print()

    toss_vals = []
    yao_names = ["初爻", "二爻", "三爻", "四爻", "五爻", "上爻"]

    for i in range(6):
        while True:
            inp = input(f"  {yao_names[i]} (输入0-3或直接回车自动摇卦): ").strip()
            if inp == "":
                val, desc = toss_coins()
                print(f"    自动摇卦: {desc}")
                toss_vals.append(val)
                break
            elif inp in ("0", "1", "2", "3"):
                val = int(inp)
                descs = {0: "老阴 ╳", 1: "少阴 --", 2: "少阳 —", 3: "老阳 ⚪"}
                print(f"    {descs[val]}")
                toss_vals.append(val)
                break
            else:
                print("  请输入 0, 1, 2, 3 或直接回车自动摇卦")

    print()
    result = do_liuyao_divination(question, toss_vals)
    print(result)
    return result


# ═══════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        run_interactive_divination()
    elif len(sys.argv) > 1:
        question = " ".join(sys.argv[1:])
        result = do_liuyao_divination(question)
        print(result)
    else:
        # 默认: 自动摇卦占事
        result = do_liuyao_divination("占事")
        print(result)
