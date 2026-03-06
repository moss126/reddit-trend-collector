# Reddit Trend Collector V1.4

V1.4 = Reddit 产品机会引擎 + Amazon 验证层（可直接跑的手工CSV模式）

## 新增能力
- 2~4词产品机会识别
- Showcase / Problem / Question 帖子识别
- 产品机会评分（Reddit）
- Amazon 验证层
  - **默认可用：CSV 验证模式**
  - **预留：可扩展 API 适配器**
- 输出：
  - Reddit 产品机会 Top20
  - Amazon 验证 Top20
  - 综合机会 Top20

## 你现在就能用的方式
1. 先跑 Reddit 报告
2. 打开 `data/validation_template.csv`
3. 填入 Amazon 观察值（搜索结果数、评分、价格、评论量等）
4. 再跑一次，系统会输出综合机会榜

## 运行
```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt

python src/main.py --config config.yaml --outdir data
```

## 输出
- `data/report_YYYY-MM-DD.md`
- `data/opportunities_YYYY-MM-DD.json`
- `data/validation_template.csv`

## Amazon 验证 CSV 字段说明
- phrase: 产品词（必须与系统输出短语一致）
- amazon_results: 搜索结果数量（越少通常越好）
- avg_rating: 平均评分（0~5）
- avg_price: 平均价格
- avg_reviews: 平均评论数
- fit: 你主观判断的适配度（0~10）
- notes: 备注

## 综合评分思路
- Reddit 强需求 / 高展示 / 高讨论 = 高 Reddit 分
- Amazon 结果数低、评分空间好、评论不卷、价格合适 = 高 Amazon 分
- 最终输出 total_score
