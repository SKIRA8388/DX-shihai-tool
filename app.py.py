import tkinter as tk
from tkinter import ttk
import re

def parse_dx_result(log: str):
    """
    判定ログを解析して、各ロールの出目リストと補正値を返す
    """
    # 出目部分を抽出
    rolls = re.findall(r"\[(.*?)\]", log)
    parsed_rolls = [list(map(int, r.split(','))) for r in rolls]

    # 補正値を抽出
    bonus_match = re.search(r"\+(\d+)\s*＞", log)
    bonus = int(bonus_match.group(1)) if bonus_match else 0

    # クリティカル値を抽出
    crit_match = re.search(r"DX(\d+)", log)
    critical_value = int(crit_match.group(1)) if crit_match else 10

    return parsed_rolls, bonus, critical_value


def apply_shihai(rolls, bonus, critical_value, absolute_domination_level=0):
    """
    支配の領域／絶対支配を適用して最小達成値を返す
    """
    # Lv+1個まで1にできる
    max_replace = absolute_domination_level + 1

    # 左から順にロールを確認
    for roll_index, roll in enumerate(rolls):
        crits = [r for r in roll if r >= critical_value]
        if len(crits) <= max_replace:
            # このロールでクリティカルを止められる
            modified = roll[:]
            # まずクリティカルを全部1に
            for c in crits:
                idx = modified.index(c)
                modified[idx] = 1
            used = len(crits)
            # 残り枠で最大値を下げる
            if used < max_replace:
                non_crits_sorted = sorted([r for r in modified if r < critical_value], reverse=True)
                for nc in non_crits_sorted[:max_replace-used]:
                    idx = modified.index(nc)
                    modified[idx] = 1
            # このロールの最大値が達成値
            roll_value = max(modified)
            # 直前までのロールはクリティカルが残っているので達成値10扱い
            total = 10 * roll_index + roll_value + bonus
            return total

    # どこでも止められない場合は通常通り
    return sum([10 for _ in rolls[:-1]]) + max(rolls[-1]) + bonus


def calculate():
    log = log_entry.get("1.0", tk.END).strip()
    try:
        level = int(level_entry.get())
    except ValueError:
        result_var.set("絶対支配Lvは整数で入力してください。")
        return

    if not log:
        result_var.set("判定ログを入力してください。")
        return

    rolls, bonus, critical_value = parse_dx_result(log)
    result = apply_shihai(rolls, bonus, critical_value, absolute_domination_level=level)
    result_var.set(f"最小達成値: {result}")


# --- GUI構築 ---
root = tk.Tk()
root.title("ダブルクロス3rd 支配の領域計算ツール")

# 判定ログ入力欄
ttk.Label(root, text="判定ログを入力:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
log_entry = tk.Text(root, width=80, height=6)
log_entry.grid(row=1, column=0, columnspan=2, padx=5, pady=5)

# 絶対支配レベル入力欄
ttk.Label(root, text="絶対支配Lv:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
level_entry = ttk.Entry(root, width=5)
level_entry.insert(0, "0")
level_entry.grid(row=2, column=1, sticky="w", padx=5, pady=5)

# 計算ボタン
calc_button = ttk.Button(root, text="計算開始", command=calculate)
calc_button.grid(row=3, column=0, columnspan=2, pady=10)

# 結果表示欄
result_var = tk.StringVar()
result_label = ttk.Label(root, textvariable=result_var, foreground="blue", font=("Arial", 12))
result_label.grid(row=4, column=0, columnspan=2, padx=5, pady=10)

root.mainloop()