from __future__ import annotations

import time

from _bootstrap import add_repo_src_to_path

add_repo_src_to_path()

from agent_labs.observability import StructuredLogger, Tracer


def main() -> None:
    logger = StructuredLogger(name="demo").with_context(run_id="trace-demo-1")
    tracer = Tracer(logger=logger)

    with tracer.span("observe"):
        time.sleep(0.01)

    with tracer.span("plan"):
        time.sleep(0.02)

    snapshot = tracer.metrics.snapshot()
    print("OK: counters=", snapshot["counters"])
    print("OK: latencies_keys=", sorted(snapshot["latencies"].keys()))


if __name__ == "__main__":
    main()

