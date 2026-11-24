import {request} from './api.js';
import {actionForm} from './controls.js';
import {el} from './dom.js';
import {dataView, status, titleBlock} from './widgets.js';

function ledger(caption, path, columns, view) {
  const panel = el('section', {class:'ledger', 'aria-label':caption});
  const refresh = async () => {
    try {
      const rows = await request(path);
      panel.replaceChildren(el('h2',{},caption),dataView(rows, columns, view));
    } catch (error) { panel.replaceChildren(status(error.message,'error')); }
  };
  return {panel, refresh};
}

export function workspace(root, role, page) {
  const main = ledger(page.caption, page.path, page.columns, page.view);
  const extra = (page.extras || []).map(x => ledger(x.caption, x.path, x.columns, x.view));
  const refresh = async () => {
    await Promise.all([main.refresh(), ...extra.map(x => x.refresh())]);
  };
  const actions = page.actions.filter(x => x.roles.includes(role));
  root.replaceChildren(titleBlock(page.module, page.title, page.detail),
    el('div',{class:'work '+page.layout},main.panel,
      actions.length ? el('section',{class:'actions'},actions.map(x => actionForm(x, refresh))) : null),
    extra.length ? el('div',{class:'extras'},extra.map(x => x.panel)) : null);
  return refresh();
}
