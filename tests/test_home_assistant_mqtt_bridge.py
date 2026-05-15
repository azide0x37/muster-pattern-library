import os
from pathlib import Path
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
T2R6 = ROOT / "patterns/t2/rare/T2R6.home-assistant-mqtt-bridge"


def run_script(script: Path, *args: str, env: dict[str, str]) -> subprocess.CompletedProcess[str]:
    full_env = os.environ.copy()
    full_env.update(env)
    return subprocess.run([str(script), *args], cwd=ROOT, env=full_env, text=True, capture_output=True, check=True)


class HomeAssistantMqttBridgeTests(unittest.TestCase):
    def test_discovery_state_and_control_are_mockable(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            env = {"MUSTER_MOCK_ROOT": str(root)}
            script = T2R6 / "scripts/ha-mqtt-bridge.sh"

            run_script(script, "--discover", env=env)
            outbox = root / "run/muster/home-assistant-mqtt-bridge/mqtt-outbox"
            discovery = outbox / "homeassistant_device_muster_bridge_config.json"
            self.assertTrue(discovery.exists())
            discovery_text = discovery.read_text()
            self.assertIn('"restart_service"', discovery_text)
            self.assertIn('"enabled"', discovery_text)
            self.assertIn("muster/home-assistant-mqtt-bridge/cmd/restart", discovery_text)
            self.assertIn("muster/home-assistant-mqtt-bridge/cmd/enabled/set", discovery_text)

            run_script(script, "--state", "enabled", "ON", env=env)
            state = root / "run/muster/home-assistant-mqtt-bridge/state.json"
            self.assertIn('"state":"ON"', state.read_text())

            control_dir = root / "run/muster/home-assistant-mqtt-bridge/mqtt-control"
            (control_dir / "enabled.cmd").write_text("OFF\n")
            run_script(script, "--control", env=env)
            self.assertIn('"state":"OFF"', state.read_text())
            self.assertTrue((control_dir / "enabled.cmd.processed").exists())

            (control_dir / "restart.cmd").write_text("PRESS\n")
            run_script(script, "--control", env=env)
            result = root / "run/muster/home-assistant-mqtt-bridge/control-result.json"
            self.assertIn('"control":"restart"', result.read_text())
            self.assertTrue((control_dir / "restart.cmd.processed").exists())

    def test_rollback_restores_previous_state_payload(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            env = {"MUSTER_MOCK_ROOT": str(root)}
            script = T2R6 / "scripts/ha-mqtt-bridge.sh"

            run_script(script, "--state", "enabled", "ON", env=env)
            run_script(script, "--state", "enabled", "OFF", env=env)
            run_script(T2R6 / "scripts/rollback.sh", "--apply", env={"MUSTER_ROOT": str(root)})

            state = root / "run/muster/home-assistant-mqtt-bridge/state.json"
            self.assertIn('"state":"ON"', state.read_text())
            outbox_state = root / "run/muster/home-assistant-mqtt-bridge/mqtt-outbox/muster_home-assistant-mqtt-bridge_enabled_state.json"
            self.assertIn('"state":"ON"', outbox_state.read_text())

    def test_install_and_uninstall_support_staged_roots(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            env = {"MUSTER_ROOT": str(root)}
            run_script(T2R6 / "scripts/install.sh", "--apply", env=env)

            self.assertTrue((root / "etc/systemd/system/muster-ha-mqtt-bridge.service").exists())
            self.assertTrue((root / "usr/local/lib/muster/home-assistant-mqtt-bridge/ha-mqtt-bridge.sh").exists())
            config = root / "etc/muster/home-assistant-mqtt-bridge.env"
            config.write_text(config.read_text() + "USER_SETTING=kept\n")

            run_script(T2R6 / "scripts/install.sh", "--apply", env=env)
            self.assertIn("USER_SETTING=kept", config.read_text())

            run_script(T2R6 / "scripts/uninstall.sh", "--apply", env=env)
            self.assertFalse((root / "etc/systemd/system/muster-ha-mqtt-bridge.service").exists())
            self.assertFalse((root / "usr/local/lib/muster/home-assistant-mqtt-bridge").exists())
            self.assertTrue(config.exists())


if __name__ == "__main__":
    unittest.main()
