"""
Teste E2E Simples para PyReact
==============================

Este script testa a funcionalidade basica do PyReact usando Playwright.
Pode ser executado diretamente: python tests/e2e/test_simple_e2e.py
"""

import subprocess
import time
import sys
from pathlib import Path

# Adicionar o diretorio raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    print("[WARN] Playwright nao instalado. Instalando...")
    subprocess.run([sys.executable, "-m", "pip", "install", "playwright"], capture_output=True)
    subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"], capture_output=True)
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_AVAILABLE = True


def create_test_project():
    """Cria projeto de teste"""
    print("\n[DIR] Criando projeto de teste...")
    result = subprocess.run(
        ["pyreact", "create", "test_e2e_project"],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print(f"[ERROR] Erro ao criar projeto: {result.stderr}")
        return False
    
    print("[OK] Projeto criado com sucesso")
    return True


def start_dev_server(port=3008):
    """Inicia servidor de desenvolvimento"""
    print(f"\n[SERVER] Iniciando servidor na porta {port}...")
    
    server_process = subprocess.Popen(
        ["pyreact", "dev", "--port", str(port)],
        cwd="test_e2e_project",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Aguardar servidor iniciar
    time.sleep(3)
    
    return server_process, f"http://localhost:{port}"


def run_e2e_tests(url):
    """Executa testes E2E"""
    print(f"\n[TEST] Executando testes E2E em {url}...")
    
    test_results = []
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        try:
            # Teste 1: Pagina carrega
            print("\n  Teste 1: Verificando se a pagina carrega...")
            page.goto(url, timeout=10000)
            page.wait_for_load_state("networkidle")
            
            title = page.title()
            if "PyReact App" in title:
                print("  [PASS] Pagina carregou corretamente")
                test_results.append(("Pagina carrega", True))
            else:
                print(f"  [FAIL] Titulo incorreto: {title}")
                test_results.append(("Pagina carrega", False))
            
            # Teste 2: Elemento root existe
            print("\n  Teste 2: Verificando elemento root...")
            root = page.query_selector("#root")
            if root:
                print("  [PASS] Elemento #root encontrado")
                test_results.append(("Elemento root", True))
            else:
                print("  [FAIL] Elemento #root nao encontrado")
                test_results.append(("Elemento root", False))
            
            # Teste 3: Titulo principal
            print("\n  Teste 3: Verificando titulo principal...")
            h1 = page.locator("h1")
            h1_text = h1.text_content()
            if h1_text == "Welcome to PyReact!":
                print("  [PASS] Titulo correto")
                test_results.append(("Titulo principal", True))
            else:
                print(f"  [FAIL] Titulo incorreto: {h1_text}")
                test_results.append(("Titulo principal", False))
            
            # Teste 4: Contador inicial
            print("\n  Teste 4: Verificando contador inicial...")
            counter = page.locator(".counter span")
            counter_text = counter.text_content()
            if "Count: 0" in counter_text:
                print("  [PASS] Contador inicial correto")
                test_results.append(("Contador inicial", True))
            else:
                print(f"  [FAIL] Contador incorreto: {counter_text}")
                test_results.append(("Contador inicial", False))
            
            # Teste 5: Incremento
            print("\n  Teste 5: Testando incremento...")
            increment_btn = page.locator("button:has-text('+')")
            increment_btn.click()
            time.sleep(0.5)
            
            counter_text = counter.text_content()
            if "Count: 1" in counter_text:
                print("  [PASS] Incremento funcionou")
                test_results.append(("Incremento", True))
            else:
                print(f"  [FAIL] Incremento falhou: {counter_text}")
                test_results.append(("Incremento", False))
            
            # Teste 6: Decremento
            print("\n  Teste 6: Testando decremento...")
            decrement_btn = page.locator("button:has-text('-')")
            decrement_btn.click()
            time.sleep(0.5)
            
            counter_text = counter.text_content()
            if "Count: 0" in counter_text:
                print("  [PASS] Decremento funcionou")
                test_results.append(("Decremento", True))
            else:
                print(f"  [FAIL] Decremento falhou: {counter_text}")
                test_results.append(("Decremento", False))
            
            # Teste 7: Multiplos cliques
            print("\n  Teste 7: Testando multiplos cliques...")
            for _ in range(5):
                increment_btn.click()
            time.sleep(0.5)
            
            counter_text = counter.text_content()
            if "Count: 5" in counter_text:
                print("  [PASS] Multiplos incrementos funcionaram")
                test_results.append(("Multiplos cliques", True))
            else:
                print(f"  [FAIL] Multiplos incrementos falharam: {counter_text}")
                test_results.append(("Multiplos cliques", False))
            
            # Teste 8: Estrutura da pagina
            print("\n  Teste 8: Verificando estrutura da pagina...")
            app_div = page.locator(".app")
            if app_div.is_visible():
                print("  [PASS] Estrutura correta")
                test_results.append(("Estrutura", True))
            else:
                print("  [FAIL] Estrutura incorreta")
                test_results.append(("Estrutura", False))
            
        except Exception as e:
            print(f"\n[ERROR] Erro durante os testes: {e}")
            test_results.append(("Execucao", False))
        
        finally:
            browser.close()
    
    return test_results


def generate_report(test_results):
    """Gera relatorio de testes"""
    print("\n" + "="*60)
    print("RELATORIO DE TESTES E2E")
    print("="*60)
    
    passed = sum(1 for _, result in test_results if result)
    failed = sum(1 for _, result in test_results if not result)
    total = len(test_results)
    
    print(f"\nTotal de testes: {total}")
    print(f"[PASS] Passou: {passed}")
    print(f"[FAIL] Falhou: {failed}")
    print(f"Taxa de sucesso: {(passed/total*100):.1f}%")
    
    print("\nDetalhes:")
    for test_name, result in test_results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"  {test_name}: {status}")
    
    print("\n" + "="*60)
    
    return passed, failed, total


def save_report(test_results, passed, failed, total):
    """Salva relatorio em arquivo"""
    from datetime import datetime
    
    report_dir = Path("Teste_Documentos")
    report_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = report_dir / f"e2e_test_report_{timestamp}.md"
    
    with open(report_file, "w", encoding="utf-8") as f:
        f.write("# Relatorio de Testes E2E - PyReact\n\n")
        f.write(f"**Data:** {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n\n")
        f.write("## Resumo\n\n")
        f.write(f"- **Total de testes:** {total}\n")
        f.write(f"- **Passou:** {passed}\n")
        f.write(f"- **Falhou:** {failed}\n")
        f.write(f"- **Taxa de sucesso:** {(passed/total*100):.1f}%\n\n")
        f.write("## Detalhes dos Testes\n\n")
        f.write("| Teste | Resultado |\n")
        f.write("|-------|----------|\n")
        
        for test_name, result in test_results:
            status = "[PASS]" if result else "[FAIL]"
            f.write(f"| {test_name} | {status} |\n")
        
        f.write("\n## Conclusao\n\n")
        if failed == 0:
            f.write("[OK] Todos os testes passaram com sucesso!\n")
        else:
            f.write(f"[WARN] {failed} teste(s) falharam. Verifique os erros acima.\n")
    
    print(f"\n[REPORT] Relatorio salvo em: {report_file}")


def cleanup():
    """Limpa arquivos de teste"""
    import shutil
    
    print("\n[CLEANUP] Limpando arquivos de teste...")
    
    # Remover projeto de teste
    test_project = Path("test_e2e_project")
    if test_project.exists():
        shutil.rmtree(test_project)
        print("[OK] Projeto de teste removido")


def main():
    """Funcao principal"""
    print("="*60)
    print("TESTES E2E - PyReact")
    print("="*60)
    
    try:
        # Criar projeto
        if not create_test_project():
            return 1
        
        # Iniciar servidor
        server_process, url = start_dev_server()
        
        # Executar testes
        test_results = run_e2e_tests(url)
        
        # Gerar relatorio
        passed, failed, total = generate_report(test_results)
        
        # Salvar relatorio
        save_report(test_results, passed, failed, total)
        
        # Parar servidor
        print("\n[SERVER] Parando servidor...")
        server_process.terminate()
        try:
            server_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            server_process.kill()
        
        # Cleanup
        cleanup()
        
        print("\n[OK] Testes E2E concluidos!")
        
        # Retornar codigo de saida
        return 0 if failed == 0 else 1
        
    except Exception as e:
        print(f"\n[ERROR] Erro fatal: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code if exit_code is not None else 1)
