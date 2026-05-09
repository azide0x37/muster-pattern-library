import os
import shlex
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class DeviceTriggeredConveyorTests(unittest.TestCase):
    def test_backpressure_waits_for_drain_then_continues(self) -> None:
        script = ROOT / "patterns/t2/rare/TR4.device-triggered-conveyor/scripts/device-convey.sh"
        wait_script = ROOT / "patterns/t2/common/TC1.hot-cold-nas-conveyor/scripts/wait-for-hot-capacity.sh"

        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            ready_file = tmp_path / "run/muster/capacity-ready"
            env = os.environ.copy()
            env.update(
                {
                    "MUSTER_MOCK_ROOT": tmp,
                    "WAIT_FOR_HOT_CAPACITY": str(wait_script),
                    "MUSTER_MOCK_BACKPRESSURE": "1",
                    "MIN_HOT_FREE_BYTES": "1",
                    "CAPACITY_TIMEOUT_SECONDS": "5",
                    "CAPACITY_INTERVAL_SECONDS": "1",
                    "DRAIN_COMMAND": f"touch {shlex.quote(str(ready_file))}",
                }
            )

            subprocess.run([str(script), "/dev/sr0"], env=env, text=True, capture_output=True, check=True)

            self.assertTrue((tmp_path / "run/muster/hot-capacity.json").exists())
            self.assertTrue((tmp_path / "run/muster/device-conveyor.json").exists())
            self.assertTrue((tmp_path / "run/muster/device-conveyor-handoff.json").exists())
            handoff_root = tmp_path / "var/cache/muster/hot/device-conveyor"
            self.assertTrue(any(handoff_root.iterdir()))


if __name__ == "__main__":
    unittest.main()
