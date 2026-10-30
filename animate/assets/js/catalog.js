const ROOT = '/Users/rtadewald/.agents/skills/animate';

const MODES = {
  components: { label: 'Componentes', note: 'Componentes animados e interativos para interfaces.', itemLabel: 'componentes' },
  backgrounds: { label: 'Backgrounds', note: 'Atmosferas animadas para superfícies e seções.', itemLabel: 'backgrounds' },
};

const ANIMATIONS = [
  { id: 'IDL-01', slug: 'cloth-flag', name: 'Cloth flag', mode: 'components', category: 'Mídia e marca', sourcePage: 'component-motion.html', sourceId: 'cloth-flag' },
  { id: 'IDL-02', slug: 'glass-object', name: 'Glass object', mode: 'components', category: 'Objetos 3D', sourcePage: 'spatial-3d.html', sourceId: 'glass-object', hint: 'Arraste para orbitar' },
  { id: 'INT-01', slug: 'glass-shimmer-cta', name: 'Glass shimmer CTA', mode: 'components', category: 'Botões e CTAs', sourcePage: 'component-motion.html', sourceId: 'aura-glass-cta', hint: 'Passe o cursor e clique' },
  { id: 'INT-02', slug: 'valence-core', name: 'Valence Core', mode: 'components', category: 'Botões e CTAs', sourcePage: 'component-motion.html', sourceId: 'valence-core', hint: 'Passe o cursor e clique' },
  { id: 'INT-03', slug: 'border-glow', name: 'Border glow', mode: 'components', category: 'Cards e containers', sourcePage: 'component-motion.html', sourceId: 'border-glow', hint: 'Aproxime o cursor das bordas' },
  { id: 'INT-04', slug: 'option-wheel', name: 'Option wheel', mode: 'components', category: 'Navegação e seleção', sourcePage: 'component-motion.html', sourceId: 'option-wheel', hint: 'Role, arraste ou use o teclado' },

  { id: 'BG-01', slug: 'liquid-shader', name: 'Liquid shader', mode: 'backgrounds', category: 'Página e seções', sourcePage: 'live-backgrounds.html', sourceId: 'liquid-shader' },
  { id: 'BG-02', slug: 'blaze', name: 'Blaze', mode: 'backgrounds', category: 'Página e seções', sourcePage: 'live-backgrounds.html', sourceId: 'blaze' },
  { id: 'BG-03', slug: 'droplets', name: 'Droplets', mode: 'backgrounds', category: 'Overlays de superfície', sourcePage: 'live-backgrounds.html', sourceId: 'droplets', hint: 'Mova o cursor sobre o vidro' },
  { id: 'BG-04', slug: 'frost', name: 'Frost', mode: 'backgrounds', category: 'Overlays de superfície', sourcePage: 'live-backgrounds.html', sourceId: 'frost', hint: 'Mova o cursor para derreter' },
  { id: 'BG-05', slug: 'matrix', name: 'Matrix', mode: 'backgrounds', category: 'Página e seções', sourcePage: 'live-backgrounds.html', sourceId: 'unicorn-matrix' },
  { id: 'BG-06', slug: 'aura-laser', name: 'Aura laser', mode: 'backgrounds', category: 'Hero e banners', sourcePage: 'live-backgrounds.html', sourceId: 'aura-laser' },
  { id: 'BG-07', slug: 'gradient-field', name: 'Gradient field', mode: 'backgrounds', category: 'Página e seções', sourcePage: 'live-backgrounds.html', sourceId: 'gradient-field' },
  { id: 'BG-08', slug: 'masked-matrix', name: 'Masked Matrix', mode: 'backgrounds', category: 'Bordas de seção', sourcePage: 'live-backgrounds.html', sourceId: 'masked-matrix' },
  { id: 'BG-09', slug: 'glass-wave', name: 'Glass wave', mode: 'backgrounds', category: 'Hero e banners', sourcePage: 'live-backgrounds.html', sourceId: 'glass-wave' },
  { id: 'BG-10', slug: 'aurora', name: 'Aurora', mode: 'backgrounds', category: 'Página e seções', sourcePage: 'live-backgrounds.html', sourceId: 'reactbits-aurora' },
  { id: 'BG-11', slug: 'floating-lines', name: 'Floating lines', mode: 'backgrounds', category: 'Página e seções', sourcePage: 'live-backgrounds.html', sourceId: 'floating-lines' },
  { id: 'BG-12', slug: 'light-pillar', name: 'Light pillar', mode: 'backgrounds', category: 'Hero e banners', sourcePage: 'live-backgrounds.html', sourceId: 'light-pillar' },
].map((item) => ({
  ...item,
  folder: `${item.id.toLowerCase()}-${item.slug}`,
  path: `${ROOT}/assets/animations/${item.id.toLowerCase()}-${item.slug}/`,
}));

const catalog = document.querySelector('#catalog');
const sourceCache = new Map();
const loadedModes = new Set();

const slugify = (value) => value
  .normalize('NFD')
  .replace(/[\u0300-\u036f]/g, '')
  .toLowerCase()
  .replace(/[^a-z0-9]+/g, '-')
  .replace(/(^-|-$)/g, '');

async function getSourcePage(name) {
  if (!sourceCache.has(name)) {
    sourceCache.set(name, fetch(`assets/runtime/source/${name}`)
      .then((response) => {
        if (!response.ok) throw new Error(`Não foi possível carregar ${name}.`);
        return response.text();
      })
      .then((html) => new DOMParser().parseFromString(html, 'text/html')));
  }
  return sourceCache.get(name);
}

function makeSpecimen(item, sourceDocument) {
  const source = sourceDocument.querySelector(`#${item.sourceId}`);
  if (!source) throw new Error(`Exemplo ${item.sourceId} não encontrado em ${item.sourcePage}.`);

  const specimen = source.cloneNode(true);
  specimen.classList.add('specimen');
  specimen.dataset.animationId = item.id;
  specimen.dataset.category = slugify(item.category);
  specimen.querySelectorAll('.parameter-panel').forEach((node) => node.remove());

  const card = specimen.querySelector('.demo-card');
  card?.querySelector('.demo-card-bar')?.remove();

  const header = document.createElement('header');
  header.className = 'specimen-head';
  header.innerHTML = `<div class="specimen-title"><span>${item.id}</span><h3>${item.name}</h3></div>`;

  const actions = document.createElement('div');
  actions.className = 'specimen-actions';

  const copy = document.createElement('button');
  copy.type = 'button';
  copy.className = 'specimen-action';
  copy.dataset.copyPath = item.path;
  copy.title = `Copiar ${item.path}`;
  copy.textContent = 'COPY PATH';
  actions.append(copy);
  header.append(actions);
  card?.append(header);

  return specimen;
}

function groupByCategory(items) {
  const groups = new Map();
  items.forEach((item) => {
    if (!groups.has(item.category)) groups.set(item.category, []);
    groups.get(item.category).push(item);
  });
  return groups;
}

async function renderCatalog() {
  const pages = [...new Set(ANIMATIONS.map((item) => item.sourcePage))];
  await Promise.all(pages.map(getSourcePage));
  catalog.replaceChildren();

  for (const [mode, info] of Object.entries(MODES)) {
    const items = ANIMATIONS.filter((item) => item.mode === mode);
    const groups = groupByCategory(items);
    const view = document.createElement('section');
    view.className = 'mode-view';
    view.dataset.modeView = mode;
    view.hidden = true;

    const side = document.createElement('aside');
    side.className = 'category-rail';
    side.setAttribute('aria-label', `Categorias de ${info.label}`);
    const sideIntro = document.createElement('div');
    sideIntro.className = 'rail-intro';
    sideIntro.innerHTML = `<span>${info.label}</span><p>${info.note}</p>`;
    side.append(sideIntro);
    const sideNav = document.createElement('nav');

    const content = document.createElement('div');
    content.className = 'mode-content';

    const allLink = document.createElement('a');
    allLink.href = `#${mode}`;
    allLink.dataset.categoryLink = `${mode}-all`;
    allLink.dataset.categoryLabel = `Todos os ${info.itemLabel}`;
    allLink.innerHTML = '<span>Todos</span>';
    sideNav.append(allLink);

    let index = 0;
    for (const [category] of groups.entries()) {
      index += 1;
      const categorySlug = slugify(category);
      const link = document.createElement('a');
      link.href = `#${mode}/${categorySlug}`;
      link.dataset.categoryLink = `${mode}-${categorySlug}`;
      link.dataset.categoryLabel = category;
      link.innerHTML = `<b>${String(index).padStart(2, '0')}</b><span>${category}</span>`;
      sideNav.append(link);
    }

    const section = document.createElement('section');
    section.className = 'category-section';
    section.dataset.catalogSection = mode;
    section.innerHTML = `
      <header class="category-head">
        <h2 data-results-label>Todos os ${info.itemLabel}</h2>
        <span data-results-count>${String(items.length).padStart(2, '0')} ${info.itemLabel}</span>
      </header>
    `;
    const grid = document.createElement('div');
    grid.className = 'specimen-grid';
    for (const item of items) {
      const source = await getSourcePage(item.sourcePage);
      grid.append(makeSpecimen(item, source));
    }
    section.append(grid);
    content.append(section);

    side.append(sideNav);
    view.append(side, content);
    catalog.append(view);
  }
}

function loadClassic(src) {
  return new Promise((resolve, reject) => {
    if (document.querySelector(`script[data-runtime-src="${src}"]`)) return resolve();
    const script = document.createElement('script');
    script.src = src;
    script.dataset.runtimeSrc = src;
    script.onload = resolve;
    script.onerror = reject;
    document.body.append(script);
  });
}

async function loadModeRuntime(mode) {
  if (loadedModes.has(mode)) return;
  loadedModes.add(mode);
  if (mode === 'components') {
    await Promise.all([
      import('../runtime/js/cloth-flag.js'),
      import('../runtime/js/glass-object.js'),
    ]);
    await loadClassic('assets/runtime/js/aura-glass-cta.js');
    await loadClassic('assets/runtime/js/valence-core.js');
    await loadClassic('assets/runtime/js/reactbits-border-glow.js');
    await loadClassic('assets/runtime/js/reactbits-option-wheel.js');
  }
  if (mode === 'backgrounds') {
    await loadClassic('assets/runtime/js/live-backgrounds.js');
    await Promise.all([
      import('../runtime/js/blaze-background.js'),
      import('../runtime/js/droplets-background.js'),
      import('../runtime/js/frost-background.js'),
    ]);
    await loadClassic('assets/runtime/js/unicorn-backgrounds.js');
    await loadClassic('assets/runtime/js/spline-background.js');
    await loadClassic('assets/runtime/js/reactbits-aurora.js');
    await loadClassic('assets/runtime/js/reactbits-floating-lines.js');
    await loadClassic('assets/runtime/js/reactbits-light-pillar.js');
  }
}

function currentRoute() {
  const raw = location.hash.replace(/^#/, '') || 'components';
  const [candidate, category] = raw.split('/');
  return { mode: MODES[candidate] ? candidate : 'components', category };
}

async function activateRoute() {
  const { mode, category } = currentRoute();
  document.querySelectorAll('[data-mode-view]').forEach((view) => {
    view.hidden = view.dataset.modeView !== mode;
  });
  document.querySelectorAll('[data-mode-link]').forEach((link) => {
    const active = link.dataset.modeLink === mode;
    link.classList.toggle('is-active', active);
    if (active) link.setAttribute('aria-current', 'page');
    else link.removeAttribute('aria-current');
  });
  document.body.dataset.mode = mode;
  await loadModeRuntime(mode);
  const visibleView = document.querySelector(`[data-mode-view="${mode}"]`);
  const requestedLink = category
    ? visibleView?.querySelector(`[data-category-link="${mode}-${category}"]`)
    : null;
  const activeCategory = requestedLink ? `${mode}-${category}` : `${mode}-all`;
  document.querySelectorAll('[data-category-link]').forEach((link) => {
    const active = link.dataset.categoryLink === activeCategory;
    link.classList.toggle('is-active', active);
    if (active) link.setAttribute('aria-current', 'location');
    else link.removeAttribute('aria-current');
  });
  const selectedCategory = requestedLink ? category : null;
  let visibleCount = 0;
  visibleView?.querySelectorAll('.specimen').forEach((specimen) => {
    const visible = !selectedCategory || specimen.dataset.category === selectedCategory;
    specimen.hidden = !visible;
    if (visible) visibleCount += 1;
  });
  const resultsLabel = visibleView?.querySelector('[data-results-label]');
  const resultsCount = visibleView?.querySelector('[data-results-count]');
  const itemLabel = MODES[mode].itemLabel;
  if (resultsLabel) resultsLabel.textContent = requestedLink?.dataset.categoryLabel || `Todos os ${itemLabel}`;
  if (resultsCount) resultsCount.textContent = `${String(visibleCount).padStart(2, '0')} ${itemLabel}`;
  scrollTo({ top: 0, behavior: 'instant' });
}

function installCopy() {
  const toast = document.querySelector('.copy-toast');
  let toastTimer;
  document.addEventListener('click', async (event) => {
    const button = event.target.closest('[data-copy-path]');
    if (!button) return;
    const path = button.dataset.copyPath;
    try {
      await navigator.clipboard.writeText(path);
    } catch {
      const textarea = document.createElement('textarea');
      textarea.value = path;
      textarea.style.position = 'fixed';
      textarea.style.opacity = '0';
      document.body.append(textarea);
      textarea.select();
      document.execCommand('copy');
      textarea.remove();
    }
    button.textContent = 'COPIED';
    toast.textContent = path;
    toast.hidden = false;
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => {
      toast.hidden = true;
      button.textContent = 'COPY PATH';
    }, 1800);
  });
}

function installVisibilityEvents() {
  document.addEventListener('visibilitychange', () => {
    document.dispatchEvent(new Event(document.hidden ? 'motion:pause' : 'motion:resume'));
  });
}

try {
  await renderCatalog();
  installCopy();
  installVisibilityEvents();
  window.addEventListener('hashchange', activateRoute);
  await activateRoute();
} catch (error) {
  console.error(error);
  catalog.innerHTML = `<div class="loading-state error"><span>Catalog error</span><strong>${error.message}</strong></div>`;
}
