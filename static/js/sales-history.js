// ===============================
// SIMS SALES HISTORY
// ===============================

// ===============================
// DOM ELEMENTS
// ===============================

const sidebar = document.getElementById("sidebar");

const menuBtn = document.getElementById("menuBtn");

const searchInput = document.getElementById("searchInput");

const salesTableBody = document.getElementById("salesTableBody");

const totalSalesElement = document.getElementById("totalSales");

const totalRevenueElement = document.getElementById("totalRevenue");

const totalDiscountElement = document.getElementById("totalDiscount");

const salesCountElement = document.getElementById("salesCount");

// ===============================
// MODAL ELEMENTS
// ===============================

const saleDetailsModal = document.getElementById("saleDetailsModal");

const closeModalBtn = document.getElementById("closeModalBtn");

const saleDetailsInfo = document.getElementById("saleDetailsInfo");

const detailCustomer = document.getElementById("detailCustomer");

const detailDate = document.getElementById("detailDate");

const detailSubtotal = document.getElementById("detailSubtotal");

const detailDiscount = document.getElementById("detailDiscount");

const detailFinalAmount = document.getElementById("detailFinalAmount");

const saleDetailsTableBody = document.getElementById("saleDetailsTableBody");

// ===============================
// DATA
// ===============================

let sales = [];

// ===============================
// SIDEBAR
// ===============================

if (menuBtn && sidebar) {
  menuBtn.addEventListener("click", function () {
    sidebar.classList.toggle("show");
  });
}

// ===============================
// LOAD SALES
// ===============================

async function loadSales() {
  try {
    const response = await fetch("/api/sales");

    if (!response.ok) {
      throw new Error("Failed to load sales.");
    }

    const result = await response.json();

    if (!result.success) {
      throw new Error(result.message || "Failed to load sales.");
    }

    sales = result.sales || [];

    renderSales();

    calculateStats();
  } catch (error) {
    console.error("Sales loading error:", error);

    salesTableBody.innerHTML = `
        <tr>
            <td
                colspan="7"
                class="empty-state"
            >
                Failed to load sales.
            </td>
        </tr>
    `;
  }
}

// ===============================
// RENDER SALES
// ===============================

function renderSales(filteredSales = sales) {
  salesTableBody.innerHTML = "";

  // ===============================
  // EMPTY
  // ===============================

  if (filteredSales.length === 0) {
    salesTableBody.innerHTML = `
        <tr>

            <td
                colspan="7"
                class="empty-state"
            >
                No sales found.
            </td>

        </tr>
    `;

    salesCountElement.textContent = "0 sales";

    return;
  }

  // ===============================
  // SALES
  // ===============================

  filteredSales.forEach(function (sale) {
    const row = document.createElement("tr");

    const createdDate = formatDate(sale.created_at);

    row.innerHTML = `

            <td>
                <strong>
                    #${sale.id}
                </strong>
            </td>

            <td>
                ${escapeHTML(sale.customer_name)}
            </td>

            <td>
                ${createdDate}
            </td>

            <td>
                ${formatMoney(sale.total_amount)}
            </td>

            <td>
                ${formatMoney(sale.discount)}
            </td>

            <td>
                <strong>
                    ${formatMoney(sale.final_amount)}
                </strong>
            </td>

            <td>

                <button
                    type="button"
                    class="view-btn"
                    onclick="viewSaleDetails(${sale.id})"
                >
                    View Details
                </button>

            </td>

        `;

    salesTableBody.appendChild(row);
  });

  salesCountElement.textContent = `${filteredSales.length} ${
    filteredSales.length === 1 ? "sale" : "sales"
  }`;
}

// ===============================
// CALCULATE STATS
// ===============================

function calculateStats() {
  const totalSales = sales.length;

  const totalRevenue = sales.reduce(function (total, sale) {
    return total + Number(sale.final_amount || 0);
  }, 0);

  const totalDiscount = sales.reduce(function (total, sale) {
    return total + Number(sale.discount || 0);
  }, 0);

  totalSalesElement.textContent = totalSales;

  totalRevenueElement.textContent = formatMoney(totalRevenue);

  totalDiscountElement.textContent = formatMoney(totalDiscount);
}

// ===============================
// SEARCH
// ===============================

searchInput.addEventListener("input", function () {
  const searchTerm = searchInput.value.trim().toLowerCase();

  if (!searchTerm) {
    renderSales();

    return;
  }

  const filteredSales = sales.filter(function (sale) {
    const saleId = String(sale.id);

    const customer = String(sale.customer_name || "").toLowerCase();

    return saleId.includes(searchTerm) || customer.includes(searchTerm);
  });

  renderSales(filteredSales);
});

// ===============================
// VIEW SALE DETAILS
// ===============================

async function viewSaleDetails(saleId) {
  try {
    saleDetailsTableBody.innerHTML = `
        <tr>

            <td
                colspan="5"
                class="loading"
            >
                Loading details...
            </td>

        </tr>
    `;

    saleDetailsModal.classList.add("show");

    const response = await fetch(`/api/sales/${saleId}`);

    if (!response.ok) {
      throw new Error("Failed to load sale details.");
    }

    const result = await response.json();

    if (!result.success) {
      throw new Error(result.message || "Failed to load sale details.");
    }

    const sale = result.sale;

    const items = result.items || [];

    // ===============================
    // SALE INFORMATION
    // ===============================

    saleDetailsInfo.textContent = `Sale #${sale.id}`;

    detailCustomer.textContent = sale.customer_name || "Walk-in Customer";

    detailDate.textContent = formatDate(sale.created_at);

    detailSubtotal.textContent = formatMoney(sale.total_amount);

    detailDiscount.textContent = formatMoney(sale.discount);

    detailFinalAmount.textContent = formatMoney(sale.final_amount);

    // ===============================
    // SALE ITEMS
    // ===============================

    saleDetailsTableBody.innerHTML = "";

    if (items.length === 0) {
      saleDetailsTableBody.innerHTML = `
            <tr>

                <td
                    colspan="5"
                    class="empty-state"
                >
                    No items found.
                </td>

            </tr>
        `;

      return;
    }

    items.forEach(function (item) {
      const row = document.createElement("tr");

      row.innerHTML = `

            <td>
                <strong>
                    ${escapeHTML(item.product_name)}
                </strong>
            </td>

            <td>
                ${escapeHTML(item.sku)}
            </td>

            <td>
                ${item.quantity}
            </td>

            <td>
                ${formatMoney(item.unit_price)}
            </td>

            <td>
                ${formatMoney(item.subtotal)}
            </td>

        `;

      saleDetailsTableBody.appendChild(row);
    });
  } catch (error) {
    console.error("Sale details error:", error);

    saleDetailsTableBody.innerHTML = `
        <tr>

            <td
                colspan="5"
                class="empty-state"
            >
                Failed to load sale details.
            </td>

        </tr>
    `;
  }
}

// ===============================
// CLOSE MODAL
// ===============================

closeModalBtn.addEventListener("click", closeSaleDetails);

function closeSaleDetails() {
  saleDetailsModal.classList.remove("show");
}

// ===============================
// CLOSE MODAL
// WHEN CLICKING OUTSIDE
// ===============================

saleDetailsModal.addEventListener("click", function (event) {
  if (event.target === saleDetailsModal) {
    closeSaleDetails();
  }
});

// ===============================
// FORMAT MONEY
// ===============================

function formatMoney(value) {
  return Number(value || 0).toFixed(2);
}

// ===============================
// FORMAT DATE
// ===============================

function formatDate(value) {
  if (!value) {
    return "-";
  }

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return value;
  }

  return date.toLocaleString("en-PK", {
    day: "2-digit",
    month: "short",
    year: "numeric",

    hour: "2-digit",
    minute: "2-digit",
  });
}

// ===============================
// ESCAPE HTML
// ===============================

function escapeHTML(value) {
  if (value === null || value === undefined) {
    return "";
  }

  return String(value)
    .replace(/&/g, "&amp;")

    .replace(/</g, "&lt;")

    .replace(/>/g, "&gt;")

    .replace(/"/g, "&quot;")

    .replace(/'/g, "&#039;");
}

// ===============================
// INITIALIZE
// ===============================

document.addEventListener("DOMContentLoaded", function () {
  loadSales();
});
