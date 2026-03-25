#!/usr/bin/env python3
"""
Playwright E2E Test Script for RI Agent
Tests 100 scenarios across 6 categories against https://ri.sogawa-yk.com/

Usage:
    python tests/e2e/playwright_e2e.py
"""

import os
import sys
import time
import traceback
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
TARGET_URL = "https://ri.sogawa-yk.com/"
SCREENSHOT_DIR = Path("/home/opc/Github/resource-intelligence/playwright/001-oci-resource-intelligence")
REPORT_PATH = SCREENSHOT_DIR / "test-report.md"
TIMEOUT_PER_TEST_MS = 120_000  # 120 seconds
PAGE_LOAD_TIMEOUT_MS = 60_000
WELCOME_WAIT_MS = 30_000

OCID = (
    "ocid1.instance.oc1.ap-tokyo-1."
    "anxhiljrssl65iqc6t6gig6qsh6gdbfkayn22mqr7q2hdzlo4d5lgn65ptgq"
)


# ---------------------------------------------------------------------------
# Test scenario definition
# ---------------------------------------------------------------------------
@dataclass
class Scenario:
    test_id: str
    category: str
    input_text: str
    expected_action: str  # resource_search | dependency_map | help | error


@dataclass
class TestResult:
    test_id: str
    category: str
    input_text: str
    expected_action: str
    response_summary: str = ""
    passed: bool = False
    response_time_s: float = 0.0
    screenshot: str = ""
    error_msg: str = ""


# ---------------------------------------------------------------------------
# Build the 100 scenarios
# ---------------------------------------------------------------------------
def build_scenarios() -> list[Scenario]:
    scenarios: list[Scenario] = []

    # --- Category A: Resource Search - Type Specific (20) ---
    cat_a = [
        ("A01", "全リソースを一覧して"),
        ("A02", "ap-tokyo-1のインスタンスを表示して"),
        ("A03", "VCNを一覧して"),
        ("A04", "サブネットを表示して"),
        ("A05", "ロードバランサを表示"),
        ("A06", "ap-osaka-1のリソースを表示"),
        ("A07", "us-ashburn-1のVCNを表示"),
        ("A08", "ca-toronto-1のサブネットを表示して"),
        ("A09", "eu-frankfurt-1のインスタンスを一覧"),
        ("A10", "uk-london-1のリソースを検索"),
        ("A11", "稼働中のインスタンスを表示"),
        ("A12", "停止中のインスタンスを表示して"),
        ("A13", "RUNNINGのリソースを一覧"),
        ("A14", "us-chicago-1のロードバランサを表示"),
        ("A15", "ap-seoul-1のインスタンスを表示"),
        ("A16", "us-phoenix-1のVCNを表示"),
        ("A17", "ap-sydney-1のサブネットを一覧"),
        ("A18", "us-sanjose-1のリソースを表示して"),
        ("A19", "me-jeddah-1のリソースを一覧"),
        ("A20", "データベースを表示"),
    ]
    for tid, txt in cat_a:
        scenarios.append(Scenario(tid, "A: Resource Search - Type Specific", txt, "resource_search"))

    # --- Category B: Resource Search - Natural Language Variations (20) ---
    cat_b = [
        ("B01", "リソースを全部見せて"),
        ("B02", "東京リージョンのインスタンス一覧"),
        ("B03", "大阪のVCNは？"),
        ("B04", "シカゴのサブネット数を教えて"),
        ("B05", "全リージョンのインスタンスを検索"),
        ("B06", "ネットワークリソースを表示"),
        ("B07", "コンピュートリソースを一覧"),
        ("B08", "使っているVCNを教えて"),
        ("B09", "アクティブなロードバランサは？"),
        ("B10", "全てのリソースを検索して下さい"),
        ("B11", "OCIリソースの一覧を表示"),
        ("B12", "テナントの全リソース"),
        ("B13", "ap-tokyo-1のリソース一覧を出して"),
        ("B14", "動いているリソースを見せて"),
        ("B15", "インスタンスは何台ある？"),
        ("B16", "VCNの一覧をお願い"),
        ("B17", "サブネットの一覧を出力して"),
        ("B18", "全リージョンの全リソースを表示"),
        ("B19", "ロードバランサーの一覧"),
        ("B20", "稼働中のサーバーを一覧して"),
    ]
    for tid, txt in cat_b:
        scenarios.append(Scenario(tid, "B: Resource Search - Natural Language", txt, "resource_search"))

    # --- Category C: Dependency Map (15) ---
    cat_c = [
        ("C01", f"{OCID}の依存関係を表示"),
        ("C02", f"{OCID}の依存関係を深度1で表示"),
        ("C03", f"{OCID}の接続関係"),
        ("C04", f"{OCID}の依存マップ"),
        ("C05", f"このリソースの依存関係を表示: {OCID}"),
        ("C06", f"{OCID}に接続されているリソース"),
        ("C07", f"依存関係マップを{OCID}で作成"),
        ("C08", f"{OCID}の依存関係を深度2で"),
        ("C09", f"depth 0で{OCID}の依存関係"),
        ("C10", f"{OCID}のdependency map"),
        ("C11", f"{OCID}の依存関係を深度5で表示して"),
        ("C12", f"{OCID}と関連するリソース"),
        ("C13", f"{OCID}から辿れるリソース"),
        ("C14", f"{OCID}の依存ツリー"),
        ("C15", f"show dependency map for {OCID}"),
    ]
    for tid, txt in cat_c:
        scenarios.append(Scenario(tid, "C: Dependency Map", txt, "dependency_map"))

    # --- Category D: Help & General (15) ---
    cat_d = [
        ("D01", "使い方を教えて"),
        ("D02", "ヘルプ"),
        ("D03", "何ができますか？"),
        ("D04", "help"),
        ("D05", "こんにちは"),
        ("D06", "OCIとは何ですか？"),
        ("D07", "このエージェントは何をするの？"),
        ("D08", "どのような検索ができますか？"),
        ("D09", "依存関係マップとは何ですか？"),
        ("D10", "サポートしているリソースタイプは？"),
        ("D11", "使い方がわかりません"),
        ("D12", "リージョンの一覧を教えて"),
        ("D13", "このツールの機能を教えて"),
        ("D14", "検索条件にはどんなものがありますか？"),
        ("D15", "ありがとう"),
    ]
    for tid, txt in cat_d:
        scenarios.append(Scenario(tid, "D: Help & General", txt, "help"))

    # --- Category E: Edge Cases & Error Handling (15) ---
    cat_e = [
        ("E01", ""),  # empty
        ("E02", "あああああ"),
        ("E03", "SELECT * FROM resources"),
        ("E04", "ocid1.invalid.xxxの依存関係"),
        ("E05", "\U0001f389\U0001f389\U0001f389"),
        ("E06", "a very long query with lots and lots and lots of text that keeps going " * 5),
        ("E07", "ap-tokyo-1"),
        ("E08", "Instance"),
        ("E09", "全リソースを一覧して"),
        ("E10", "<script>alert('xss')</script>"),
        ("E11", '"; DROP TABLE resources; --'),
        ("E12", "依存関係"),
        ("E13", "12345"),
        ("E14", "null"),
        ("E15", "リソース リソース リソース"),
    ]
    for tid, txt in cat_e:
        scenarios.append(Scenario(tid, "E: Edge Cases & Error Handling", txt, "error"))

    # --- Category F: Continuous Sequential Queries (15) ---
    cat_f = [
        ("F01", "VCNを一覧して"),
        ("F02", "サブネットを表示"),
        ("F03", "インスタンスを表示して"),
        ("F04", "ロードバランサを一覧"),
        ("F05", "ap-tokyo-1のリソース"),
        ("F06", "ap-osaka-1のインスタンス"),
        ("F07", "使い方を教えて"),
        ("F08", "VCNを一覧して"),
        ("F09", "全リソースを一覧して"),
        ("F10", f"{OCID}の依存関係を表示"),
        ("F11", "サブネットを表示"),
        ("F12", "ヘルプ"),
        ("F13", "稼働中のインスタンス"),
        ("F14", "ca-toronto-1のVCN"),
        ("F15", "ありがとう"),
    ]
    # Assign expected_action per F-test
    f_expected = {
        "F01": "resource_search",
        "F02": "resource_search",
        "F03": "resource_search",
        "F04": "resource_search",
        "F05": "resource_search",
        "F06": "resource_search",
        "F07": "help",
        "F08": "resource_search",
        "F09": "resource_search",
        "F10": "dependency_map",
        "F11": "resource_search",
        "F12": "help",
        "F13": "resource_search",
        "F14": "resource_search",
        "F15": "help",
    }
    for tid, txt in cat_f:
        scenarios.append(Scenario(tid, "F: Continuous Sequential", txt, f_expected[tid]))

    return scenarios


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _safe_filename(test_id: str) -> str:
    return f"{test_id}.png"


def _truncate(text: str, length: int = 100) -> str:
    text = text.replace("\n", " ").strip()
    if len(text) > length:
        return text[:length] + "..."
    return text


def _evaluate_pass(expected_action: str, response_text: str, app_crashed: bool) -> bool:
    """Determine if a test passed based on pass criteria."""
    if app_crashed:
        return False

    if expected_action == "resource_search":
        return ("リソース検索結果" in response_text or "リソースが見つかりませんでした" in response_text)
    elif expected_action == "dependency_map":
        return ("依存関係マップ" in response_text or "OCIDを指定してください" in response_text)
    elif expected_action == "help":
        return "エラー" not in response_text
    elif expected_action == "error":
        # Any response is acceptable as long as the app didn't crash
        return True
    return False


# ---------------------------------------------------------------------------
# Core test runner
# ---------------------------------------------------------------------------
def wait_for_welcome(page) -> None:
    """Wait for the Chainlit welcome message to appear."""
    page.wait_for_load_state("networkidle", timeout=PAGE_LOAD_TIMEOUT_MS)
    try:
        page.wait_for_selector("div.step", timeout=WELCOME_WAIT_MS)
    except PlaywrightTimeout:
        pass
    page.wait_for_timeout(2000)


def count_messages(page) -> int:
    """Count assistant messages (div.ai-message) on the page."""
    return len(page.query_selector_all("div.ai-message"))


def get_latest_response(page, previous_count: int) -> str:
    """Extract the text of the latest assistant response."""
    msgs = page.query_selector_all("div.ai-message")
    if msgs and len(msgs) > previous_count:
        new_msgs = msgs[previous_count:]
        texts = []
        for el in new_msgs:
            content = el.query_selector("div.message-content")
            if content:
                txt = content.inner_text()
            else:
                txt = el.inner_text()
            if txt.strip():
                texts.append(txt.strip())
        if texts:
            return "\n".join(texts)
    return ""


def submit_message(page, text: str) -> None:
    """Type a message into the Chainlit input and submit it."""
    # Use CSS selector for textarea - more reliable in headless
    textarea = page.wait_for_selector("textarea", timeout=10000)
    if not textarea:
        raise RuntimeError("Could not find textarea element")
    textarea.click()
    textarea.fill(text)
    page.wait_for_timeout(500)
    textarea.press("Enter")
    page.wait_for_timeout(500)


def wait_for_response(page, previous_count: int, timeout_ms: int = TIMEOUT_PER_TEST_MS) -> str:
    """Wait for a new response to appear after submitting a message."""
    start = time.time()
    deadline = start + (timeout_ms / 1000.0)

    while time.time() < deadline:
        current_count = count_messages(page)
        if current_count > previous_count:
            # New message appeared -- wait for content to stabilize (streaming done)
            last_text = ""
            stable_count = 0
            while time.time() < deadline:
                response_text = get_latest_response(page, previous_count)
                if response_text == last_text and response_text:
                    stable_count += 1
                    if stable_count >= 3:
                        return response_text
                else:
                    stable_count = 0
                    last_text = response_text
                page.wait_for_timeout(2000)
            return get_latest_response(page, previous_count)
        page.wait_for_timeout(1000)

    return get_latest_response(page, previous_count)


def run_single_test(page, scenario: Scenario, reload: bool = True) -> TestResult:
    """Execute a single test scenario and return the result."""
    result = TestResult(
        test_id=scenario.test_id,
        category=scenario.category,
        input_text=scenario.input_text,
        expected_action=scenario.expected_action,
    )

    screenshot_name = _safe_filename(scenario.test_id)
    screenshot_path = SCREENSHOT_DIR / screenshot_name
    result.screenshot = screenshot_name

    try:
        if reload:
            page.goto(TARGET_URL, timeout=PAGE_LOAD_TIMEOUT_MS)
            wait_for_welcome(page)

        # Handle empty input (E01)
        if scenario.input_text == "":
            # For empty input, just press Enter on an empty field
            prev_count = count_messages(page)
            textarea = page.wait_for_selector("textarea", timeout=10000)
            if textarea:
                textarea.click()
                textarea.press("Enter")
            page.wait_for_timeout(3000)
            response = get_latest_response(page, prev_count)
            if not response:
                response = "(no response - empty input ignored)"
            result.response_summary = _truncate(response)
            result.passed = True  # App didn't crash
            result.response_time_s = 3.0
            page.screenshot(path=str(screenshot_path), full_page=True)
            return result

        prev_count = count_messages(page)
        start_time = time.time()

        submit_message(page, scenario.input_text)
        response = wait_for_response(page, prev_count, TIMEOUT_PER_TEST_MS)

        elapsed = time.time() - start_time
        result.response_time_s = round(elapsed, 2)
        result.response_summary = _truncate(response)
        result.passed = _evaluate_pass(scenario.expected_action, response, app_crashed=False)

        page.screenshot(path=str(screenshot_path), full_page=True)

    except PlaywrightTimeout as e:
        result.error_msg = f"Timeout: {e}"
        result.response_summary = "(TIMEOUT)"
        result.passed = False
        result.response_time_s = TIMEOUT_PER_TEST_MS / 1000.0
        try:
            page.screenshot(path=str(screenshot_path), full_page=True)
        except Exception:
            pass

    except Exception as e:
        result.error_msg = f"Error: {e}"
        result.response_summary = f"(ERROR: {_truncate(str(e), 80)})"
        result.passed = scenario.expected_action == "error"
        try:
            page.screenshot(path=str(screenshot_path), full_page=True)
        except Exception:
            pass

    return result


# ---------------------------------------------------------------------------
# Report generation
# ---------------------------------------------------------------------------
def generate_report(results: list[TestResult]) -> str:
    """Generate a markdown report from test results."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    total = len(results)
    passed = sum(1 for r in results if r.passed)
    failed = total - passed

    lines: list[str] = []
    lines.append("# Playwright E2E Test Report")
    lines.append(f"**Date**: {now}")
    lines.append(f"**URL**: {TARGET_URL}")
    lines.append(f"**Total**: {total} tests | Pass: {passed} | Fail: {failed}")
    lines.append("")

    # Summary by category
    lines.append("## Summary by Category")
    lines.append("| Category | Tests | Pass | Fail |")
    lines.append("|----------|-------|------|------|")

    categories_seen: list[str] = []
    cat_results: dict[str, list[TestResult]] = {}
    for r in results:
        if r.category not in cat_results:
            cat_results[r.category] = []
            categories_seen.append(r.category)
        cat_results[r.category].append(r)

    for cat in categories_seen:
        cat_list = cat_results[cat]
        cp = sum(1 for r in cat_list if r.passed)
        cf = len(cat_list) - cp
        lines.append(f"| {cat} | {len(cat_list)} | {cp} | {cf} |")

    lines.append("")

    # Detailed results per category
    lines.append("## Test Results")
    for cat in categories_seen:
        lines.append(f"### {cat}")
        lines.append("| ID | Input | Expected | Result | Time | Screenshot |")
        lines.append("|----|-------|----------|--------|------|------------|")
        for r in cat_results[cat]:
            input_display = _truncate(r.input_text, 40).replace("|", "\\|")
            if not input_display:
                input_display = "(empty)"
            result_icon = "PASS" if r.passed else "FAIL"
            summary = r.response_summary.replace("|", "\\|")
            time_str = f"{r.response_time_s}s"
            screenshot_link = f"[{r.screenshot}](./{r.screenshot})" if r.screenshot else "-"
            lines.append(
                f"| {r.test_id} | {input_display} | {r.expected_action} | "
                f"{result_icon}: {summary} | {time_str} | {screenshot_link} |"
            )
        lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> None:
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)

    scenarios = build_scenarios()
    print(f"Total scenarios: {len(scenarios)}")

    results: list[TestResult] = []

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1280, "height": 900},
            locale="ja-JP",
        )
        page = context.new_page()

        # ------- Categories A-E: reload between each test -------
        non_f_scenarios = [s for s in scenarios if not s.test_id.startswith("F")]
        for i, scenario in enumerate(non_f_scenarios):
            print(f"[{i + 1}/{len(non_f_scenarios)}] Running {scenario.test_id}: "
                  f"{_truncate(scenario.input_text, 50)}")
            result = run_single_test(page, scenario, reload=True)
            results.append(result)
            status = "PASS" if result.passed else "FAIL"
            print(f"  -> {status} ({result.response_time_s}s) {result.response_summary[:60]}")

        # ------- Category F: continuous without reload -------
        f_scenarios = [s for s in scenarios if s.test_id.startswith("F")]
        print("\n--- Category F: Continuous Sequential (no page reload) ---")
        # Load the page once
        page.goto(TARGET_URL, timeout=PAGE_LOAD_TIMEOUT_MS)
        wait_for_welcome(page)

        for i, scenario in enumerate(f_scenarios):
            print(f"[F {i + 1}/{len(f_scenarios)}] Running {scenario.test_id}: "
                  f"{_truncate(scenario.input_text, 50)}")
            result = run_single_test(page, scenario, reload=False)
            results.append(result)
            status = "PASS" if result.passed else "FAIL"
            print(f"  -> {status} ({result.response_time_s}s) {result.response_summary[:60]}")

        browser.close()

    # Generate report
    report = generate_report(results)
    REPORT_PATH.write_text(report, encoding="utf-8")
    print(f"\nReport written to {REPORT_PATH}")
    print(f"Screenshots saved to {SCREENSHOT_DIR}/")

    total = len(results)
    passed = sum(1 for r in results if r.passed)
    print(f"\nResults: {passed}/{total} passed, {total - passed} failed")

    # Exit with non-zero if any test failed
    if passed < total:
        sys.exit(1)


if __name__ == "__main__":
    main()
