# Playwright 测试报告

- 开始时间：2026-03-27 17:45:58
- 结束时间：2026-03-27 17:46:47
- 总耗时：49.07s
- 总用例数：2
- 通过数：0
- 失败数：2
- 忽略数：0

## 分类统计

- 通过: `--------------------` 0
- 失败: `####################` 2
- 忽略: `--------------------` 0

## 用例明细

| 用例 | 结果 | 耗时 | 失败信息 | 截图 |
| --- | --- | --- | --- | --- |
| test_26_business_module_selector_is_visible[chromium] | failed | 0.09s | 登录后未展示业务模块选择区域 assert False  +  where False = <bound method LoginPage.has_business_module_selector of <playwright_login_test.LoginPage object at 0x000001EDB88F46D0>>()  +    where <bound method LoginPage.has_business_module_selector of <playwright_login_test.LoginPage object at 0x000001EDB88F46D0>> = <playwright_login_test.LoginPage object at 0x000001EDB88F46D0>.has_business_module_selector | - |
| test_27_select_business_module_switches_business_line[chromium] | failed | 0.63s | 业务模块选择区域不存在，无法执行模块切换 assert False  +  where False = <bound method LoginPage.has_business_module_selector of <playwright_login_test.LoginPage object at 0x000001EDB8DA1D60>>()  +    where <bound method LoginPage.has_business_module_selector of <playwright_login_test.LoginPage object at 0x000001EDB8DA1D60>> = <playwright_login_test.LoginPage object at 0x000001EDB8DA1D60>.has_business_module_selector | playwright_screenshots\test_27_select_business_module_switches_business_line[chromium].png |