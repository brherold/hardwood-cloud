#!/usr/bin/env python
"""
Hardwood Scraper & DataAdder Entrypoint
Convenient runner for Windows Task Scheduler and manual invocations.
"""
import sys
import os
import subprocess

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
cmd = [sys.executable, "-m", "backend.scripts.dataAdder"] + sys.argv[1:]
sys.exit(subprocess.run(cmd, cwd=PROJECT_ROOT).returncode)
