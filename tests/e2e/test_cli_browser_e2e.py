"""End-to-end tests for the generated project, CLI, build and browser UI."""

import os
import socket
import subprocess
import sys
import time
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen

import pytest


playwright = pytest.importorskip("playwright.sync_api")
CLI = [sys.executable, "-m", "pyreact.cli.main"]
PROJECT_ROOT = Path(__file__).resolve().parents[2]
SUBPROCESS_ENV = {
    **os.environ,
    "PYTHONPATH": os.pathsep.join(
        filter(None, [str(PROJECT_ROOT), os.environ.get("PYTHONPATH", "")])
    ),
}


def _free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def _wait_until_ready(url: str, process: subprocess.Popen, timeout: float = 10) -> None:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if process.poll() is not None:
            stdout, stderr = process.communicate()
            raise RuntimeError(f"Server stopped early.\n{stdout}\n{stderr}")
        try:
            with urlopen(url, timeout=0.5) as response:
                if response.status == 200:
                    return
        except (URLError, TimeoutError):
            time.sleep(0.1)
    raise TimeoutError(f"Server did not become ready at {url}")


@pytest.fixture
def generated_project(tmp_path: Path) -> Path:
    result = subprocess.run(
        [*CLI, "create", "sample_app"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        timeout=15,
        env=SUBPROCESS_ENV,
    )
    assert result.returncode == 0, result.stderr
    return tmp_path / "sample_app"


@pytest.fixture
def dev_server(generated_project: Path):
    port = _free_port()
    url = f"http://127.0.0.1:{port}"
    process = subprocess.Popen(
        [*CLI, "dev", "--port", str(port), "--no-open"],
        cwd=generated_project,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=SUBPROCESS_ENV,
    )
    try:
        _wait_until_ready(url, process)
        yield url
    finally:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)


def test_scaffold_generate_and_build(generated_project: Path):
    expected = [
        "pyproject.toml",
        "README.md",
        "src/index.py",
        "public/index.html",
        "tests/test_app.py",
    ]
    assert all((generated_project / item).exists() for item in expected)

    component = subprocess.run(
        [*CLI, "generate", "component", "Button"],
        cwd=generated_project,
        capture_output=True,
        text=True,
        timeout=15,
        env=SUBPROCESS_ENV,
    )
    hook = subprocess.run(
        [*CLI, "generate", "hook", "useCounter"],
        cwd=generated_project,
        capture_output=True,
        text=True,
        timeout=15,
        env=SUBPROCESS_ENV,
    )
    build = subprocess.run(
        [*CLI, "build"],
        cwd=generated_project,
        capture_output=True,
        text=True,
        timeout=15,
        env=SUBPROCESS_ENV,
    )
    generated_tests = subprocess.run(
        [sys.executable, "-m", "pytest", "-q"],
        cwd=generated_project,
        capture_output=True,
        text=True,
        timeout=30,
        env=SUBPROCESS_ENV,
    )

    assert component.returncode == hook.returncode == build.returncode == 0
    assert generated_tests.returncode == 0, generated_tests.stderr
    assert (generated_project / "src/components/Button.py").exists()
    assert (generated_project / "src/hooks/use_counter.py").exists()
    assert (generated_project / "dist/index.html").exists()


def test_counter_user_flow_in_browser(dev_server: str):
    with playwright.sync_playwright() as runtime:
        browser = runtime.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            page.goto(dev_server, wait_until="networkidle")
            assert page.title() == "PyReact App"
            assert page.locator("h1").text_content() == "Welcome to PyReact!"

            counter = page.locator(".counter span")
            increment = page.get_by_role("button", name="Increment counter")
            decrement = page.get_by_role("button", name="Decrement counter")

            assert counter.text_content() == "Count: 0"
            increment.click()
            increment.click()
            decrement.click()
            assert counter.text_content() == "Count: 1"
        finally:
            browser.close()
