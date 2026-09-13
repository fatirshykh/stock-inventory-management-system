// =========================
// Stock Management
// =========================

// =========================
// DOM Elements
// =========================

const stockTableBody = document.getElementById("stockTableBody");

const searchStock = document.getElementById("searchStock");

const categoryFilter = document.getElementById("categoryFilter");

const totalProducts = document.getElementById("totalProducts");

const totalStock = document.getElementById("totalStock");

const lowStock = document.getElementById("lowStock");

const outOfStock = document.getElementById("outOfStock");

// =========================
// Stock Modal Elements
// =========================

const stockModalElement = document.getElementById("stockModal");

const stockProductId = document.getElementById("stockProductId");

const stockProductName = document.getElementById("stockProductName");

const currentStock = document.getElementById("currentStock");

const stockQuantity = document.getElementById("stockQuantity");

const stockActionType = document.getElementById("stockActionType");

const stockModalTitle = document.getElementById("stockModalTitle");

const saveStockBtn = document.getElementById("saveStockBtn");

// =========================
// Sidebar Elements
// =========================

const sidebar = document.getElementById("sidebar");

const menuBtn = document.getElementById("menuBtn");

// =========================
// Store All Stock Data
// =========================

let stockData = [];

// =========================
// Sidebar Toggle
// =========================

if (menuBtn && sidebar) {
  menuBtn.addEventListener("click", () => {
    sidebar.classList.toggle("show");
  });
}

// =========================
// Load Stock
// =========================

async function loadStock() {
  try {
    const response = await fetch("/api/stock");

    if (!response.ok) {
      throw new Error("Failed to load stock");
    }

    const result = await response.json();

    if (!result.success) {
      throw new Error(result.message || "Failed to load stock");
    }

    stockData = result.stock;

    updateStats(stockData);

    renderStock(stockData);
  } catch (error) {
    console.error("Error loading stock:", error);

    stockTableBody.innerHTML = `
            <tr>
                <td colspan="8">

                    <div class="empty-state">

                        <div class="empty-icon">
                            !
                        </div>

                        <p>
                            Failed to load stock.
                        </p>

                    </div>

                </td>
            </tr>
        `;
  }
}

// =========================
// Update Statistics
// =========================

function updateStats(products) {
  // Total Products

  totalProducts.textContent = products.length;

  // Total Stock Units

  const stockUnits = products.reduce(
    (total, product) => total + Number(product.stock_quantity),
    0,
  );

  totalStock.textContent = stockUnits;

  // Low Stock

  const lowStockProducts = products.filter((product) => {
    return (
      Number(product.stock_quantity) > 0 &&
      Number(product.stock_quantity) <= Number(product.minimum_stock)
    );
  });

  lowStock.textContent = lowStockProducts.length;

  // Out Of Stock

  const outOfStockProducts = products.filter((product) => {
    return Number(product.stock_quantity) === 0;
  });

  outOfStock.textContent = outOfStockProducts.length;
}

// =========================
// Render Stock Table
// =========================

function renderStock(products) {
  stockTableBody.innerHTML = "";

  // No Products

  if (products.length === 0) {
    stockTableBody.innerHTML = `
            <tr>

                <td colspan="8">

                    <div class="empty-state">

                        <div class="empty-icon">
                            ◈
                        </div>

                        <p>
                            No products found.
                        </p>

                    </div>

                </td>

            </tr>
        `;

    return;
  }

  // Render Products

  products.forEach((product, index) => {
    const status = getStockStatus(product);

    const row = document.createElement("tr");

    row.innerHTML = `

            <td>
                ${index + 1}
            </td>


            <td>

                <strong>
                    ${product.product_name}
                </strong>

            </td>


            <td>
                ${product.sku}
            </td>


            <td>
                ${product.category_name}
            </td>


            <td>

                <span class="stock-number">
                    ${product.stock_quantity}
                </span>

            </td>


            <td>
                ${product.minimum_stock}
            </td>


            <td>

                <span class="status-badge ${status.className}">
                    ${status.text}
                </span>

            </td>


            <td>

                <button
                    class="stock-action stock-in"
                    onclick="openStockModal(
                        ${product.id},
                        '${escapeProductName(product.product_name)}',
                        ${product.stock_quantity},
                        'in'
                    )"
                >
                    + Stock In
                </button>


                <button
                    class="stock-action stock-out"
                    onclick="openStockModal(
                        ${product.id},
                        '${escapeProductName(product.product_name)}',
                        ${product.stock_quantity},
                        'out'
                    )"
                >
                    − Stock Out
                </button>

            </td>

        `;

    stockTableBody.appendChild(row);
  });
}

// =========================
// Get Stock Status
// =========================

function getStockStatus(product) {
  const stock = Number(product.stock_quantity);

  const minimum = Number(product.minimum_stock);

  // Out of Stock

  if (stock === 0) {
    return {
      text: "Out of Stock",
      className: "status-out-stock",
    };
  }

  // Low Stock

  if (stock <= minimum) {
    return {
      text: "Low Stock",
      className: "status-low-stock",
    };
  }

  // In Stock

  return {
    text: "In Stock",
    className: "status-in-stock",
  };
}

// =========================
// Load Categories
// =========================

async function loadCategories() {
  try {
    const response = await fetch("/api/categories");

    if (!response.ok) {
      throw new Error("Failed to load categories");
    }

    const result = await response.json();

    if (!result.success) {
      throw new Error(result.message || "Failed to load categories");
    }

    const categories = result.categories;

    categoryFilter.innerHTML = `
            <option value="">
                All Categories
            </option>
        `;

    categories.forEach((category) => {
      const option = document.createElement("option");

      option.value = category.id;

      option.textContent = category.name;

      categoryFilter.appendChild(option);
    });
  } catch (error) {
    console.error("Error loading categories:", error);
  }
}

// =========================
// Search Stock
// =========================

searchStock.addEventListener("input", filterStock);

// =========================
// Category Filter
// =========================

categoryFilter.addEventListener("change", filterStock);

// =========================
// Filter Stock
// =========================

function filterStock() {
  const searchValue = searchStock.value.toLowerCase().trim();

  const selectedCategory = categoryFilter.value;

  const filteredProducts = stockData.filter((product) => {
    // Search

    const productName = String(product.product_name).toLowerCase();

    const sku = String(product.sku).toLowerCase();

    const categoryName = String(product.category_name).toLowerCase();

    const matchesSearch =
      productName.includes(searchValue) ||
      sku.includes(searchValue) ||
      categoryName.includes(searchValue);

    // Category

    const matchesCategory =
      selectedCategory === "" ||
      String(product.category_id) === selectedCategory;

    return matchesSearch && matchesCategory;
  });

  renderStock(filteredProducts);
}

// =========================
// Escape Product Name
// =========================

function escapeProductName(name) {
  return String(name).replace(/\\/g, "\\\\").replace(/'/g, "\\'");
}

// =========================
// Open Stock Modal
// =========================

function openStockModal(productId, productName, stock, action) {
  stockProductId.value = productId;

  stockProductName.value = productName;

  currentStock.value = stock;

  stockQuantity.value = "";

  stockActionType.value = action;

  if (action === "in") {
    stockModalTitle.textContent = "Add Stock";

    saveStockBtn.textContent = "+ Add Stock";

    saveStockBtn.className = "save-btn stock-save-in";
  } else {
    stockModalTitle.textContent = "Remove Stock";

    saveStockBtn.textContent = "− Remove Stock";

    saveStockBtn.className = "save-btn stock-save-out";
  }

  // Show modal

  stockModalElement.classList.add("show");

  // Focus quantity input

  setTimeout(() => {
    stockQuantity.focus();
  }, 100);
}

// =========================
// Close Stock Modal
// =========================

function closeStockModal() {
  stockModalElement.classList.remove("show");
}

// =========================
// Close Modal When Clicking Outside
// =========================

stockModalElement.addEventListener("click", function (event) {
  if (event.target === stockModalElement) {
    closeStockModal();
  }
});

// =========================
// Close Modal With Escape
// =========================

document.addEventListener("keydown", function (event) {
  if (event.key === "Escape" && stockModalElement.classList.contains("show")) {
    closeStockModal();
  }
});

// =========================
// Save Stock Adjustment
// =========================

saveStockBtn.addEventListener("click", async function () {
  const productId = stockProductId.value;

  const quantity = Number(stockQuantity.value);

  const action = stockActionType.value;

  // Validate Quantity

  if (!quantity || quantity <= 0) {
    alert("Please enter a valid quantity.");

    return;
  }

  // Prevent Negative Stock

  if (action === "out" && quantity > Number(currentStock.value)) {
    alert("Stock Out quantity cannot be greater than current stock.");

    return;
  }

  try {
    saveStockBtn.disabled = true;

    const response = await fetch(`/api/stock/${productId}`, {
      method: "PUT",

      headers: {
        "Content-Type": "application/json",
      },

      body: JSON.stringify({
        quantity: quantity,

        action: action,
      }),
    });

    const result = await response.json();

    if (!response.ok || !result.success) {
      alert(result.message || "Stock update failed.");

      return;
    }

    alert(result.message);

    // Close Modal

    closeStockModal();

    // Reload Stock

    await loadStock();
  } catch (error) {
    console.error("Stock update error:", error);

    alert("Something went wrong while updating stock.");
  } finally {
    saveStockBtn.disabled = false;
  }
});

// =========================
// Page Load
// =========================

document.addEventListener("DOMContentLoaded", () => {
  loadCategories();

  loadStock();
});
