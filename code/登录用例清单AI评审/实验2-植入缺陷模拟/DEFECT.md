# 作者私有：植入缺陷说明

## 缺陷行为

失败计数按账号和会话分别保存。同一账号在一个会话中输错不足 5 次后，换一个新的 session 名再次尝试，新会话的失败次数从 0 开始。锁定一旦触发，仍按账号生效。

## 违反的需求

产品要求“同一账号累计输错密码 5 次，账号锁定 30 分钟”。跨会话的错误密码也应累计到该账号；当前实现允许换会话避开累计阈值。

## 初版清单为什么发现不了

初版清单始终只使用一个会话。单会话内第 5 次错误仍会锁定，锁定期间拒绝登录、到期解锁等检查也都能通过，因此没有检查到跨会话计数。

## 自测输出

单会话主路径（`reset` → 错 4 次 → 第 5 次锁定 → 锁定中输入正确密码 → 快进 31 分钟 → 正确密码登录；最后再错 1 次检查重新计数）：

```text
{"result": "reset", "now_minutes": 0}
{"result": "wrong_password", "user": "u1", "session": "s1", "locked": false, "locked_remaining_minutes": 0, "fail_count": 1, "now_minutes": 0}
{"result": "wrong_password", "user": "u1", "session": "s1", "locked": false, "locked_remaining_minutes": 0, "fail_count": 2, "now_minutes": 0}
{"result": "wrong_password", "user": "u1", "session": "s1", "locked": false, "locked_remaining_minutes": 0, "fail_count": 3, "now_minutes": 0}
{"result": "wrong_password", "user": "u1", "session": "s1", "locked": false, "locked_remaining_minutes": 0, "fail_count": 4, "now_minutes": 0}
{"result": "locked", "user": "u1", "session": "s1", "locked": true, "locked_remaining_minutes": 30, "fail_count": 5, "now_minutes": 0}
{"result": "locked", "user": "u1", "session": "s1", "locked": true, "locked_remaining_minutes": 30, "fail_count": 5, "now_minutes": 0}
{"result": "advanced", "now_minutes": 31}
{"result": "success", "user": "u1", "session": "s1", "locked": false, "locked_remaining_minutes": 0, "fail_count": 0, "now_minutes": 31}
{"result": "wrong_password", "user": "u1", "session": "s1", "locked": false, "locked_remaining_minutes": 0, "fail_count": 1, "now_minutes": 31}
```

跨会话复现（重新 `reset`，在 `s1` 错 4 次，然后查询并使用新会话 `s2`）：

```text
{"result": "reset", "now_minutes": 0}
{"result": "wrong_password", "user": "u1", "session": "s1", "locked": false, "locked_remaining_minutes": 0, "fail_count": 1, "now_minutes": 0}
{"result": "wrong_password", "user": "u1", "session": "s1", "locked": false, "locked_remaining_minutes": 0, "fail_count": 2, "now_minutes": 0}
{"result": "wrong_password", "user": "u1", "session": "s1", "locked": false, "locked_remaining_minutes": 0, "fail_count": 3, "now_minutes": 0}
{"result": "wrong_password", "user": "u1", "session": "s1", "locked": false, "locked_remaining_minutes": 0, "fail_count": 4, "now_minutes": 0}
{"user": "u1", "session": "s2", "locked": false, "locked_remaining_minutes": 0, "fail_count": 0, "now_minutes": 0}
{"result": "wrong_password", "user": "u1", "session": "s2", "locked": false, "locked_remaining_minutes": 0, "fail_count": 1, "now_minutes": 0}
{"user": "u1", "session": "s1", "locked": false, "locked_remaining_minutes": 0, "fail_count": 4, "now_minutes": 0}
```
