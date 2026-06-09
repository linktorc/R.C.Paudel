/* Invoice form: dynamic item rows + live totals */

let rowCount = 0;

function addItemRow(data) {
  rowCount++;
  const d = data || {};
  const tbody = document.getElementById("items-tbody");
  const tr = document.createElement("tr");
  tr.className = "item-row-tr";
  tr.innerHTML = `
    <td class="text-center align-middle text-muted" style="width:40px">${tbody.children.length + 1}</td>
    <td style="width:110px">
      <input type="text" name="hs_code[]" class="form-control form-control-sm"
             placeholder="-" value="${d.hs_code || '-'}">
    </td>
    <td>
      <input type="text" name="description[]" class="form-control form-control-sm desc-input"
             placeholder="Description of goods / services" value="${d.description || ''}" required>
    </td>
    <td style="width:90px">
      <input type="number" name="qty[]" class="form-control form-control-sm qty-input"
             placeholder="1" step="0.01" min="0" value="${d.qty || ''}">
    </td>
    <td style="width:80px">
      <input type="text" name="unit[]" class="form-control form-control-sm"
             placeholder="Job" value="${d.unit || 'Job'}">
    </td>
    <td style="width:120px">
      <input type="number" name="rate[]" class="form-control form-control-sm rate-input"
             placeholder="0.00" step="0.01" min="0" value="${d.rate || ''}">
    </td>
    <td style="width:120px">
      <input type="text" class="form-control form-control-sm amt-display bg-light"
             placeholder="0.00" readonly tabindex="-1">
    </td>
    <td style="width:36px" class="text-center align-middle">
      <button type="button" class="remove-item btn btn-sm" onclick="removeRow(this)" title="Remove">
        <i class="bi bi-x-lg"></i>
      </button>
    </td>`;
  tbody.appendChild(tr);
  const row = tr;
  row.querySelector(".qty-input").addEventListener("input", () => recalcRow(row));
  row.querySelector(".rate-input").addEventListener("input", () => recalcRow(row));
  if (d.qty && d.rate) recalcRow(row);
}

function removeRow(btn) {
  const tr = btn.closest("tr");
  tr.remove();
  reindexRows();
  recalcTotals();
}

function reindexRows() {
  document.querySelectorAll("#items-tbody tr").forEach((tr, i) => {
    const numCell = tr.querySelector("td:first-child");
    if (numCell) numCell.textContent = i + 1;
  });
}

function recalcRow(row) {
  const qty = parseFloat(row.querySelector(".qty-input").value) || 0;
  const rate = parseFloat(row.querySelector(".rate-input").value) || 0;
  const amt = qty * rate;
  row.querySelector(".amt-display").value = amt > 0 ? fmt(amt) : "";
  recalcTotals();
}

function recalcTotals() {
  let subtotal = 0;
  document.querySelectorAll("#items-tbody tr").forEach(row => {
    const qty = parseFloat(row.querySelector(".qty-input")?.value) || 0;
    const rate = parseFloat(row.querySelector(".rate-input")?.value) || 0;
    subtotal += qty * rate;
  });
  const vat = Math.round(subtotal * 13) / 100;
  const total = subtotal + vat;

  setText("preview-subtotal", fmt(subtotal));
  setText("preview-vat", fmt(vat));
  setText("preview-total", fmt(total));
}

function setText(id, val) {
  const el = document.getElementById(id);
  if (el) el.textContent = val;
}

function fmt(n) {
  return n.toLocaleString("en-IN", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

// ── Init ──────────────────────────────────────────────
document.addEventListener("DOMContentLoaded", () => {
  // Pre-fill existing items (edit mode) via data attribute
  const existing = window.EXISTING_ITEMS || [];
  if (existing.length) {
    existing.forEach(item => addItemRow(item));
  } else {
    addItemRow(); // one blank row on create
  }

  document.getElementById("add-row-btn")?.addEventListener("click", () => addItemRow());
});
