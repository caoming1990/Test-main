import time
from pathlib import Path
from typing import Dict, List

import pytest
from playwright.sync_api import Error, Page, expect

from playwright_login_test import CONFIG, LoginPage, delete_existing_screenshot, save_failure_screenshot

NATURAL_PERSON_MODULE = "自然人"
NATURAL_PERSON_SCREENSHOT_DIR = Path("playwright_screenshots")
NATURAL_PERSON_SCREENSHOT_DIR.mkdir(exist_ok=True)

NATURAL_PERSON_ROUTES: Dict[str, str] = {
    "home": "/accounting/home",
    "practitioner_management": "/accounting/practitioner-management",
    "natural_manage": "/accounting/natural-manage",
}

HOME_METRICS: List[str] = [
    "待审核充值",
    "今日提交结算单",
    "待审核开票",
    "待审核开户",
]
HOME_TABLE_HEADERS: List[str] = [
    "平台订单号",
    "商户名",
    "所属机构",
    "提交时间",
    "结算金额 (元)",
    "订单状态",
]
PRACTITIONER_FILTERS: List[str] = [
    "首次认证时间",
    "所属机构",
    "查询信息",
    "身份证状态",
    "手机号是否已认证",
    "是否有正反面",
    "是否有活体",
]
PRACTITIONER_TABLE_HEADERS: List[str] = [
    "所属机构",
    "姓名",
    "身份证",
    "登录手机号",
    "身份证状态",
    "手机号是否已认证",
    "详情",
]
NATURAL_MANAGE_FILTERS: List[str] = [
    "商户名称",
    "查询信息",
    "搜索",
    "刷新",
]
NATURAL_MANAGE_TABLE_HEADERS: List[str] = [
    "商户名",
    "姓名",
    "身份证",
    "创建时间",
    "银行卡账号",
    "支付宝账号",
]
GET_CODE_READY_TEXT = "获取短信验证码"
GET_CODE_SENDING_TEXT = "发送中"
GET_CODE_RETRY_TEXT = "重新获取"
EMPTY_STATE_TEXT = "暂无数据"
PRACTITIONER_TOTAL_TEXT = "共 "
SKIP_LOGIN_MESSAGE = "当前环境未成功进入业务模块选择页"


class NaturalPersonPage(LoginPage):
    def wait_for_natural_person_dashboard(self) -> None:
        deadline = time.time() + 8
        while time.time() < deadline:
            if self.page.url.endswith("/accounting/home") and self.page.locator(f"text={NATURAL_PERSON_MODULE}").count() > 0:
                if all(self.page.locator(f"text={label}").first.is_visible(timeout=500) for label in HOME_METRICS):
                    return
            self.page.wait_for_timeout(300)
        raise AssertionError("自然人业务首页未正常加载")

    def open_natural_person_module(self) -> None:
        if self.has_business_module_selector():
            self.select_business_module(NATURAL_PERSON_MODULE)
        self.wait_for_natural_person_dashboard()

    def module_popup_hidden(self) -> bool:
        try:
            return self.business_module_action_buttons().count() == 0
        except Error:
            return True

    def goto_business_route(self, route_key: str) -> None:
        target = f"http://192.168.12.36:7050{NATURAL_PERSON_ROUTES[route_key]}"
        self.page.goto(target, wait_until="domcontentloaded")
        self.page.wait_for_timeout(800)

    def page_has_all_texts(self, labels: List[str]) -> bool:
        for label in labels:
            try:
                if not self.page.locator(f"text={label}").first.is_visible(timeout=1000):
                    return False
            except Error:
                return False
        return True

    def practitioner_table_ready(self) -> bool:
        try:
            if self.page.locator(f"text={PRACTITIONER_TOTAL_TEXT}").first.is_visible(timeout=1000):
                return True
        except Error:
            pass
        try:
            if self.page.locator(f"text={EMPTY_STATE_TEXT}").first.is_visible(timeout=1000):
                return True
        except Error:
            return False
        return False

    def natural_manage_table_ready(self) -> bool:
        try:
            if self.page.locator(f"text={EMPTY_STATE_TEXT}").first.is_visible(timeout=1000):
                return True
        except Error:
            pass
        return self.page_has_all_texts(NATURAL_MANAGE_TABLE_HEADERS)


@pytest.fixture
def natural_person_page(page: Page, request) -> NaturalPersonPage:
    lp = NaturalPersonPage(page)
    lp.open()
    lp.page_ready()
    lp.fill_phone(CONFIG.phone)
    lp.click_get_code()

    send_deadline = time.time() + 3
    while time.time() < send_deadline:
        text, is_disabled = lp.get_code_button_state()
        if is_disabled or text != GET_CODE_READY_TEXT or GET_CODE_SENDING_TEXT in text or GET_CODE_RETRY_TEXT in text:
            break
        lp.page.wait_for_timeout(200)

    lp.fill_code(CONFIG.valid_code)
    expect(lp.login_button()).to_be_enabled()
    lp.click_login()

    login_deadline = time.time() + 8
    while time.time() < login_deadline:
        if "/accounting/home" in lp.page.url.lower() and lp.has_business_module_selector():
            break
        lp.page.wait_for_timeout(300)

    if "/accounting/home" not in lp.page.url.lower():
        lp.page.screenshot(path=str(Path("playwright_screenshots") / f"{request.node.name}.png"), full_page=True)
        pytest.skip(SKIP_LOGIN_MESSAGE)

    lp.open_natural_person_module()
    return lp


def test_np_01_enter_natural_person_business(natural_person_page: NaturalPersonPage, request) -> None:
    assert natural_person_page.page.url.endswith("/accounting/home")
    assert natural_person_page.page_has_all_texts(HOME_METRICS)
    assert natural_person_page.module_popup_hidden(), "进入自然人业务后业务模块弹框仍未收起"
    delete_existing_screenshot(request)


def test_np_02_home_metrics_visible(natural_person_page: NaturalPersonPage, request) -> None:
    assert natural_person_page.page_has_all_texts(HOME_METRICS), "自然人业务首页统计卡片缺失"
    delete_existing_screenshot(request)


def test_np_03_home_table_headers_visible(natural_person_page: NaturalPersonPage, request) -> None:
    assert natural_person_page.page_has_all_texts(HOME_TABLE_HEADERS), "自然人业务首页表格表头缺失"
    delete_existing_screenshot(request)


def test_np_04_top_business_line_visible(natural_person_page: NaturalPersonPage, request) -> None:
    assert natural_person_page.page.locator(f"text={NATURAL_PERSON_MODULE}").first.is_visible(timeout=1000)
    delete_existing_screenshot(request)


def test_np_05_practitioner_management_filters_visible(natural_person_page: NaturalPersonPage, request) -> None:
    try:
        natural_person_page.goto_business_route("practitioner_management")
        assert natural_person_page.page.url.endswith(NATURAL_PERSON_ROUTES["practitioner_management"])
        assert natural_person_page.page_has_all_texts(PRACTITIONER_FILTERS), "从业者管理筛选区缺失"
        delete_existing_screenshot(request)
    except Exception:
        save_failure_screenshot(natural_person_page, request)
        raise


def test_np_06_practitioner_management_table_headers_visible(natural_person_page: NaturalPersonPage, request) -> None:
    try:
        natural_person_page.goto_business_route("practitioner_management")
        assert natural_person_page.page_has_all_texts(PRACTITIONER_TABLE_HEADERS), "从业者管理表格表头缺失"
        delete_existing_screenshot(request)
    except Exception:
        save_failure_screenshot(natural_person_page, request)
        raise


def test_np_07_practitioner_management_table_ready(natural_person_page: NaturalPersonPage, request) -> None:
    try:
        natural_person_page.goto_business_route("practitioner_management")
        assert natural_person_page.practitioner_table_ready(), "从业者管理页列表区域未正常加载"
        delete_existing_screenshot(request)
    except Exception:
        save_failure_screenshot(natural_person_page, request)
        raise


def test_np_08_natural_manage_filters_visible(natural_person_page: NaturalPersonPage, request) -> None:
    try:
        natural_person_page.goto_business_route("natural_manage")
        assert natural_person_page.page.url.endswith(NATURAL_PERSON_ROUTES["natural_manage"])
        assert natural_person_page.page_has_all_texts(NATURAL_MANAGE_FILTERS), "自然人管理筛选区缺失"
        delete_existing_screenshot(request)
    except Exception:
        save_failure_screenshot(natural_person_page, request)
        raise


def test_np_09_natural_manage_table_headers_visible(natural_person_page: NaturalPersonPage, request) -> None:
    try:
        natural_person_page.goto_business_route("natural_manage")
        assert natural_person_page.page_has_all_texts(NATURAL_MANAGE_TABLE_HEADERS), "自然人管理表格表头缺失"
        delete_existing_screenshot(request)
    except Exception:
        save_failure_screenshot(natural_person_page, request)
        raise


def test_np_10_natural_manage_table_ready(natural_person_page: NaturalPersonPage, request) -> None:
    try:
        natural_person_page.goto_business_route("natural_manage")
        assert natural_person_page.natural_manage_table_ready(), "自然人管理页列表区域未正常加载"
        delete_existing_screenshot(request)
    except Exception:
        save_failure_screenshot(natural_person_page, request)
        raise
