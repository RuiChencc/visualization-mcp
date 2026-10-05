#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""v0.2.0 单元测试：11 种图表类型"""
import sys
import json
import os

sys.path.insert(0, "D:/OpenCode/.opencode-skills/visualization-mcp")
import visualization_server as vs

print("=== Python AST 语法检查 ===")
import ast
with open("D:/OpenCode/.opencode-skills/visualization-mcp/visualization_server.py", encoding="utf-8") as f:
    ast.parse(f.read())
print("AST OK")

print("")
print("=== 11 种图表单元测试 ===")
cases = [
    ("line", {"series":[{"name":"A","data":[1,2,3]},{"name":"B","data":[4,3,2]}]}),
    ("bar", {"A":10,"B":20,"C":15}),
    ("pie", {"A":30,"B":50,"C":20}),
    ("donut", {"A":30,"B":50,"C":20}),
    ("scatter", {"x":[1,2,3,4],"y":[2,4,6,8]}),
    ("histogram", [1,2,3,4,5,6,7,8,9,10,5,3,7,2,8]),
    ("area", {"series":[{"name":"A","data":[1,3,2,4]}]}),
    ("waterfall", {"labels":["Start","Add","Sub","Total"],"values":[10,5,-3,12]}),
    ("combo", {"bars":["A","B","C"],"lines":[{"name":"L1","data":[2,4,3]}]}),
    ("kline", {"candles":[
        {"o":10,"h":12,"l":9,"c":11,"v":100,"t":"2024-01-01"},
        {"o":11,"h":13,"l":10,"c":12,"v":150,"t":"2024-01-02"},
        {"o":12,"h":14,"l":11,"c":11,"v":80,"t":"2024-01-03"},
    ], "ma_periods":[2]}),
    ("decision_tree", {
        "root":"n1",
        "nodes":[
            {"id":"n1","text":"Start","children":["n2","n3"]},
            {"id":"n2","text":"Buy","children":[]},
            {"id":"n3","text":"Wait","children":[]},
        ],
        "highlights":["n2"]
    }),
]

passed = 0
failed = 0
for ct, data in cases:
    try:
        r = vs.visualize(json.dumps(data), ct, "测试" + ct)
        parsed = json.loads(r)
        img_kb = len(parsed["image_base64"]) // 1000
        style = parsed["meta"]["style"]
        font = parsed["meta"]["font"]
        print(f"OK  {ct:15s}  image={img_kb}KB  style={style:6s}  font={font}")
        passed += 1
    except Exception as e:
        print(f"FAIL  {ct:15s}  {type(e).__name__}: {e}")
        failed += 1

print("")
print(f"通过 {passed} / {len(cases)}，失败 {failed}")

print("")
print("=== dark 样式 + 中文标题测试 ===")
try:
    r = vs.visualize(json.dumps({"series":[{"name":"股价","data":[1,2,3,4,5]}]}), "line", "K线走势", style="dark")
    parsed = json.loads(r)
    print(f"OK  dark+中文  image={len(parsed['image_base64'])//1000}KB")
    passed += 1
except Exception as e:
    print(f"FAIL  dark+中文  {e}")
    failed += 1

print("")
print("=== 错误处理测试 ===")
try:
    vs.visualize(json.dumps({}), "unsupported_type")
    print("FAIL  未抛异常")
    failed += 1
except ValueError as e:
    print(f"OK  ValueError: {e}")
    passed += 1

print("")
print(f"最终：通过 {passed} / {len(cases)+2}")
