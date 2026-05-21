# Minimal AI Analysis Sidecar

This sketch assumes a service writes:

- `/var/lib/example/www/snapshot.json`
- `/var/lib/example/www/changes.json`
- `/var/lib/example/www/analysis.json`

The sidecar worker reads the first two files, checks `/etc/example/example.ai.env`, and writes the third file. The main dashboard should render deterministic summaries when `analysis.json` is missing, stale, disabled, or failed.

The timer is the safe first trigger. A path unit can be added later when the primary service writes an atomic request marker after each snapshot render.
