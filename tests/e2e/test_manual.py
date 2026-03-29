"""
Teste Manual Simples - PyReact
==============================

Este script cria um projeto e verifica se os arquivos foram criados corretamente.
"""

import subprocess
import sys
from pathlib import Path


def test_create_project():
    """Testa criacao de projeto"""
    print("\n[TEST] Criando projeto de teste...")
    
    result = subprocess.run(
        ["pyreact", "create", "manual_test_project"],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print(f"[FAIL] Erro ao criar projeto: {result.stderr}")
        return False
    
    print("[PASS] Projeto criado")
    
    # Verificar arquivos
    project_path = Path("manual_test_project")
    
    files_to_check = [
        "pyproject.toml",
        "README.md",
        "src/index.py",
        "src/__init__.py",
        "public/.gitkeep",
        "tests/test_app.py"
    ]
    
    print("\n[TEST] Verificando arquivos...")
    all_ok = True
    
    for file_path in files_to_check:
        full_path = project_path / file_path
        if full_path.exists():
            print(f"  [PASS] {file_path}")
        else:
            print(f"  [FAIL] {file_path} - nao encontrado")
            all_ok = False
    
    # Verificar conteudo do HTML gerado
    print("\n[TEST] Verificando HTML gerado...")
    
    # Iniciar servidor brevemente para gerar HTML
    server_process = subprocess.Popen(
        ["pyreact", "dev", "--port", "3020"],
        cwd="manual_test_project",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    import time
    time.sleep(2)
    
    # Verificar se HTML foi criado
    html_path = project_path / "public" / "index.html"
    if html_path.exists():
        print("[PASS] HTML gerado")
        
        # Verificar conteudo
        html_content = html_path.read_text(encoding='utf-8')
        
        checks = [
            ("DOCTYPE", "<!DOCTYPE html>" in html_content),
            ("Title", "PyReact App" in html_content),
            ("Root element", 'id="root"' in html_content),
            ("Counter", "Count:" in html_content),
            ("Buttons", "+" in html_content and "-" in html_content)
        ]
        
        print("\n[TEST] Verificando conteudo do HTML...")
        for check_name, check_result in checks:
            if check_result:
                print(f"  [PASS] {check_name}")
            else:
                print(f"  [FAIL] {check_name}")
                all_ok = False
    else:
        print("[FAIL] HTML nao foi gerado")
        all_ok = False
    
    # Parar servidor
    server_process.terminate()
    try:
        server_process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        server_process.kill()
    
    # Cleanup
    import shutil
    import time
    
    print("\n[CLEANUP] Removendo projeto de teste...")
    time.sleep(1)  # Aguardar processos liberarem arquivos
    
    try:
        shutil.rmtree(project_path)
    except PermissionError:
        print("[WARN] Nao foi possivel remover o projeto (arquivos em uso)")
    
    return all_ok


def test_cli_commands():
    """Testa comandos CLI"""
    print("\n[TEST] Testando comandos CLI...")
    
    # Criar projeto temporario
    subprocess.run(["pyreact", "create", "cli_test"], capture_output=True)
    
    # Testar geracao de componente
    print("\n[TEST] Gerando componente...")
    result = subprocess.run(
        ["pyreact", "generate", "component", "Button"],
        cwd="cli_test",
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0 and Path("cli_test/src/components/Button.py").exists():
        print("[PASS] Componente gerado")
    else:
        print("[FAIL] Componente nao gerado")
    
    # Testar geracao de hook
    print("\n[TEST] Gerando hook...")
    result = subprocess.run(
        ["pyreact", "generate", "hook", "useCounter"],
        cwd="cli_test",
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0 and Path("cli_test/src/hooks/useCounter.py").exists():
        print("[PASS] Hook gerado")
    else:
        print("[FAIL] Hook nao gerado")
    
    # Cleanup
    import shutil
    shutil.rmtree(Path("cli_test"))


def main():
    """Funcao principal"""
    print("="*60)
    print("TESTE MANUAL - PyReact")
    print("="*60)
    
    # Teste 1: Criacao de projeto
    result1 = test_create_project()
    
    # Teste 2: Comandos CLI
    test_cli_commands()
    
    print("\n" + "="*60)
    print("RESULTADO")
    print("="*60)
    
    if result1:
        print("[OK] Todos os testes passaram!")
        return 0
    else:
        print("[FAIL] Alguns testes falharam")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
