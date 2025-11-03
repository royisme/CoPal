# Context7 使用指引 - 计划阶段

## 工具说明

Context7 是一个上下文文档查询工具，在计划阶段帮助您设计技术方案和制定实施步骤。

## 计划阶段使用建议

在计划阶段，使用 Context7 来：

1. **确认 API 和接口**：
   - 查询将要使用的 API 的签名和参数
   - 了解接口的输入输出格式
   - 确认 API 的版本兼容性

2. **设计技术方案**：
   - 查找推荐的设计模式和架构
   - 了解常见的实现方式和最佳实践
   - 评估不同技术选型的优劣

3. **识别依赖和约束**：
   - 列出需要的第三方库和版本要求
   - 确认环境依赖（Python 版本、Node.js 版本等）
   - 识别潜在的兼容性问题

4. **制定实施步骤**：
   - 基于文档，将任务拆分为具体的实施步骤
   - 为每个步骤标注相关的 API 和文档链接
   - 预估每个步骤的复杂度和风险

## 示例查询

```
# 查询特定库的安装和配置方法
context7 query "FastAPI installation and setup"

# 查询 API 的详细用法
context7 query "pandas DataFrame merge method"

# 查询最佳实践
context7 query "React hooks best practices"
```

## 交付要求

在计划文档（`.copal/artifacts/plan.md`）中：
- 列出将要使用的主要 API 和方法
- 标注 API 的文档链接或版本号
- 说明选择特定技术方案的理由
- 记录任何需要特别注意的兼容性问题
