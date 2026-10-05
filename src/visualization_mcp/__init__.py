"""
visualization-mcp: MCP skill for data visualization.

11 chart types (line/bar/pie/donut/scatter/histogram/area/waterfall/combo/kline/decision_tree),
A-share red-up-green-down K-line, decision-tree visualization, dark/light styles, CJK font auto-detect.

Usage:
    from visualization_mcp import visualize
    
    result = visualize(
        data='{"series": [{"name": "Stock A", "data": [100, 102, 101, 105]}]}',
        chart_type='line',
        title='Stock A Trend',
        style='dark'
    )
    print(result)  # JSON with base64 PNG
"""
from visualization_mcp.server import visualize, STYLES, _setup_cjk_font

__all__ = ['visualize', 'STYLES', '_setup_cjk_font']
