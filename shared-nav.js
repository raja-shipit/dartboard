/* shared-nav.js — injected by each dashboard page */
(function() {
  const pages = [
    { id: 'hub',       label: 'Home',            href: 'index.html' },
    { id: 'map',       label: 'BESS map',         href: 'map.html' },
    { id: 'market',    label: 'Market sizing',    href: 'market.html' },
    { id: 'pipeline',  label: 'Sales pipeline',   href: 'pipeline.html' },
    { id: 'insurance', label: 'Insurance brief',  href: 'insurance.html' },
    { id: 'ml',        label: 'ML labels',        href: '#', soon: true },
  ];
  const current = document.body.dataset.page;
  const nav = document.getElementById('topnav');
  if (!nav) return;
  nav.innerHTML = `
    <div style="display:flex;align-items:center;gap:0;height:44px;padding:0 20px;
      background:#fff;border-bottom:0.5px solid #e0dfd7;
      font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;
      overflow-x:auto;white-space:nowrap;">
      <a href="index.html" style="font-size:13px;font-weight:500;color:#1a1a1a;
        text-decoration:none;display:inline-flex;align-items:center;gap:6px;
        margin-right:20px;flex-shrink:0;">
        <span style="width:8px;height:8px;border-radius:50%;background:#1D9E75;
          display:inline-block;"></span>Dartboard Fletch
      </a>
      ${pages.map(p => `
        <a href="${p.href}" style="padding:0 14px;height:44px;display:inline-flex;
          align-items:center;font-size:12px;text-decoration:none;flex-shrink:0;
          color:${p.id === current ? '#1a1a1a' : '#666'};
          font-weight:${p.id === current ? '500' : '400'};
          border-bottom:2px solid ${p.id === current ? '#1a1a1a' : 'transparent'};
          opacity:${p.soon ? '0.4' : '1'};
          pointer-events:${p.soon ? 'none' : 'auto'};">
          ${p.label}${p.soon
            ? ' <span style="font-size:9px;background:#f4f3ef;color:#999;padding:1px 5px;border-radius:10px;margin-left:4px;">soon</span>'
            : ''}
        </a>`).join('')}
    </div>`;
})();
