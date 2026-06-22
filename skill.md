# Fortune Teller Skill

A comprehensive Chinese metaphysics divination system implementing:
- Bazi (Four Pillars of Destiny / 八字四柱)
- Plum Blossom I Ching (梅花易数)
- Zhou Yi 64 Hexagrams (周易六十四卦)
- Six Yao Najia (六爻纳甲 / 铜钱占卜)
- Grand Luck (大运) analysis

Based on classic texts including 《渊海子平》《滴天髓》《穷通宝鉴》《增删卜易》《卜筮正宗》《黄金策》《周易》《梅花易数》《中国古代算命术》《命运的求索》.

## Usage

### 八字命理 (Bazi / Four Pillars)

Full birth chart with five elements, Ten Gods, and grand luck analysis.

```bash
python divination.py <year> <month> <day> [hour] [minute] [gender]
```
Example: `python divination.py 1990 5 15 8 0 男`

### 六爻纳甲占卜 (Six Yao Coin Divination)

Ask a question and receive an automatic coin-toss divination.

```bash
python divination.py --liuyao [your question]
```
Example: `python divination.py --liuyao 丢了东西能找到吗`

For interactive coin tossing (you provide the toss results):
```bash
python divination.py --liuyao --interactive
```

Shortcuts: `-l` or `--六爻` or `六爻`

### 梅花易数占卜 (Plum Blossom I Ching)

Divination based on date and time.

```bash
python divination.py --meihua <year> <month> <day> [hour] [minute]
```
Example: `python divination.py --meihua 2026 6 22`

Shortcuts: `-m` or `--梅花`

## Files

- `divination.py` — Bazi engine (~1040 lines) + Plum Blossom I Ching + CLI
- `liuyao.py` — Six Yao Najia engine (~700 lines) with 64-hexagram database
- `skill.md` — This file
- `README.md` — Documentation
