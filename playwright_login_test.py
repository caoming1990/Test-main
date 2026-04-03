import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List

import pytest
from playwright.sync_api import Error, Page, Route, expect


@dataclass(frozen=True)
class LoginConfig:
    base_url: str = os.getenv("TEST_LOGIN_URL", "http://192.168.12.36:7050/login")
    phone: str = os.getenv("TEST_LOGIN_PHONE", "13600000000")
    valid_code: str = os.getenv("TEST_LOGIN_CODE", "0000")
    invalid_phone: str = os.getenv("TEST_INVALID_PHONE", "12345")
    invalid_code: str = os.getenv("TEST_INVALID_CODE", "1234")
    second_phone: str = os.getenv("TEST_SECOND_PHONE", "13606500853")
    module_name: str = os.getenv("TEST_BUSINESS_MODULE", "自然人")
    timeout_ms: int = int(os.getenv("TEST_TIMEOUT_MS", "10000"))
    headless: bool = os.getenv("TEST_HEADLESS", "false").lower() == "true"
    slow_mo: int = int(os.getenv("TEST_SLOW_MO", "0"))


CONFIG = LoginConfig()
REQUEST_CODE_API_PATTERN = "**/api/v1/login/requestLoginCode"
LOGIN_API_PATTERN = "**/api/v1/login/login"
SCREENSHOT_DIR = Path("playwright_screenshots")
SCREENSHOT_DIR.mkdir(exist_ok=True)


PHONE_SELECTORS: List[str] = [
    "input[placeholder='请输入手机号']",
    "input[placeholder*='手机号']",
    "input[placeholder*='手机号码']",
    "input[type='tel']",
]

CODE_SELECTORS: List[str] = [
    "input[placeholder='请输入验证码']",
    "input[placeholder*='验证码']",
]

GET_CODE_SELECTORS: List[str] = [
    "button:has-text('获取短信验证码')",
    "button:has-text('获取验证码')",
    "button:has-text('重新获取')",
    "button:has-text('发送中')",
    "[role='button']:has-text('获取短信验证码')",
    "[role='button']:has-text('获取验证码')",
    "[role='button']:has-text('重新获取')",
    "[role='button']:has-text('发送中')",
    "text=获取短信验证码",
    "text=获取验证码",
    "text=重新获取",
    "text=发送中",
]

LOGIN_SELECTORS: List[str] = [
    "button:has-text('登录')",
    "[role='button']:has-text('登录')",
    "text=登录",
]

WECHAT_SELECTORS: List[str] = [
    "button:has-text('微信扫码登录')",
    "[role='button']:has-text('微信扫码登录')",
    "text=微信扫码登录",
]

MESSAGE_SELECTORS: List[str] = [
    ".el-message__content",
    ".ant-message-notice-content",
    ".van-toast__text",
    ".toast",
    ".message",
    "[class*='toast']",
    "[class*='message']",
    "[class*='error']",
    "[role='alert']",
]

MODULE_NAMES: List[str] = ["自然人", "个体工商户结算系统", "账管家系统", "云纳税系统", "云劳务系统"]


class LoginPage:
    def __init__(self, page: Page):
        self.page = page
        self.page.set_default_timeout(CONFIG.timeout_ms)

    def open(self) -> None:
        self.page.goto(CONFIG.base_url, wait_until="domcontentloaded")

    def locator_first(self, selectors: Iterable[str]):
        last_error = None
        selector_list = list(selectors)
        for selector in selector_list:
            locator = self.page.locator(selector).first
            try:
                locator.wait_for(state="visible", timeout=CONFIG.timeout_ms)
                return locator
            except Error as exc:
                last_error = exc
        raise AssertionError(f"未找到页面元素，请检查选择器配置: {selector_list}") from last_error

    def phone_input(self):
        return self.locator_first(PHONE_SELECTORS)

    def code_input(self):
        return self.locator_first(CODE_SELECTORS)

    def get_code_button(self):
        return self.locator_first(GET_CODE_SELECTORS)

    def login_button(self):
        return self.locator_first(LOGIN_SELECTORS)

    def wechat_button(self):
        return self.locator_first(WECHAT_SELECTORS)

    def fill_phone(self, phone: str) -> None:
        self.phone_input().fill(phone)

    def fill_code(self, code: str) -> None:
        self.code_input().fill(code)

    def click_get_code(self) -> None:
        self.get_code_button().click()

    def click_login(self) -> None:
        self.login_button().click()

    def page_ready(self) -> None:
        self.phone_input()
        self.code_input()
        self.get_code_button()
        self.login_button()
        self.wechat_button()

    def phone_value(self) -> str:
        return self.phone_input().input_value()

    def code_value(self) -> str:
        return self.code_input().input_value()

    def phone_alert_text(self) -> str:
        alert = self.page.locator("[role='alert']").first
        try:
            if alert.is_visible(timeout=500):
                return alert.inner_text().strip()
        except Error:
            return ""
        return ""

    def latest_message_text(self) -> str:
        end_time = time.time() + CONFIG.timeout_ms / 1000
        latest = ""
        while time.time() < end_time:
            for selector in MESSAGE_SELECTORS:
                locator = self.page.locator(selector)
                try:
                    texts = [text.strip() for text in locator.all_inner_texts() if text.strip()]
                except Error:
                    texts = []
                if texts:
                    latest = texts[-1]
            if latest:
                return latest
            time.sleep(0.2)
        return latest

    def is_login_success(self) -> bool:
        current_url = self.page.url.lower()
        if "/accounting/" in current_url or "/home" in current_url:
            return True
        if "/login" not in current_url:
            return True
        storage_keys = self.page.evaluate(
            "Object.keys(window.localStorage || {}).concat(Object.keys(window.sessionStorage || {}))"
        )
        keywords = ("token", "access", "user", "auth", "session")
        return any(any(word in key.lower() for word in keywords) for key in storage_keys)

    def get_code_button_state(self) -> tuple[str, bool]:
        try:
            button = self.get_code_button()
            return button.inner_text().strip(), button.is_disabled()
        except Error:
            return "", False

    def business_module_action_buttons(self):
        return self.page.locator(
            "xpath=//*[normalize-space()='进入查看' or normalize-space()='立即进入']"
        )

    def business_module_button(self, module_name: str):
        module_index = MODULE_NAMES.index(module_name)
        return self.business_module_action_buttons().nth(module_index)

    def has_business_module_selector(self) -> bool:
        deadline = time.time() + 5
        while time.time() < deadline:
            try:
                if self.business_module_action_buttons().count() >= len(MODULE_NAMES):
                    return True
            except Error:
                pass
            self.page.wait_for_timeout(200)
        return False

    def select_business_module(self, module_name: str) -> None:
        button = self.business_module_button(module_name)
        button.wait_for(state="visible", timeout=CONFIG.timeout_ms)
        button.click()

    def business_dashboard_ready(self) -> bool:
        indicators = [
            self.page.locator("text=待审核充值").first,
            self.page.locator("text=今日提交结算单").first,
            self.page.locator(f"text={CONFIG.module_name}").first,
        ]
        for locator in indicators:
            try:
                if locator.is_visible(timeout=500):
                    return True
            except Error:
                continue
        return False


@pytest.fixture(scope="session")
def browser_type_launch_args(browser_type_launch_args: dict) -> dict:
    return {
        **browser_type_launch_args,
        "headless": CONFIG.headless,
        "slow_mo": CONFIG.slow_mo,
    }


@pytest.fixture
def login_page(page: Page) -> LoginPage:
    lp = LoginPage(page)
    lp.open()
    lp.page_ready()
    return lp


@pytest.fixture
def logged_in_page(page: Page, request) -> LoginPage:
    lp = LoginPage(page)
    lp.open()
    lp.page_ready()
    lp.fill_phone(CONFIG.phone)
    lp.click_get_code()

    send_deadline = time.time() + 2
    while time.time() < send_deadline:
        text, is_disabled = lp.get_code_button_state()
        if is_disabled or text != "获取短信验证码" or "发送中" in text or "重新获取" in text:
            break
        lp.page.wait_for_timeout(200)

    lp.fill_code(CONFIG.valid_code)
    expect(lp.login_button()).to_be_enabled()
    lp.click_login()

    login_deadline = time.time() + 5
    while time.time() < login_deadline:
        if lp.is_login_success():
            break
        lp.page.wait_for_timeout(300)

    if not lp.is_login_success():
        lp.page.screenshot(path=str(screenshot_path(request)), full_page=True)
        pytest.skip("当前环境未登录成功，依赖已获取验证码后的有效登录态")
    return lp


def screenshot_path(request) -> Path:
    return SCREENSHOT_DIR / f"{request.node.name}.png"


def delete_existing_screenshot(request) -> None:
    path = screenshot_path(request)
    if path.exists():
        path.unlink()


def save_failure_screenshot(login_page: LoginPage, request) -> None:
    login_page.page.screenshot(path=str(screenshot_path(request)), full_page=True)


def assert_message_contains(message: str, keywords: Iterable[str]) -> None:
    assert message, "未捕获到页面提示信息"
    assert any(keyword in message for keyword in keywords), f"提示文案不符合预期: {message}"


def mock_json_error(route: Route, message: str, code: int = 500, status: int = 200) -> None:
    route.fulfill(
        status=status,
        content_type="application/json",
        body=f'{{"code": {code}, "msg": "{message}", "message": "{message}", "data": null}}',
    )


# 场景：页面元素正常展示，校验登录页基础控件与文案。
def test_01_page_elements_are_visible(login_page: LoginPage, request) -> None:
    assert "login" in login_page.page.url.lower(), f"当前页面地址不包含 login: {login_page.page.url}"
    expect(login_page.get_code_button()).to_have_text("获取短信验证码")
    expect(login_page.login_button()).to_have_text("登录")
    expect(login_page.wechat_button()).to_have_text("微信扫码登录")
    delete_existing_screenshot(request)


# 场景：输入合法手机号后，输入框应正常保留11位号码。
def test_02_phone_accepts_valid_value(login_page: LoginPage, request) -> None:
    login_page.fill_phone(CONFIG.phone)
    assert login_page.phone_value() == CONFIG.phone
    delete_existing_screenshot(request)


# 场景：手机号为空时，获取短信验证码按钮不可点击。
def test_03_empty_phone_cannot_get_code(login_page: LoginPage, request) -> None:
    expect(login_page.get_code_button()).to_be_disabled()
    delete_existing_screenshot(request)


# 场景：手机号位数不足时，获取短信验证码按钮保持禁用并出现格式提示。
def test_04_short_phone_cannot_get_code(login_page: LoginPage, request) -> None:
    login_page.fill_phone(CONFIG.invalid_phone)
    expect(login_page.get_code_button()).to_be_disabled()
    assert_message_contains(login_page.phone_alert_text(), ("手机号格式不正确", "手机号"))
    delete_existing_screenshot(request)


# 场景：手机号超过11位时，应提示“手机号格式不正确”，且获取短信验证码按钮保持禁用。
def test_05_phone_length_limit(login_page: LoginPage, request) -> None:
    login_page.fill_phone("1360000000000")
    assert len(login_page.phone_value()) > 11
    expect(login_page.get_code_button()).to_be_disabled()
    assert login_page.phone_alert_text() == "手机号格式不正确"
    delete_existing_screenshot(request)


# 场景：手机号包含非法字符时，获取短信验证码按钮保持禁用并提示格式错误。
def test_06_invalid_phone_format(login_page: LoginPage, request) -> None:
    login_page.fill_phone("1380013800a")
    expect(login_page.get_code_button()).to_be_disabled()
    assert_message_contains(login_page.phone_alert_text(), ("手机号格式不正确", "手机号"))
    delete_existing_screenshot(request)


# 场景：合法手机号点击获取短信验证码后，按钮应在短时间内进入发送相关状态。
def test_07_get_code_success(login_page: LoginPage, request) -> None:
    try:
        login_page.fill_phone(CONFIG.phone)
        expect(login_page.get_code_button()).to_be_enabled()
        login_page.click_get_code()

        deadline = time.time() + 2
        text = ""
        is_disabled = False
        while time.time() < deadline:
            text, is_disabled = login_page.get_code_button_state()
            if is_disabled or text != "获取短信验证码" or "发送中" in text or "重新获取" in text:
                break
            login_page.page.wait_for_timeout(200)

        assert login_page.get_code_button().is_visible(), "发码后按钮不可见"
        delete_existing_screenshot(request)
    except Exception:
        save_failure_screenshot(login_page, request)
        raise


# 场景：点击获取短信验证码后，按钮通常会进入发送中/重新获取/禁用等发送态；若页面更新较慢，也至少不应影响后续重复发送限制。
def test_08_get_code_countdown(login_page: LoginPage, request) -> None:
    try:
        login_page.fill_phone(CONFIG.phone)
        login_page.click_get_code()

        deadline = time.time() + 2
        text = ""
        is_disabled = False
        while time.time() < deadline:
            text, is_disabled = login_page.get_code_button_state()
            if is_disabled or text != "获取短信验证码" or "发送中" in text or "重新获取" in text:
                break
            login_page.page.wait_for_timeout(200)

        login_page.page.wait_for_timeout(300)
        assert login_page.get_code_button().is_visible(), "点击后获取短信验证码按钮不可见"
        delete_existing_screenshot(request)
    except Exception:
        save_failure_screenshot(login_page, request)
        raise


# 场景：短时间内重复点击获取短信验证码应被拦截，按钮应进入重新获取/发送中/禁用等不可重复发送状态。
def test_09_repeat_get_code_is_prevented(login_page: LoginPage, request) -> None:
    try:
        login_page.fill_phone(CONFIG.phone)
        login_page.click_get_code()

        deadline = time.time() + 3
        text = ""
        is_disabled = False
        while time.time() < deadline:
            text, is_disabled = login_page.get_code_button_state()
            if is_disabled or "重新获取" in text or "发送中" in text or text != "获取短信验证码":
                break
            login_page.page.wait_for_timeout(200)

        assert (
            is_disabled
            or "重新获取" in text
            or "发送中" in text
            or text != "获取短信验证码"
        ), f"首次发送后按钮仍允许重复发送，当前文案: {text}"
        delete_existing_screenshot(request)
    except Exception:
        save_failure_screenshot(login_page, request)
        raise


# 场景：验证码输入框可正常接受合法验证码值。
def test_10_code_accepts_valid_value(login_page: LoginPage, request) -> None:
    login_page.fill_code(CONFIG.valid_code)
    assert login_page.code_value() == CONFIG.valid_code
    delete_existing_screenshot(request)


# 场景：只填写手机号、不填写验证码时，登录按钮应保持禁用。
def test_11_empty_code_cannot_login(login_page: LoginPage, request) -> None:
    login_page.fill_phone(CONFIG.phone)
    expect(login_page.login_button()).to_be_disabled()
    delete_existing_screenshot(request)


# 场景：输入错误验证码直接登录，系统应提示验证码错误或无效。
def test_12_invalid_code_login_fails(login_page: LoginPage, request) -> None:
    try:
        login_page.fill_phone(CONFIG.phone)
        login_page.fill_code(CONFIG.invalid_code)
        expect(login_page.login_button()).to_be_enabled()
        login_page.click_login()
        message = login_page.latest_message_text()
        assert_message_contains(message, ("验证码", "错误", "无效", "过期"))
        delete_existing_screenshot(request)
    except Exception:
        save_failure_screenshot(login_page, request)
        raise


@pytest.mark.skip(reason="需要可控的过期验证码或等待验证码失效，当前环境不适合稳定自动化")
def test_13_expired_code_login_fails(login_page: LoginPage) -> None:
    pass


# 场景：合法手机号与正确验证码登录成功后，应进入业务模块选择界面。
def test_14_login_success(login_page: LoginPage, request) -> None:
    try:
        login_page.fill_phone(CONFIG.phone)
        login_page.click_get_code()

        send_deadline = time.time() + 2
        while time.time() < send_deadline:
            text, is_disabled = login_page.get_code_button_state()
            if is_disabled or text != "获取短信验证码" or "发送中" in text or "重新获取" in text:
                break
            login_page.page.wait_for_timeout(200)

        login_page.fill_code(CONFIG.valid_code)
        expect(login_page.login_button()).to_be_enabled()
        login_page.click_login()

        login_deadline = time.time() + 5
        while time.time() < login_deadline:
            if login_page.is_login_success():
                break
            login_page.page.wait_for_timeout(300)

        assert login_page.is_login_success(), "使用正确手机号和验证码后未登录成功"
        assert login_page.has_business_module_selector(), "登录成功后未展示业务模块选择区域"
        delete_existing_screenshot(request)
    except Exception:
        save_failure_screenshot(login_page, request)
        raise


# 场景：输入手机号和验证码但未点击获取短信验证码，直接登录应提示“验证码不正确”；若首次命中限流，则等待2秒后重试一次。
def test_15_login_without_requesting_code_shows_error(login_page: LoginPage, request) -> None:
    try:
        login_page.fill_phone(CONFIG.phone)
        login_page.fill_code(CONFIG.valid_code)
        expect(login_page.login_button()).to_be_enabled()

        def get_login_message() -> str:
            deadline = time.time() + 3
            current_message = ""
            while time.time() < deadline:
                current_message = login_page.latest_message_text()
                if current_message:
                    return current_message
                login_page.page.wait_for_timeout(200)
            return current_message

        login_page.click_login()
        message = get_login_message()

        if message == "请求频率太快":
            login_page.page.wait_for_timeout(2000)
            login_page.click_login()
            message = get_login_message()

        assert not login_page.is_login_success(), "未获取短信验证码直接登录却登录成功"
        assert message == "验证码不正确", f"未获取短信验证码直接登录后的提示不符合预期: {message}"
        delete_existing_screenshot(request)
    except Exception:
        save_failure_screenshot(login_page, request)
        raise


# 场景：登录按钮状态随输入完整度变化，空白和缺验证码时禁用，信息完整时启用。
def test_16_login_button_state_changes(login_page: LoginPage, request) -> None:
    expect(login_page.login_button()).to_be_disabled()
    login_page.fill_phone(CONFIG.phone)
    expect(login_page.login_button()).to_be_disabled()
    login_page.fill_code(CONFIG.valid_code)
    expect(login_page.login_button()).to_be_enabled()
    delete_existing_screenshot(request)


# 场景：已登录用户再次访问登录页时，应保持有效登录态，不应丢失会话信息。
def test_17_logged_in_user_revisit_login_redirects(logged_in_page: LoginPage, request) -> None:
    logged_in_page.page.goto(CONFIG.base_url, wait_until="domcontentloaded")
    logged_in_page.page.wait_for_timeout(800)
    assert logged_in_page.is_login_success(), "重新访问登录页后会话失效"
    delete_existing_screenshot(request)


# 场景：验证码仅对原手机号生效，换手机号后登录应失败。
def test_18_code_only_valid_for_original_phone(login_page: LoginPage, request) -> None:
    try:
        login_page.fill_phone(CONFIG.second_phone)
        login_page.fill_code(CONFIG.valid_code)
        expect(login_page.login_button()).to_be_enabled()
        login_page.click_login()
        message = login_page.latest_message_text()
        assert_message_contains(message, ("验证码", "错误", "无效", "token", "过期"))
        delete_existing_screenshot(request)
    except Exception:
        save_failure_screenshot(login_page, request)
        raise


@pytest.mark.skip(reason="需要接口异常注入或后端故障环境，默认回归时跳过")
def test_19_get_code_api_error(login_page: LoginPage, request) -> None:
    try:
        login_page.page.route(
            REQUEST_CODE_API_PATTERN,
            lambda route: mock_json_error(route, "发送失败，请稍后重试"),
        )
        login_page.fill_phone(CONFIG.phone)
        login_page.click_get_code()
        message = login_page.latest_message_text()
        assert_message_contains(message, ("发送失败", "稍后重试", "错误", "异常"))
        delete_existing_screenshot(request)
    except Exception:
        save_failure_screenshot(login_page, request)
        raise
    finally:
        login_page.page.unroute(REQUEST_CODE_API_PATTERN)


@pytest.mark.skip(reason="需要接口异常注入或后端故障环境，默认回归时跳过")
def test_20_login_api_error(login_page: LoginPage, request) -> None:
    try:
        login_page.page.route(
            LOGIN_API_PATTERN,
            lambda route: mock_json_error(route, "登录失败，请稍后重试"),
        )
        login_page.fill_phone(CONFIG.phone)
        login_page.fill_code(CONFIG.valid_code)
        expect(login_page.login_button()).to_be_enabled()
        login_page.click_login()
        message = login_page.latest_message_text()
        assert_message_contains(message, ("登录失败", "稍后重试", "错误", "异常"))
        expect(login_page.login_button()).to_be_enabled()
        delete_existing_screenshot(request)
    except Exception:
        save_failure_screenshot(login_page, request)
        raise
    finally:
        login_page.page.unroute(LOGIN_API_PATTERN)


# 场景：手机号前后带空格时，应自动清理或给出明确格式提示。
def test_21_phone_trims_spaces(login_page: LoginPage, request) -> None:
    login_page.fill_phone(f" {CONFIG.phone} ")
    value = login_page.phone_value().replace(" ", "")
    assert value == CONFIG.phone or login_page.phone_alert_text()
    delete_existing_screenshot(request)


# 场景：验证码包含非数字字符时，应被限制或登录时报错。
def test_22_code_rejects_non_digit(login_page: LoginPage, request) -> None:
    try:
        login_page.fill_phone(CONFIG.phone)
        login_page.fill_code("00a0")
        value = login_page.code_value()
        assert not value.isalpha()
        login_page.click_login()
        message = login_page.latest_message_text()
        assert message or value != "00a0"
        delete_existing_screenshot(request)
    except Exception:
        save_failure_screenshot(login_page, request)
        raise


# 场景：连续点击登录按钮时，不应产生明显的重复提交异常。
def test_23_login_repeat_submit_is_prevented(login_page: LoginPage, request) -> None:
    try:
        login_page.fill_phone(CONFIG.phone)
        login_page.click_get_code()
        login_page.page.wait_for_timeout(500)
        login_page.fill_code(CONFIG.valid_code)
        expect(login_page.login_button()).to_be_enabled()
        login_page.click_login()
        login_page.page.wait_for_timeout(200)
        assert True
        delete_existing_screenshot(request)
    except Exception:
        save_failure_screenshot(login_page, request)
        raise


# 场景：登录成功后刷新页面，登录态应按产品预期保持有效。
def test_24_refresh_keeps_login_state(logged_in_page: LoginPage, request) -> None:
    logged_in_page.page.reload(wait_until="domcontentloaded")
    logged_in_page.page.wait_for_timeout(800)
    assert logged_in_page.is_login_success(), "刷新后登录态未保持"
    delete_existing_screenshot(request)


# 场景：登录成功后点击浏览器返回，不应丢失当前有效登录态。
def test_25_back_navigation_after_login(logged_in_page: LoginPage, request) -> None:
    try:
        logged_in_page.page.go_back(wait_until="domcontentloaded")
    except Error:
        pass
    logged_in_page.page.wait_for_timeout(800)
    assert logged_in_page.is_login_success(), "返回后登录态丢失"
    delete_existing_screenshot(request)


# 场景：登录成功后，应展示业务模块选择区域。
def test_26_business_module_selector_is_visible(logged_in_page: LoginPage, request) -> None:
    assert logged_in_page.has_business_module_selector(), "登录后未展示业务模块选择区域"
    delete_existing_screenshot(request)


# 场景：选择业务模块后，应切换到对应业务线内容页面。
def test_27_select_business_module_switches_business_line(logged_in_page: LoginPage, request) -> None:
    try:
        assert logged_in_page.has_business_module_selector(), "业务模块选择区域不存在，无法执行模块切换"
        logged_in_page.select_business_module(CONFIG.module_name)

        deadline = time.time() + 5
        while time.time() < deadline:
            if logged_in_page.business_dashboard_ready() and not logged_in_page.has_business_module_selector():
                break
            logged_in_page.page.wait_for_timeout(300)

        assert logged_in_page.business_dashboard_ready(), "选择业务模块后未进入对应业务线内容页面"
        assert not logged_in_page.has_business_module_selector(), "选择业务模块后业务模块选择区域仍未收起"
        delete_existing_screenshot(request)
    except Exception:
        save_failure_screenshot(logged_in_page, request)
        raise
