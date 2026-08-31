# 命理精研（destiny_cn）

一款中国古典命理研习桌面应用，古朴典雅，本地运行，无需联网。

## 功能

- **八字详盘** —— 输入姓名、性别、公历/农历生日与时辰，排出四柱八字、
  十神、藏干、纳音、大运流年等完整命盘。
- **紫微斗数** —— 安命身宫、定五行局、排紫微主星与十四辅星、
  四化、大限流年，十二宫布局一览（闰月默认「按下月」派）。
- **黄大仙灵签** —— 完整一百签签文与典故，按传统规则抽签。
- **周易六十四卦** —— 支持时间起卦（梅花易数）、铜钱摇卦与指定查卦，
  展示本卦、变卦、动爻爻辞与吉凶解读。
- **AI 提示词** —— 一键把命盘结果整理成提示词，复制给任意 AI 深入分析。

## 运行

```bash
python -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python main.py
```

需要图形环境（Linux / Windows / macOS 均可，基于 Qt6）。

## 打包

```bash
.venv/bin/pyinstaller --clean --onefile --windowed --name destiny_cn \
    --add-data "data/gua64.json:data" \
    --add-data "data/lingqian100.json:data" \
    main.py
# 产物在 dist/destiny_cn（单文件可执行）
```

## 目录结构

```
main.py            应用入口
algorithm/         排盘算法（八字 bazi、紫微 ziwei、灵签 lingqian、周易 zhouyi）
data/              卦辞 / 签文等数据
ui/                界面（古风主题与五个页面）
utils/             配置、剪贴板、AI 提示词、真太阳时
tools/             数据生成脚本
```

## 声明

本项目内容源于中国传统命理文化，仅供文化研习与娱乐参考。

## License

MIT
