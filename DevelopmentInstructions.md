### Agent Cleanup

# Features added:
- Install multiple agents types in same machine.
- During deployment specify the metrics that need to be reported.
- In a machine which has multiple agent types installed, stop only one agent. See proc/README.md for this instructions of stopping one agent or all agents.

The changes in this cleanup branch are old. The following changes are need to be done:
 - Bring the latest changes from all agents.
 - Add new agents like collectd, elasticsearch, hypervisor, metricFileReplay, logFileReplay.
