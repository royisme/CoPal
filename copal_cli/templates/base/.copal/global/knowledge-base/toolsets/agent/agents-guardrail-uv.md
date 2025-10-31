---
id: agents-guardrail-uv
origin: copal
type: guardrail
owner: copal-team
enforcement: optional
updated: 2025-10-31
---

# UV Guardrail 脚本（示例）

## 目标

演示如何在执行终端命令前拦截裸 `python`、`pip` 等敏感调用，并给出 `uv run` / `uv pip` 等安全替代。

## 调用方式

```bash
uv run python .copal/global/knowledge-base/toolsets/agent/scripts/guardrails/check_shell.py --command "python manage.py"
```

- `--command`：待校验的单条命令；
- `--snapshot`：输出最近的违规记录（保存在 `logs/guardrail-history.jsonl`）。

## 输出示例

```
[违规] detected-python: python manage.py
[建议] 使用: uv run python manage.py
```

## 扩展建议

- 可根据项目使用的语言或命令调整匹配规则；
- 需要钩进 CLI 时，可在 shell profile 或任务脚本中调用；
- 若项目已有成熟的守卫系统，可忽略此示例。
