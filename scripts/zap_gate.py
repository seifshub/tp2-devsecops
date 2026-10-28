"""Fail the build if a ZAP JSON report contains alerts at or above a given risk level.

Usage: python3 zap_gate.py <zap-report.json> [informational|low|medium|high]
"""
import json
import sys

RISK_LEVELS = {"informational": 0, "low": 1, "medium": 2, "high": 3}
FALSE_POSITIVE = "0"


def main(report_path, threshold="high"):
    min_risk = RISK_LEVELS[threshold.lower()]
    with open(report_path, encoding="utf-8") as f:
        report = json.load(f)

    blocking = []
    for site in report.get("site", []):
        for alert in site.get("alerts", []):
            count = alert.get("count", len(alert.get("instances", [])))
            line = f"[{alert['riskdesc']}] {alert['name']} (plugin {alert['pluginid']}, {count} instance(s))"
            print(line)
            if int(alert["riskcode"]) >= min_risk and alert.get("confidence") != FALSE_POSITIVE:
                blocking.append(line)

    if blocking:
        print(f"\nFAIL: {len(blocking)} alert(s) at or above '{threshold}' risk:")
        print("\n".join(f"  {line}" for line in blocking))
        return 1

    print(f"\nPASS: no alerts at or above '{threshold}' risk.")
    return 0


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:]))
