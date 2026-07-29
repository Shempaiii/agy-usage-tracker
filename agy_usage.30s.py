#!/usr/bin/env python3

# <xbar.title>Agy Usage</xbar.title>
# <xbar.version>v1.1.0</xbar.version>
# <xbar.author>Google Antigravity</xbar.author>
# <xbar.desc>Displays Antigravity CLI quota usage</xbar.desc>
# <xbar.dependencies>python,tmux</xbar.dependencies>

import subprocess
import re
import os
from datetime import datetime, timedelta

VERSION = "v1.1.0"

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
SCRIPT_PATH = os.path.join(SCRIPT_DIR, "get_agy_usage.sh")

def get_menu_color(percent):
    if percent < 50:
        return "white"
    elif percent < 90:
        return "orange"
    else:
        return "red"

def get_dropdown_color(percent):
    if percent < 50:
        return "green"
    elif percent < 90:
        return "orange"
    else:
        return "red"

def generate_bar(percent, total_blocks=20):
    filled = int((percent / 100) * total_blocks)
    empty = total_blocks - filled
    return ("█" * filled) + ("░" * empty)

def parse_limit(block, limit_name):
    # Match the specific limit section up to the next limit header or end of block
    limit_match = re.search(rf'{limit_name}(.*?)(?=(?:Weekly Limit|Five Hour Limit|$))', block, re.DOTALL)
    if not limit_match:
        return {'percent': 0, 'refreshes': 'Quota available'}
    
    sub = limit_match.group(1)
    
    percent = 0
    rem_match = re.search(r'(\d+(?:\.\d+)?)%\s+remaining', sub)
    if not rem_match:
        rem_match = re.search(r'(\d+(?:\.\d+)?)%', sub)
    
    if rem_match:
        rem_val = float(rem_match.group(1))
        percent = int(round(100.0 - rem_val))
        percent = max(0, min(100, percent))
    
    refreshes = "Quota available"
    ref_match = re.search(r'(?:Refreshes|Resets)\s+in\s+((?:(\d+)d\s*)?(?:(\d+)h\s*)?(?:(\d+)m)?)', sub)
    if ref_match and percent > 0:
        d_str = ref_match.group(1).strip()
        d_match = re.search(r'(?:(\d+)d)?\s*(?:(\d+)h)?\s*(?:(\d+)m)?', d_str)
        if d_match:
            days = int(d_match.group(1) or 0)
            hours = int(d_match.group(2) or 0)
            mins = int(d_match.group(3) or 0)
            
            if days > 0 or hours > 0 or mins > 0:
                target_dt = datetime.now() + timedelta(days=days, hours=hours, minutes=mins)
                formatted = target_dt.strftime("%b %d, %I:%M %p").replace(" 0", " ")
                refreshes = f"Refreshes: {formatted}"
    
    return {'percent': percent, 'refreshes': refreshes}

def parse_section(text, section_pattern):
    match = re.search(section_pattern, text, re.DOTALL)
    if not match:
        return None
    block = match.group(1)
    return {
        'weekly': parse_limit(block, 'Weekly Limit'),
        'session': parse_limit(block, 'Five Hour Limit')
    }

def main():
    try:
        result = subprocess.run(['bash', SCRIPT_PATH], capture_output=True, text=True, cwd=SCRIPT_DIR)
        text = result.stdout
    except Exception as e:
        print("W: ? S: ?")
        print("---")
        print(f"Error running script: {e}")
        return

    # Strip ANSI escape codes
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    text = ansi_escape.sub('', text)

    gemini_data = parse_section(text, r'GEMINI MODELS(.*?)((?:CLAUDE AND GPT MODELS)|$)')
    claude_data = parse_section(text, r'CLAUDE AND GPT MODELS(.*)')

    # Fallbacks if section headers were not matched
    if not gemini_data and not claude_data:
        gemini_data = {
            'weekly': parse_limit(text, 'Weekly Limit'),
            'session': parse_limit(text, 'Five Hour Limit')
        }

    # Calculate overall max for menu bar indicator
    max_w = 0
    max_s = 0
    if gemini_data:
        max_w = max(max_w, gemini_data['weekly']['percent'])
        max_s = max(max_s, gemini_data['session']['percent'])
    if claude_data:
        max_w = max(max_w, claude_data['weekly']['percent'])
        max_s = max(max_s, claude_data['session']['percent'])

    # 1. Menu bar string
    print(f"W: {max_w}%  S: {max_s}% | color={get_menu_color(max(max_w, max_s))}")
    print("---")
    
    # 2. Gemini Dropdown
    if gemini_data:
        g_s_pct = gemini_data['session']['percent']
        g_w_pct = gemini_data['weekly']['percent']
        
        print(f"Gemini Session Usage  {g_s_pct}% | color={get_dropdown_color(g_s_pct)} size=12 font=Menlo-Bold")
        print("5-hour rolling window | color=gray size=10")
        print(f"[{generate_bar(g_s_pct)}] | color={get_dropdown_color(g_s_pct)} size=11 font=Menlo")
        print(f"{gemini_data['session']['refreshes']} | color=gray size=10")
        print("---")
        print(f"Gemini Weekly Limit  {g_w_pct}% | color={get_dropdown_color(g_w_pct)} size=12 font=Menlo-Bold")
        print(f"[{generate_bar(g_w_pct)}] | color={get_dropdown_color(g_w_pct)} size=11 font=Menlo")
        print(f"{gemini_data['weekly']['refreshes']} | color=gray size=10")
        print("---")

    # 3. Claude & GPT Dropdown
    if claude_data:
        c_s_pct = claude_data['session']['percent']
        c_w_pct = claude_data['weekly']['percent']
        
        print(f"Claude & GPT Session Usage  {c_s_pct}% | color={get_dropdown_color(c_s_pct)} size=12 font=Menlo-Bold")
        print("5-hour rolling window | color=gray size=10")
        print(f"[{generate_bar(c_s_pct)}] | color={get_dropdown_color(c_s_pct)} size=11 font=Menlo")
        print(f"{claude_data['session']['refreshes']} | color=gray size=10")
        print("---")
        print(f"Claude & GPT Weekly Limit  {c_w_pct}% | color={get_dropdown_color(c_w_pct)} size=12 font=Menlo-Bold")
        print(f"[{generate_bar(c_w_pct)}] | color={get_dropdown_color(c_w_pct)} size=11 font=Menlo")
        print(f"{claude_data['weekly']['refreshes']} | color=gray size=10")
        print("---")

    print(f"Version {VERSION} | color=gray size=10")
    print("☕ Buy me a coffee | href='https://raw.githubusercontent.com/Shempaiii/agy-usage-tracker/main/coffee_qr.png'")
    print("⭐ Star on GitHub | href='https://github.com/Shempaiii/agy-usage-tracker'")
    print("🔄 Refresh | refresh=true")
    print("⬆️ Update | bash='/bin/bash' param1='-c' param2='\"brew upgrade agy-usage-tracker\"' terminal=true")
    print("❌ Quit | bash='/usr/bin/osascript' param1='-e' param2='quit app \"SwiftBar\"' terminal=false")

if __name__ == "__main__":
    main()
