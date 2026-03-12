```

███╗   ██╗        ███╗   ███╗██████╗ ██╗   ██╗ █████╗ ██████╗ ██╗       ██████╗██╗     ██╗
████╗  ██║        ████╗ ████║╚════██╗██║   ██║██╔══██╗██╔══██╗██║      ██╔════╝██║     ██║
██╔██╗ ██║        ██╔████╔██║ █████╔╝██║   ██║╚█████╔╝██║  ██║██║█████╗██║     ██║     ██║
██║╚██╗██║        ██║╚██╔╝██║ ╚═══██╗██║   ██║██╔══██╗██║  ██║██║╚════╝██║     ██║     ██║
██║ ╚████║███████╗██║ ╚═╝ ██║██████╔╝╚██████╔╝╚█████╔╝██████╔╝███████╗ ╚██████╗███████╗██║
╚═╝  ╚═══╝╚══════╝╚═╝     ╚═╝╚═════╝  ╚═════╝  ╚════╝ ╚═════╝ ╚══════╝  ╚═════╝╚══════╝╚═╝
                                                                                          
```
---
[![img](https://img.shields.io/github/stars/nilaoda/N_m3u8DL-CLI?label=%E7%82%B9%E8%B5%9E)](https://github.com/nilaoda/N_m3u8DL-CLI)  [![img](https://img.shields.io/github/last-commit/nilaoda/N_m3u8DL-CLI?label=%E6%9C%80%E8%BF%91%E6%8F%90%E4%BA%A4)](https://github.com/nilaoda/N_m3u8DL-CLI)  [![img](https://img.shields.io/github/release/nilaoda/N_m3u8DL-CLI?label=%E6%9C%80%E6%96%B0%E7%89%88%E6%9C%AC)](https://github.com/nilaoda/N_m3u8DL-CLI/releases)  [![img](https://img.shields.io/github/license/nilaoda/N_m3u8DL-CLI?label=%E8%AE%B8%E5%8F%AF%E8%AF%81)](https://github.com/nilaoda/N_m3u8DL-CLI)  [![img](https://img.shields.io/badge/URL-%E7%94%A8%E6%88%B7%E6%96%87%E6%A1%A3-blue)](https://nilaoda.github.io/N_m3u8DL-CLI/)


# [ENGLISH VERSION](https://github.com/nilaoda/N_m3u8DL-CLI/blob/master/README_ENG.md)

# 下载使用
* 发行版: https://github.com/nilaoda/N_m3u8DL-CLI/releases
* 自动构建版`(供测试)`: https://github.com/nilaoda/N_m3u8DL-CLI/actions
 
# 关于开源
本项目已于2019年10月9日开源，采用MIT许可证，各取所需。

# 关于跨平台
* N_m3u8DL-CLI `(本项目)`: 基于 .NET Framework, 不具备跨平台能力. 目前已进入维护阶段.

* [N_m3u8DL-RE](https://github.com/nilaoda/N_m3u8DL-RE) : 抛弃历史包袱从零做起, 支持Win/Linux/Mac, 更丰富的功能会在这里出现 ...

# N_m3u8DL-CLI
一个**简单易用的**m3u8下载器，下载地址：https://github.com/nilaoda/N_m3u8DL-CLI/releases  

支持下载m3u8链接或文件为`mp4`或`ts`格式，并提供丰富的命令行选项。
  * **不支持**优酷视频解密
  * **不支持**气球云视频解密
  * 支持`AES-128-CBC`加密自动解密
  * 支持多线程下载
  * 支持下载限速
  * 支持断点续传
  * 支持`Master List`
  * 支持直播流录制(`BETA`)
  * 支持自定义`HTTP Headers`
  * 支持自动合并 (二进制合并或使用ffmpeg合并)
  * 支持选择下载`m3u8`中的指定时间段/分片内容
  * 支持下载路径为网络驱动器的情况
  * 支持下载外挂字幕轨道、音频轨道
  * 支持仅合并为音频
  * 支持设置特定http代理
  * 支持自动使用系统代理（默认行为, 可禁止）
  * 支持m3u8dl链接协议（通过web链接调用本机客户端）
  * 提供SimpleG简易的`GUI`生成常用参数



![运行截图](https://nilaoda.github.io/N_m3u8DL-CLI/source/images/%E7%9B%B4%E6%8E%A5%E4%BD%BF%E7%94%A8.gif)  


# 网页标题自动命名下载器（附加脚本）
如果你希望“输入网页 URL → 自动抓取 m3u8 → 用网页标题命名视频文件”，可以直接使用仓库根目录的 `m3u8_web_downloader.py`。

```bash
python3 m3u8_web_downloader.py "https://example.com/video-page" --output-dir ./downloads
```

常见参数：

```bash
# 仅列出页面里识别出的 m3u8 链接
python3 m3u8_web_downloader.py "https://example.com/video-page" --list-only

# 多条 m3u8 时选择第2条（下标从0开始）
python3 m3u8_web_downloader.py "https://example.com/video-page" --index 1

# 页面提取失败时手动指定 m3u8，并指定输出名
python3 m3u8_web_downloader.py "https://example.com/video-page" --m3u8 "https://cdn.example.com/a.m3u8" --output-name "我的视频"

# 携带 Referer / Cookie
python3 m3u8_web_downloader.py "https://example.com/video-page" --referer "https://example.com" --cookie "token=xxx"
```

> 依赖：系统需安装 `ffmpeg`（或通过 `--ffmpeg` 指定路径）。


#### 常见失败原因（下载不了）
1. **未安装 ffmpeg**（最常见）
   - 安装 ffmpeg 并加入 PATH；或启动时加 `--ffmpeg "D:\tools\ffmpeg\bin\ffmpeg.exe"`。
   - 现在脚本也会自动查找“程序同目录”的 `ffmpeg.exe`。
2. **站点需要请求头**
   - 补充 `--referer` 和 `--cookie` 再试。
3. **页面里没有直接暴露 m3u8**
   - 先用 `--list-only` 看是否提取到链接；提取不到时用 `--m3u8` 手动指定。


### GUI 版本（桌面程序）
如果你更习惯点按钮操作，可使用 `m3u8_web_downloader_gui.py`：
- 输入网页 URL
- 点击“解析网页”自动识别 m3u8
- 选择链接后点击“下载选中链接”

```bash
python3 m3u8_web_downloader_gui.py
```

#### 打包 GUI 为 EXE（Windows）
```bat
build_m3u8_web_downloader_gui_exe.bat
```

输出文件：`dist\m3u8_web_downloader_gui.exe`

### 打包成 EXE（Windows）
仓库根目录已提供 `build_m3u8_web_downloader_exe.bat`，双击或在 CMD 执行即可：

```bat
build_m3u8_web_downloader_exe.bat
```

打包成功后输出文件在：`dist\m3u8_web_downloader.exe`

# 命令行选项
```
N_m3u8DL-CLI

USAGE:

  N_m3u8DL-CLI <URL|JSON|FILE> [OPTIONS]

OPTIONS:

  --workDir                  设定程序工作目录
  --saveName                 设定存储文件名(不包括后缀)
  --baseUrl                  设定Baseurl
  --headers                  设定请求头，格式 key:value 使用|分割不同的key&value
  --maxThreads               (Default: 32) 设定程序的最大线程数
  --minThreads               (Default: 16) 设定程序的最小线程数
  --retryCount               (Default: 15) 设定程序的重试次数
  --timeOut                  (Default: 10) 设定程序网络请求的超时时间(单位为秒)
  --muxSetJson               使用外部json文件定义混流选项
  --useKeyFile               使用外部16字节文件定义AES-128解密KEY
  --useKeyBase64             使用Base64字符串定义AES-128解密KEY
  --useKeyIV                 使用HEX字符串定义AES-128解密IV
  --downloadRange            仅下载视频的一部分分片或长度
  --liveRecDur               直播录制时，达到此长度自动退出软件(HH:MM:SS)
  --stopSpeed                当速度低于此值时，重试(单位为KB/s)
  --maxSpeed                 设置下载速度上限(单位为KB/s)
  --proxyAddress             设置HTTP/SOCKS5代理, 如 http://127.0.0.1:8080
  --enableDelAfterDone       开启下载后删除临时文件夹的功能
  --enableMuxFastStart       开启混流mp4的FastStart特性
  --enableBinaryMerge        开启二进制合并分片
  --enableParseOnly          开启仅解析模式(程序只进行到meta.json)
  --enableAudioOnly          合并时仅封装音频轨道
  --disableDateInfo          关闭混流中的日期写入
  --disableIntegrityCheck    不检测分片数量是否完整
  --noMerge                  禁用自动合并
  --noProxy                  不自动使用系统代理
  --registerUrlProtocol      注册m3u8dl链接协议
  --unregisterUrlProtocol    取消注册m3u8dl链接协议
  --enableChaCha20           enableChaCha20
  --chaCha20KeyBase64        ChaCha20KeyBase64
  --chaCha20NonceBase64      ChaCha20NonceBase64
  --help                     Display this help screen.
  --version                  Display version information.
```

# 关于`m3u8dl://`协议
新增命令行参数：
```
--registerUrlProtocol          注册m3u8dl链接协议
--unregisterUrlProtocol     取消注册m3u8dl链接协议
```

URI格式：
```
m3u8dl://<base64编码的客户端命令行文本>
```

URI示例：
```
m3u8dl://Imh0dHBzOi8vZXhhbXBsZS5jb20vYWJjLm0zdTgiIC0td29ya0RpciAiJVVTRVJQUk9GSUxFJVxEb3dubG9hZHNcbTN1OGRsIiAtLXNhdmVOYW1lICJhYmMiIC0tZW5hYmxlRGVsQWZ0ZXJEb25lIC0tZGlzYWJsZURhdGVJbmZvIC0tbm9Qcm94eQ==
```

URI解码结果：
```
"https://example.com/abc.m3u8" --workDir "%USERPROFILE%\Downloads\m3u8dl" --saveName "abc" --enableDelAfterDone --disableDateInfo --noProxy
```

# 用户文档
https://nilaoda.github.io/N_m3u8DL-CLI/

# 聊聊
https://discord.gg/SSGwKrjC44

# 赞赏
![Wow](https://nilaoda.github.io/N_m3u8DL-CLI/source/images/alipay.png)
