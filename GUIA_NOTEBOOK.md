# Análise de Probabilidades JDB — Guia Rápido

## 📋 O que foi entregue

Um **notebook Jupyter completo e operacional** (`analise_probabilidades_operacional.ipynb`) que implementa um pipeline de análise de probabilidades focado em:
- **Capacidade**: Dados reais (cache do pernambucoaval)
- **Clareza**: Métricas quantificadas e auditáveis
- **Certeza**: Intervalos credíveis, testes estatísticos, calibração

---

## 🔄 Pipeline Implementado

### 1. **ETL — Extração e Limpeza**
- Carrega `cache_results.json`
- Valida completude, duplicatas, range de grupos
- Retorna dataset limpo pronto para análise

### 2. **Análise de Qualidade de Dados**
- **Distribuição** por dezena (0–99), grupo (1–25), último dígito
- **Teste Chi-square** de uniformidade (H0: distribuição é uniforme)
- **Coeficiente de variação** para detectar assimetrias
- **Q-Q plot** para normalidade

### 3. **Modelos Probabilísticos**

#### a) **Poisson (Contagens)**
- Estima λ (taxa de aparição por dezena)
- Verifica overdispersão (Var/Média)
- Identifica se modelo é apropriado

#### b) **Bayesiano Hierárquico (Beta-Binomial)**
- Usa PyMC para amostrar posterior
- Implementa pooling parcial (regularização)
- Gera intervalos credíveis 95% por dezena/grupo
- Reduz variância comparado a MLE puro

#### c) **Intervalos de Confiança (Clopper-Pearson)**
- Método exato para proporções binomiais
- Garante cobertura verdadeira (não assintótico)

### 4. **Calibração e Métricas de Certeza**
- **Brier Score**: erro quadrático médio (0 = perfeito)
- **Log-Loss**: penalidade de probabilidade
- **Reliability Diagram**: visual de calibração
- **Calibration Error (MAE)**

### 5. **Walk-Forward Backtest**
- Treina em 70% histórico, valida em 30%
- **Sem lookahead bias**: modelo usa apenas dados passados
- Computa **Mean Log-Likelihood** e **Perplexity** no test set

### 6. **VaR/CVaR — Risco**
- Simula P&L de estratégia (10.000 Monte Carlo, 100 rodadas)
- **VaR_95%**: pior cenário 5%
- **CVaR_95%**: média das 5% piores perdas
- **Win Rate**: % de simulações com lucro
- **Sharpe Ratio**: retorno/risco

### 7. **Relatório Final**
- Sumário de dados, uniformidade, modelos, risco
- Recomendações acionáveis
- Alertas críticos
- Exporta em JSON

---

## 🚀 Como Usar

### Pré-requisitos
```bash
pip install pandas numpy matplotlib seaborn statsmodels scikit-learn scipy pymc
```

### Executar
1. Abra `analise_probabilidades_operacional.ipynb` no Jupyter
2. Execute célula por célula
3. Leia o relatório final (última célula)

Ou via terminal:
```bash
jupyter notebook analise_probabilidades_operacional.ipynb
```

---

## 📊 Saídas Esperadas

### Gráficos
- Distribuição por dezena, grupo, último dígito
- Q-Q plot (normalidade)
- Reliability diagram (calibração)
- Histograma P&L (Monte Carlo)
- CDF do P&L com VaR

### Tabelas
- Estatísticas de frequência (min, max, média, CV)
- Intervalos de confiança (top-5 dezenas)
- Summary posterior (Bayesiano)
- Walk-forward performance

### Relatório JSON
- `relatorio_analise_probabilidades.json`
  - Qualidade de dados
  - Testes de uniformidade
  - Métricas de modelos
  - Probabilidades posteriores (todas dezenas/grupos)
  - Risco (VaR, CVaR, Sharpe)

---

## 🎯 Interpretação das Métricas

| Métrica | Bom | Ruim | Interpretação |
|---------|-----|------|---------------|
| **p-value (Chi-square)** | > 0.05 | < 0.05 | Uniforme ✓ vs. viés detectado ⚠ |
| **Brier Score** | < 0.15 | > 0.25 | Calibração boa vs. má |
| **Log-Loss** | < 0.69 | > 0.69 | Melhor que aleatório vs. pior |
| **Calibration Error** | < 0.05 | > 0.1 | Bem calibrado vs. descalibrado |
| **VaR_95%** | > 0 (lucro) | < 0 (perda) | Cenário 5% é ganho vs. perda |
| **Win Rate** | > 50% | < 50% | Mais ganhos vs. mais perdas |
| **Sharpe Ratio** | > 0 | < 0 | Retorno justifica risco vs. não |

---

## ⚠️ Limitações e Avisos

1. **Dados únicos**: análise baseada em 1 coleta (pernambucoaval). Para decisões, coletar histórico temporal.
2. **Período**: amostra atual é um "snapshot". Padrões podem variar no tempo.
3. **Modelo assume aleatoriedade**: Chi-square testa uniformidade. Se rejeitar, pode indicar:
   - Manipulação
   - Viés de coleta
   - Período insuficiente
4. **Monte Carlo simplificado**: simulação assume prob uniforme para próximas rodadas (não usa histórico).
5. **Estratégia demo**: apostas em top-5 grupos é exemplo. Otimizar com Kelly Criterion antes de usar.

---

## 🔍 Próximos Passos Recomendados

1. **Histórico temporal**: coletar dados com timestamps (data/hora de cada sorteio)
2. **Modelos avançados**:
   - AR(1) em logit para dependência temporal
   - HMM para detectar regimes (mudanças estruturais)
   - Hawkes process se houve "clustering" de eventos
3. **Dados externos**: se disponível, incorporar:
   - Padrões de apostas (se acesso)
   - Notícias/eventos locais (NLP)
4. **Validação contínua**: reestimar modelo a cada nova coleta, acompanhar drift
5. **Otimização**: usar Kelly Criterion para dimensionar stakes baseado em confiança

---

## 📝 Arquivos Gerados

- `analise_probabilidades_operacional.ipynb` — Notebook completo
- `relatorio_analise_probabilidades.json` — Saída estruturada (usa após rodar notebook)

---

## 📞 Suporte

Se modelos não rodarem:
- Verificar PyMC instalado: `python -c "import pymc; print(pymc.__version__)"`
- Se amostragem lenta, reduzir `tune=1000` para `tune=500`
- Para dados grandes, considerar Stan em vez de PyMC

Dúvidas sobre interpretação? Revisar seção "Interpretação das Métricas" acima.

---

**Versão**: 1.0  
**Data**: 3 de Dezembro de 2025  
**Status**: Pronto para uso operacional
