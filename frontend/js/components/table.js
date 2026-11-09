export function table({ caption, columns, rows = [], emptyMessage = 'No hay registros para mostrar.', rowKey }) {
  const wrapper = document.createElement('div');
  wrapper.className = 'table-wrap';
  wrapper.tabIndex = 0; wrapper.setAttribute('role', 'region'); wrapper.setAttribute('aria-label', caption);
  const element = document.createElement('table');
  const title = document.createElement('caption');
  title.textContent = caption;
  const head = document.createElement('thead');
  const headRow = document.createElement('tr');
  for (const column of columns) {
    const th = document.createElement('th');
    th.scope = 'col'; th.textContent = column.label; headRow.append(th);
  }
  head.append(headRow);
  const body = document.createElement('tbody');
  if (!rows.length) {
    const row = document.createElement('tr');
    const cell = document.createElement('td');
    cell.colSpan = columns.length; cell.className = 'empty-cell'; cell.textContent = emptyMessage;
    row.append(cell); body.append(row);
  } else for (const data of rows) {
    const row = document.createElement('tr');
    if (rowKey) row.dataset.recordId = data[rowKey];
    for (const column of columns) {
      const td = document.createElement('td');
      if (column.render) td.append(column.render(data));
      else td.textContent = String(column.format ? column.format(data[column.key], data) : data[column.key] ?? '—');
      row.append(td);
    }
    body.append(row);
  }
  element.append(title, head, body); wrapper.append(element);
  return wrapper;
}
