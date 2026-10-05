# visualization-mcp

MCP skill for data visualization - 11 chart types, A-share K-line, decision-tree visualization, CJK font auto-detect.

## Features

- **11 chart types**: line / area / bar / pie / donut / scatter / histogram / kline / decision_tree / combo / waterfall
- **K-line**: A-share red-up-green-down + volume subplot + MA overlay + time axis
- **Decision tree**: BFS layout + highlighted paths + arrow connectors
- **CJK font auto-detect**: Windows SimHei / macOS PingFang / Linux Noto CJK
- **Dual themes**: light / dark styles
- **Backward compatible**: v0.1.0 API still works

## Installation

pip install visualization-mcp

Or from source:

git clone https://github.com/RuiChencc/visualization-mcp.git
cd visualization-mcp
pip install -e .

## Quick Start

from visualization_mcp import visualize
import json

# Line chart
result = visualize(
    data='{"series": [{"name": "Stock A", "data": [100, 102, 101, 105]}]}',
    chart_type='line',
    title='Stock A Trend',
    style='dark'
)

## Chart Types

| Type | Description |
|---|---|
| line | Line chart |
| area | Area chart |
| bar | Bar chart |
| pie | Pie chart |
| donut | Donut chart |
| scatter | Scatter plot |
| histogram | Histogram |
| kline | K-line (candlestick) |
| decision_tree | Decision tree |
| combo | Combo chart (bar + line) |
| waterfall | Waterfall chart |

## License

MIT License - see [LICENSE](LICENSE) for details.

---

**Author**: RuiChencc
**Version**: 0.2.0
**Release**: 2026-10-05
