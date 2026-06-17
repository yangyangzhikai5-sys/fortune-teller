# Fortune Teller Skill

A comprehensive Chinese metaphysics divination system implementing:
- Bazi (Four Pillars of Destiny / 八字四柱)
- Plum Blossom I Ching (梅花易数)
- Zhou Yi 64 Hexagrams (周易六十四卦)

Based on classic texts including 《渊海子平》《滴天髓》《穷通宝鉴》《周易》《梅花易数》《中国古代算命术》《命运的求索》.

## Usage

When the user asks to:
- Calculate their 八字 (Bazi / Four Pillars)
- Get a fortune reading / 算命
- Use 梅花易数 for divination
- Analyze their 命理 (destiny analysis)

Execute the following command:

```bash
cd "C:\Users\63229\.claude\skills\fortune-teller" && python divination.py <year> <month> <day> <hour> <minute> <gender>
```

Example:
```bash
python divination.py 1990 5 15 8 0 男
```
