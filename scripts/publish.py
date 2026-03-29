#!/usr/bin/env python3
"""
Script de Publicação - PyReact
===============================

Este script automatiza o processo de build e publicação do PyReact no PyPI.
"""

import subprocess
import sys
import os
from pathlib import Path


def run_command(cmd, check=True):
    """Executa comando e retorna resultado"""
    print(f"\n> {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr)
    
    if check and result.returncode != 0:
        print(f"\n[ERROR] Comando falhou com código {result.returncode}")
        sys.exit(1)
    
    return result


def clean_build():
    """Limpa arquivos de build anteriores"""
    print("\n" + "="*60)
    print("LIMPANDO BUILDS ANTERIORES")
    print("="*60)
    
    dirs_to_clean = ['build', 'dist', 'pyreact.egg-info']
    for dir_name in dirs_to_clean:
        if Path(dir_name).exists():
            import shutil
            shutil.rmtree(dir_name)
            print(f"[OK] Removido: {dir_name}")
    
    print("[OK] Limpeza concluída")


def create_build():
    """Cria nova build"""
    print("\n" + "="*60)
    print("CRIANDO BUILD")
    print("="*60)
    
    run_command([sys.executable, "-m", "build"])
    
    print("\n[OK] Build criada com sucesso")


def check_build():
    """Verifica se a build está correta"""
    print("\n" + "="*60)
    print("VERIFICANDO BUILD")
    print("="*60)
    
    result = run_command(["twine", "check", "dist/*"])
    
    if "Failed" in result.stdout or "Failed" in result.stderr:
        print("\n[ERROR] Verificação falhou")
        return False
    
    print("\n[OK] Build verificada com sucesso")
    return True


def upload_testpypi():
    """Faz upload para TestPyPI"""
    print("\n" + "="*60)
    print("UPLOAD PARA TESTPYPI")
    print("="*60)
    
    print("\n[INFO] Isso vai publicar no TestPyPI para testes")
    response = input("Continuar? (y/n): ")
    
    if response.lower() != 'y':
        print("[CANCEL] Operação cancelada")
        return False
    
    run_command(["twine", "upload", "--repository", "testpypi", "dist/*"])
    
    print("\n[OK] Upload para TestPyPI concluído")
    print("\nPara testar:")
    print("  pip install --index-url https://test.pypi.org/simple/ pyreact")
    
    return True


def upload_pypi():
    """Faz upload para PyPI"""
    print("\n" + "="*60)
    print("UPLOAD PARA PYPI")
    print("="*60)
    
    print("\n[WARNING] Isso vai publicar no PyPI oficial!")
    print("[WARNING] Esta ação é IRREVERSÍVEL!")
    response = input("Tem certeza? (yes/no): ")
    
    if response.lower() != 'yes':
        print("[CANCEL] Operação cancelada")
        return False
    
    run_command(["twine", "upload", "dist/*"])
    
    print("\n[OK] Upload para PyPI concluído")
    print("\nPara instalar:")
    print("  pip install pyreact")
    
    return True


def main():
    """Função principal"""
    print("="*60)
    print("PUBLICAÇÃO DO PYREACT")
    print("="*60)
    
    # Verificar se twine está instalado
    try:
        subprocess.run(["twine", "--version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("\n[ERROR] Twine não instalado")
        print("Instale com: pip install twine")
        sys.exit(1)
    
    # Menu de opções
    print("\nO que você quer fazer?")
    print("1. Limpar e criar build")
    print("2. Verificar build")
    print("3. Upload para TestPyPI")
    print("4. Upload para PyPI")
    print("5. Processo completo (limpar, build, verificar, TestPyPI)")
    print("6. Processo completo (limpar, build, verificar, PyPI)")
    print("0. Sair")
    
    choice = input("\nEscolha uma opção: ")
    
    if choice == '1':
        clean_build()
        create_build()
    elif choice == '2':
        check_build()
    elif choice == '3':
        upload_testpypi()
    elif choice == '4':
        upload_pypi()
    elif choice == '5':
        clean_build()
        create_build()
        if check_build():
            upload_testpypi()
    elif choice == '6':
        clean_build()
        create_build()
        if check_build():
            upload_pypi()
    elif choice == '0':
        print("\n[OK] Saindo...")
        return
    else:
        print("\n[ERROR] Opção inválida")
        return
    
    print("\n" + "="*60)
    print("CONCLUÍDO")
    print("="*60)


if __name__ == "__main__":
    main()
