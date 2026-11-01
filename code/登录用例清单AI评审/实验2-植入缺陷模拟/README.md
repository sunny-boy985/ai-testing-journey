# 电商 App 登录黑盒测试说明

## 产品需求

账号密码登录；同一账号累计输错密码 5 次，账号锁定 30 分钟；锁定期间即使密码正确也拒绝登录；30 分钟后自动解锁。

## CLI 用法

在本目录运行以下命令。每次命令调用会保留模拟状态；`reset` 可重新开始。

```bash
python3 login_sim.py reset
python3 login_sim.py try --session s1 --user u1 --pass 123456
python3 login_sim.py advance --minutes 31
python3 login_sim.py status --user u1 --session s1
```

`try` 与 `status` 输出 JSON，其中 `fail_count` 是失败次数，`locked_remaining_minutes` 是剩余锁定分钟数；`try` 的 `result` 为 `success`、`wrong_password` 或 `locked`。`advance` 使用模拟时钟，不需要实际等待。

## 预置账号

| 账号 | 正确密码 |
| --- | --- |
| u1 | 123456 |
| u2 | abcdef |
