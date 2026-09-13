// ===============================
// SIMS NEW SALE PAGE
// ===============================

// ===============================
// DOM ELEMENTS
// ===============================

const customerSelect = document.getElementById("customerSelect");
const productSelect = document.getElementById("productSelect");
const quantityInput = document.getElementById("quantity");

const addItemBtn = document.getElementById("addItemBtn");

const saleItemsTableBody = document.getElementById("saleItemsTableBody");

const subtotalElement = document.getElementById("subtotal");

const discountInput = document.getElementById("discount");

const grandTotalElement = document.getElementById("grandTotal");

const completeSaleBtn = document.getElementById("completeSaleBtn");

// ===============================
// SIDEBAR
// ===============================

const sidebar = document.getElementById("sidebar");
const menuBtn = document.getElementById("menuBtn");

if (menuBtn && sidebar) {
  menuBtn.addEventListener("click", function () {
    sidebar.classList.toggle("show");
  });
}

// ===============================
// DATA
// ===============================

let customers = [];
let products = [];
let saleItems = [];

// ===============================
// LOAD CUSTOMERS
// ===============================

async function loadCustomers() {
  try {
    const response = await fetch("/api/customers");

    if (!response.ok) {
      throw new Error("Failed to load customers.");
    }

    const result = await response.json();

    if (!result.success) {
      throw new Error(result.message || "Failed to load customers.");
    }

    customers = result.customers || [];

    customerSelect.innerHTML = `
      <option value="">
        Walk-in Customer
      </option>
    `;

    customers.forEach(function (customer) {
      const option = document.createElement("option");

      option.value = customer.id;

      option.textContent = `${customer.customer_name} - ${
        customer.phone || "No phone"
      }`;

      customerSelect.appendChild(option);
    });
  } catch (error) {
    console.error("Customer loading error:", error);

    alert("Failed to load customers.");
  }
}

// ===============================
// LOAD PRODUCTS
// ===============================

async function loadProducts() {
  try {
    const response = await fetch("/api/products");

    if (!response.ok) {
      throw new Error("Failed to load products.");
    }

    const result = await response.json();

    if (Array.isArray(result)) {
      products = result;
    } else if (result.success) {
      products = result.products || [];
    } else {
      throw new Error(result.message || "Failed to load products.");
    }

    populateProductSelect();
  } catch (error) {
    console.error("Product loading error:", error);

    alert("Failed to load products.");
  }
}

// ===============================
// POPULATE PRODUCT DROPDOWN
// ===============================

function populateProductSelect() {
  productSelect.innerHTML = `
    <option value="">
      Select Product
    </option>
  `;

  products.forEach(function (product) {
    const stock = Number(product.stock_quantity || 0);

    const option = document.createElement("option");

    option.value = product.id;

    option.textContent = `${product.product_name} | ${product.sku} | Stock: ${stock}`;

    if (stock <= 0) {
      option.disabled = true;
    }

    productSelect.appendChild(option);
  });
}

// ===============================
// PRODUCT SELECTION
// ===============================

productSelect.addEventListener("change", function () {
  const selectedProductId = Number(productSelect.value);

  const product = products.find(function (item) {
    return Number(item.id) === selectedProductId;
  });

  if (!product) {
    quantityInput.value = 1;
    quantityInput.removeAttribute("max");

    return;
  }

  const stock = Number(product.stock_quantity || 0);

  if (stock <= 0) {
    alert("This product is out of stock.");

    productSelect.value = "";

    quantityInput.value = 1;
    quantityInput.removeAttribute("max");

    return;
  }

  quantityInput.value = 1;
  quantityInput.max = stock;
});

// ===============================
// ADD ITEM
// ===============================

addItemBtn.addEventListener("click", function () {
  addSaleItem();
});

function addSaleItem() {
  const productId = Number(productSelect.value);

  const quantity = Number(quantityInput.value);

  if (!productId) {
    alert("Please select a product.");
    return;
  }

  if (!quantity || quantity <= 0) {
    alert("Please enter a valid quantity.");
    return;
  }

  const product = products.find(function (item) {
    return Number(item.id) === productId;
  });

  if (!product) {
    alert("Product not found.");
    return;
  }

  const availableStock = Number(product.stock_quantity || 0);

  if (quantity > availableStock) {
    alert(
      `Only ${availableStock} units of ${product.product_name} are available.`,
    );

    return;
  }

  const existingItem = saleItems.find(function (item) {
    return item.product_id === productId;
  });

  if (existingItem) {
    const newQuantity = existingItem.quantity + quantity;

    if (newQuantity > availableStock) {
      alert(
        `You cannot add more than ${availableStock} units of ${product.product_name}.`,
      );

      return;
    }

    existingItem.quantity = newQuantity;

    existingItem.subtotal = newQuantity * existingItem.unit_price;
  } else {
    const unitPrice = Number(product.selling_price || 0);

    saleItems.push({
      product_id: product.id,
      product_name: product.product_name,
      sku: product.sku,
      quantity: quantity,
      unit_price: unitPrice,
      subtotal: quantity * unitPrice,
    });
  }

  renderSaleItems();

  calculateTotals();

  productSelect.value = "";

  quantityInput.value = 1;

  quantityInput.removeAttribute("max");
}

// ===============================
// RENDER SALE ITEMS
// ===============================

function renderSaleItems() {
  saleItemsTableBody.innerHTML = "";

  if (saleItems.length === 0) {
    saleItemsTableBody.innerHTML = `
      <tr>
        <td colspan="6">
          <div class="empty-state">
            <div class="empty-icon">＋</div>
            <p>No products added yet.</p>
          </div>
        </td>
      </tr>
    `;

    return;
  }

  saleItems.forEach(function (item, index) {
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
        ${item.unit_price.toFixed(2)}
      </td>

      <td>
        ${item.subtotal.toFixed(2)}
      </td>

      <td>
        <button
          type="button"
          class="action-btn delete-btn"
          onclick="removeSaleItem(${index})"
        >
          Remove
        </button>
      </td>
    `;

    saleItemsTableBody.appendChild(row);
  });
}

// ===============================
// REMOVE SALE ITEM
// ===============================

function removeSaleItem(index) {
  if (index < 0 || index >= saleItems.length) {
    return;
  }

  saleItems.splice(index, 1);

  renderSaleItems();

  calculateTotals();
}

// ===============================
// DISCOUNT
// ===============================

discountInput.addEventListener("input", calculateTotals);

// ===============================
// CALCULATE TOTALS
// ===============================

function calculateTotals() {
  const subtotal = saleItems.reduce(function (total, item) {
    return total + item.subtotal;
  }, 0);

  let discountPercentage = Number(discountInput.value || 0);

  if (discountPercentage < 0) {
    discountPercentage = 0;

    discountInput.value = 0;
  }

  if (discountPercentage > 100) {
    discountPercentage = 100;

    discountInput.value = 100;
  }

  const discountAmount = subtotal * (discountPercentage / 100);

  const grandTotal = subtotal - discountAmount;

  subtotalElement.textContent = subtotal.toFixed(2);

  grandTotalElement.textContent = grandTotal.toFixed(2);

  completeSaleBtn.disabled = saleItems.length === 0;
}

// ===============================
// COMPLETE SALE
// ===============================

completeSaleBtn.addEventListener("click", completeSale);

async function completeSale() {
  if (saleItems.length === 0) {
    alert("Please add at least one product.");

    return;
  }

  const customerId = customerSelect.value ? Number(customerSelect.value) : null;

  const subtotal = saleItems.reduce(function (total, item) {
    return total + item.subtotal;
  }, 0);

  const discountPercentage = Number(discountInput.value || 0);

  const discountAmount = subtotal * (discountPercentage / 100);

  const finalAmount = subtotal - discountAmount;

  const saleData = {
    customer_id: customerId,

    total_amount: subtotal,

    discount: discountAmount,

    final_amount: finalAmount,

    items: saleItems.map(function (item) {
      return {
        product_id: item.product_id,

        quantity: item.quantity,

        unit_price: item.unit_price,

        subtotal: item.subtotal,
      };
    }),
  };

  console.log("Sending sale data:", saleData);

  try {
    completeSaleBtn.disabled = true;

    completeSaleBtn.textContent = "Processing...";

    const response = await fetch("/api/sales", {
      method: "POST",

      headers: {
        "Content-Type": "application/json",
      },

      body: JSON.stringify(saleData),
    });

    const result = await response.json();

    console.log("Flask response:", result);

    if (!response.ok || !result.success) {
      alert(result.message || "Failed to complete sale.");

      return;
    }

    // ===============================
    // SHOW INVOICE
    // ===============================

    showInvoice(result.invoice_url, result.sale_id);
  } catch (error) {
    console.error("Complete sale error:", error);

    alert("Something went wrong while completing the sale.");
  } finally {
    completeSaleBtn.disabled = saleItems.length === 0;

    completeSaleBtn.textContent = "Complete Sale";
  }
}

// ===============================
// SHOW INVOICE
// ===============================

function showInvoice(invoiceUrl, saleId) {
  if (!invoiceUrl) {
    alert(
      `Sale completed successfully!\n\nSale ID: ${saleId}\n\nInvoice could not be generated.`,
    );

    window.location.href = "/sales-history";

    return;
  }

  // Create invoice overlay
  const invoiceOverlay = document.createElement("div");

  invoiceOverlay.id = "invoiceOverlay";

  invoiceOverlay.innerHTML = `
    <div class="invoice-modal">

      <div class="invoice-modal-header">
        <div>
          <h2>Invoice Generated</h2>
          <p>Sale #${saleId}</p>
        </div>

        <button
          type="button"
          class="invoice-close-btn"
          id="invoiceCloseBtn"
        >
          ×
        </button>
      </div>

      <div class="invoice-image-container">
        <img
          src="${invoiceUrl}"
          alt="Invoice for Sale ${saleId}"
          class="invoice-image"
        />
      </div>

      <div class="invoice-modal-actions">

        <button
          type="button"
          class="btn-primary"
          id="printInvoiceBtn"
        >
          🖨 Print Invoice
        </button>

        <button
          type="button"
          class="btn-secondary"
          id="salesHistoryBtn"
        >
          Sales History
        </button>

      </div>

    </div>
  `;

  document.body.appendChild(invoiceOverlay);

  // ===============================
  // CLOSE INVOICE
  // ===============================

  const invoiceCloseBtn = document.getElementById("invoiceCloseBtn");

  invoiceCloseBtn.addEventListener("click", function () {
    invoiceOverlay.remove();

    window.location.href = "/sales-history";
  });

  // ===============================
  // PRINT INVOICE
  // ===============================

  const printInvoiceBtn = document.getElementById("printInvoiceBtn");

  printInvoiceBtn.addEventListener("click", function () {
    printInvoice(invoiceUrl);
  });

  // ===============================
  // SALES HISTORY
  // ===============================

  const salesHistoryBtn = document.getElementById("salesHistoryBtn");

  salesHistoryBtn.addEventListener("click", function () {
    window.location.href = "/sales-history";
  });
}

// ===============================
// PRINT INVOICE
// ===============================

function printInvoice(invoiceUrl) {
  const printWindow = window.open("", "_blank");

  if (!printWindow) {
    alert("Please allow pop-ups to print the invoice.");

    return;
  }

  printWindow.document.write(`
    <!DOCTYPE html>

    <html>

      <head>

        <title>SIMS Invoice</title>

        <style>

          body {
            margin: 0;
            padding: 20px;
            text-align: center;
            background: #ffffff;
          }

          img {
            max-width: 100%;
            height: auto;
          }

          @media print {

            body {
              padding: 0;
            }

            img {
              width: 100%;
              max-width: none;
            }

          }

        </style>

      </head>

      <body>

        <img
          src="${invoiceUrl}"
          alt="SIMS Invoice"
          onload="window.print();"
        />

      </body>

    </html>
  `);

  printWindow.document.close();
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
  loadCustomers();

  loadProducts();

  calculateTotals();
});
