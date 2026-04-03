# 登录测试用例

## 测试范围

- 登录页基础元素展示
- 手机号与验证码输入校验
- 获取短信验证码与重复发送控制
- 登录成功、登录失败与错误提示校验
- 登录成功后的业务模块选择
- 登录态保持、刷新与返回场景

## 前置条件

- 测试环境地址：`http://192.168.12.36:7050/login`
- 测试手机号：`13600000000`
- 第二测试手机号：`13606500853`
- 测试验证码：`0000`
- 自动化脚本：`playwright_login_test.py`

## 执行说明

- 自动化脚本文件：`playwright_login_test.py`
- 执行命令：

```bash
pytest -s playwright_login_test.py
```

## 用例列表

| 用例ID | 用例名称 | 前置条件 | 测试步骤 | 预期结果 |
| --- | --- | --- | --- | --- |
| LOGIN-001 | 登录页元素正常展示 | 打开登录页 | 1. 进入登录页 2. 观察页面元素 | 页面展示手机号输入框、验证码输入框、`获取短信验证码`、`登录`、`微信扫码登录` |
| LOGIN-002 | 合法手机号可正常输入 | 已进入登录页 | 1. 输入 `13600000000` | 输入框保留正确手机号 |
| LOGIN-003 | 手机号为空时不可获取验证码 | 已进入登录页 | 1. 不输入手机号 2. 观察按钮状态 | `获取短信验证码` 按钮保持禁用 |
| LOGIN-004 | 短位手机号格式校验 | 已进入登录页 | 1. 输入非法短号 2. 观察提示和按钮状态 | 按钮保持禁用，并提示手机号格式不正确 |
| LOGIN-005 | 超长手机号格式校验 | 已进入登录页 | 1. 输入超过 11 位手机号 | 提示 `手机号格式不正确`，获取验证码按钮保持禁用 |
| LOGIN-006 | 非法字符手机号格式校验 | 已进入登录页 | 1. 输入包含字母的手机号 | 获取验证码按钮禁用，并提示手机号格式不正确 |
| LOGIN-007 | 点击获取验证码后发码成功 | 已进入登录页 | 1. 输入合法手机号 2. 点击 `获取短信验证码` | 发码动作成功触发，页面无异常 |
| LOGIN-008 | 获取验证码后进入发送状态 | 已进入登录页 | 1. 输入合法手机号 2. 点击 `获取短信验证码` | 按钮进入发送中、重新获取或倒计时状态 |
| LOGIN-009 | 重复获取验证码受限 | 已进入登录页 | 1. 输入合法手机号 2. 点击 `获取短信验证码` | 短时间内不能重复发送，按钮进入不可重复发送状态 |
| LOGIN-010 | 验证码可正常输入 | 已进入登录页 | 1. 输入验证码 `0000` | 验证码输入框保留正确值 |
| LOGIN-011 | 验证码为空时不可登录 | 已进入登录页 | 1. 输入合法手机号 2. 不输入验证码 | `登录` 按钮保持禁用 |
| LOGIN-012 | 错误验证码登录失败 | 已进入登录页 | 1. 输入合法手机号 2. 输入错误验证码 3. 点击登录 | 系统提示验证码错误、无效或过期 |
| LOGIN-013 | 过期验证码登录失败 | 需具备可控过期验证码 | 1. 输入手机号 2. 输入过期验证码 3. 点击登录 | 系统拒绝登录并提示验证码失效 |
| LOGIN-014 | 正确账号登录成功 | 已进入登录页 | 1. 输入手机号 2. 点击获取验证码 3. 输入正确验证码 4. 点击登录 | 登录成功并进入业务模块选择界面 |
| LOGIN-015 | 未获取验证码直接登录提示错误 | 已进入登录页 | 1. 输入手机号和验证码 2. 不点击获取验证码 3. 点击登录 | 登录失败，并提示 `验证码不正确` |
| LOGIN-016 | 登录按钮状态随输入变化 | 已进入登录页 | 1. 分别测试空白、缺验证码、完整输入状态 | 登录按钮随输入完整度正确启用或禁用 |
| LOGIN-017 | 已登录用户再访登录页 | 已存在有效登录态 | 1. 登录成功 2. 再次访问登录页 | 会话保持有效，不应丢失登录态 |
| LOGIN-018 | 验证码仅对原手机号生效 | 已进入登录页 | 1. 输入第二手机号 `13606500853` 2. 输入默认验证码 3. 点击登录 | 登录失败，并提示验证码、token 或无效相关错误 |
| LOGIN-019 | 获取验证码接口异常处理 | 需异常注入环境 | 1. 模拟发码接口异常 2. 点击获取验证码 | 页面正确处理异常，不应误判发码成功 |
| LOGIN-020 | 登录接口异常处理 | 需异常注入环境 | 1. 模拟登录接口异常 2. 点击登录 | 页面正确处理异常，不应错误进入登录成功态 |
| LOGIN-021 | 手机号前后空格处理 | 已进入登录页 | 1. 输入带空格手机号 | 页面自动处理空格或给出格式提示 |
| LOGIN-022 | 非数字验证码处理 | 已进入登录页 | 1. 输入非数字验证码 2. 点击登录 | 页面限制输入或在登录时提示错误 |
| LOGIN-023 | 登录重复提交控制 | 已进入登录页 | 1. 正常输入并连续点击登录 | 不应产生明显重复提交异常 |
| LOGIN-024 | 登录成功后刷新保持登录态 | 已成功登录 | 1. 登录成功 2. 刷新页面 | 页面刷新后登录态保持有效 |
| LOGIN-025 | 登录成功后返回仍保持登录态 | 已成功登录 | 1. 登录成功 2. 浏览器返回 | 返回后不应丢失当前有效登录态 |
| LOGIN-026 | 登录成功后展示业务模块选择区 | 已成功登录 | 1. 正常登录成功 | 页面展示业务模块选择弹框或区域 |
| LOGIN-027 | 选择业务模块后切换到对应业务线 | 已进入业务模块选择区 | 1. 选择 `自然人` 模块 2. 点击 `进入查看` | 页面进入对应业务线内容区，业务模块选择区收起 |

## 自动化脚本对应关系

| 用例ID | 自动化测试函数 |
| --- | --- |
| LOGIN-001 | `test_01_page_elements_are_visible` |
| LOGIN-002 | `test_02_phone_accepts_valid_value` |
| LOGIN-003 | `test_03_empty_phone_cannot_get_code` |
| LOGIN-004 | `test_04_short_phone_cannot_get_code` |
| LOGIN-005 | `test_05_phone_length_limit` |
| LOGIN-006 | `test_06_invalid_phone_format` |
| LOGIN-007 | `test_07_get_code_success` |
| LOGIN-008 | `test_08_get_code_countdown` |
| LOGIN-009 | `test_09_repeat_get_code_is_prevented` |
| LOGIN-010 | `test_10_code_accepts_valid_value` |
| LOGIN-011 | `test_11_empty_code_cannot_login` |
| LOGIN-012 | `test_12_invalid_code_login_fails` |
| LOGIN-013 | `test_13_expired_code_login_fails` |
| LOGIN-014 | `test_14_login_success` |
| LOGIN-015 | `test_15_login_without_requesting_code_shows_error` |
| LOGIN-016 | `test_16_login_button_state_changes` |
| LOGIN-017 | `test_17_logged_in_user_revisit_login_redirects` |
| LOGIN-018 | `test_18_code_only_valid_for_original_phone` |
| LOGIN-019 | `test_19_get_code_api_error` |
| LOGIN-020 | `test_20_login_api_error` |
| LOGIN-021 | `test_21_phone_trims_spaces` |
| LOGIN-022 | `test_22_code_rejects_non_digit` |
| LOGIN-023 | `test_23_login_repeat_submit_is_prevented` |
| LOGIN-024 | `test_24_refresh_keeps_login_state` |
| LOGIN-025 | `test_25_back_navigation_after_login` |
| LOGIN-026 | `test_26_business_module_selector_is_visible` |
| LOGIN-027 | `test_27_select_business_module_switches_business_line` |

## 备注

- 当前文档已与 `playwright_login_test.py` 同步。
- `LOGIN-013`、`LOGIN-019`、`LOGIN-020` 依赖特殊环境或异常注入，是否执行以当前脚本标记为准。
- 登录成功后的业务模块选择场景，当前已覆盖 `自然人` 主路径；后续可继续补充个体工商户、账管家等业务线。
