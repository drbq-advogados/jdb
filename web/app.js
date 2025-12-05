(function(){
  const data = window.LANDING_DATA || {};
  const resumo = data.resumo || {};
  const ranking = data.ranking_dezenas || [];
  const top10 = data.top_10 || [];
  const bottom5 = data.bottom_5 || [];
  const grupos = data.grupos || [];
  const recomendacoes = data.recomendacoes || {};

  // ============= METADATA =============
  const genDate = new Date(data.generated_at);
  const dateStr = genDate.toLocaleString('pt-BR');
  document.getElementById('meta_sorteios').textContent = `📍 ${resumo.total_sorteios || 0} sorteios`;
  document.getElementById('meta_data').textContent = resumo.data_coleta ? `📅 ${resumo.data_coleta}` : '';
  document.getElementById('meta_generated').textContent = `⏰ Gerado: ${dateStr}`;
  document.getElementById('footer_generated_at').textContent = dateStr;

  // ============= RESUMO ESTATÍSTICO =============
  const dezena_mais = resumo.dezena_mais_sorteada || {};
  const dezena_menos = resumo.dezena_menos_sorteada || {};
  const grupo_mais = resumo.grupo_mais_sorteado || {};
  const grupo_menos = resumo.grupo_menos_sorteado || {};
  const chi2 = resumo.chi2_teste || {};

  document.getElementById('resumo_total').textContent = resumo.total_sorteios || '—';
  document.getElementById('resumo_mais_dezena').textContent = dezena_mais.dezena || '—';
  document.getElementById('resumo_mais_dezena_freq').textContent = `${dezena_mais.frequencia || 0}x (${dezena_mais.percentual || 0}%)`;
  document.getElementById('resumo_menos_dezena').textContent = dezena_menos.dezena || '—';
  document.getElementById('resumo_menos_dezena_freq').textContent = `${dezena_menos.frequencia || 0}x (${dezena_menos.percentual || 0}%)`;
  document.getElementById('resumo_mais_grupo').textContent = grupo_mais.animal || '—';
  document.getElementById('resumo_mais_grupo_freq').textContent = `${grupo_mais.frequencia || 0}x (${grupo_mais.percentual || 0}%)`;
  document.getElementById('resumo_menos_grupo').textContent = grupo_menos.animal || '—';
  document.getElementById('resumo_menos_grupo_freq').textContent = `${grupo_menos.frequencia || 0}x (${grupo_menos.percentual || 0}%)`;
  document.getElementById('resumo_chi2').textContent = `χ² = ${chi2.estatistica || 0}`;
  document.getElementById('resumo_chi2_result').textContent = `p=${chi2.p_value || 0}  →  ${chi2.resultado || '?'}`;

  // ============= RANKING DE DEZENAS =============
  let rankingData = [...ranking];
  const renderRanking = () => {
    const tbody = document.getElementById('ranking_tbody');
    tbody.innerHTML = '';
    rankingData.forEach((item, idx) => {
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td>${idx + 1}</td>
        <td><strong>${item.dezena}</strong></td>
        <td>${item.frequencia}</td>
        <td>${(item.probabilidade * 100).toFixed(2)}%</td>
        <td>${item.percentual}%</td>
      `;
      tbody.appendChild(tr);
    });
  };

  const searchInput = document.getElementById('ranking_search');
  const sortSelect = document.getElementById('ranking_sort');

  searchInput.addEventListener('input', (e) => {
    const query = e.target.value.toLowerCase();
    rankingData = ranking.filter(item => item.dezena.includes(query));
    renderRanking();
  });

  sortSelect.addEventListener('change', (e) => {
    const val = e.target.value;
    if (val === 'freq_desc') rankingData.sort((a, b) => b.frequencia - a.frequencia);
    else if (val === 'freq_asc') rankingData.sort((a, b) => a.frequencia - b.frequencia);
    else if (val === 'prob_desc') rankingData.sort((a, b) => b.probabilidade - a.probabilidade);
    renderRanking();
  });

  renderRanking();

  // ============= TOP 10 E BOTTOM 5 =============
  const renderTopBottom = () => {
    const top10_tbody = document.getElementById('top10_tbody');
    top10_tbody.innerHTML = '';
    top10.forEach(item => {
      const tr = document.createElement('tr');
      tr.innerHTML = `<td>${item.dezena}</td><td>${item.frequencia}</td><td>${item.percentual}%</td>`;
      top10_tbody.appendChild(tr);
    });

    const bottom5_tbody = document.getElementById('bottom5_tbody');
    bottom5_tbody.innerHTML = '';
    bottom5.forEach(item => {
      const tr = document.createElement('tr');
      tr.innerHTML = `<td>${item.dezena}</td><td>${item.frequencia}</td><td>${item.percentual}%</td>`;
      bottom5_tbody.appendChild(tr);
    });
  };
  renderTopBottom();

  // ============= GRUPOS (ANIMAIS) =============
  const renderGrupos = () => {
    const tbody = document.getElementById('grupos_tbody');
    tbody.innerHTML = '';
    grupos.forEach(item => {
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td>${item.grupo}</td>
        <td>${item.animal}</td>
        <td>${item.frequencia}</td>
        <td>${(item.probabilidade * 100).toFixed(2)}%</td>
        <td>${item.percentual}%</td>
      `;
      tbody.appendChild(tr);
    });
  };
  renderGrupos();

  // ============= RECOMENDAÇÕES =============
  const renderRecomendacoes = () => {
    const container = document.getElementById('recomendacoes_container');
    container.innerHTML = '';

    ['conservador', 'diversificado', 'contrarian'].forEach(key => {
      const rec = recomendacoes[key];
      if (!rec) return;
      const div = document.createElement('div');
      div.className = 'recom-card';
      div.innerHTML = `
        <h3>${rec.titulo}</h3>
        <p class="recom-desc">${rec.descricao}</p>
        <p class="recom-estrat"><em>${rec.estrategia}</em></p>
        <div class="recom-dezenas">
          ${rec.dezenas.map(dez => `<span class="badge">${dez}</span>`).join('')}
        </div>
      `;
      container.appendChild(div);
    });
  };
  renderRecomendacoes();

  // ============= PREDICTIVE BY GROUP =============
  const renderPredictiveByGroup = () => {
    const container = document.getElementById('predictive_container');
    container.innerHTML = '';
    const pbg = data.predictive_by_group || {};
    if (!pbg || Object.keys(pbg).length === 0) {
      container.innerHTML = '<p class="muted">Nenhum metadado condicional disponível nos dados.</p>';
      return;
    }

    Object.keys(pbg).forEach(groupKey => {
      const box = document.createElement('div');
      box.className = 'predictive-box';
      const mapping = pbg[groupKey];
      const values = Object.keys(mapping).sort();

      // header
      const header = document.createElement('div');
      header.innerHTML = `<h3>${groupKey}</h3>`;
      box.appendChild(header);

      // select
      const select = document.createElement('select');
      select.className = 'predictive-select';
      values.forEach(v => {
        const opt = document.createElement('option');
        opt.value = v;
        opt.textContent = `${v} (${mapping[v].count || 0})`;
        select.appendChild(opt);
      });
      box.appendChild(select);

      // table placeholder
      const table = document.createElement('table');
      table.className = 'small-table predictive-table';
      table.innerHTML = '<thead><tr><th>Dezena</th><th>Count</th><th>Probabilidade</th></tr></thead><tbody></tbody>';
      box.appendChild(table);

      const renderFor = (val) => {
        const info = mapping[val];
        const tbody = table.querySelector('tbody');
        tbody.innerHTML = '';
        if (!info) return;
        info.top.forEach(row => {
          const tr = document.createElement('tr');
          tr.innerHTML = `<td>${row.dezena}</td><td>${row.count}</td><td>${(row.prob*100).toFixed(2)}%</td>`;
          tbody.appendChild(tr);
        });
      };

      select.addEventListener('change', (e) => renderFor(e.target.value));
      // default
      if (values.length > 0) renderFor(values[0]);

      container.appendChild(box);
    });
  };
  renderPredictiveByGroup();

  // ============= EXPORT =============
  document.getElementById('export_json').addEventListener('click', () => {
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'jdb_landing_data.json';
    a.click();
    URL.revokeObjectURL(url);
  });

  document.getElementById('refresh_data').addEventListener('click', () => {
    alert('Para regenerar os dados, execute:\n\n  .\\.venv\\Scripts\\python.exe generate_landing_data.py\n\nEntão atualize esta página.');
  });
})();