/**
 * equations-history web UI
 * Terminal-inspired navigation with equation display and visualizations
 */

const API_BASE = 'http://localhost:8000/api';

// State
const state = {
    currentTopic: null,
    currentEquation: null,
    topics: ['autoencoder', 'bert'],
    equations: {},
    selectedTopicIdx: 0,
    selectedEquationIdx: 0,
};

// Topics mapping
const topicNames = {
    autoencoder: 'Autoencoders',
    bert: 'BERT',
};

/**
 * Fetch equations from API
 */
async function fetchEquations() {
    try {
        for (const topic of state.topics) {
            const response = await fetch(`${API_BASE}/equations/${topic}`);
            if (response.ok) {
                state.equations[topic] = await response.json();
            }
        }
    } catch (error) {
        console.error('Failed to fetch equations:', error);
    }
}

/**
 * Render topic buttons
 */
function renderTopics() {
    const topicList = document.querySelector('.topic-list');
    topicList.innerHTML = '';

    state.topics.forEach((topic, idx) => {
        const li = document.createElement('li');
        const btn = document.createElement('button');
        btn.className = 'topic-btn';
        btn.textContent = topicNames[topic];
        btn.dataset.topic = topic;

        if (idx === state.selectedTopicIdx) {
            btn.classList.add('active');
        }

        btn.addEventListener('click', () => selectTopic(topic));
        li.appendChild(btn);
        topicList.appendChild(li);
    });
}

/**
 * Render equations for current topic
 */
function renderEquations() {
    const equationList = document.querySelector('#equation-list');
    const equationsSection = document.querySelector('#equations-section');

    if (!state.currentTopic || !state.equations[state.currentTopic]) {
        equationsSection.style.display = 'none';
        return;
    }

    equationsSection.style.display = 'block';
    equationList.innerHTML = '';

    const equations = Object.entries(state.equations[state.currentTopic]);
    equations.forEach(([key, data], idx) => {
        const li = document.createElement('li');
        const btn = document.createElement('button');
        btn.className = 'equation-btn';
        btn.textContent = data.name.length > 30 ? data.name.substring(0, 27) + '...' : data.name;
        btn.dataset.equation = key;
        btn.title = data.name;

        if (idx === state.selectedEquationIdx) {
            btn.classList.add('active');
        }

        btn.addEventListener('click', () => selectEquation(key));
        li.appendChild(btn);
        equationList.appendChild(li);
    });
}

/**
 * Select topic
 */
function selectTopic(topic) {
    state.currentTopic = topic;
    state.selectedEquationIdx = 0;
    state.selectedTopicIdx = state.topics.indexOf(topic);

    renderTopics();
    renderEquations();

    // Auto-select first equation
    const equations = Object.keys(state.equations[topic] || {});
    if (equations.length > 0) {
        selectEquation(equations[0]);
    }
}

/**
 * Select equation
 */
function selectEquation(key) {
    if (!state.currentTopic || !state.equations[state.currentTopic]) {
        return;
    }

    const equations = Object.entries(state.equations[state.currentTopic]);
    const equationIdx = equations.findIndex(([k]) => k === key);

    if (equationIdx !== -1) {
        state.currentEquation = key;
        state.selectedEquationIdx = equationIdx;
        renderEquations();
        displayEquation(key);
    }
}

/**
 * Display equation details
 */
async function displayEquation(key) {
    const equation = state.equations[state.currentTopic][key];
    const detailDiv = document.getElementById('equation-detail');

    const html = `
        <div class="equation">
            <h2>${escapeHtml(equation.name)}</h2>

            <div class="equation-section">
                <h3>Formula</h3>
                <div class="equation-latex">
                    $$${equation.latex}$$
                </div>
            </div>

            <div class="equation-section">
                <h3>Description</h3>
                <p class="equation-description">${escapeHtml(equation.description)}</p>
            </div>

            <div class="equation-section">
                <h3>History</h3>
                <p class="equation-history">${escapeHtml(equation.history)}</p>
            </div>

            <div class="equation-metadata">
                <div class="metadata-item">
                    <div class="metadata-label">Source Line</div>
                    <div class="metadata-value">
                        <a href="#" class="source-link" data-line="${equation.source_line}">
                            equations/${state.currentTopic}.py:${equation.source_line}
                        </a>
                    </div>
                </div>
                <div class="metadata-item">
                    <div class="metadata-label">Concepts</div>
                    <div class="concepts">
                        ${equation.concepts.map(c => `<span class="concept-tag">${escapeHtml(c)}</span>`).join('')}
                    </div>
                </div>
            </div>

            ${equation.citations.length > 0 ? `
                <div class="citations">
                    <h4>Citations</h4>
                    ${equation.citations.map(c => `<p class="citation-item">${escapeHtml(c)}</p>`).join('')}
                </div>
            ` : ''}
        </div>
    `;

    detailDiv.innerHTML = html;

    // Re-render MathJax
    MathJax.typesetPromise([detailDiv]).catch(err => console.error('MathJax error:', err));

    // Handle source link click
    detailDiv.querySelector('.source-link')?.addEventListener('click', (e) => {
        e.preventDefault();
        const line = e.target.dataset.line;
        const url = `https://github.com/baseline0/equations-history/blob/main/src/equations_history/equations/${state.currentTopic}.py#L${line}`;
        window.open(url, '_blank');
    });

    // Fetch and display related equations
    await displayRelatedEquations();

    // Show visualizations if available
    displayVisualization(key);
}

/**
 * Fetch and display related equations from taxonomy
 */
async function displayRelatedEquations() {
    if (!state.currentTopic) return;

    try {
        const response = await fetch(`${API_BASE}/taxonomy/${getTaxonomyDomain()}/${getTaxonomyFamily()}/${state.currentEquation}`);
        if (!response.ok) return;

        const taxonomy = await response.json();

        if (!taxonomy.related_equations || taxonomy.related_equations.length === 0) {
            return;
        }

        // Insert related equations section after citations
        const equationDiv = document.querySelector('.equation');
        if (!equationDiv) return;

        const relatedHtml = `
            <div class="related-equations">
                <h3>Related Equations</h3>
                ${taxonomy.related_equations.map(related => `
                    <div class="relation-card">
                        <div class="relation-header">
                            <strong>${related.target_name}</strong>
                            <span class="relation-kind">${formatRelationshipKind(related.relationship.kind)}</span>
                            <span class="relation-strength ${related.relationship.strength.replace('_', '-')}">${formatRelationshipStrength(related.relationship.strength)}</span>
                        </div>

                        <p class="relation-description">${escapeHtml(related.relationship.definition)}</p>

                        ${Object.keys(related.parameter_mapping).length > 0 ? `
                            <div class="parameter-mapping">
                                <h4>Parameter Correspondence</h4>
                                <table class="mapping-table">
                                    <tr>
                                        <th>This System</th>
                                        <th>Target System</th>
                                        <th>Interpretation</th>
                                    </tr>
                                    ${Object.values(related.parameter_mapping).map(mapping => `
                                        <tr>
                                            <td><code>${escapeHtml(mapping.source_param)}</code> (${escapeHtml(mapping.source_name)})</td>
                                            <td><code>${escapeHtml(mapping.target_param)}</code> (${escapeHtml(mapping.target_name)})</td>
                                            <td>${escapeHtml(mapping.interpretation)}</td>
                                        </tr>
                                    `).join('')}
                                </table>
                            </div>
                        ` : ''}

                        ${related.normalized_form_source ? `
                            <div class="normalized-forms">
                                <h4>Normalized Forms</h4>
                                <div class="form-pair">
                                    <div class="form-item">
                                        <small>This System</small>
                                        <div class="equation-latex">$$${related.normalized_form_source}$$</div>
                                    </div>
                                    <div class="form-item">
                                        <small>Target System</small>
                                        <div class="equation-latex">$$${related.normalized_form_target}$$</div>
                                    </div>
                                </div>
                            </div>
                        ` : ''}

                        ${related.relationship.formal_proof ? `
                            <div class="formal-proof">
                                <a href="${related.relationship.formal_proof_url || '#'}" class="proof-link" target="_blank">
                                    📐 View formal proof in math-trace
                                </a>
                            </div>
                        ` : ''}
                    </div>
                `).join('')}
            </div>
        `;

        equationDiv.insertAdjacentHTML('afterend', relatedHtml);

        // Re-render MathJax for normalized forms
        MathJax.typesetPromise().catch(err => console.error('MathJax error:', err));
    } catch (error) {
        console.error('Failed to fetch related equations:', error);
    }
}

/**
 * Map topic to taxonomy domain/family
 */
function getTaxonomyDomain() {
    // For now, map topic to domain
    const domainMap = {
        'autoencoder': 'ml_math',
        'bert': 'ml_math'
    };
    return domainMap[state.currentTopic] || state.currentTopic;
}

function getTaxonomyFamily() {
    return state.currentTopic;
}

/**
 * Format relationship kind for display
 */
function formatRelationshipKind(kind) {
    const labels = {
        'analogy': '🔄 Analogy',
        'parameter_correspondence': '↔️ Parameter Correspondence',
        'model_equivalence': '≡ Model Equivalence',
        'isomorphism': '≅ Isomorphism',
        'simulation': '→ Simulation',
        'shared_structure': '📐 Shared Structure',
        'shared_hamiltonian_pattern': '⚡ Hamiltonian Pattern',
        'historical_relation': '📜 Historical'
    };
    return labels[kind] || kind;
}

/**
 * Format relationship strength for display
 */
function formatRelationshipStrength(strength) {
    const labels = {
        'informal': 'Informal',
        'structural': 'Structural',
        'proven_equivalence': 'Proven ✓'
    };
    return labels[strength] || strength;
}

/**
 * Display context-specific visualizations
 */
function displayVisualization(key) {
    const vizDiv = document.getElementById('visualization');

    if (state.currentTopic === 'autoencoder' && key === 'vae_elbo') {
        vizDiv.style.display = 'block';
        vizDiv.innerHTML = `
            <h3>Interactive: VAE Latent Space</h3>
            <div class="viz-controls">
                <div class="control-group">
                    <label for="latent-slider">Latent Dimension</label>
                    <input type="range" id="latent-slider" min="2" max="10" value="2" step="1">
                    <span id="latent-value">2D</span>
                </div>
            </div>
            <div id="latent-viz" class="viz-container"></div>
        `;

        const slider = document.getElementById('latent-slider');
        const valueSpan = document.getElementById('latent-value');

        slider.addEventListener('input', (e) => {
            const dim = parseInt(e.target.value);
            valueSpan.textContent = `${dim}D`;
            renderLatentSpace(dim);
        });

        renderLatentSpace(2);
    } else if (state.currentTopic === 'bert' && key === 'scaled_dot_product_attention') {
        vizDiv.style.display = 'block';
        vizDiv.innerHTML = `
            <h3>Interactive: Attention Weights</h3>
            <div class="viz-controls">
                <div class="control-group">
                    <label for="attention-slider">Attention Head</label>
                    <input type="range" id="attention-slider" min="1" max="8" value="1" step="1">
                    <span id="attention-head">Head 1</span>
                </div>
            </div>
            <div id="attention-viz" class="viz-container"></div>
        `;

        const slider = document.getElementById('attention-slider');
        const headSpan = document.getElementById('attention-head');

        slider.addEventListener('input', (e) => {
            const head = parseInt(e.target.value);
            headSpan.textContent = `Head ${head}`;
            renderAttentionMatrix(head);
        });

        renderAttentionMatrix(1);
    } else if (state.currentTopic === 'bert' && key === 'masked_language_modeling_loss') {
        vizDiv.style.display = 'block';
        vizDiv.innerHTML = `
            <h3>Training Dynamics: MLM Loss</h3>
            <div id="mlm-loss-viz" class="viz-container"></div>
        `;
        renderMLMLossCurve();
    } else {
        vizDiv.style.display = 'none';
    }
}

/**
 * Render VAE latent space visualization
 */
function renderLatentSpace(dims) {
    const container = document.getElementById('latent-viz');
    if (!container) return;

    // Generate synthetic 2D latent space samples
    const samples = [];
    const gridSize = 20;

    for (let i = 0; i < gridSize; i++) {
        for (let j = 0; j < gridSize; j++) {
            const x = (i - gridSize / 2) / (gridSize / 2);
            const y = (j - gridSize / 2) / (gridSize / 2);
            // Simple Gaussian prior density
            const z = Math.exp(-(x * x + y * y) / 2);
            samples.push({ x, y, z });
        }
    }

    const trace = {
        x: samples.map(s => s.x),
        y: samples.map(s => s.y),
        z: samples.map(s => s.z),
        type: 'heatmap',
        colorscale: 'Viridis',
        hovertemplate: 'z: %{z:.3f}<extra></extra>',
    };

    const layout = {
        title: `${dims}D Latent Space (Prior Density)`,
        xaxis: { title: 'z₁', zeroline: true },
        yaxis: { title: 'z₂', zeroline: true },
        plot_bgcolor: 'rgba(0,0,0,0)',
        paper_bgcolor: '#161b22',
        font: { color: '#c9d1d9' },
        margin: { l: 60, r: 20, t: 40, b: 60 },
    };

    Plotly.newPlot(container, [trace], layout, { responsive: true });
}

/**
 * Render attention matrix heatmap
 */
function renderAttentionMatrix(head) {
    const container = document.getElementById('attention-viz');
    if (!container) return;

    // Generate synthetic attention weights
    const seqLen = 10;
    const attentionWeights = [];

    for (let i = 0; i < seqLen; i++) {
        const row = [];
        for (let j = 0; j < seqLen; j++) {
            // Synthetic: attention decays from current position
            const distance = Math.abs(i - j);
            row.push(Math.exp(-distance / 2) / 2 + 0.1 * Math.random());
        }
        // Normalize
        const sum = row.reduce((a, b) => a + b, 0);
        attentionWeights.push(row.map(v => v / sum));
    }

    const trace = {
        z: attentionWeights,
        type: 'heatmap',
        colorscale: 'Blues',
        hovertemplate: 'Position %{x} ← %{y}: %{z:.3f}<extra></extra>',
    };

    const layout = {
        title: `Attention Weights (Head ${head})`,
        xaxis: { title: 'Key Position' },
        yaxis: { title: 'Query Position' },
        plot_bgcolor: 'rgba(0,0,0,0)',
        paper_bgcolor: '#161b22',
        font: { color: '#c9d1d9' },
        margin: { l: 80, r: 20, t: 40, b: 80 },
    };

    Plotly.newPlot(container, [trace], layout, { responsive: true });
}

/**
 * Render MLM training loss curve
 */
function renderMLMLossCurve() {
    const container = document.getElementById('mlm-loss-viz');
    if (!container) return;

    // Synthetic training loss curve
    const steps = 100;
    const x = Array.from({ length: steps }, (_, i) => i + 1);
    const y = x.map(i => 5 - 4 * Math.tanh(i / 20) + 0.2 * Math.random());

    const trace = {
        x,
        y,
        mode: 'lines',
        line: { color: '#58a6ff', width: 2 },
        hovertemplate: 'Step %{x}: Loss = %{y:.3f}<extra></extra>',
    };

    const layout = {
        title: 'Masked Language Modeling Loss (Training)',
        xaxis: { title: 'Training Step' },
        yaxis: { title: 'Loss' },
        plot_bgcolor: 'rgba(0,0,0,0)',
        paper_bgcolor: '#161b22',
        font: { color: '#c9d1d9' },
        margin: { l: 60, r: 20, t: 40, b: 60 },
        hovermode: 'x unified',
    };

    Plotly.newPlot(container, [trace], layout, { responsive: true });
}

/**
 * Keyboard navigation
 */
function setupKeyboardNavigation() {
    document.addEventListener('keydown', (e) => {
        switch (e.key) {
            case 'ArrowUp':
                e.preventDefault();
                navigateEquationUp();
                break;
            case 'ArrowDown':
                e.preventDefault();
                navigateEquationDown();
                break;
            case 'ArrowLeft':
                e.preventDefault();
                navigateTopicLeft();
                break;
            case 'ArrowRight':
                e.preventDefault();
                navigateTopicRight();
                break;
            case 'Enter':
                e.preventDefault();
                if (state.currentEquation) {
                    selectEquation(state.currentEquation);
                }
                break;
            case '?':
                e.preventDefault();
                toggleHelpModal();
                break;
            case 'c':
            case 'C':
                if (state.currentEquation && state.equations[state.currentTopic]) {
                    const latex = state.equations[state.currentTopic][state.currentEquation].latex;
                    navigator.clipboard.writeText(latex);
                }
                break;
        }
    });
}

function navigateEquationUp() {
    if (!state.currentTopic || !state.equations[state.currentTopic]) return;
    const equations = Object.keys(state.equations[state.currentTopic]);
    state.selectedEquationIdx = (state.selectedEquationIdx - 1 + equations.length) % equations.length;
    selectEquation(equations[state.selectedEquationIdx]);
}

function navigateEquationDown() {
    if (!state.currentTopic || !state.equations[state.currentTopic]) return;
    const equations = Object.keys(state.equations[state.currentTopic]);
    state.selectedEquationIdx = (state.selectedEquationIdx + 1) % equations.length;
    selectEquation(equations[state.selectedEquationIdx]);
}

function navigateTopicLeft() {
    state.selectedTopicIdx = (state.selectedTopicIdx - 1 + state.topics.length) % state.topics.length;
    selectTopic(state.topics[state.selectedTopicIdx]);
}

function navigateTopicRight() {
    state.selectedTopicIdx = (state.selectedTopicIdx + 1) % state.topics.length;
    selectTopic(state.topics[state.selectedTopicIdx]);
}

function toggleHelpModal() {
    const modal = document.getElementById('help-modal');
    modal.style.display = modal.style.display === 'none' ? 'block' : 'none';
}

/**
 * Close help modal
 */
function setupHelpModal() {
    const modal = document.getElementById('help-modal');
    const closeBtn = document.querySelector('.close');

    closeBtn.addEventListener('click', () => {
        modal.style.display = 'none';
    });

    window.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.style.display = 'none';
        }
    });
}

/**
 * Escape HTML for safety
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

/**
 * Initialize app
 */
async function init() {
    await fetchEquations();
    renderTopics();
    setupKeyboardNavigation();
    setupHelpModal();

    // Select first topic
    if (state.topics.length > 0) {
        selectTopic(state.topics[0]);
    }
}

// Start app when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}
