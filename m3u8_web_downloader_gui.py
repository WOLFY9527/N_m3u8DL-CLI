#!/usr/bin/env python3
"""简单 GUI：输入网页 URL，自动提取 m3u8 并下载为视频。"""

from __future__ import annotations

import html
import re
import shutil
import subprocess
import sys
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen


def fetch_text(url: str, headers: dict[str, str], timeout: int = 15) -> str:
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


def extract_m3u8_urls(page_url: str, html_text: str) -> list[str]:
    normalized = html_text.replace("\\/", "/")
    absolute_pattern = r'((?:https?:)?//[^"\'\s<>]+?\.m3u8(?:\?[^"\'\s<>]*)?)'
    relative_pattern = r'((?:\./|\.\./|/(?!/))[^"\'\s<>]+?\.m3u8(?:\?[^"\'\s<>]*)?)'

    found: list[str] = []
    for raw in re.findall(absolute_pattern, normalized, re.IGNORECASE):
        if raw.startswith("//"):
            found.append(f"{urlparse(page_url).scheme}:{raw}")
        else:
            found.append(raw)

    scrubbed = re.sub(absolute_pattern, " ", normalized, flags=re.IGNORECASE)
    for raw in re.findall(relative_pattern, scrubbed, re.IGNORECASE):
        found.append(urljoin(page_url, raw))

    unique: list[str] = []
    seen = set()
    for item in found:
        if item not in seen:
            seen.add(item)
            unique.append(item)
    return unique


def resolve_ffmpeg(configured: str) -> str:
    if configured and configured != "ffmpeg":
        return configured
    if shutil.which("ffmpeg"):
        return "ffmpeg"

    exe_dir = Path(sys.executable).resolve().parent
    script_dir = Path(__file__).resolve().parent
    for base in {exe_dir, script_dir}:
        for candidate in [base / "ffmpeg.exe", base / "ffmpeg"]:
            if candidate.exists() and candidate.is_file():
                return str(candidate)

    return configured or "ffmpeg"


def build_ffmpeg_cmd(
    ffmpeg_path: str,
    m3u8_url: str,
    output_file: Path,
    user_agent: str,
    referer: str,
    cookie: str,
) -> list[str]:
    cmd = [ffmpeg_path, "-y"]
    if user_agent:
        cmd.extend(["-user_agent", user_agent])

    headers = []
    if referer:
        headers.append(f"Referer: {referer}")
    if cookie:
        headers.append(f"Cookie: {cookie}")
    if headers:
        cmd.extend(["-headers", "\r\n".join(headers) + "\r\n"])

    cmd.extend(["-i", m3u8_url, "-c", "copy", str(output_file)])
    return cmd


class App:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("M3U8 网页下载器 GUI")
        self.root.geometry("860x600")

        self.default_ua = (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/125.0.0.0 Safari/537.36"
        )
        self.downloading = False

        self.url_var = tk.StringVar()
        self.output_dir_var = tk.StringVar(value=str(Path.cwd()))
        self.output_name_var = tk.StringVar()
        self.referer_var = tk.StringVar()
        self.cookie_var = tk.StringVar()
        self.ua_var = tk.StringVar(value=self.default_ua)
        self.ffmpeg_var = tk.StringVar(value="ffmpeg")

        self._build_ui()

    def _build_ui(self) -> None:
        frame = ttk.Frame(self.root, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)

        def row_label(text: str, r: int) -> None:
            ttk.Label(frame, text=text).grid(row=r, column=0, sticky="w", pady=4)

        row_label("网页 URL", 0)
        ttk.Entry(frame, textvariable=self.url_var, width=95).grid(row=0, column=1, sticky="ew", padx=5)

        row_label("输出目录", 1)
        ttk.Entry(frame, textvariable=self.output_dir_var, width=80).grid(row=1, column=1, sticky="ew", padx=5)
        ttk.Button(frame, text="浏览", command=self.choose_dir).grid(row=1, column=2)

        row_label("输出文件名（可留空）", 2)
        ttk.Entry(frame, textvariable=self.output_name_var, width=95).grid(row=2, column=1, sticky="ew", padx=5)

        row_label("Referer（可选）", 3)
        ttk.Entry(frame, textvariable=self.referer_var, width=95).grid(row=3, column=1, sticky="ew", padx=5)

        row_label("Cookie（可选）", 4)
        ttk.Entry(frame, textvariable=self.cookie_var, width=95).grid(row=4, column=1, sticky="ew", padx=5)

        row_label("User-Agent", 5)
        ttk.Entry(frame, textvariable=self.ua_var, width=95).grid(row=5, column=1, sticky="ew", padx=5)

        row_label("ffmpeg 路径", 6)
        ttk.Entry(frame, textvariable=self.ffmpeg_var, width=80).grid(row=6, column=1, sticky="ew", padx=5)
        ttk.Button(frame, text="选择", command=self.choose_ffmpeg).grid(row=6, column=2)

        row_label("识别到的 m3u8", 7)
        self.listbox = tk.Listbox(frame, height=8)
        self.listbox.grid(row=7, column=1, sticky="nsew", padx=5)

        btns = ttk.Frame(frame)
        btns.grid(row=8, column=1, sticky="w", pady=8)
        ttk.Button(btns, text="1) 解析网页", command=self.parse_page).pack(side=tk.LEFT, padx=4)
        self.download_btn = ttk.Button(btns, text="2) 下载选中链接", command=self.download_selected)
        self.download_btn.pack(side=tk.LEFT, padx=4)

        row_label("日志", 9)
        self.log = tk.Text(frame, height=14)
        self.log.grid(row=9, column=1, columnspan=2, sticky="nsew", padx=5)

        frame.columnconfigure(1, weight=1)
        frame.rowconfigure(7, weight=1)
        frame.rowconfigure(9, weight=1)

    def choose_dir(self) -> None:
        selected = filedialog.askdirectory()
        if selected:
            self.output_dir_var.set(selected)

    def choose_ffmpeg(self) -> None:
        selected = filedialog.askopenfilename(title="选择 ffmpeg 可执行文件")
        if selected:
            self.ffmpeg_var.set(selected)

    def write_log(self, text: str) -> None:
        self.log.insert(tk.END, text + "\n")
        self.log.see(tk.END)

    def parse_page(self) -> None:
        url = self.url_var.get().strip()
        if not url:
            messagebox.showwarning("提示", "请先输入网页 URL")
            return

        headers = {
            "User-Agent": self.ua_var.get().strip() or self.default_ua,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        }
        if self.referer_var.get().strip():
            headers["Referer"] = self.referer_var.get().strip()
        if self.cookie_var.get().strip():
            headers["Cookie"] = self.cookie_var.get().strip()

        try:
            html_text = fetch_text(url, headers)
        except (HTTPError, URLError, TimeoutError) as exc:
            messagebox.showerror("错误", f"获取网页失败：{exc}")
            return

        title = extract_title(html_text)
        if not self.output_name_var.get().strip():
            self.output_name_var.set(sanitize_filename(title))

        links = extract_m3u8_urls(url, html_text)
        self.listbox.delete(0, tk.END)
        for link in links:
            self.listbox.insert(tk.END, link)

        self.write_log(f"[INFO] 网页标题: {title}")
        self.write_log(f"[INFO] 识别到 {len(links)} 条 m3u8")

        if not links:
            messagebox.showwarning("提示", "未识别到 m3u8 链接，可手动粘贴到页面源码里再试。")

    def download_selected(self) -> None:
        if self.downloading:
            messagebox.showinfo("提示", "正在下载，请稍候")
            return

        selected = self.listbox.curselection()
        if not selected:
            messagebox.showwarning("提示", "请先在列表中选择一个 m3u8 链接")
            return

        m3u8_url = self.listbox.get(selected[0])
        output_dir = Path(self.output_dir_var.get().strip() or ".").expanduser().resolve()
        output_dir.mkdir(parents=True, exist_ok=True)
        base_name = sanitize_filename(self.output_name_var.get().strip() or "video")
        output_file = output_dir / f"{base_name}.mp4"

        ffmpeg_path = resolve_ffmpeg(self.ffmpeg_var.get().strip() or "ffmpeg")
        cmd = build_ffmpeg_cmd(
            ffmpeg_path,
            m3u8_url,
            output_file,
            self.ua_var.get().strip() or self.default_ua,
            self.referer_var.get().strip(),
            self.cookie_var.get().strip(),
        )

        self.write_log(f"[INFO] 输出: {output_file}")
        self.write_log("[INFO] 命令: " + " ".join(cmd))

        self.downloading = True
        self.download_btn.configure(state=tk.DISABLED)

        def worker() -> None:
            try:
                result = subprocess.run(cmd, check=False)
                if result.returncode == 0:
                    self.root.after(0, lambda: self.write_log("[DONE] 下载完成"))
                    self.root.after(0, lambda: messagebox.showinfo("完成", f"下载完成：\n{output_file}"))
                else:
                    self.root.after(0, lambda: self.write_log(f"[ERROR] ffmpeg 退出码: {result.returncode}"))
                    self.root.after(0, lambda: messagebox.showerror("失败", f"ffmpeg 退出码: {result.returncode}"))
            except FileNotFoundError:
                msg = (
                    "未找到 ffmpeg。请安装并加入 PATH，\n"
                    "或在界面中指定 ffmpeg.exe 路径，\n"
                    "或将 ffmpeg.exe 放到本程序同目录。"
                )
                self.root.after(0, lambda: self.write_log("[ERROR] " + msg.replace("\n", " ")))
                self.root.after(0, lambda: messagebox.showerror("错误", msg))
            finally:
                self.downloading = False
                self.root.after(0, lambda: self.download_btn.configure(state=tk.NORMAL))

        threading.Thread(target=worker, daemon=True).start()


def main() -> int:
    root = tk.Tk()
    App(root)
    root.mainloop()
    return 0


if __name__ == "__main__":
    sys.exit(main())
