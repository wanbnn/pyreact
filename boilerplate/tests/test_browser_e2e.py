"""Browser E2E for the served Orbit Board."""

import socket
import subprocess
import time
from urllib.error import URLError
from urllib.request import urlopen

import pytest


playwright = pytest.importorskip("playwright.sync_api")


def _free_port():
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


@pytest.fixture
def app_url():
    port = _free_port()
    url = f"http://127.0.0.1:{port}"
    process = subprocess.Popen(
        ["pyreact", "dev", "--port", str(port), "--no-open"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    deadline = time.monotonic() + 10
    try:
        while time.monotonic() < deadline:
            if process.poll() is not None:
                stdout, stderr = process.communicate()
                raise RuntimeError(f"Servidor encerrou antes do esperado:\n{stdout}\n{stderr}")
            try:
                with urlopen(url, timeout=0.5) as response:
                    if response.status == 200:
                        break
            except (URLError, TimeoutError):
                time.sleep(0.1)
        else:
            raise TimeoutError(f"Servidor não respondeu em {url}")
        yield url
    finally:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)


def test_real_user_flow(app_url):
    with playwright.sync_playwright() as runtime:
        browser = runtime.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            page.goto(app_url, wait_until="networkidle")
            assert page.title() == "Orbit Board · PyReact"
            playwright.expect(page.locator(".task-card")).to_have_count(3)
            playwright.expect(
                page.get_by_test_id("stat-progresso").locator(".stat-card__value")
            ).to_have_text("33%")

            page.get_by_test_id("add-demo-task").click()
            playwright.expect(page.get_by_text("Preparar experimento de aquisição")).to_be_visible()
            playwright.expect(
                page.get_by_test_id("stat-total").locator(".stat-card__value")
            ).to_have_text("4")

            page.get_by_test_id("toggle-2").click()
            playwright.expect(
                page.get_by_test_id("stat-progresso").locator(".stat-card__value")
            ).to_have_text("50%")

            page.get_by_test_id("filter-done").click()
            playwright.expect(page.locator(".task-card")).to_have_count(2)
        finally:
            browser.close()
