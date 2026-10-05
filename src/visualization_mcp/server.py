#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
MCP Server for visualization-mcp skill v0.2.0.

v0.2.0 升级（对标 mplfinance + ECharts component model）：
- 11 种图表类型（v0.1.0 仅 5 种）：line/area/bar/pie/donut/scatter/histogram/kline/decision_tree/combo/waterfall
- CJK 字体自动检测（Windows/macOS/Linux）
- K 线专业渲染：A 股红涨绿跌 + 成交量 subplot + MA 均线覆盖
- 决策树可视化（CandleMind 集成用）
- 多系列数据支持
- 样式参数：light / dark
- 保留 v0.1.0 API 向后兼容：visualize(data_str, chart_type, title)

Author: RuiChencc
License: MIT
"""
import json
import base64
import io
import sys
import os
from collections import OrderedDict

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyBboxPatch
import matplotlib.patches as mpatches


def _setup_cjk_font():
    """自动检测系统中文字体，避免豆腐块。返回所用字体名。"""
    candidates = [
        "SimHei", "Microsoft YaHei", "SimSun",
        "PingFang SC", "Hiragino Sans GB", "STHeiti", "Source Han Sans SC",
        "WenQuanYi Micro Hei", "Noto Sans CJK SC", "Droid Sans Fallback",
        "Arial Unicode MS",
    ]
    available = {f.name for f in matplotlib.font_manager.fontManager.ttflist}
    for f in candidates:
        if f in available:
            plt.rcParams["font.sans-serif"] = [f] + plt.rcParams["font.sans-serif"]
            plt.rcParams["axes.unicode_minus"] = False
            return f
    plt.rcParams["axes.unicode_minus"] = False
    return None


STYLES = {
    "light": {
        "figure": "#ffffff", "axes": "#ffffff", "grid": "#e0e0e0", "text": "#333333",
        "up_color": "#ef5350", "down_color": "#26a69a",
        "series_colors": ["#1976d2", "#ef5350", "#43a047", "#ff9800", "#ab47bc", "#00acc1"],
    },
    "dark": {
        "figure": "#1a1a2e", "axes": "#16213e", "grid": "#333355", "text": "#e0e0e0",
        "up_color": "#ef5350", "down_color": "#26a69a",
        "series_colors": ["#42a5f5", "#ef5350", "#66bb6a", "#ffa726", "#ab47bc", "#26c6da"],
    },
}


def _apply_style(style_name="light"):
    cfg = STYLES.get(style_name, STYLES["light"])
    fig = plt.figure(figsize=(10, 6), facecolor=cfg["figure"])
    ax = fig.add_subplot(111)
    ax.set_facecolor(cfg["axes"])
    ax.grid(True, color=cfg["grid"], alpha=0.6, linestyle="--")
    ax.tick_params(colors=cfg["text"], which="both")
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("bottom", "left"):
        ax.spines[s].set_color(cfg["grid"])
    ax.xaxis.label.set_color(cfg["text"])
    ax.yaxis.label.set_color(cfg["text"])
    ax.title.set_color(cfg["text"])
    return fig, ax
def visualize(data_str, chart_type, title="Chart", style="light", **kwargs):
    """
    生成图表并返回 base64 PNG 的 JSON 字符串。

    Args:
        data_str: JSON 字符串或已解析的对象
        chart_type: line/area/bar/pie/donut/scatter/histogram/kline/decision_tree/combo/waterfall
        title: 图表标题
        style: light / dark
    Returns:
        JSON 字符串：{image_base64, format, chart_type, title, meta}
    """
    font_used = _setup_cjk_font()
    data = json.loads(data_str) if isinstance(data_str, str) else data_str

    if chart_type == "kline":
        fig, buf = _render_kline(data, title, style)
    elif chart_type == "decision_tree":
        fig, buf = _render_decision_tree(data, title, style)
    elif chart_type == "combo":
        fig, buf = _render_combo(data, title, style)
    elif chart_type == "waterfall":
        fig, buf = _render_waterfall(data, title, style)
    elif chart_type in ("line", "area", "bar", "pie", "donut", "scatter", "histogram"):
        fig, buf = _render_basic(data, chart_type, title, style)
    else:
        raise ValueError(f"Unsupported chart type: {chart_type}")

    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode("utf-8")
    plt.close(fig)
    return json.dumps({
        "image_base64": img_base64,
        "format": "png",
        "chart_type": chart_type,
        "title": title,
        "meta": {
            "style": style,
            "font": font_used,
            "width": fig.get_size_inches()[0] * 100,
            "height": fig.get_size_inches()[1] * 100,
        },
    })


def _render_basic(data, chart_type, title, style):
    fig, ax = _apply_style(style)
    cfg = STYLES[style]
    colors = cfg["series_colors"]

    if chart_type in ("line", "area"):
        if isinstance(data, dict) and "series" in data:
            for i, s in enumerate(data["series"]):
                name = s.get("name", f"Series {i+1}")
                vals = s.get("data", [])
                color = colors[i % len(colors)]
                if chart_type == "area":
                    ax.fill_between(range(len(vals)), vals, alpha=0.5, label=name, color=color)
                    ax.plot(range(len(vals)), vals, label=name, color=color, linewidth=1.2)
                else:
                    ax.plot(range(len(vals)), vals, marker="o", label=name, color=color, linewidth=1.8)
        elif isinstance(data, dict):
            for i, (k, v) in enumerate(data.items()):
                if isinstance(v, list):
                    color = colors[i % len(colors)]
                    if chart_type == "area":
                        ax.fill_between(range(len(v)), v, alpha=0.5, label=k, color=color)
                        ax.plot(range(len(v)), v, label=k, color=color, linewidth=1.2)
                    else:
                        ax.plot(range(len(v)), v, marker="o", label=k, color=color, linewidth=1.8)
        elif isinstance(data, list):
            ax.plot(data, marker="o", color=colors[0], linewidth=1.8)
        ax.set_xlabel("Index")
        ax.set_ylabel("Value")
        if isinstance(data, dict):
            ax.legend(loc="upper left", fontsize=9)

    elif chart_type == "bar":
        if isinstance(data, dict):
            labels = list(data.keys())
            values = list(data.values())
            ax.bar(labels, values, color=colors[:len(values)], edgecolor="none")
        elif isinstance(data, list):
            ax.bar(range(len(data)), data, color=colors[0], edgecolor="none")
        ax.set_xlabel("Category")
        ax.set_ylabel("Value")

    elif chart_type in ("pie", "donut"):
        if isinstance(data, dict):
            labels = list(data.keys())
            values = list(data.values())
        elif isinstance(data, list):
            labels = [f"C{i+1}" for i in range(len(data))]
            values = data
        wedges, texts, autotexts = ax.pie(
            values, labels=labels, autopct="%1.1f%%",
            startangle=90, colors=colors[:len(values)],
            textprops={"color": cfg["text"]},
        )
        for at in autotexts:
            at.set_color("#ffffff")
            at.set_fontweight("bold")
        if chart_type == "donut":
            ax.pie(
                values, radius=0.6, wedgeprops={"width": 0.4, "color": cfg["axes"]},
                center=(0, 0),
            )

    elif chart_type == "scatter":
        if isinstance(data, dict) and "x" in data and "y" in data:
            ax.scatter(data["x"], data["y"], color=colors[0], alpha=0.7, s=60)
        elif isinstance(data, list):
            x = [p[0] for p in data]
            y = [p[1] for p in data]
            ax.scatter(x, y, color=colors[0], alpha=0.7, s=60)
        ax.set_xlabel("X")
        ax.set_ylabel("Y")

    elif chart_type == "histogram":
        if isinstance(data, list):
            ax.hist(data, bins="auto", color=colors[0], edgecolor=cfg["axes"], alpha=0.8)
        ax.set_xlabel("Value")
        ax.set_ylabel("Frequency")

    ax.set_title(title or chart_type.title() + " Chart", fontsize=14, fontweight="bold", pad=15, color=cfg["text"])
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    return fig, buf

def _render_kline(data, title, style):
    """
    K 线渲染。data 格式：
    {
        "candles": [{"o":, "h":, "l":, "c":, "v":, "t":}, ...],
        "ma_periods": [5, 10, 20],
        "show_volume": true,
        "up_color": "#ef5350",
        "down_color": "#26a69a"
    }
    """
    cfg = STYLES[style]
    fig, (ax_price, ax_vol) = plt.subplots(
        2, 1, figsize=(12, 8), sharex=True,
        gridspec_kw={"height_ratios": [4, 1]},
        facecolor=cfg["figure"],
    )
    ax_price.set_facecolor(cfg["axes"])
    ax_vol.set_facecolor(cfg["axes"])

    candles = data.get("candles", [])
    if not candles:
        ax_price.set_title("无数据", fontsize=14, color=cfg["text"])
        ax_price.grid(True, color=cfg["grid"], alpha=0.4, linestyle="--")
        buf = io.BytesIO()
        fig.savefig(buf, format="png", dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
        return fig, buf

    xs = list(range(len(candles)))
    up_color = data.get("up_color", cfg["up_color"])
    down_color = data.get("down_color", cfg["down_color"])

    for i, c in enumerate(candles):
        o, h, l, c_ = c["o"], c["h"], c["l"], c["c"]
        color = up_color if c_ >= o else down_color
        ax_price.plot([i, i], [l, h], color=color, linewidth=0.8, zorder=2)
        body_low, body_high = min(o, c_), max(o, c_)
        body_height = max(body_high - body_low, 0.001)
        ax_price.add_patch(Rectangle(
            (i - 0.3, body_low), 0.6, body_height,
            facecolor=color, edgecolor=color, linewidth=0.8, zorder=3,
        ))

    ma_periods = data.get("ma_periods", [5, 10, 20])
    ma_colors = ["#ffeb3b", "#42a5f5", "#ab47bc", "#ff9800"]
    closes = [c["c"] for c in candles]
    for j, period in enumerate(ma_periods):
        if len(closes) >= period:
            ma = [
                sum(closes[max(0, i - period + 1):i + 1]) / period
                for i in range(period - 1, len(closes))
            ]
            ax_price.plot(
                range(period - 1, len(closes)), ma,
                color=ma_colors[j % len(ma_colors)], linewidth=1.2,
                label=f"MA{period}", zorder=4,
            )

    show_volume = data.get("show_volume", True)
    if show_volume and any(c.get("v", 0) for c in candles):
        for i, c in enumerate(candles):
            v = c.get("v", 0)
            color = up_color if c["c"] >= c["o"] else down_color
            ax_vol.bar(i, v, color=color, alpha=0.7, width=0.7)
        ax_vol.set_ylabel("Volume", color=cfg["text"])

    if candles and "t" in candles[0]:
        step = max(1, len(candles) // 10)
        ticks = list(range(0, len(candles), step))
        ax_vol.set_xticks(ticks)
        ax_vol.set_xticklabels(
            [candles[i]["t"] for i in ticks],
            rotation=45, ha="right", fontsize=8, color=cfg["text"],
        )
        ax_vol.tick_params(axis="x", colors=cfg["text"])
        ax_price.tick_params(axis="y", colors=cfg["text"])

    ax_price.legend(loc="upper left", fontsize=8, framealpha=0.8)
    ax_price.set_ylabel("Price", color=cfg["text"])
    ax_price.set_title(
        title or "K 线图",
        fontsize=14, fontweight="bold", pad=15, color=cfg["text"],
    )

    for ax in (ax_price, ax_vol):
        ax.grid(True, color=cfg["grid"], alpha=0.4, linestyle="--")
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    return fig, buf


def _render_decision_tree(data, title, style):
    """
    决策树可视化。data 格式：
    {
        "root": "node_id",
        "nodes": [{"id": "n1", "text": "文本", "children": ["n2", "n3"]}, ...],
        "highlights": ["n2"],
        "width": 12,
    }
    """
    cfg = STYLES[style]
    canvas_w = data.get("width", 12)
    canvas_h = data.get("height", 7)
    fig = plt.figure(figsize=(canvas_w, canvas_h), facecolor=cfg["figure"])
    ax = fig.add_subplot(111)
    ax.set_facecolor(cfg["axes"])
    ax.set_xlim(0, canvas_w)
    ax.set_ylim(0, canvas_h)
    ax.axis("off")
    ax.tick_params(colors=cfg["text"])

    nodes = data.get("nodes", [])
    highlights = set(data.get("highlights", []))
    root_id = data.get("root", nodes[0]["id"] if nodes else None)

    if not nodes:
        ax.text(canvas_w / 2, canvas_h / 2, "无决策树数据",
                ha="center", va="center", fontsize=14, color=cfg["text"])
        buf = io.BytesIO()
        fig.savefig(buf, format="png", dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
        return fig, buf

    by_id = {n["id"]: n for n in nodes}

    level = {root_id: 0}
    queue = [root_id]
    while queue:
        cur = queue.pop(0)
        node = by_id.get(cur)
        if not node:
            continue
        for child_id in node.get("children", []):
            if child_id not in level:
                level[child_id] = level[cur] + 1
                queue.append(child_id)

    max_level = max(level.values()) if level else 0
    by_level = {}
    for nid, lv in level.items():
        by_level.setdefault(lv, []).append(nid)

    node_positions = {}
    for lv, ids in by_level.items():
        y = canvas_h * (0.9 - lv * 0.75 / max(1, max_level))
        for idx, nid in enumerate(ids):
            node = by_id[nid]
            x = canvas_w * (idx + 1) / (len(ids) + 1)
            node_positions[nid] = (x, y)
            is_highlight = nid in highlights
            box_color = "#ef5350" if is_highlight else cfg["axes"]
            edge_color = "#ff9800" if is_highlight else "#666666"
            ax.add_patch(FancyBboxPatch(
                (x - 1.0, y - 0.35), 2.0, 0.7,
                boxstyle="round,pad=0.15",
                facecolor=box_color, edgecolor=edge_color,
                linewidth=2.0 if is_highlight else 1.2,
                zorder=3,
            ))
            ax.text(x, y, node.get("text", nid),
                    ha="center", va="center", fontsize=10,
                    color="#ffffff" if is_highlight else cfg["text"],
                    fontweight="bold" if is_highlight else "normal",
                    zorder=4)

    for nid, (nx, ny) in node_positions.items():
        if nid == root_id:
            continue
        parent = next((n for n in nodes if nid in n.get("children", [])), None)
        if parent and parent["id"] in node_positions:
            px, py = node_positions[parent["id"]]
            ax.annotate(
                "", xy=(nx, ny + 0.35), xytext=(px, py - 0.35),
                arrowprops={
                    "arrowstyle": "->",
                    "color": "#ff9800" if nid in highlights else "#888888",
                    "lw": 1.8 if nid in highlights else 1.0,
                    "connectionstyle": "arc3,rad=0.0",
                },
                zorder=2,
            )

    ax.set_title(title or "决策树",
                 fontsize=14, fontweight="bold", pad=15, color=cfg["text"])

    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    return fig, buf

def _render_combo(data, title, style):
    """
    组合图。data 格式：
    {
        "bars": {"A": 10, "B": 20, ...} 或 [10, 20, ...],
        "lines": [{"name": "Line1", "data": [...]}],
    }
    """
    cfg = STYLES[style]
    fig = plt.figure(figsize=(10, 6), facecolor=cfg["figure"])
    ax1 = fig.add_subplot(111)
    ax1.set_facecolor(cfg["axes"])
    ax2 = ax1.twinx()

    bars = data.get("bars", [])
    lines = data.get("lines", [])

    if isinstance(bars, dict):
        labels = list(bars.keys())
        values = list(bars.values())
        ax1.bar(labels, values, color=cfg["series_colors"][1], alpha=0.7,
                edgecolor="none", label="Bar")
        x_pos = labels
    elif isinstance(bars, list):
        ax1.bar(range(len(bars)), bars, color=cfg["series_colors"][1], alpha=0.7,
                edgecolor="none", label="Bar")
        x_pos = list(range(len(bars)))

    for i, line in enumerate(lines):
        name = line.get("name", f"Line {i+1}")
        vals = line.get("data", [])
        ax2.plot(x_pos, vals, marker="o", label=name,
                 color=cfg["series_colors"][i % len(cfg["series_colors"])], linewidth=1.8)

    ax1.set_ylabel("Bar Value", color=cfg["series_colors"][1])
    ax2.set_ylabel("Line Value", color=cfg["series_colors"][0])
    ax1.tick_params(colors=cfg["text"])
    ax1.tick_params(axis="y", colors=cfg["series_colors"][1])
    ax2.tick_params(axis="y", colors=cfg["series_colors"][0])
    ax1.set_title(title or "Combo Chart",
                  fontsize=14, fontweight="bold", pad=15, color=cfg["text"])

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left", fontsize=9)

    for ax in (ax1, ax2):
        ax.grid(True, color=cfg["grid"], alpha=0.4, linestyle="--")
        ax.spines["top"].set_visible(False)

    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    return fig, buf


def _render_waterfall(data, title, style):
    """
    瀑布图。data 格式：
    {
        "labels": ["A", "B", "C"],
        "values": [10, 5, -3, 8],
    }
    """
    cfg = STYLES[style]
    fig, ax = _apply_style(style)

    labels = data.get("labels", [str(i) for i in range(len(data.get("values", [])))])
    values = data.get("values", [])
    if not values:
        ax.set_title("无数据", fontsize=14, color=cfg["text"])
        buf = io.BytesIO()
        fig.savefig(buf, format="png", dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
        return fig, buf

    cum = 0
    bottoms = []
    heights = []
    colors = []
    for v in values:
        if v >= 0:
            bottoms.append(cum)
            heights.append(v)
            colors.append(cfg["series_colors"][2])
        else:
            bottoms.append(cum + v)
            heights.append(-v)
            colors.append(cfg["series_colors"][1])
        cum += v

    ax.bar(range(len(values)), heights, bottom=bottoms, color=colors, edgecolor="none")
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, color=cfg["text"])
    ax.set_xlabel("Category", color=cfg["text"])
    ax.set_ylabel("Value", color=cfg["text"])
    ax.set_title(title or "Waterfall Chart",
                 fontsize=14, fontweight="bold", pad=15, color=cfg["text"])

    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    return fig, buf


def main():
    print("Visualization MCP server v0.2.0 started (stdio mode)", file=sys.stderr)
    print("Supported chart types: line, area, bar, pie, donut, scatter, histogram, kline, decision_tree, combo, waterfall", file=sys.stderr)
    print(f"Supported styles: {list(STYLES.keys())}", file=sys.stderr)
    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                break
            line = line.strip()
            if not line:
                continue
            try:
                request = json.loads(line)
            except json.JSONDecodeError as e:
                print(json.dumps({"error": f"Invalid JSON: {e}"}))
                sys.stdout.flush()
                continue

            tool = request.get("tool")
            args = request.get("arguments", {})

            if tool == "visualize":
                data_str = args.get("data")
                chart_type = args.get("chart_type")
                title = args.get("title", "Chart")
                style = args.get("style", "light")
                if not data_str or not chart_type:
                    response = {"error": "Missing required arguments: data and chart_type"}
                else:
                    try:
                        result = visualize(data_str, chart_type, title, style)
                        response = {"result": result}
                    except Exception as e:
                        response = {"error": str(e)}
            else:
                response = {"error": f"Unknown tool: {tool}"}

            print(json.dumps(response))
            sys.stdout.flush()
        except Exception as e:
            print(json.dumps({"error": str(e)}))
            sys.stdout.flush()


if __name__ == "__main__":
    main()