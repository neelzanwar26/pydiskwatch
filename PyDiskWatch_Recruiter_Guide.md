# PyDiskWatch - Complete Recruiter Interview Guide

## 1. Project Overview & Real-World Relevance

**Elevator Pitch:** "PyDiskWatch is a cross-platform, modular Storage Monitoring and Automation tool. It acts as an unattended watchdog for critical servers—fetching live disk metrics, actively parsing low-level OS storage logs for corruption or I/O errors, and automatically dispatching threshold-driven alerts via Email and Desktop notifications, while regularly generating static HTML status reports."

**Real-World Relevance:**
In enterprise server infrastructure (like at Seagate), hardware failure is not an "if," but a "when." Storage arrays degrade, bad blocks appear over time, and applications suddenly crash when drives fill up unexpectedly at 3 AM. 
PyDiskWatch solves this exact real-world problem by providing:
1. **Proactive alerting:** Warning sysadmins when drives reach 80% capacity *before* a catastrophic outage occurs.
2. **Predictive maintenance:** Finding subtle "I/O errors" or "bad block" warnings buried in thousands of lines of syslog/Event viewer logs so that corrupted hard drives can be swapped out before total failure.
3. **Cross-Platform Consistency:** Running identical logic without modification across both Windows and Linux, which is crucial for heterogeneous enterprise networks.

## 2. Technical Stack & Their Importance

I deliberately chose the following stack to emphasize a balance between standard libraries and high-performance third-party packages:

*   **`psutil` (Core Monitoring):** The backbone for cross-platform hardware access. Instead of writing brittle subprocess scripts invoking `df -h` or `wmic` that break across versions, `psutil` talks directly to the OS kernel to reliably retrieve partitioned usage %, total gigabytes, mount points, and physical I/O bytes.
*   **`re` and `subprocess` (Log Parsing):** Deployed for extracting the needle from the haystack. Using compiled Regular Expressions over `syslog` on Linux and hooking natively into `wevtutil` on Windows allows the tool to parse massive log streams in microseconds to spot "disk full" or "read-only mount" anomalies.
*   **`Jinja2` (Reporting):** The industry-standard Python templating engine. Allowed me to cleanly separate the complex Python logic from the Presentation layer (HTML/CSS), enabling the programmatic generation of beautiful, loop-driven dashboard tables without messy string concatenation.
*   **`smtplib` & `plyer` (Alerting):** Using standard `smtplib` handles secure TLS/SSL SMTP connections to email providers (preventing plain-text snooping), while `plyer` injects cross-platform OS-level toast/desktop notifications directly into the user's notification bar (Windows Action Center/Linux DBus).
*   **`pytest` & `unittest.mock` (Testing):** Testing hardware software is incredibly difficult because you cannot physically inject a "failed drive" on the CI server. I utilized `MagicMock` and `patch` to intercept Python's OS calls, faking disk sizes and log errors to ensure 100% of my logic is testable on ephemeral GitHub Action runners.
*   **`PyYAML` (Configuration):** Hardcoded thresholds are awful practice. Moving all targets to a YAML file provides an operations team the ability to tweak memory sizes and alert recipients without ever modifying the source code.

## 3. Architecture & Implementation Details

The project relies on a highly decoupled **Modular Monolith Architectue**:
1.  **Orchestrator (`cli.py`):** Uses Python's native `argparse` to establish distinct sub-commands (`monitor`, `report`, `log-scan`).
2.  **Telemetry Collector (`monitor.py`):** Extracts system states and returns heavily structured `dataclass` objects.
3.  **Anomaly Engine (`log_parser.py`):** OS-aware. If on Linux -> parse `/var/log/syslog`. If on Windows -> spin up a subprocess running `wevtutil` to query XML-based System events for disk errors. 
4.  **Presentation (`reporter.py`):** Accepts the standard Python dataclasses and serializes them out into CSV files (for parsing by other tools) or static HTML (for human readability).
5.  **Dispatcher (`alerter.py`):** Triggers if usage percentages exceed the thresholds defined in `config.yaml`.

**Key Architectural Decision:** Returning explicitly typed `dataclasses` from my core engine rather than raw dictionaries or tuples guarantees schema enforcement and enables flawless autocomplete across all modules.

## 4. Scalability

When asked "How does this scale?", answer from two perspectives—**Code Scalability** and **Infrastructure Scalability**:

*   **Code Scalability (Extensibility):** Because of the module separation, if Seagate wants to add a new alerting channel (like Slack or Microsoft Teams Webhooks), the developer *only* touches `alerter.py`. `monitor.py` doesn't even know Slack exists. If we need to parse macOS logs, we add one function to `log_parser.py`. 
*   **Infrastructure Scalability (Deployment):** Right now, the tool is a standalone CLI designed for a single machine. To scale this across a 10,000-node server farm:
    1.  We would convert `reporter.py` to push metrics into an API endpoint or a Time-Series Database (like Prometheus).
    2.  We would deploy `PyDiskWatch` as a centralized background `systemd` daemon.
    3.  We could wrap the tool in a Docker container (passing through `/dev` volumes) and dispatch it globally via a Kubernetes DaemonSet. 

## 5. Real-World Performance & Optimization Scenarios

**Scenario 1: Massive Log Files (Memory Exhaustion)**
*The Problem:* A server's `syslog` is 15GB. Doing `lines = file.read().split()` will instantly cause an Out Of Memory (OOM) crash in Python.
*The Solution Implemented:* In `log_parser.py`, I process the log utilizing Python generators and `with open(): for line in f:` reading line-by-line. This means Python only ever loads 1 single string into RAM at a time. The tool can scan a 100GB log file while using only 5 Megabytes of RAM.

**Scenario 2: Permission Restrictions (Silent Failures)**
*The Problem:* Trying to view the disk capacity of a restricted or encrypted root mount triggers a `PermissionError`.
*The Solution Implemented:* I specifically wrapped the `disk_usage` call in a `try... except PermissionError:` block instead of letting the entire pipeline crash. This means the program gracefully ignores unreadable locked partitions while still successfully reporting on all the other healthy drives.

**Scenario 3: Avoiding False Positives**
*The Problem:* Evaluating pseudo-filesystems (`/proc`, `/sys`) or temporary RAM disks clutters the report with useless information that can trigger false alerts.
*The Solution Implemented:* By exclusively passing `all=False` to `psutil.disk_partitions` and explicitly skipping `cdrom` and empty filesystem types, the tool ensures that it **only** wastes CPU cycles analyzing actual hardware block storage devices.
