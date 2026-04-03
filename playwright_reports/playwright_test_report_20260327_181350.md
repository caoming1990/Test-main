# Playwright 测试报告

- 开始时间：2026-03-27 18:09:20
- 结束时间：2026-03-27 18:13:50
- 总耗时：269.26s
- 总用例数：27
- 通过数：24
- 失败数：0
- 忽略数：3

## 分类统计

- 通过: `##################--` 24
- 失败: `--------------------` 0
- 忽略: `##------------------` 3

## 用例明细

| 用例 | 结果 | 耗时 | 失败信息 | 截图 |
| --- | --- | --- | --- | --- |
| test_01_page_elements_are_visible[chromium] | passed | 0.20s | - | - |
| test_02_phone_accepts_valid_value[chromium] | passed | 0.51s | - | - |
| test_03_empty_phone_cannot_get_code[chromium] | passed | 0.19s | - | - |
| test_04_short_phone_cannot_get_code[chromium] | passed | 0.37s | - | - |
| test_05_phone_length_limit[chromium] | passed | 0.57s | - | - |
| test_06_invalid_phone_format[chromium] | passed | 0.54s | - | - |
| test_07_get_code_success[chromium] | passed | 41.49s | - | - |
| test_08_get_code_countdown[chromium] | passed | 31.71s | - | - |
| test_09_repeat_get_code_is_prevented[chromium] | passed | 21.65s | - | - |
| test_10_code_accepts_valid_value[chromium] | passed | 0.22s | - | - |
| test_11_empty_code_cannot_login[chromium] | passed | 0.48s | - | - |
| test_12_invalid_code_login_fails[chromium] | passed | 0.56s | - | - |
| test_13_expired_code_login_fails[chromium] | ignored | 0.00s | 需要可控的过期验证码或等待验证码失效，当前环境不适合稳定自动化 | - |
| test_14_login_success[chromium] | passed | 24.68s | - | - |
| test_15_login_without_requesting_code_shows_error[chromium] | passed | 0.75s | - | - |
| test_16_login_button_state_changes[chromium] | passed | 0.50s | - | - |
| test_17_logged_in_user_revisit_login_redirects[chromium] | passed | 1.04s | - | - |
| test_18_code_only_valid_for_original_phone[chromium] | passed | 0.57s | - | - |
| test_19_get_code_api_error[chromium] | ignored | 0.00s | 需要接口异常注入或后端故障环境，默认回归时跳过 | - |
| test_20_login_api_error[chromium] | ignored | 0.00s | 需要接口异常注入或后端故障环境，默认回归时跳过 | - |
| test_21_phone_trims_spaces[chromium] | passed | 0.53s | - | - |
| test_22_code_rejects_non_digit[chromium] | passed | 0.73s | - | - |
| test_23_login_repeat_submit_is_prevented[chromium] | passed | 2.35s | - | - |
| test_24_refresh_keeps_login_state[chromium] | passed | 1.01s | - | - |
| test_25_back_navigation_after_login[chromium] | passed | 0.84s | - | - |
| test_26_business_module_selector_is_visible[chromium] | passed | 2.10s | - | - |
| test_27_select_business_module_switches_business_line[chromium] | passed | 12.71s | - | - |