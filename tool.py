import streamlit as st
import re

def parse_dx_result(log: str):
    rolls = re.findall(r"\[(.*?)\]", log)
    parsed_rolls = [list(map(int, r.split(','))) for r in rolls]
    bonus_match = re.search(r"\+(\d+)\s*＞", log)
    bonus = int(bonus_match.group(1)) if bonus_match else 0
    crit_match = re.search(r"DX(\d+)", log)
    critical_value = int(crit_match.group(1)) if crit_match else 10
    return parsed_rolls, bonus, critical_value

def apply_shihai(rolls, bonus, critical_value, absolute_domination_level=0):
    max_replace = absolute_domination_level + 1
    for roll_index, roll in enumerate(rolls):
        crits = [r for r in roll if r >= critical_value]
        if len(crits) <= max_replace:
            modified = roll[:]
            for c in crits:
                idx = modified.index(c)
                modified[idx] = 1
            used = len(crits)
            if used < max_replace:
                non_crits_sorted = sorted([r for r in modified if r < critical_value], reverse=True)
                for nc in non_crits_sorted[:max_replace-used]:
                    idx = modified.index(nc)
                    modified[idx] = 1
            roll_value = max(modified)
            total = 10 * roll_index + roll_value + bonus
            return total
    return sum([10 for _ in rolls[:-1]]) + max(rolls[-1]) + bonus

# --- Streamlit UI ---
st.title("ダブルクロス3rd 支配の領域計算ツール")

log = st.text_area("判定ログを入力してください  (例：(4DX7+5) ＞ 10[1,2,3,7]+10[7]+6[6]+5 ＞ 31) ")
level = st.number_input("絶対支配Lv", min_value=0, step=1, value=0)

if st.button("計算開始"):
    if log.strip():
        rolls, bonus, critical_value = parse_dx_result(log)
        result = apply_shihai(rolls, bonus, critical_value, absolute_domination_level=level)
        st.success(f"最小達成値: {result}")
    else:

        st.warning("判定ログを入力してください。")
