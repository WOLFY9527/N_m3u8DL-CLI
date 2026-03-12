#!/usr/bin/env python3
"""从网页自动提取 m3u8 链接并按网页标题命名下载视频。"""

from __future__ import annotations

import argparse
import html
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Dict, List
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen


def build_headers(args: argparse.Namespace) -> Dict[str, str]:
    headers = {
        "User-Agent": args.user_agent,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    }
    if args.referer:
        headers["Referer"] = args.referer
    if args.cookie:
        headers["Cookie"] = args.cookie
    return headers


def fetch_text(url: str, headers: Dict[str, str], timeout: int) -> str:
    req = Request(url=url, headers=headers)
    with urlopen(req, timeout=timeout) as resp:
        charset = resp.headers.get_content_charset() or "utf-8"
        data = resp.read()
    return data.decode(charset, errors="replace")


def extract_title(html_text: str) -> str:
    match = re.search(r"<title[^>]*>(.*?)</title>", html_text, re.IGNORECASE | re.DOTALL)
    if not match:
        return "video"
    title = html.unescape(match.group(1))
    title = re.sub(r"\s+", " ", title).strip()
    return title or "video"


def sanitize_filename(name: str) -> str:
    name = re.sub(r"[\\/:*?\"<>|]", "_", name)
    name = re.sub(r"\s+", " ", name).strip().rstrip(".")
    return name[:180] or "video"


def extract_m3u8_urls(page_url: str, html_text: str) -> List[str]:
    normalized = html_text.replace("\\/", "/")

    absolute_pattern = r'((?:https?:)?//[^"\'\s<>]+?\.m3u8(?:\?[^"\'\s<>]*)?)'
    relative_pattern = r'((?:\./|\.\./|/(?!/))[^"\'\s<>]+?\.m3u8(?:\?[^"\'\s<>]*)?)'

    found: List[str] = []

    # 先提取绝对链接/协议相对链接，避免相对路径规则重复命中绝对链接中的 /path.m3u8。
    for raw in re.findall(absolute_pattern, normalized, re.IGNORECASE):
        if raw.startswith("//"):
            found.append(f"{urlparse(page_url).scheme}:{raw}")
        else:
            found.append(raw)

    scrubbed = re.sub(absolute_pattern, " ", normalized, flags=re.IGNORECASE)
    for raw in re.findall(relative_pattern, scrubbed, re.IGNORECASE):
        found.append(urljoin(page_url, raw))

    unique: List[str] = []
    seen = set()
    for item in found:
        if item not in seen:
            seen.add(item)
            unique.append(item)
    return unique


def choose_m3u8(args: argparse.Namespace, m3u8_list: List[str]) -> str:
    if args.m3u8:
        return args.m3u8
    if not m3u8_list:
        raise ValueError("在网页中未找到 m3u8 链接，请使用 --m3u8 手动指定。")
    if args.index < 0 or args.index >= len(m3u8_list):
        raise ValueError(f"--index 超出范围，可选 0 ~ {len(m3u8_list) - 1}")
    return m3u8_list[args.index]


def resolve_ffmpeg_path(configured: str) -> str:
    """Resolve ffmpeg executable path with useful fallbacks for packaged EXE usage."""
    # 1) Explicit path or command from user.
    if configured and configured != "ffmpeg":
        return configured

    # 2) PATH lookup.
    if shutil.which("ffmpeg"):
        return "ffmpeg"

    # 3) Same directory as current executable/script (works well for packaged exe + ffmpeg.exe).
    candidates = []
    exe_dir = Path(sys.executable).resolve().parent
    script_dir = Path(__file__).resolve().parent
    for base in {exe_dir, script_dir}:
        candidates.extend([base / "ffmpeg.exe", base / "ffmpeg"])

    for candidate in candidates:
        if candidate.exists() and candidate.is_file():
            return str(candidate)

    return configured or "ffmpeg"


def build_ffmpeg_command(args: argparse.Namespace, m3u8_url: str, output_file: Path) -> List[str]:
    ffmpeg_bin = resolve_ffmpeg_path(args.ffmpeg)
    cmd = [ffmpeg_bin, "-y"]

    if args.user_agent:
        cmd.extend(["-user_agent", args.user_agent])

    headers = []
    if args.referer:
        headers.append(f"Referer: {args.referer}")
    if args.cookie:
        headers.append(f"Cookie: {args.cookie}")
    if headers:
        cmd.extend(["-headers", "\r\n".join(headers) + "\r\n"])

    cmd.extend(["-i", m3u8_url, "-c", "copy", str(output_file)])
    return cmd


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="从网页自动提取 m3u8 地址，并默认使用网页标题作为保存文件名。"
    )
    parser.add_argument("page_url", help="包含 m3u8 视频的网页地址")
    parser.add_argument("--m3u8", help="手动指定 m3u8 地址（跳过网页提取）")
    parser.add_argument("--index", type=int, default=0, help="当找到多个 m3u8 时选择第几个（默认 0）")
    parser.add_argument("--output-dir", default=".", help="输出目录（默认当前目录）")
    parser.add_argument("--output-name", help="输出文件名（不含扩展名，默认网页标题）")
    parser.add_argument("--referer", help="请求头 Referer")
    parser.add_argument("--cookie", help="请求头 Cookie")
    parser.add_argument(
        "--user-agent",
        default=(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/125.0.0.0 Safari/537.36"
        ),
        help="请求头 User-Agent",
    )
    parser.add_argument("--timeout", type=int, default=15, help="网页请求超时秒数（默认 15）")
    parser.add_argument("--ffmpeg", default="ffmpeg", help="ffmpeg 可执行文件路径（默认自动查找 PATH 或程序同目录）")
    parser.add_argument("--list-only", action="store_true", help="仅列出识别出的 m3u8 链接")
    parser.add_argument("--dry-run", action="store_true", help="仅打印将要执行的 ffmpeg 命令")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    headers = build_headers(args)

    try:
        html_text = fetch_text(args.page_url, headers, args.timeout)
    except (HTTPError, URLError, TimeoutError) as exc:
        print(f"[ERROR] 获取网页失败: {exc}", file=sys.stderr)
        return 1

    title = extract_title(html_text)
    m3u8_list = extract_m3u8_urls(args.page_url, html_text)

    print(f"[INFO] 网页标题: {title}")
    if m3u8_list:
        print("[INFO] 识别出的 m3u8 地址:")
        for i, link in enumerate(m3u8_list):
            print(f"  [{i}] {link}")
    else:
        print("[WARN] 网页中暂未识别到 m3u8 地址")

    if args.list_only:
        return 0

    try:
        m3u8_url = choose_m3u8(args, m3u8_list)
    except ValueError as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 1

    base_name = sanitize_filename(args.output_name or title)
    output_dir = Path(args.output_dir).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / f"{base_name}.mp4"

    ffmpeg_cmd = build_ffmpeg_command(args, m3u8_url, output_file)
    print(f"[INFO] 选用 m3u8: {m3u8_url}")
    print(f"[INFO] 输出文件: {output_file}")
    print("[INFO] ffmpeg 命令:")
    print(" ", " ".join(f'"{x}"' if " " in x else x for x in ffmpeg_cmd))

    if args.dry_run:
        return 0

    try:
        completed = subprocess.run(ffmpeg_cmd, check=False)
    except FileNotFoundError:
        print(
            "[ERROR] 未找到 ffmpeg。请执行以下任一方案后重试：\n"
            "  1) 安装 ffmpeg 并加入 PATH；\n"
            "  2) 使用 --ffmpeg 指定 ffmpeg.exe 完整路径；\n"
            "  3) 将 ffmpeg.exe 放到本程序同目录。",
            file=sys.stderr,
        )
        return 1

    if completed.returncode != 0:
        print(f"[ERROR] ffmpeg 退出码: {completed.returncode}", file=sys.stderr)
        return completed.returncode

    print("[DONE] 下载完成")
    return 0


if __name__ == "__main__":
    sys.exit(main())
