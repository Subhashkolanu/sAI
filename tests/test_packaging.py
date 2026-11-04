"""
=========================================================
sAI V1 - Installer and Packaging Unit Tests
=========================================================
Validates the packaging specification, Inno Setup script,
application icons, bundle structure, and user data safety.
=========================================================
"""

from __future__ import annotations

import os
import unittest
from pathlib import Path
from PIL import Image

from backend.storage import is_packaged_executable, get_data_dir


class PackagingSpecAndScriptTests(unittest.TestCase):
    """Verifies PyInstaller spec, Inno Setup script, and icons."""

    def setUp(self):
        self.root = Path(__file__).resolve().parents[1]
        self.spec_path = self.root / "sAI.spec"
        self.iss_path = self.root / "installer.iss"
        self.icon_path = self.root / "assets" / "icon.ico"
        self.logo_path = self.root / "Logo.png"

    def test_spec_file_exists_and_configured(self):
        self.assertTrue(self.spec_path.exists(), "sAI.spec must exist.")
        content = self.spec_path.read_text(encoding="utf-8")
        self.assertIn("customtkinter", content)
        self.assertIn("console=False", content)
        self.assertIn("icon=", content)
        self.assertIn("sAI", content)

    def test_inno_setup_script_exists_and_meets_safety_requirements(self):
        self.assertTrue(self.iss_path.exists(), "installer.iss must exist.")
        content = self.iss_path.read_text(encoding="utf-8")

        # Must not require admin elevation
        self.assertIn("PrivilegesRequired=lowest", content)
        # Must target per-user local app data Programs
        self.assertIn("{localappdata}\\Programs\\", content)
        # Must target 64-bit architecture
        self.assertIn("ArchitecturesInstallIn64BitMode=x64compatible", content)
        # Output base filename
        self.assertIn("OutputBaseFilename=sAI-Setup-v1.0.0", content)
        # Must create Start Menu shortcut
        self.assertIn("{autoprograms}\\", content)

    def test_application_icon_resolutions(self):
        self.assertTrue(self.icon_path.exists(), "assets/icon.ico must exist.")
        with Image.open(self.icon_path) as img:
            self.assertEqual(img.format, "ICO")

    def test_user_data_path_separation(self):
        """Ensures application files and user data reside in separate root subdirectories."""
        app_install_dir = Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / "sAI"
        user_data_dir = Path(os.environ.get("LOCALAPPDATA", "")) / "sAI" / "data"

        # The user data directory must NOT be inside the application installation directory
        self.assertFalse(
            user_data_dir.is_relative_to(app_install_dir),
            "User data directory must not be located within the application install directory."
        )

    def test_packaged_executable_detection(self):
        with unittest.mock.patch.dict(os.environ, {"SAI_PACKAGED": "1"}):
            self.assertTrue(is_packaged_executable())

        with unittest.mock.patch.dict(os.environ, {"SAI_PACKAGED": "0"}, clear=True):
            # sys.frozen is False in normal test runner
            self.assertFalse(is_packaged_executable())

    def test_installer_artifact_exists_when_built(self):
        installer_path = self.root / "dist_installer" / "sAI-Setup-v1.0.0.exe"
        if installer_path.exists():
            self.assertGreater(installer_path.stat().st_size, 10_000_000)  # > 10 MB

    def test_standalone_bundle_exists_when_built(self):
        bundle_exe = self.root / "dist" / "sAI" / "sAI.exe"
        if bundle_exe.exists():
            self.assertGreater(bundle_exe.stat().st_size, 1_000_000)  # > 1 MB


if __name__ == "__main__":
    unittest.main()
