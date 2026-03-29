#!/bin/bash
# Script de Publicação - PyReact
# ================================
# 
# Este script publica o PyReact no PyPI.
# Execute: bash publish.sh

echo "========================================"
echo "PUBLICAÇÃO DO PYREACT NO PYPI"
echo "========================================"

# Verificar se twine está instalado
if ! command -v twine &> /dev/null; then
    echo "[ERROR] Twine não instalado"
    echo "Instale com: pip install twine"
    exit 1
fi

# Verificar se há arquivos de build
if [ ! -d "dist" ] || [ -z "$(ls -A dist 2>/dev/null)" ]; then
    echo "[ERROR] Nenhum arquivo de build encontrado"
    echo "Execute: python -m build"
    exit 1
fi

echo ""
echo "[INFO] Arquivos de build encontrados:"
ls -lh dist/

echo ""
echo "[WARNING] Isso vai publicar no PyPI oficial!"
echo "[WARNING] Esta ação é IRREVERSÍVEL!"
echo ""
read -p "Tem certeza? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "[CANCEL] Operação cancelada"
    exit 0
fi

echo ""
echo "[INFO] Verificando build..."
twine check dist/*

if [ $? -ne 0 ]; then
    echo "[ERROR] Verificação falhou"
    exit 1
fi

echo ""
echo "[INFO] Publicando no PyPI..."
twine upload dist/*

if [ $? -eq 0 ]; then
    echo ""
    echo "========================================"
    echo "[SUCCESS] Publicado com sucesso!"
    echo "========================================"
    echo ""
    echo "Para instalar:"
    echo "  pip install pyreact"
    echo ""
    echo "Para verificar:"
    echo "  https://pypi.org/project/pyreact/"
    echo ""
else
    echo "[ERROR] Falha na publicação"
    exit 1
fi
