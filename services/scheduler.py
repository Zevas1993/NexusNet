
from __future__ import annotations
import threading
import time
import subprocess
import yaml
import shlex
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path

# Configure logging
logger = logging.getLogger(__name__)

class _Job(threading.Thread):
    """Individual scheduled job execution thread"""

    daemon = True

    def __init__(self, name: str, period_s: int, cmd: str, timeout: int = 300,
                 max_retries: int = 3, enabled: bool = True):
        super().__init__(name=name)
        self.period_s = period_s
        self.cmd = cmd
        self.timeout = timeout
        self.max_retries = max_retries
        self.enabled = enabled
        self._stop = False
        self.last_run: Optional[float] = None
        self.last_success: Optional[float] = None
        self.failure_count = 0
        self.execution_count = 0
        self.logger = logging.getLogger(f"{__name__}.{name}")

    def run(self):
        """Main job execution loop"""
        self.logger.info(f"Job {self.name} started - interval: {self.period_s}s")

        while not self._stop:
            # Skip execution if disabled
            if not self.enabled:
                self.logger.debug(f"Job {self.name} disabled, skipping execution")
                time.sleep(1)
                continue

            try:
                start_time = time.time()

                # Execute with retry logic
                success = self._execute_with_retries()

                # Update statistics
                execution_time = time.time() - start_time
                self.execution_count += 1
                self.last_run = start_time

                if success:
                    self.last_success = start_time
                    self.failure_count = 0  # Reset failure counter
                    self.logger.info("03d")
                else:
                    self.failure_count += 1
                    if self.failure_count >= self.max_retries:
                        self.logger.error(f"Job {self.name} failed after {self.failure_count} attempts, disabling")
                        self.enabled = False
                    else:
                        self.logger.warning(f"Job {self.name} failed (attempt {self.failure_count}/{self.max_retries})")

            except Exception as e:
                self.logger.error(f"Unexpected error in job {self.name}: {e}")
                self.failure_count += 1

            # Wait for next execution cycle
            for _ in range(self.period_s):
                if self._stop:
                    break
                time.sleep(1)

        self.logger.info(f"Job {self.name} stopped")

    def _execute_with_retries(self) -> bool:
        """Execute command with retry logic"""
        for attempt in range(self.max_retries):
            try:
                self.logger.debug(f"Executing job {self.name}: {self.cmd[:50]}..." if len(self.cmd) > 50 else f"Executing: {self.cmd}")

                # Execute with timeout
                result = subprocess.run(
                    shlex.split(self.cmd),
                    capture_output=True,
                    text=True,
                    timeout=self.timeout,
                    check=False
                )

                if result.returncode == 0:
                    self.logger.debug(f"Job {self.name} completed successfully")
                    return True
                else:
                    error_msg = f"Job {self.name} failed with return code {result.returncode}"
                    if result.stderr:
                        error_msg += f": {result.stderr.strip()}"
                    self.logger.warning(error_msg)

                    # Don't retry certain types of errors immediately
                    if result.returncode in [2, 127]:  # Command not found, permission denied
                        break

            except subprocess.TimeoutExpired:
                self.logger.error(f"Job {self.name} timed out after {self.timeout}s")
                continue
            except (FileNotFoundError, OSError) as e:
                self.logger.error(f"Execution error for job {self.name}: {e}")
                break
            except Exception as e:
                self.logger.error(f"Unexpected execution error for job {self.name}: {e}")
                break

            if attempt < self.max_retries - 1 and not self._stop:
                time.sleep(min(2 ** attempt, 30))  # Exponential backoff, max 30s

        return False

    def stop(self):
        """Stop the job execution"""
        self.logger.info(f"Stopping job {self.name}")
        self._stop = True

    def get_stats(self) -> Dict[str, Any]:
        """Get job statistics"""
        return {
            "name": self.name,
            "enabled": self.enabled,
            "execution_count": self.execution_count,
            "failure_count": self.failure_count,
            "last_run": self.last_run,
            "last_success": self.last_success,
            "success_rate": (self.execution_count - self.failure_count) / max(self.execution_count, 1)
        }

class Scheduler:
    """Enterprise-grade job scheduler with comprehensive monitoring"""

    def __init__(self, cfg_path: str = "runtime/config/automation.yaml"):
        self.jobs: List[_Job] = []
        self.logger = logging.getLogger(__name__)
        self.metrics = {
            "jobs_enabled": 0,
            "jobs_total": 0,
            "successful_executions": 0,
            "failed_executions": 0,
            "runtime_errors": 0
        }

        try:
            self._load_configuration(cfg_path)
            self.logger.info(f"Scheduler initialized with {len(self.jobs)} jobs")
        except Exception as e:
            self.logger.error(f"Failed to initialize scheduler: {e}")
            # Create minimal working configuration
            self.jobs = []

    def _load_configuration(self, cfg_path: str):
        """Load scheduler configuration with validation"""
        try:
            with open(cfg_path, "r", encoding="utf-8") as f:
                cfg = yaml.safe_load(f) or {}
        except (FileNotFoundError, yaml.YAMLError) as e:
            self.logger.warning(f"Configuration file {cfg_path} not found or invalid: {e}")
            cfg = {}

        sc = cfg.get("scheduler", {})
        defaults = {
            "enabled": True,
            "jobs": []
        }

        if not sc.get("enabled", defaults["enabled"]):
            self.logger.info("Scheduler disabled in configuration")
            return

        jobs_config = sc.get("jobs", defaults["jobs"])
        if not jobs_config:
            self.logger.warning("No jobs configured in scheduler section")

        for i, job_config in enumerate(jobs_config):
            try:
                # Validate required fields
                name = job_config.get("name", f"job_{i}")
                cmd = job_config.get("cmd")
                if not cmd:
                    self.logger.error(f"Job {name} missing required 'cmd' field, skipping")
                    continue

                # Create job with defaults
                job = _Job(
                    name=name,
                    period_s=int(job_config.get("every_minutes", 60)) * 60,
                    cmd=cmd,
                    timeout=int(job_config.get("timeout_seconds", 300)),
                    max_retries=int(job_config.get("max_retries", 3)),
                    enabled=job_config.get("enabled", True)
                )

                if job.enabled:
                    self.metrics["jobs_enabled"] += 1
                    self.logger.info(f"Enabled scheduled job: {name}")
                else:
                    self.logger.info(f"Disabled scheduled job: {name}")

            except (ValueError, TypeError) as e:
                self.logger.error(f"Invalid job configuration at index {i}: {e}")
                continue

        self.metrics["jobs_total"] = len(self.jobs)

    def start(self):
        """Start all enabled jobs"""
        started_count = 0
        for job in self.jobs:
            if job.enabled:
                try:
                    job.start()
                    started_count += 1
                except Exception as e:
                    self.metrics["runtime_errors"] += 1
                    self.logger.error(f"Failed to start job {job.name}: {e}")

        self.logger.info(f"Started {started_count}/{len(self.jobs)} scheduled jobs")

    def stop(self):
        """Stop all jobs gracefully"""
        self.logger.info("Stopping all scheduled jobs")
        stopped_count = 0

        for job in self.jobs:
            try:
                job.stop()
                job.join(timeout=10)  # Wait up to 10 seconds for graceful shutdown
                stopped_count += 1
            except Exception as e:
                self.logger.error(f"Error stopping job {job.name}: {e}")

        self.logger.info(f"Successfully stopped {stopped_count}/{len(self.jobs)} jobs")

    def get_status(self) -> Dict[str, Any]:
        """Get comprehensive scheduler status"""
        job_stats = [job.get_stats() for job in self.jobs]

        return {
            "scheduler": {
                "active": any(not job._stop for job in self.jobs if hasattr(job, '_stop')),
                "metrics": self.metrics,
                "uptime_seconds": time.time() - getattr(self, '_start_time', time.time())
            },
            "jobs": job_stats
        }

    def reload_configuration(self, cfg_path: str = "runtime/config/automation.yaml"):
        """Reload scheduler configuration (needs restart to take effect for active jobs)"""
        self.logger.info("Configuration reload requested - restart required for active jobs")
        old_jobs = self.jobs

        try:
            self._load_configuration(cfg_path)
            self.logger.info(f"Configuration reloaded: {len(self.jobs)} jobs configured")
            return True
        except Exception as e:
            self.logger.error(f"Failed to reload configuration: {e}")
            self.jobs = old_jobs  # Restore previous configuration
            return False

def validate_scheduler_config(config: Dict[str, Any]) -> List[str]:
    """Validate scheduler configuration and return issues"""
    issues = []

    if not isinstance(config, dict):
        issues.append("Configuration must be a dictionary")
        return issues

    scheduler = config.get("scheduler", {})
    if not scheduler:
        issues.append("Missing 'scheduler' section")
        return issues

    jobs = scheduler.get("jobs", [])
    if not jobs:
        issues.append("No jobs defined in scheduler configuration")
    else:
        for i, job in enumerate(jobs):
            if not job.get("cmd"):
                issues.append(f"Job at index {i}: missing required 'cmd' field")
            if job.get("every_minutes", 0) <= 0:
                issues.append(f"Job at index {i}: 'every_minutes' must be positive")

    return issues
