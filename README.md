# 数据库

数据库大作业

## Git 使用规范

### 1. 分支管理

- `main` 分支：主分支，用于发布稳定版本，只能从其他分支合并，不能直接在 `main` 分支上开发。
- `front-end` 分支：前端分支，用于开发前端代码。
- `back-end` 分支：后端分支，用于开发后端代码。

对于新功能的开发，需要在 `front-end` 或 `back-end` 分支上重新开一个分支，然后合并到 `front-end` 或 `back-end` 分支上，不要直接在 `front-end` 或 `back-end` 分支上开发。代码合并请尽可能使用 `rebase`。同时，如果一个功能需要多个人开发，请在特定的功能分支上再切出新的分支。

### 2. 提交规范

请按照 Conventional Commits 规范提交代码，具体规范请参考[Conventional Commits](https://www.conventionalcommits.org/zh-hans/v1.0.0/)。VSCode 和 JetBrains 系列 IDE 都有对应的插件可以帮助你规范提交。在插件市场搜索`Conventional Commits`即可找到。

### 3. 代码规范

- 前端：请使用`prettier`格式化代码。
- 后端：请按照`black`规范格式化代码。

**以上规范请尽量遵守，如果有特殊情况，请在提交代码前与团队成员讨论。**
