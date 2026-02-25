<div align=center>
	<h1>漫画包翻译器</h1>
	<p><a href="https://hub.oomol.com/package/manga-zip-translator?open=true" target="_blank"><img src="https://static.oomol.com/assets/button.svg" alt="在 OOMOL Studio 中打开" /></a></p>
</div>

## 概述

漫画包翻译器是一个自动化工具，可以将漫画压缩包（ZIP 文件）中的文字翻译成 26 种目标语言。它使用 OCR 技术检测漫画图像中的文字，进行翻译，并返回包含翻译内容的新 ZIP 文件。

## 功能特性

### 支持的语言
- **亚洲语言**：简体中文、繁体中文、日语、韩语、泰语、印尼语、菲律宾语
- **欧洲语言**：英语、法语、德语、意大利语、西班牙语、葡萄牙语、荷兰语、捷克语、波兰语、匈牙利语、罗马尼亚语、俄语、乌克兰语、克罗地亚语、塞尔维亚语、黑山语
- **其他语言**：阿拉伯语、土耳其语、越南语

### 主要组件

#### 1. ZIP 翻译子流程
协调整个翻译过程的主工作流程：
- 验证 ZIP 文件格式
- 上传文件到云存储
- 提交翻译任务
- 轮询等待完成
- 返回翻译后的 ZIP 下载链接

**输入参数**：
- `file`：漫画 ZIP 压缩包的本地文件路径（必填）
- `target_lang`：目标语言代码，如 CHS 表示简体中文（必填）

**输出结果**：
- `status`：翻译状态（pending/processing/completed/failed）
- `result_zip_url`：翻译后 ZIP 文件的下载链接

#### 2. 漫画包翻译任务
与 OOMOL Fusion API 交互的核心翻译任务：
- 提交 ZIP URL 进行翻译
- 轮询任务完成状态
- 返回翻译结果

**输入参数**：
- `zip_url`：漫画 ZIP 文件的公开 URL（必填）
- `target_lang`：目标语言代码（必填）
- `wait_timeout`：最大等待时间，单位秒（默认：600）
- `poll_interval`：状态检查间隔，单位秒（默认：5）

**输出结果**：
- `task_id`：唯一任务标识符
- `status`：任务状态
- `result_zip_url`：翻译后 ZIP 下载链接
- `total_pages`：检测到的总页数
- `translated_pages`：已翻译页数

#### 3. ZIP 格式检查任务
通过检查魔数签名验证文件是否为有效的 ZIP 压缩包。

**输入参数**：
- `url`：本地文件路径或远程 URL（必填）

**输出结果**：
- `is_zip`：布尔值，表示是否为有效的 ZIP 格式
- `file_size`：文件大小（字节）
- `file_zip_path`：本地 ZIP 路径（如果是本地文件）
- `file_zip_url`：远程 ZIP URL（如果是网络 URL）

## 使用方法

1. 打开 ZIP 翻译子流程
2. 使用文件选择器选择漫画 ZIP 文件
3. 从下拉菜单中选择目标语言
4. 运行工作流程
5. 从结果 URL 下载翻译后的 ZIP 文件

## 技术说明

- 翻译由 OOMOL Fusion API 执行
- 支持本地文件和远程 URL
- 包含网络故障的重试逻辑
- 翻译过程中可追踪进度
