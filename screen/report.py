import json
from datetime import datetime, timezone
from pathlib import Path

import config


def format_discord(result):
    lines = [f"**Value Investing Screen — {datetime.now(timezone.utc).date().isoformat()}**"]

    if result["no_contenders"]:
        lines.append("No names cleared the discount bar today.")
        lines.append("\n**Runners-up:**")
        for c in result["runners_up"]:
            lines.append(f"  {c['symbol']:6} V-score {c['v_score']:.1f}/9  F-score {c['f_score']}/9")
    else:
        lines.append("\n**Contenders:**")
        for c in result["contenders"]:
            lines.append(
                f"  {c['symbol']:6} composite {c.get('composite_score') or 0:.2f}  "
                f"V-score {c['v_score']:.1f}/9  F-score {c['f_score']}/9"
            )

    lines.append("\n**Strongest businesses (F-score):**")
    for c in result["strongest_businesses"]:
        lines.append(f"  {c['symbol']:6} F-score {c['f_score']}/9")

    if result.get("excluded"):
        lines.append(f"\nExcluded from this run ({len(result['excluded'])}):")
        for e in result["excluded"]:
            lines.append(f"  {e['symbol']:6} — {e['reason']}")

    return "\n".join(lines)


def save_result(result):
    Path(config.OUTPUT_PATH).parent.mkdir(parents=True, exist_ok=True)
    Path(config.OUTPUT_PATH).write_text(json.dumps(result, indent=1, default=str))
