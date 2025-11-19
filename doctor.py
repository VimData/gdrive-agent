#!/usr/bin/env python3
"""
Health check script for gdrive-agent.
Verifies all dependencies and configuration required to run the agent.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path


class Doctor:
    def __init__(self):
        self.issues = []
        self.warnings = []
        self.success = []
        self.project_root = Path(__file__).parent

    def check_all(self):
        """Run all checks."""
        print("🔍 Running health checks for gdrive-agent...\n")
        
        self.check_python()
        self.check_uv()
        self.check_dependencies()
        self.check_ffmpeg()
        self.check_ollama()
        self.check_credentials()
        self.check_google_auth()
        self.check_folder_structure()
        
        self.print_summary()

    def check_python(self):
        """Check Python version."""
        print("📦 Python")
        version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        if sys.version_info >= (3, 8):
            self.success.append(f"Python {version} ✓")
            print(f"  ✓ Python {version}")
        else:
            self.issues.append(f"Python 3.8+ required (found {version})")
            print(f"  ✗ Python {version} (need 3.8+)")

    def check_uv(self):
        """Check if uv is installed."""
        print("\n📦 UV Package Manager")
        if shutil.which('uv'):
            result = subprocess.run(['uv', '--version'], capture_output=True, text=True)
            version = result.stdout.strip()
            self.success.append(f"UV installed: {version}")
            print(f"  ✓ {version}")
        else:
            self.warnings.append(
                "UV not installed. Install with: curl -LsSf https://astral.sh/uv/install.sh | sh"
            )
            print(f"  ⚠ UV not found")
            print("    Install: curl -LsSf https://astral.sh/uv/install.sh | sh")

    def check_dependencies(self):
        """Check Python dependencies."""
        print("\n📚 Python Dependencies")
        required = {
            'mcp': 'MCP Protocol',
            'google': 'Google API Client',
            'requests': 'HTTP Client',
        }
        
        missing = []
        for package, name in required.items():
            try:
                __import__(package)
                self.success.append(f"{name} installed ✓")
                print(f"  ✓ {name}")
            except ImportError:
                missing.append(f"{name} ({package})")
                print(f"  ✗ {name} ({package})")
        
        if missing:
            self.warnings.append(
                f"Missing Python packages: {', '.join(missing)}\n"
                f"    Install with: uv pip install -r requirements.txt"
            )

    def check_ffmpeg(self):
        """Check if ffmpeg is installed (required for video processing)."""
        print("\n🎬 FFmpeg")
        if shutil.which('ffmpeg'):
            result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True)
            version_line = result.stdout.split('\n')[0]
            self.success.append(f"FFmpeg installed ✓")
            print(f"  ✓ {version_line}")
        else:
            self.warnings.append(
                "FFmpeg not installed. Required for video frame extraction.\n"
                "    macOS: brew install ffmpeg\n"
                "    Linux: sudo apt-get install ffmpeg\n"
                "    Set ANALYZE_IMAGES=0 to skip video processing"
            )
            print(f"  ⚠ FFmpeg not found")
            print("    Required for: Video frame extraction, screen recording analysis")
            print("    Install macOS: brew install ffmpeg")

    def check_ollama(self):
        """Check if Ollama is running (optional, only needed if ANALYZE_IMAGES=1)."""
        print("\n🤖 Ollama (Optional)")
        analyze_images = os.getenv("ANALYZE_IMAGES", "1").lower() not in ["0", "false", "no"]
        
        try:
            result = subprocess.run(
                ['curl', '-s', 'http://localhost:11434/api/tags'],
                capture_output=True,
                timeout=2
            )
            if result.returncode == 0:
                self.success.append("Ollama running ✓")
                print("  ✓ Ollama server running at localhost:11434")
                self.check_vision_model()
            else:
                if analyze_images:
                    self.warnings.append(
                        "Ollama not responding. Required if ANALYZE_IMAGES=1.\n"
                        "    Start with: ollama serve"
                    )
                    print("  ⚠ Ollama not responding")
                    print("    Start server: ollama serve")
                else:
                    self.success.append("Ollama not needed (ANALYZE_IMAGES=0)")
                    print("  ✓ Skipped (ANALYZE_IMAGES=0)")
        except Exception as e:
            if analyze_images:
                self.warnings.append(
                    "Ollama not detected. Required if ANALYZE_IMAGES=1.\n"
                    "    Install: https://ollama.ai\n"
                    "    Start with: ollama serve"
                )
                print("  ⚠ Ollama not detected")
            else:
                self.success.append("Ollama not needed (ANALYZE_IMAGES=0)")
                print("  ✓ Skipped (ANALYZE_IMAGES=0)")

    def check_vision_model(self):
        """Check if vision model is available."""
        try:
            result = subprocess.run(
                ['ollama', 'list'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if 'llava' in result.stdout or 'moondream' in result.stdout:
                print("  ✓ Vision model available")
                self.success.append("Vision model found")
            else:
                self.warnings.append(
                    "No vision model found. Install with:\n"
                    "    ollama pull llava:7b"
                )
                print("  ⚠ No vision model installed")
                print("    Install: ollama pull llava:7b")
        except:
            pass

    def check_credentials(self):
        """Check if Google credentials are set up."""
        print("\n🔐 Google Drive Credentials")
        creds_path = self.project_root / "credentials.json"
        token_path = self.project_root / "token.json"
        
        if creds_path.exists():
            self.success.append("credentials.json found ✓")
            print("  ✓ credentials.json found")
        else:
            self.issues.append(
                "credentials.json not found.\n"
                "    1. Go to https://console.cloud.google.com\n"
                "    2. Create OAuth 2.0 credentials (Desktop app)\n"
                "    3. Download and place as credentials.json in project root"
            )
            print("  ✗ credentials.json not found")
        
        if token_path.exists():
            self.success.append("token.json found (authenticated) ✓")
            print("  ✓ token.json found (already authenticated)")
        else:
            print("  ℹ token.json will be created on first run")

    def check_google_auth(self):
        """Check if user can authenticate with Google."""
        print("\n🔑 Google Authentication")
        creds_path = self.project_root / "credentials.json"
        
        if not creds_path.exists():
            print("  ⚠ Set up credentials.json first")
            return
        
        try:
            from google.oauth2.credentials import Credentials
            self.success.append("Google Auth library available ✓")
            print("  ✓ Google authentication library available")
        except ImportError:
            self.warnings.append(
                "Google Auth library not installed.\n"
                "    Install with: uv pip install -r requirements.txt"
            )
            print("  ⚠ Google Auth not available")

    def check_folder_structure(self):
        """Check project folder structure."""
        print("\n📁 Project Structure")
        required = {
            'agent_client': 'Agent client code',
            'gdrive_server': 'MCP server code',
            'main.py': 'Entry point',
            'requirements.txt': 'Dependencies',
            'README.md': 'Documentation',
        }
        
        for item, desc in required.items():
            path = self.project_root / item
            if path.exists():
                self.success.append(f"{item} ✓")
                print(f"  ✓ {item}")
            else:
                self.issues.append(f"Missing: {item} ({desc})")
                print(f"  ✗ {item}")

    def print_summary(self):
        """Print summary of checks."""
        print("\n" + "="*60)
        print("SUMMARY")
        print("="*60)
        
        if self.success:
            print(f"\n✓ OK ({len(self.success)}):")
            for msg in self.success[:5]:
                print(f"  {msg}")
            if len(self.success) > 5:
                print(f"  ... and {len(self.success) - 5} more")
        
        if self.warnings:
            print(f"\n⚠ Warnings ({len(self.warnings)}):")
            for msg in self.warnings:
                for line in msg.split('\n'):
                    print(f"  {line}")
        
        if self.issues:
            print(f"\n✗ Critical Issues ({len(self.issues)}):")
            for msg in self.issues:
                for line in msg.split('\n'):
                    print(f"  {line}")
        
        print("\n" + "="*60)
        
        if self.issues:
            print("❌ FAILED: Fix critical issues above")
            sys.exit(1)
        elif self.warnings:
            print("⚠️  WARNING: Some features may not work. Review warnings above.")
            sys.exit(0)
        else:
            print("✅ HEALTHY: All checks passed!")
            sys.exit(0)


if __name__ == "__main__":
    doctor = Doctor()
    doctor.check_all()
