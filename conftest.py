from __future__ import annotations

import html
from datetime import datetime
from pathlib import Path
from typing import Dict, List

import pytest


REPORT_DIR = Path("playwright_reports")
REPORT_DIR.mkdir(exist_ok=True)
SCREENSHOT_DIR = Path("playwright_screenshots")
_RESULTS: List[Dict[str, str]] = []
_RECORDED_NODEIDS = set()
_START_TIME = datetime.now()


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()

    if report.nodeid in _RECORDED_NODEIDS:
        return

    should_record = False
    if report.when == "call":
        should_record = True
    elif report.when == "setup" and report.outcome == "skipped":
        should_record = True

    if not should_record:
        return

    screenshot_path = SCREENSHOT_DIR / f"{item.name}.png"
    _RESULTS.append(
        {
            "name": item.name,
            "nodeid": item.nodeid,
            "outcome": "ignored" if report.outcome == "skipped" else report.outcome,
            "duration": f"{report.duration:.2f}s",
            "message": str(call.excinfo.value) if call.excinfo else "",
            "screenshot": str(screenshot_path) if screenshot_path.exists() else "",
        }
    )
    _RECORDED_NODEIDS.add(report.nodeid)


@pytest.hookimpl(trylast=True)
def pytest_terminal_summary(terminalreporter, exitstatus, config):
    end_time = datetime.now()
    passed = len([r for r in _RESULTS if r["outcome"] == "passed"])
    failed = len([r for r in _RESULTS if r["outcome"] == "failed"])
    ignored = len([r for r in _RESULTS if r["outcome"] == "ignored"])
    total = len(_RESULTS)

    summary = {
        "passed": passed,
        "failed": failed,
        "ignored": ignored,
        "total": total,
        "start": _START_TIME.strftime("%Y-%m-%d %H:%M:%S"),
        "end": end_time.strftime("%Y-%m-%d %H:%M:%S"),
        "duration": f"{(end_time - _START_TIME).total_seconds():.2f}s",
    }

    timestamp = end_time.strftime("%Y%m%d_%H%M%S")
    md_path = REPORT_DIR / f"playwright_test_report_{timestamp}.md"
    html_path = REPORT_DIR / f"playwright_test_report_{timestamp}.html"

    max_count = max(total, 1)

    def bar(count: int) -> str:
        filled = max(1, round((count / max_count) * 20)) if count else 0
        return "#" * filled + "-" * (20 - filled)

    md_lines = [
        "# Playwright 测试报告",
        "",
        f"- 开始时间：{summary['start']}",
        f"- 结束时间：{summary['end']}",
        f"- 总耗时：{summary['duration']}",
        f"- 总用例数：{summary['total']}",
        f"- 通过数：{summary['passed']}",
        f"- 失败数：{summary['failed']}",
        f"- 忽略数：{summary['ignored']}",
        "",
        "## 分类统计",
        "",
        f"- 通过: `{bar(passed)}` {passed}",
        f"- 失败: `{bar(failed)}` {failed}",
        f"- 忽略: `{bar(ignored)}` {ignored}",
        "",
        "## 用例明细",
        "",
        "| 用例 | 结果 | 耗时 | 失败信息 | 截图 |",
        "| --- | --- | --- | --- | --- |",
    ]

    for result in _RESULTS:
        screenshot = result["screenshot"] if result["screenshot"] else "-"
        message = result["message"].replace("\n", " ").replace("|", "\\|") if result["message"] else "-"
        md_lines.append(
            f"| {result['name']} | {result['outcome']} | {result['duration']} | {message} | {screenshot} |"
        )

    md_path.write_text("\n".join(md_lines), encoding="utf-8")

    rows = []
    for result in _RESULTS:
        normalized_screenshot = result["screenshot"].replace("\\", "/") if result["screenshot"] else ""
        screenshot_html = (
            f'<a href="../{html.escape(normalized_screenshot)}">查看截图</a>' if normalized_screenshot else "-"
        )
        message_html = html.escape(result["message"]) if result["message"] else "-"
        rows.append(
            "<tr>"
            f"<td>{html.escape(result['name'])}</td>"
            f"<td class=\"{html.escape(result['outcome'])}\">{html.escape(result['outcome'])}</td>"
            f"<td>{html.escape(result['duration'])}</td>"
            f"<td><pre>{message_html}</pre></td>"
            f"<td>{screenshot_html}</td>"
            "</tr>"
        )

    chart_total = max(total, 1)
    passed_height = round((passed / chart_total) * 220) if passed else 0
    failed_height = round((failed / chart_total) * 220) if failed else 0
    ignored_height = round((ignored / chart_total) * 220) if ignored else 0
    pie_style = (
        f"background: conic-gradient("
        f"#1a7f37 0deg {passed / chart_total * 360:.2f}deg, "
        f"#cf222e {passed / chart_total * 360:.2f}deg {(passed + failed) / chart_total * 360:.2f}deg, "
        f"#9a6700 {(passed + failed) / chart_total * 360:.2f}deg 360deg);"
    )

    html_content = f"""
<!doctype html>
<html lang=\"zh-CN\">
<head>
  <meta charset=\"utf-8\" />
  <title>Playwright 测试报告</title>
  <style>
    body {{ font-family: 'Microsoft YaHei', sans-serif; margin: 24px; color: #222; }}
    h1 {{ margin-bottom: 12px; }}
    h2 {{ margin-top: 28px; }}
    .meta {{ margin-bottom: 20px; line-height: 1.8; }}
    .cards {{ display: flex; gap: 12px; margin: 16px 0 24px; flex-wrap: wrap; }}
    .card {{ min-width: 150px; padding: 14px 16px; border-radius: 10px; background: #f7f7f8; border: 1px solid #e5e7eb; }}
    .card .label {{ font-size: 13px; color: #666; margin-bottom: 6px; }}
    .card .value {{ font-size: 28px; font-weight: 700; }}
    .chart-actions {{ display: flex; gap: 8px; margin: 8px 0 16px; }}
    .chart-btn {{ border: 1px solid #d0d7de; background: #fff; padding: 8px 14px; border-radius: 999px; cursor: pointer; }}
    .chart-btn.active {{ background: #222; color: #fff; border-color: #222; }}
    .chart-panel {{ display: none; }}
    .chart-panel.active {{ display: block; }}
    .chart-wrap {{ display: flex; align-items: flex-end; gap: 24px; height: 300px; padding: 24px; border: 1px solid #e5e7eb; border-radius: 12px; background: linear-gradient(180deg, #fafafa 0%, #ffffff 100%); }}
    .bar-col {{ display: flex; flex-direction: column; align-items: center; justify-content: flex-end; width: 120px; height: 100%; }}
    .bar-value {{ font-size: 14px; margin-bottom: 8px; font-weight: 700; }}
    .bar {{ width: 72px; border-radius: 10px 10px 0 0; min-height: 8px; }}
    .bar.passed {{ background: #1a7f37; }}
    .bar.failed {{ background: #cf222e; }}
    .bar.ignored {{ background: #9a6700; }}
    .bar-label {{ margin-top: 10px; font-size: 14px; }}
    .pie-wrap {{ display: flex; align-items: center; gap: 32px; min-height: 300px; padding: 24px; border: 1px solid #e5e7eb; border-radius: 12px; background: linear-gradient(180deg, #fafafa 0%, #ffffff 100%); }}
    .pie {{ width: 220px; height: 220px; border-radius: 50%; flex-shrink: 0; }}
    .legend {{ display: flex; flex-direction: column; gap: 12px; }}
    .legend-item {{ display: flex; align-items: center; gap: 10px; font-size: 14px; }}
    .swatch {{ width: 14px; height: 14px; border-radius: 3px; }}
    .swatch.passed {{ background: #1a7f37; }}
    .swatch.failed {{ background: #cf222e; }}
    .swatch.ignored {{ background: #9a6700; }}
    table {{ width: 100%; border-collapse: collapse; margin-top: 18px; }}
    th, td {{ border: 1px solid #ddd; padding: 8px; vertical-align: top; }}
    th {{ background: #f5f5f5; text-align: left; }}
    td.passed {{ color: #1a7f37; font-weight: 700; }}
    td.failed {{ color: #cf222e; font-weight: 700; }}
    td.ignored {{ color: #9a6700; font-weight: 700; }}
    pre {{ white-space: pre-wrap; margin: 0; font-family: Consolas, monospace; }}
  </style>
</head>
<body>
  <h1>Playwright 测试报告</h1>
  <div class=\"meta\">
    <div>开始时间：{html.escape(summary['start'])}</div>
    <div>结束时间：{html.escape(summary['end'])}</div>
    <div>总耗时：{html.escape(summary['duration'])}</div>
    <div>总用例数：{html.escape(str(summary['total']))}</div>
    <div>通过数：{html.escape(str(summary['passed']))}</div>
    <div>失败数：{html.escape(str(summary['failed']))}</div>
    <div>忽略数：{html.escape(str(summary['ignored']))}</div>
  </div>

  <h2>分类统计</h2>
  <div class=\"cards\">
    <div class=\"card\"><div class=\"label\">总用例数</div><div class=\"value\">{total}</div></div>
    <div class=\"card\"><div class=\"label\">通过数</div><div class=\"value\">{passed}</div></div>
    <div class=\"card\"><div class=\"label\">失败数</div><div class=\"value\">{failed}</div></div>
    <div class=\"card\"><div class=\"label\">忽略数</div><div class=\"value\">{ignored}</div></div>
  </div>
  <div class=\"chart-actions\">
    <button class=\"chart-btn active\" type=\"button\" onclick=\"switchChart('bar')\">柱状图</button>
    <button class=\"chart-btn\" type=\"button\" onclick=\"switchChart('pie')\">圆饼图</button>
  </div>
  <div id=\"chart-bar\" class=\"chart-panel active\">
    <div class=\"chart-wrap\">
      <div class=\"bar-col\">
        <div class=\"bar-value\">{passed}</div>
        <div class=\"bar passed\" style=\"height: {passed_height}px;\"></div>
        <div class=\"bar-label\">通过</div>
      </div>
      <div class=\"bar-col\">
        <div class=\"bar-value\">{failed}</div>
        <div class=\"bar failed\" style=\"height: {failed_height}px;\"></div>
        <div class=\"bar-label\">失败</div>
      </div>
      <div class=\"bar-col\">
        <div class=\"bar-value\">{ignored}</div>
        <div class=\"bar ignored\" style=\"height: {ignored_height}px;\"></div>
        <div class=\"bar-label\">忽略</div>
      </div>
    </div>
  </div>
  <div id=\"chart-pie\" class=\"chart-panel\">
    <div class=\"pie-wrap\">
      <div class=\"pie\" style=\"{pie_style}\"></div>
      <div class=\"legend\">
        <div class=\"legend-item\"><span class=\"swatch passed\"></span>通过：{passed}</div>
        <div class=\"legend-item\"><span class=\"swatch failed\"></span>失败：{failed}</div>
        <div class=\"legend-item\"><span class=\"swatch ignored\"></span>忽略：{ignored}</div>
      </div>
    </div>
  </div>

  <h2>用例明细</h2>
  <table>
    <thead>
      <tr>
        <th>用例</th>
        <th>结果</th>
        <th>耗时</th>
        <th>失败信息</th>
        <th>截图</th>
      </tr>
    </thead>
    <tbody>
      {''.join(rows)}
    </tbody>
  </table>
  <script>
    function switchChart(type) {{
      var bar = document.getElementById('chart-bar');
      var pie = document.getElementById('chart-pie');
      var buttons = document.querySelectorAll('.chart-btn');
      bar.classList.toggle('active', type === 'bar');
      pie.classList.toggle('active', type === 'pie');
      buttons.forEach(function(btn) {{
        btn.classList.toggle('active', btn.textContent.indexOf(type === 'bar' ? '柱状' : '圆饼') >= 0);
      }});
    }}
  </script>
</body>
</html>
"""
    html_path.write_text(html_content, encoding="utf-8")

    terminalreporter.write_sep("=", f"已生成测试报告: {md_path}")
    terminalreporter.write_sep("=", f"已生成测试报告: {html_path}")
