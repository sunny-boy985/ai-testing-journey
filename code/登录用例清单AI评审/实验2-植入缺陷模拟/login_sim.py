#!/usr/bin/env python3
"""电商 App 登录命令行模拟器。"""

import argparse
import json
from pathlib import Path


STATE_FILE = Path(__file__).with_name(".login_sim_state.json")
PASSWORDS = {"u1": "123456", "u2": "abcdef"}
LOCK_MINUTES = 30
MAX_FAILURES = 5


def initial_state():
    return {"now_minutes": 0, "failures": {}, "locked_until": {}}


def load_state():
    if not STATE_FILE.exists():
        return initial_state()
    with STATE_FILE.open(encoding="utf-8") as file:
        return json.load(file)


def save_state(state):
    with STATE_FILE.open("w", encoding="utf-8") as file:
        json.dump(state, file, ensure_ascii=False, indent=2)
        file.write("\n")


def refresh_lock(state, user):
    until = state["locked_until"].get(user)
    if until is not None and state["now_minutes"] >= until:
        del state["locked_until"][user]
        state["failures"].pop(user, None)


def remaining_minutes(state, user):
    return max(0, state["locked_until"].get(user, 0) - state["now_minutes"])


def fail_count(state, user, session):
    return state["failures"].get(user, {}).get(session, 0)


def account_status(state, user, session):
    refresh_lock(state, user)
    remaining = remaining_minutes(state, user)
    return {
        "user": user,
        "session": session,
        "locked": remaining > 0,
        "locked_remaining_minutes": remaining,
        "fail_count": fail_count(state, user, session),
        "now_minutes": state["now_minutes"],
    }


def attempt_login(state, user, session, password):
    status = account_status(state, user, session)
    if status["locked"]:
        result = "locked"
    elif PASSWORDS.get(user) == password:
        result = "success"
    else:
        failures = state["failures"].setdefault(user, {})
        failures[session] = failures.get(session, 0) + 1
        if failures[session] >= MAX_FAILURES:
            state["locked_until"][user] = state["now_minutes"] + LOCK_MINUTES
            result = "locked"
        else:
            result = "wrong_password"
    return {"result": result, **account_status(state, user, session)}


def nonnegative_minutes(value):
    try:
        minutes = int(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError("minutes 必须是非负整数") from error
    if minutes < 0:
        raise argparse.ArgumentTypeError("minutes 必须是非负整数")
    return minutes


def main():
    parser = argparse.ArgumentParser(description="电商 App 登录模拟器")
    commands = parser.add_subparsers(dest="command", required=True)

    attempt = commands.add_parser("try", help="尝试登录")
    attempt.add_argument("--session", required=True)
    attempt.add_argument("--user", required=True)
    attempt.add_argument("--pass", dest="password", required=True)

    advance = commands.add_parser("advance", help="快进模拟时间")
    advance.add_argument("--minutes", type=nonnegative_minutes, required=True)

    status = commands.add_parser("status", help="查询状态")
    status.add_argument("--user", required=True)
    status.add_argument("--session", required=True)

    commands.add_parser("reset", help="重置状态和时间")
    args = parser.parse_args()

    state = initial_state() if args.command == "reset" else load_state()
    if args.command == "reset":
        output = {"result": "reset", "now_minutes": 0}
    elif args.command == "advance":
        state["now_minutes"] += args.minutes
        for user in list(state["locked_until"]):
            refresh_lock(state, user)
        output = {"result": "advanced", "now_minutes": state["now_minutes"]}
    elif args.command == "status":
        output = account_status(state, args.user, args.session)
    else:
        output = attempt_login(state, args.user, args.session, args.password)

    save_state(state)
    print(json.dumps(output, ensure_ascii=False))


if __name__ == "__main__":
    main()
