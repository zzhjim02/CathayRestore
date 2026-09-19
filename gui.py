# -*- coding: utf-8 -*-
"""
CathayRestore · TXT 文本层写回工具 —— 图形界面（独立版 v1.0）

原为 CathayOCR v1.2.4 Pro 的附属工具「TXT写回工具」（依赖 CathayOCR 目录下的
portapython 才能启动）。本版本已完全独立：自带启动脚本 + 依赖探测，
只需系统里有一个带 tkinter 的 Python 3。

功能与原工具一致：
  · 递归扫描目录，按 3 条后缀规则配对 TXT 与 PDF
  · 把 TXT 按页码竖排写回 PDF，替换错误的旧文字层
  · 输出 <原名>_fixed.pdf，保留原件；多核并行；可改输出后缀与并行数

界面增强（不改处理行为）：拖入文件夹、行状态着色、双击打开结果、
“不选任何行 = 全部处理”。
"""
import os
import re
import sys
import threading
import tkinter as tk
from concurrent.futures import ThreadPoolExecutor
from tkinter import ttk, filedialog, messagebox

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from restore import PAIR_RULES, app_dir, process_pair, res_dir, scan_pairs

try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    HAS_DND = True
except Exception:
    HAS_DND = False

APP_TITLE = 'CathayRestore  ·  TXT 文本层写回工具  v1.0'
HELP_TEXT = (
    "它做什么\n"
    "  把 OCR 结果 TXT 按页码写回 PDF，替换掉错误/搜不到的旧文字层，\n"
    "  让双层 PDF 重新可搜索、可复制（图像层像素级不动）。\n\n"
    "配对规则（同一目录下，其余后缀一律忽略）\n"
    "  XXX_result.txt      ↔  XXX_layered.pdf          CathayOCR Lite 输出\n"
    "  XXX_PD6AIFOCR.txt   ↔  XXX_PD6AIFOCR_opt.pdf    FOCR 工具输出\n"
    "  XXX_PD6AIFOCR.txt   ↔  XXX_PD6AIFOCR.pdf        无 _opt 变体\n\n"
    "用法\n"
    "  1. 选目录（可把文件夹直接拖进窗口）→ 自动递归扫描所有子目录\n"
    "  2. 需要就改输出后缀（默认 _fixed）和并行数（默认 4，可 1~16）\n"
    "  3. 选若干行 → 开始处理选中项（一行都不选 = 全部处理）\n"
    "  4. 每个 PDF 同目录下生成 XXX_..._fixed.pdf，用 Chrome/Edge 打开即可搜索\n\n"
    "说明\n"
    "  · TXT 里的 ===== 分隔线会被自动过滤；某页无内容则跳过、保留原状\n"
    "  · 原件不会被覆盖（输出另存 _fixed）\n"
    "  · 并行数不要超过 CPU 核数；大文件多时建议降到 2~4"
)


def split_drop_paths(data):
    """解析 tkinterdnd2 的拖放串（含 {带空格路径} 形式）。"""
    out = []
    for m in re.findall(r'\{([^}]*)\}|(\S+)', data or ''):
        p = m[0] or m[1]
        if p:
            out.append(p)
    return out


class App:
    def __init__(self, root):
        self.root = root
        root.title(APP_TITLE)
        root.geometry('980x640')
        root.minsize(820, 520)

        self.pairs = []        # [(txt, pdf, stem)]
        self.running = False
        self.outdir = ''

        # ---------- 目录 ----------
        frm_dir = ttk.Frame(root, padding=(10, 8, 10, 4))
        frm_dir.pack(fill='x')
        ttk.Label(frm_dir, text='目录:').pack(side='left')
        self.dir_var = tk.StringVar()
        ent = ttk.Entry(frm_dir, textvariable=self.dir_var)
        ent.pack(side='left', padx=4, fill='x', expand=True)
        ttk.Button(frm_dir, text='选择目录', command=self.pick_dir).pack(side='left', padx=2)
        ttk.Button(frm_dir, text='扫描配对', command=self.scan).pack(side='left', padx=2)
        ttk.Button(frm_dir, text='说明', command=lambda: messagebox.showinfo('说明', HELP_TEXT)).pack(
            side='left', padx=2)

        self.drop_hint = ttk.Label(
            root,
            text=('（把文件夹或文件直接拖进窗口即可自动扫描）' if HAS_DND
                  else '（未安装 tkinterdnd2，拖放不可用；请用「选择目录」按钮）'),
            foreground=('#555555' if HAS_DND else '#8a2b2b'),
            padding=(12, 0, 10, 4))
        self.drop_hint.pack(fill='x')

        # ---------- 选项 ----------
        frm_opt = ttk.Frame(root, padding=(10, 4))
        frm_opt.pack(fill='x')
        self.opt_suffix = tk.StringVar(value='_fixed')
        ttk.Label(frm_opt, text='输出后缀:').pack(side='left')
        ttk.Entry(frm_opt, textvariable=self.opt_suffix, width=10).pack(side='left', padx=4)
        ttk.Label(frm_opt, text='并行数:').pack(side='left', padx=(14, 2))
        self.workers_var = tk.IntVar(value=min(4, (os.cpu_count() or 4)))
        ttk.Spinbox(frm_opt, from_=1, to=16, textvariable=self.workers_var, width=4).pack(side='left')
        ttk.Label(frm_opt, text='（CPU %d 核）' % (os.cpu_count() or 1),
                  foreground='#777777').pack(side='left', padx=(4, 0))
        ttk.Button(frm_opt, text='全选', command=lambda: self.select_all(True)).pack(side='left', padx=(16, 2))
        ttk.Button(frm_opt, text='全不选', command=lambda: self.select_all(False)).pack(side='left', padx=2)

        # ---------- 列表 ----------
        frm_list = ttk.Frame(root, padding=(10, 4))
        frm_list.pack(fill='both', expand=True)
        self.tree = ttk.Treeview(frm_list, columns=('pdf', 'status'), show='tree headings', height=16)
        self.tree.heading('#0', text='TXT 文件（相对路径）')
        self.tree.heading('pdf', text='PDF 文件')
        self.tree.heading('status', text='状态')
        self.tree.column('#0', width=360, anchor='w')
        self.tree.column('pdf', width=330, anchor='w')
        self.tree.column('status', width=230, anchor='w')
        self.tree.tag_configure('run', background='#fff4cc')     # 处理中
        self.tree.tag_configure('ok', background='#e8f7e8')      # 完成
        self.tree.tag_configure('bad', background='#ffd9d9')     # 失败
        vsb = ttk.Scrollbar(frm_list, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.pack(side='left', fill='both', expand=True)
        vsb.pack(side='right', fill='y')
        self.tree.bind('<Double-1>', self.open_row)

        # ---------- 进度 ----------
        frm_prog = ttk.Frame(root, padding=(10, 4))
        frm_prog.pack(fill='x')
        self.prog = ttk.Progressbar(frm_prog, mode='determinate')
        self.prog.pack(fill='x')
        self.log_var = tk.StringVar(value='就绪：选择目录后点「扫描配对」')
        ttk.Label(frm_prog, textvariable=self.log_var).pack(anchor='w', pady=2)

        # ---------- 按钮 ----------
        frm_btn = ttk.Frame(root, padding=(10, 2, 10, 10))
        frm_btn.pack(fill='x')
        self.btn_run = ttk.Button(frm_btn, text='开始处理选中项', command=self.start)
        self.btn_run.pack(side='left')
        self.btn_open = ttk.Button(frm_btn, text='打开输出目录', command=self.open_outdir,
                                   state='disabled')
        self.btn_open.pack(side='left', padx=4)

        if HAS_DND:
            for w in (root, self.tree, self.drop_hint):
                try:
                    w.drop_target_register(DND_FILES)
                    w.dnd_bind('<<Drop>>', self.on_drop)
                except Exception:
                    pass

    # ---------------- 目录与扫描 ----------------
    def pick_dir(self):
        d = filedialog.askdirectory()
        if d:
            self.dir_var.set(d)
            self.scan()

    def on_drop(self, ev):
        items = [p for p in split_drop_paths(getattr(ev, 'data', '')) if os.path.exists(p)]
        if not items:
            return
        p = items[0]
        d = p if os.path.isdir(p) else os.path.dirname(p)
        self.dir_var.set(d)
        self.scan()

    def scan(self):
        d = self.dir_var.get().strip().strip('"')
        if not d or not os.path.isdir(d):
            messagebox.showerror('错误', '请选择有效目录')
            return
        self.tree.delete(*self.tree.get_children())
        self.pairs = scan_pairs(d)          # 递归扫描（含所有子目录）
        for i, (txt, pdf, stem) in enumerate(self.pairs):
            self.tree.insert('', 'end', iid='p%d' % i,
                             text=os.path.relpath(txt, d),
                             values=(os.path.relpath(pdf, d), '待处理'))
        self.prog.config(maximum=max(1, len(self.pairs)), value=0)
        self.log_var.set('扫描到 %d 对文件（含子目录）' % len(self.pairs))
        self.outdir = d
        if not self.pairs:
            messagebox.showinfo('提示', '未找到可配对的 TXT 与 PDF 文件\n\n'
                                        '（只认 _result / _PD6AIFOCR 这几条后缀规则，'
                                        '点「说明」看详情）')

    def select_all(self, on):
        items = self.tree.get_children()
        if on:
            self.tree.selection_set(items)
        else:
            self.tree.selection_remove(items)

    # ---------------- 处理 ----------------
    def start(self):
        if self.running:
            return
        sel = list(self.tree.selection())
        if not sel:                                  # 一行都没选 = 全部处理（与原工具一致）
            sel = list(self.tree.get_children())
            if not sel:
                messagebox.showinfo('提示', '没有可处理的文件，请先扫描')
                return
            self.log_var.set('未选中任何行 → 处理全部 %d 对' % len(sel))
        suffix = self.opt_suffix.get().strip() or '_fixed'
        try:
            nw = int(self.workers_var.get())
        except Exception:
            nw = 4
        nw = max(1, min(16, nw))
        tasks = []
        for iid in sel:
            idx = int(iid[1:])
            txt, pdf, stem = self.pairs[idx]
            tasks.append((iid, txt, pdf))
        self.running = True
        self.btn_run.config(state='disabled')
        self.btn_open.config(state='disabled')
        self.prog.config(maximum=len(tasks), value=0)
        self.outdir = self.dir_var.get().strip()
        threading.Thread(target=self._worker, args=(tasks, suffix, nw), daemon=True).start()

    def _set(self, iid, status=None, tag=None):
        def do():
            vals = list(self.tree.item(iid, 'values'))
            if status is not None and vals:
                vals[1] = status
            self.tree.item(iid, values=vals, tags=(tag,) if tag else ())
        self.root.after(0, do)

    def _worker(self, tasks, suffix, n_workers):
        total = len(tasks)
        lock = threading.Lock()
        state = {'ok': 0, 'fail': 0, 'done': 0}

        def run_one(item):
            iid, txt, pdf = item
            self._set(iid, '处理中…', 'run')
            try:
                out, n = process_pair(txt, pdf, suffix)
                with lock:
                    state['ok'] += 1
                self._set(iid, '完成 → %s（%d 页）' % (os.path.basename(out), n), 'ok')
            except Exception as e:
                with lock:
                    state['fail'] += 1
                self._set(iid, '失败: %s' % str(e)[:60], 'bad')
            finally:
                with lock:
                    state['done'] += 1
                    d = state['done']
                self.root.after(0, lambda v=d: self.prog.config(value=v))
                self.root.after(0, lambda dd=d, tt=total: self.log_var.set('[%d/%d]' % (dd, tt)))

        with ThreadPoolExecutor(max_workers=n_workers) as ex:
            for _ in ex.map(run_one, tasks):
                pass
        ok, fail = state['ok'], state['fail']
        self.running = False
        self.root.after(0, lambda: self.btn_run.config(state='normal'))
        self.root.after(0, lambda: self.btn_open.config(state='normal'))
        self.root.after(0, lambda: self.log_var.set('完成: 成功 %d，失败 %d（输出后缀 %s）'
                                                    % (ok, fail, suffix)))

    # ---------------- 其它 ----------------
    def open_row(self, ev):
        iid = self.tree.identify_row(ev.y)
        if not iid:
            return
        try:
            txt, pdf, stem = self.pairs[int(iid[1:])]
        except Exception:
            return
        suffix = self.opt_suffix.get().strip() or '_fixed'
        cand = os.path.join(os.path.dirname(pdf), stem + os.path.basename(pdf)[len(stem):-4] + suffix + '.pdf')
        target = cand if os.path.exists(cand) else pdf
        if os.path.exists(target):
            os.startfile(target)

    def open_outdir(self):
        d = self.outdir or self.dir_var.get().strip()
        if d and os.path.isdir(d):
            os.startfile(d)


def main():
    root = TkinterDnD.Tk() if HAS_DND else tk.Tk()
    try:
        root.call('tk', 'scaling', 1.15)
    except Exception:
        pass
    try:
        ico = os.path.join(res_dir(), 'app.ico')
        if os.path.exists(ico):
            root.iconbitmap(ico)
    except Exception:
        pass
    App(root)
    root.mainloop()


def selftest():
    """--selftest：把自检结果写到 app_dir/_selftest.txt（用来验证打包/便携环境是否完好）"""
    import shutil
    import tempfile
    out = []

    def w(k, v):
        out.append('%s = %s' % (k, v))
    w('frozen', getattr(sys, 'frozen', False))
    w('app_dir', app_dir())
    w('res_dir', res_dir())
    try:
        import fitz
        w('fitz', fitz.VersionBind)
    except Exception as e:
        w('fitz', 'FAIL %s' % e)
    w('dnd', HAS_DND)
    # 引擎实测：造一对文件真跑一遍
    d = tempfile.mkdtemp(prefix='crs_')
    try:
        import fitz
        doc = fitz.open()
        pg = doc.new_page(width=595, height=842)
        pg.insert_text((50, 50), 'OLD-WRONG', fontsize=12)
        pdf = os.path.join(d, 't_layered.pdf')
        doc.save(pdf)
        doc.close()
        open(os.path.join(d, 't_result.txt'), 'w', encoding='utf-8').write('第1页\n测试文字\n')
        pairs = scan_pairs(d)
        o, n = process_pair(pairs[0][0], pairs[0][1], '_fixed')
        doc = fitz.open(o)
        txt = doc[0].get_text().strip()
        imgs = len(doc[0].get_images())
        doc.close()
        w('engine', '%d 对处理 %d 页 -> 文本=%r 图像=%d' % (len(pairs), n, txt, imgs))
    except Exception as e:
        w('engine', 'FAIL %s' % e)
    finally:
        shutil.rmtree(d, ignore_errors=True)
    try:
        root = TkinterDnD.Tk() if HAS_DND else tk.Tk()
        root.withdraw()
        App(root)
        w('gui', 'ok')
        w('icon_exists', os.path.exists(os.path.join(res_dir(), 'app.ico')))
        root.destroy()
    except Exception as e:
        w('gui', 'FAIL %s' % e)
    w('result', 'FAIL' if any('FAIL' in x for x in out) else 'OK')
    p = os.path.join(app_dir(), '_selftest.txt')
    try:
        open(p, 'w', encoding='utf-8').write('\n'.join(out) + '\n')
    except Exception:
        p = os.path.join(os.environ.get('TEMP', '.'), '_selftest.txt')
        open(p, 'w', encoding='utf-8').write('\n'.join(out) + '\n')
    return p


if __name__ == '__main__':
    if '--selftest' in sys.argv:
        selftest()
    else:
        main()
