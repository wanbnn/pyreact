"""
PyReact E2E Tests
=================

Testes end-to-end para validar a funcionalidade do PyReact.
Usa Playwright para automação de navegador.
"""

import pytest
from playwright.sync_api import sync_playwright, Page, Browser
import subprocess
import time
import signal
import os
from pathlib import Path


class TestPyReactE2E:
    """Testes E2E para aplicações PyReact"""
    
    @pytest.fixture(scope="class")
    def browser(self):
        """Fixture para navegador Playwright"""
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            yield browser
            browser.close()
    
    @pytest.fixture(scope="class")
    def dev_server(self):
        """Fixture para servidor de desenvolvimento"""
        # Criar projeto de teste
        project_name = "test_e2e_app"
        subprocess.run(["pyreact", "create", project_name], capture_output=True)
        
        # Iniciar servidor
        server_process = subprocess.Popen(
            ["pyreact", "dev", "--port", "3007"],
            cwd=project_name,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Aguardar servidor iniciar
        time.sleep(3)
        
        yield f"http://localhost:3007"
        
        # Cleanup
        server_process.terminate()
        try:
            server_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            server_process.kill()
    
    def test_homepage_loads(self, browser: Browser, dev_server: str):
        """Testa se a homepage carrega corretamente"""
        page = browser.new_page()
        page.goto(dev_server)
        
        # Verificar título
        title = page.title()
        assert "PyReact App" in title
        
        # Verificar se o elemento root existe
        root = page.query_selector("#root")
        assert root is not None
        
        page.close()
    
    def test_counter_initial_state(self, browser: Browser, dev_server: str):
        """Testa estado inicial do contador"""
        page = browser.new_page()
        page.goto(dev_server)
        page.wait_for_load_state("networkidle")
        
        # Verificar contador inicial
        counter_text = page.locator(".counter span").text_content()
        assert "Count: 0" in counter_text
        
        page.close()
    
    def test_counter_increment(self, browser: Browser, dev_server: str):
        """Testa incremento do contador"""
        page = browser.new_page()
        page.goto(dev_server)
        page.wait_for_load_state("networkidle")
        
        # Clicar no botão de incremento
        increment_btn = page.locator("button:has-text('+')")
        increment_btn.click()
        
        # Verificar contador
        counter_text = page.locator(".counter span").text_content()
        assert "Count: 1" in counter_text
        
        # Clicar novamente
        increment_btn.click()
        counter_text = page.locator(".counter span").text_content()
        assert "Count: 2" in counter_text
        
        page.close()
    
    def test_counter_decrement(self, browser: Browser, dev_server: str):
        """Testa decremento do contador"""
        page = browser.new_page()
        page.goto(dev_server)
        page.wait_for_load_state("networkidle")
        
        # Clicar no botão de decremento
        decrement_btn = page.locator("button:has-text('-')")
        decrement_btn.click()
        
        # Verificar contador
        counter_text = page.locator(".counter span").text_content()
        assert "Count: -1" in counter_text
        
        page.close()
    
    def test_multiple_interactions(self, browser: Browser, dev_server: str):
        """Testa múltiplas interações"""
        page = browser.new_page()
        page.goto(dev_server)
        page.wait_for_load_state("networkidle")
        
        increment_btn = page.locator("button:has-text('+')")
        decrement_btn = page.locator("button:has-text('-')")
        
        # Incrementar 5 vezes
        for _ in range(5):
            increment_btn.click()
        
        counter_text = page.locator(".counter span").text_content()
        assert "Count: 5" in counter_text
        
        # Decrementar 3 vezes
        for _ in range(3):
            decrement_btn.click()
        
        counter_text = page.locator(".counter span").text_content()
        assert "Count: 2" in counter_text
        
        page.close()
    
    def test_page_structure(self, browser: Browser, dev_server: str):
        """Testa estrutura da página"""
        page = browser.new_page()
        page.goto(dev_server)
        page.wait_for_load_state("networkidle")
        
        # Verificar elementos principais
        h1 = page.locator("h1")
        assert h1.text_content() == "Welcome to PyReact!"
        
        p = page.locator("p")
        assert "Edit src/index.py" in p.text_content()
        
        # Verificar classe app
        app_div = page.locator(".app")
        assert app_div.is_visible()
        
        page.close()


class TestPyReactCLI:
    """Testes para CLI do PyReact"""
    
    def test_create_project(self, tmp_path):
        """Testa criação de projeto"""
        project_name = "test_cli_project"
        
        # Mudar para diretório temporário
        original_dir = os.getcwd()
        os.chdir(tmp_path)
        
        try:
            # Criar projeto
            result = subprocess.run(
                ["pyreact", "create", project_name],
                capture_output=True,
                text=True
            )
            
            # Verificar se projeto foi criado
            assert result.returncode == 0
            assert Path(project_name).exists()
            assert Path(project_name / "pyproject.toml").exists()
            assert Path(project_name / "src" / "index.py").exists()
            assert Path(project_name / "README.md").exists()
            
        finally:
            os.chdir(original_dir)
    
    def test_create_component(self, tmp_path):
        """Testa criação de componente"""
        project_name = "test_component_project"
        
        original_dir = os.getcwd()
        os.chdir(tmp_path)
        
        try:
            # Criar projeto
            subprocess.run(["pyreact", "create", project_name], capture_output=True)
            
            # Criar componente
            os.chdir(project_name)
            result = subprocess.run(
                ["pyreact", "generate", "component", "Button"],
                capture_output=True,
                text=True
            )
            
            # Verificar se componente foi criado
            assert result.returncode == 0
            assert Path("src/components/Button.py").exists()
            
        finally:
            os.chdir(original_dir)
    
    def test_create_hook(self, tmp_path):
        """Testa criação de hook"""
        project_name = "test_hook_project"
        
        original_dir = os.getcwd()
        os.chdir(tmp_path)
        
        try:
            # Criar projeto
            subprocess.run(["pyreact", "create", project_name], capture_output=True)
            
            # Criar hook
            os.chdir(project_name)
            result = subprocess.run(
                ["pyreact", "generate", "hook", "useCounter"],
                capture_output=True,
                text=True
            )
            
            # Verificar se hook foi criado
            assert result.returncode == 0
            assert Path("src/hooks/useCounter.py").exists()
            
        finally:
            os.chdir(original_dir)


class TestPyReactRendering:
    """Testes de renderização do PyReact"""
    
    def test_vnode_creation(self):
        """Testa criação de VNode"""
        from pyreact import h
        
        # Criar elemento simples
        element = h("div", {"className": "test"}, "Hello")
        
        assert element.type == "div"
        assert element.props["className"] == "test"
        assert len(element.children) == 1
        assert element.children[0] == "Hello"
    
    def test_nested_elements(self):
        """Testa elementos aninhados"""
        from pyreact import h
        
        # Criar elementos aninhados
        element = h("div", None,
            h("h1", None, "Title"),
            h("p", None, "Paragraph")
        )
        
        assert element.type == "div"
        assert len(element.children) == 2
        assert element.children[0].type == "h1"
        assert element.children[1].type == "p"
    
    def test_component_creation(self):
        """Testa criação de componente"""
        from pyreact import Component
        
        class TestComponent(Component):
            def render(self):
                return h("div", None, "Test")
        
        component = TestComponent({"title": "Test"})
        assert component.props["title"] == "Test"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
