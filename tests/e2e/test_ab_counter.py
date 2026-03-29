"""
Teste A/B - PyReact Counter
===========================

Este script realiza testes A/B comparando diferentes implementações
do contador para identificar a melhor versão em termos de:
- Performance
- Usabilidade
- Estabilidade

Métricas coletadas:
- Tempo de resposta ao clique
- Número de erros
- Memória utilizada
- Experiência do usuário
"""

import subprocess
import time
import sys
import json
from pathlib import Path
from datetime import datetime
import statistics

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("⚠ Playwright não instalado. Instalando...")
    subprocess.run([sys.executable, "-m", "pip", "install", "playwright"], capture_output=True)
    subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"], capture_output=True)
    from playwright.sync_api import sync_playwright


class ABTestResult:
    """Resultado de um teste A/B"""
    
    def __init__(self, variant_name: str):
        self.variant_name = variant_name
        self.click_times = []
        self.errors = []
        self.memory_usage = []
        self.user_interactions = 0
        self.successful_interactions = 0
    
    def add_click_time(self, time_ms: float):
        """Adiciona tempo de clique"""
        self.click_times.append(time_ms)
    
    def add_error(self, error: str):
        """Adiciona erro"""
        self.errors.append(error)
    
    def add_memory_usage(self, usage: float):
        """Adiciona uso de memória"""
        self.memory_usage.append(usage)
    
    def record_interaction(self, success: bool):
        """Registra interação"""
        self.user_interactions += 1
        if success:
            self.successful_interactions += 1
    
    @property
    def avg_click_time(self) -> float:
        """Tempo médio de clique"""
        return statistics.mean(self.click_times) if self.click_times else 0
    
    @property
    def success_rate(self) -> float:
        """Taxa de sucesso"""
        if self.user_interactions == 0:
            return 0
        return (self.successful_interactions / self.user_interactions) * 100
    
    def to_dict(self):
        """Converte para dicionário"""
        return {
            "variant": self.variant_name,
            "avg_click_time_ms": round(self.avg_click_time, 2),
            "total_interactions": self.user_interactions,
            "successful_interactions": self.successful_interactions,
            "success_rate": round(self.success_rate, 2),
            "total_errors": len(self.errors),
            "avg_memory_mb": round(statistics.mean(self.memory_usage), 2) if self.memory_usage else 0
        }


def create_variant_a():
    """Cria variante A: Contador padrão"""
    print("\n📦 Criando Variante A (Contador Padrão)...")
    
    result = subprocess.run(
        ["pyreact", "create", "variant_a"],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print(f"❌ Erro: {result.stderr}")
        return False
    
    print("✅ Variante A criada")
    return True


def create_variant_b():
    """Cria variante B: Contador com feedback visual"""
    print("\n📦 Criando Variante B (Contador com Feedback Visual)...")
    
    result = subprocess.run(
        ["pyreact", "create", "variant_b"],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print(f"❌ Erro: {result.stderr}")
        return False
    
    # Modificar HTML para incluir feedback visual
    html_path = Path("variant_b/public/index.html")
    if html_path.exists():
        html_content = html_path.read_text(encoding='utf-8')
        
        # Adicionar animação CSS
        animation_css = """
        <style>
            .counter button {
                transition: transform 0.1s ease, background-color 0.2s ease;
            }
            .counter button:active {
                transform: scale(0.95);
                background-color: #e0e0e0;
            }
            .counter span {
                transition: font-size 0.2s ease;
            }
            .counter span.highlight {
                font-size: 1.2em;
                color: #4CAF50;
            }
        </style>
        """
        
        # Adicionar highlight no JavaScript
        highlight_js = """
        function highlightCounter() {
            const span = document.querySelector('.counter span');
            span.classList.add('highlight');
            setTimeout(() => span.classList.remove('highlight'), 300);
        }
        """
        
        # Modificar onClick para incluir highlight
        html_content = html_content.replace(
            "setCount(count + 1)",
            "setCount(count + 1); highlightCounter()"
        )
        html_content = html_content.replace(
            "setCount(count - 1)",
            "setCount(count - 1); highlightCounter()"
        )
        
        # Adicionar estilos e scripts
        html_content = html_content.replace("</style>", animation_css + "</style>")
        html_content = html_content.replace("// State management", highlight_js + "\n\n        // State management")
        
        html_path.write_text(html_content, encoding='utf-8')
    
    print("✅ Variante B criada com feedback visual")
    return True


def run_ab_test(variant: str, port: int, num_interactions: int = 50) -> ABTestResult:
    """Executa teste A/B para uma variante"""
    
    result = ABTestResult(f"Variante {variant.upper()}")
    
    print(f"\n🧪 Testando {result.variant_name} (Porta: {port})...")
    
    # Iniciar servidor
    server_process = subprocess.Popen(
        ["pyreact", "dev", "--port", str(port)],
        cwd=f"variant_{variant}",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    time.sleep(3)
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            # Ir para página
            url = f"http://localhost:{port}"
            page.goto(url, timeout=10000)
            page.wait_for_load_state("networkidle")
            
            # Executar interações
            increment_btn = page.locator("button:has-text('+')")
            decrement_btn = page.locator("button:has-text('-')")
            counter = page.locator(".counter span")
            
            expected_value = 0
            
            for i in range(num_interactions):
                # Alternar entre incremento e decremento
                if i % 2 == 0:
                    # Incremento
                    start_time = time.time()
                    increment_btn.click()
                    end_time = time.time()
                    expected_value += 1
                else:
                    # Decremento
                    start_time = time.time()
                    decrement_btn.click()
                    end_time = time.time()
                    expected_value -= 1
                
                # Medir tempo de resposta
                click_time_ms = (end_time - start_time) * 1000
                result.add_click_time(click_time_ms)
                
                # Verificar resultado
                time.sleep(0.1)
                counter_text = counter.text_content()
                actual_value = int(counter_text.replace("Count: ", ""))
                
                if actual_value == expected_value:
                    result.record_interaction(True)
                else:
                    result.record_interaction(False)
                    result.add_error(f"Valor incorreto: esperado {expected_value}, obtido {actual_value}")
                
                # Medir memória (simulado)
                metrics = page.evaluate("() => ({ heapSize: performance.memory ? performance.memory.usedJSHeapSize : 0 })")
                if metrics.get("heapSize", 0) > 0:
                    result.add_memory_usage(metrics["heapSize"] / (1024 * 1024))  # MB
            
            browser.close()
    
    except Exception as e:
        result.add_error(str(e))
    
    finally:
        # Parar servidor
        server_process.terminate()
        try:
            server_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            server_process.kill()
    
    return result


def compare_results(result_a: ABTestResult, result_b: ABTestResult):
    """Compara resultados dos testes A/B"""
    
    print("\n" + "="*70)
    print("📊 RESULTADOS DO TESTE A/B")
    print("="*70)
    
    print(f"\n{'Métrica':<30} {'Variante A':<20} {'Variante B':<20} {'Melhor'}")
    print("-" * 70)
    
    # Tempo médio de clique
    avg_time_a = result_a.avg_click_time
    avg_time_b = result_b.avg_click_time
    better_time = "A" if avg_time_a < avg_time_b else "B"
    print(f"{'Tempo médio de clique (ms)':<30} {avg_time_a:<20.2f} {avg_time_b:<20.2f} {better_time}")
    
    # Taxa de sucesso
    success_a = result_a.success_rate
    success_b = result_b.success_rate
    better_success = "A" if success_a > success_b else "B"
    print(f"{'Taxa de sucesso (%)':<30} {success_a:<20.2f} {success_b:<20.2f} {better_success}")
    
    # Total de erros
    errors_a = len(result_a.errors)
    errors_b = len(result_b.errors)
    better_errors = "A" if errors_a < errors_b else "B"
    print(f"{'Total de erros':<30} {errors_a:<20} {errors_b:<20} {better_errors}")
    
    # Interações bem-sucedidas
    successful_a = result_a.successful_interactions
    successful_b = result_b.successful_interactions
    better_successful = "A" if successful_a > successful_b else "B"
    print(f"{'Interações bem-sucedidas':<30} {successful_a:<20} {successful_b:<20} {better_successful}")
    
    # Memória média
    mem_a = statistics.mean(result_a.memory_usage) if result_a.memory_usage else 0
    mem_b = statistics.mean(result_b.memory_usage) if result_b.memory_usage else 0
    better_mem = "A" if mem_a < mem_b else "B"
    print(f"{'Memória média (MB)':<30} {mem_a:<20.2f} {mem_b:<20.2f} {better_mem}")
    
    print("\n" + "="*70)
    
    # Determinar vencedor
    scores = {"A": 0, "B": 0}
    if avg_time_a < avg_time_b:
        scores["A"] += 1
    else:
        scores["B"] += 1
    
    if success_a > success_b:
        scores["A"] += 1
    else:
        scores["B"] += 1
    
    if errors_a < errors_b:
        scores["A"] += 1
    else:
        scores["B"] += 1
    
    if mem_a < mem_b:
        scores["A"] += 1
    else:
        scores["B"] += 1
    
    winner = "A" if scores["A"] > scores["B"] else "B"
    
    print(f"\n🏆 VENCEDOR: Variante {winner}")
    print(f"   Pontuação: A={scores['A']} | B={scores['B']}")
    
    return winner, scores


def save_ab_report(result_a: ABTestResult, result_b: ABTestResult, winner: str, scores: dict):
    """Salva relatório A/B"""
    
    report_dir = Path("Teste_Documentos")
    report_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = report_dir / f"ab_test_report_{timestamp}.md"
    
    with open(report_file, "w", encoding="utf-8") as f:
        f.write("# Relatório de Teste A/B - PyReact Counter\n\n")
        f.write(f"**Data:** {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n\n")
        
        f.write("## Resumo\n\n")
        f.write(f"- **Vencedor:** Variante {winner}\n")
        f.write(f"- **Pontuação:** A={scores['A']} | B={scores['B']}\n\n")
        
        f.write("## Variante A - Contador Padrão\n\n")
        f.write(f"- Tempo médio de clique: {result_a.avg_click_time:.2f}ms\n")
        f.write(f"- Taxa de sucesso: {result_a.success_rate:.2f}%\n")
        f.write(f"- Total de erros: {len(result_a.errors)}\n")
        f.write(f"- Interações bem-sucedidas: {result_a.successful_interactions}/{result_a.user_interactions}\n\n")
        
        f.write("## Variante B - Contador com Feedback Visual\n\n")
        f.write(f"- Tempo médio de clique: {result_b.avg_click_time:.2f}ms\n")
        f.write(f"- Taxa de sucesso: {result_b.success_rate:.2f}%\n")
        f.write(f"- Total de erros: {len(result_b.errors)}\n")
        f.write(f"- Interações bem-sucedidas: {result_b.successful_interactions}/{result_b.user_interactions}\n\n")
        
        f.write("## Comparação Detalhada\n\n")
        f.write("| Métrica | Variante A | Variante B | Diferença |\n")
        f.write("|---------|------------|------------|----------|\n")
        
        diff_time = result_a.avg_click_time - result_b.avg_click_time
        f.write(f"| Tempo médio (ms) | {result_a.avg_click_time:.2f} | {result_b.avg_click_time:.2f} | {diff_time:+.2f} |\n")
        
        diff_success = result_a.success_rate - result_b.success_rate
        f.write(f"| Taxa sucesso (%) | {result_a.success_rate:.2f} | {result_b.success_rate:.2f} | {diff_success:+.2f} |\n")
        
        diff_errors = len(result_a.errors) - len(result_b.errors)
        f.write(f"| Total erros | {len(result_a.errors)} | {len(result_b.errors)} | {diff_errors:+d} |\n")
        
        f.write("\n## Conclusão\n\n")
        f.write(f"A **Variante {winner}** apresentou melhor performance geral.\n\n")
        
        if winner == "B":
            f.write("**Recomendação:** Implementar feedback visual em todos os componentes interativos.\n")
        else:
            f.write("**Recomendação:** Manter implementação atual, sem feedback visual adicional.\n")
    
    print(f"\n📄 Relatório A/B salvo em: {report_file}")


def cleanup():
    """Limpa arquivos de teste"""
    import shutil
    
    print("\n🧹 Limpando arquivos de teste...")
    
    for variant in ["a", "b"]:
        variant_dir = Path(f"variant_{variant}")
        if variant_dir.exists():
            shutil.rmtree(variant_dir)
    
    print("✅ Arquivos de teste removidos")


def main():
    """Função principal"""
    print("="*70)
    print("🧪 TESTE A/B - PyReact Counter")
    print("="*70)
    
    try:
        # Criar variantes
        if not create_variant_a():
            return 1
        
        if not create_variant_b():
            return 1
        
        # Executar testes
        print("\n📊 Executando testes com 50 interações cada...")
        
        result_a = run_ab_test("a", 3010, num_interactions=50)
        result_b = run_ab_test("b", 3011, num_interactions=50)
        
        # Comparar resultados
        winner, scores = compare_results(result_a, result_b)
        
        # Salvar relatório
        save_ab_report(result_a, result_b, winner, scores)
        
        # Cleanup
        cleanup()
        
        print("\n✅ Teste A/B concluído!")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Erro fatal: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code if exit_code is not None else 1)
