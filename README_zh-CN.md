<div align=center>
	<h1>漫画包翻译</h1>
	<p><a href="https://hub.oomol.com/package/manga-zip-translator?open=true" target="_blank"><img src="https://static.oomol.com/assets/button.svg" alt="在 OOMOL Studio 中打开" /></a></p>
</div>

## 项目概述

自动将漫画 ZIP 压缩包翻译为 26 种目标语言，支持 OCR 技术和可选上色功能。本服务会使用 oomol 内部的 token 进行扣费，扣费主题为 `manga-zip-translate`。

> 翻译过程会使用少量 AI 进行翻译，并记录相关费用。

## 功能块能力

### 本地 Zip 文件翻译
翻译本地漫画 ZIP 文件。上传文件、验证格式、提交翻译，返回下载链接。适合 OOMOL Studio 使用。

### 网络 Zip 网址翻译器
翻译 URL 中的漫画 ZIP。验证 URL、提交翻译，返回下载链接。适合网页或 API 集成使用。

### 检查 Zip 格式
通过检查魔术数字签名验证本地文件或远程 URL 是否为有效的 ZIP 压缩包。

## 功能块组合建议

- 在 OOMOL Studio 中处理本地文件时使用**本地 Zip 文件翻译**
- 集成网页应用或 API 时使用**网络 Zip 网址翻译器**
- 翻译前使用**检查 Zip 格式**验证文件有效性

## 基本用法

1. 根据输入源选择翻译功能块（本地文件或 URL）
2. 从 26 种支持语言中选择目标语言
3. 如需为黑白漫画上色，启用上色选项
4. 运行工作流并下载翻译后的 ZIP

## 示例

**本地文件翻译：**
- 输入：使用文件选择器选择漫画 ZIP 文件
- 目标语言：CHS（简体中文）
- 输出：翻译后 ZIP 的下载链接

**URL 翻译：**
- 输入：漫画 ZIP 文件的公开 URL
- 目标语言：ENG（英语）
- 输出：翻译后 ZIP 的下载链接
