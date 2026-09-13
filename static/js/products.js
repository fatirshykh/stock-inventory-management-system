// ===============================
// SIMS PRODUCTS PAGE
// ===============================

// ===============================
// DOM ELEMENTS
// ===============================

const productsTableBody = document.getElementById("productsTableBody");

const searchProduct = document.getElementById("searchProduct");

const categoryFilter = document.getElementById("categoryFilter");

const addProductBtn = document.getElementById("addProductBtn");

const productModal = document.getElementById("productModal");

const modalTitle = document.getElementById("modalTitle");

const closeModalBtn = document.getElementById("closeModalBtn");

const cancelBtn = document.getElementById("cancelBtn");

const productForm = document.getElementById("productForm");

const productId = document.getElementById("productId");

const productName = document.getElementById("productName");

const productSku = document.getElementById("productSku");

const productCategory = document.getElementById("productCategory");

const purchasePrice = document.getElementById("purchasePrice");

const sellingPrice = document.getElementById("sellingPrice");

const stockQuantity = document.getElementById("stockQuantity");

const minimumStock = document.getElementById("minimumStock");

const productDescription = document.getElementById("productDescription");

// ===============================
// DASHBOARD ELEMENTS
// ===============================

const totalProducts = document.getElementById("totalProducts");

const totalStock = document.getElementById("totalStock");

const inventoryValue = document.getElementById("inventoryValue");

const lowStock = document.getElementById("lowStock");

// ===============================
// SIDEBAR ELEMENTS
// ===============================

const sidebar = document.getElementById("sidebar");

const menuBtn = document.getElementById("menuBtn");

// ===============================
// STORE PRODUCTS
// ===============================

let products = [];

// ===============================
// SIDEBAR TOGGLE
// ===============================

if (menuBtn && sidebar) {
  menuBtn.addEventListener("click", function () {
    sidebar.classList.toggle("show");
  });
}

// ===============================
// LOAD PRODUCTS
// ===============================

async function loadProducts() {
  try {
    const response = await fetch("/api/products");

    if (!response.ok) {
      throw new Error("Failed to load products");
    }

    const result = await response.json();

    // ===============================
    // HANDLE API RESPONSE
    // ===============================

    if (Array.isArray(result)) {
      products = result;
    } else if (result.success) {
      products = result.products;
    } else {
      throw new Error(result.message || "Failed to load products");
    }

    // ===============================
    // UPDATE DASHBOARD STATS
    // ===============================

    updateProductStats(products);

    // ===============================
    // RENDER PRODUCTS
    // ===============================

    filterProducts();
  } catch (error) {
    console.error("Error loading products:", error);

    productsTableBody.innerHTML = `

  <tr>

    <td colspan="9">

      <div class="empty-state">

        <div class="empty-icon">
          !
        </div>

        <p>
          Failed to load products.
        </p>

      </div>

    </td>

  </tr>

`;
  }
}

// ===============================
// UPDATE PRODUCT STATISTICS
// ===============================

function updateProductStats(productList) {
  // Total products

  if (totalProducts) {
    totalProducts.textContent = productList.length;
  }

  // Total stock

  const totalStockUnits = productList.reduce(function (total, product) {
    return total + Number(product.stock_quantity || 0);
  }, 0);

  if (totalStock) {
    totalStock.textContent = totalStockUnits;
  }

  // Inventory value

  const inventoryTotal = productList.reduce(function (total, product) {
    const purchasePrice = Number(product.purchase_price || 0);

    const stock = Number(product.stock_quantity || 0);

    return total + purchasePrice * stock;
  }, 0);

  if (inventoryValue) {
    inventoryValue.textContent = inventoryTotal.toFixed(2);
  }

  // Low stock products

  const lowStockProducts = productList.filter(function (product) {
    const stock = Number(product.stock_quantity || 0);

    const minimum = Number(product.minimum_stock || 0);

    return stock > 0 && stock <= minimum;
  });

  if (lowStock) {
    lowStock.textContent = lowStockProducts.length;
  }
}

// ===============================
// RENDER PRODUCTS
// ===============================

function renderProducts(productList) {
  productsTableBody.innerHTML = "";

  // ===============================
  // EMPTY STATE
  // ===============================

  if (productList.length === 0) {
    productsTableBody.innerHTML = `

  <tr>

    <td colspan="9">

      <div class="empty-state">

        <div class="empty-icon">
          ▦
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

  // ===============================
  // PRODUCTS
  // ===============================

  productList.forEach(function (product) {
    const row = document.createElement("tr");

    const purchase = Number(product.purchase_price || 0).toFixed(2);

    const selling = Number(product.selling_price || 0).toFixed(2);

    row.innerHTML = `

    <td>
      ${product.id}
    </td>


    <td>
      <strong>
        ${escapeHTML(product.product_name)}
      </strong>
    </td>


    <td>
      ${escapeHTML(product.sku)}
    </td>


    <td>
      ${escapeHTML(product.category_name || "Uncategorized")}
    </td>


    <td>
      ${purchase}
    </td>


    <td>
      ${selling}
    </td>


    <td>

      <span class="stock-number">
        ${product.stock_quantity}
      </span>

    </td>


    <td>

      ${getStockStatus(
        Number(product.stock_quantity),
        Number(product.minimum_stock),
      )}

    </td>


    <td>

      <div class="action-buttons">

        <button
          class="action-btn edit-btn"
          onclick="editProduct(${product.id})"
        >
          Edit
        </button>


        <button
          class="action-btn delete-btn"
          onclick="deleteProduct(${product.id})"
        >
          Delete
        </button>

      </div>

    </td>

  `;

    productsTableBody.appendChild(row);
  });
}

// ===============================
// STOCK STATUS
// ===============================

function getStockStatus(stock, minimumStock) {
  if (stock === 0) {
    return `

  <span class="status-badge status-out-stock">
    Out of Stock
  </span>

`;
  }

  if (stock <= minimumStock) {
    return `

  <span class="status-badge status-low-stock">
    Low Stock
  </span>

`;
  }

  return `


<span class="status-badge status-in-stock">
  In Stock
</span>


`;
}

// ===============================
// LOAD CATEGORIES
// ===============================

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

    // ===============================
    // PRODUCT CATEGORY SELECT
    // ===============================

    productCategory.innerHTML = `

  <option value="">
    Select Category
  </option>

`;

    // ===============================
    // FILTER CATEGORY SELECT
    // ===============================

    categoryFilter.innerHTML = `

  <option value="">
    All Categories
  </option>

`;

    categories.forEach(function (category) {
      // Product form option

      const productOption = document.createElement("option");

      productOption.value = category.id;

      productOption.textContent = category.name;

      productCategory.appendChild(productOption);

      // Filter option

      const filterOption = document.createElement("option");

      filterOption.value = category.id;

      filterOption.textContent = category.name;

      categoryFilter.appendChild(filterOption);
    });
  } catch (error) {
    console.error("Error loading categories:", error);
  }
}

// ===============================
// SEARCH EVENT
// ===============================

searchProduct.addEventListener("input", filterProducts);

// ===============================
// CATEGORY FILTER EVENT
// ===============================

categoryFilter.addEventListener("change", filterProducts);

// ===============================
// FILTER PRODUCTS
// ===============================

function filterProducts() {
  const searchValue = searchProduct.value.toLowerCase().trim();

  const selectedCategory = categoryFilter.value;

  const filteredProducts = products.filter(function (product) {
    // ===============================
    // SEARCH
    // ===============================

    const productNameValue = String(product.product_name || "").toLowerCase();

    const skuValue = String(product.sku || "").toLowerCase();

    const categoryNameValue = String(product.category_name || "").toLowerCase();

    const matchesSearch =
      productNameValue.includes(searchValue) ||
      skuValue.includes(searchValue) ||
      categoryNameValue.includes(searchValue);

    // ===============================
    // CATEGORY
    // ===============================

    const matchesCategory =
      selectedCategory === "" ||
      String(product.category_id) === selectedCategory;

    return matchesSearch && matchesCategory;
  });

  renderProducts(filteredProducts);
}

// ===============================
// OPEN ADD PRODUCT MODAL
// ===============================

addProductBtn.addEventListener("click", function () {
  openAddModal();
});

// ===============================
// OPEN ADD MODAL
// ===============================

function openAddModal() {
  modalTitle.textContent = "Add Product";

  productForm.reset();

  productId.value = "";

  productModal.classList.add("show");

  setTimeout(function () {
    productName.focus();
  }, 100);
}

// ===============================
// CLOSE MODAL
// ===============================

function closeModal() {
  productModal.classList.remove("show");

  productForm.reset();

  productId.value = "";
}

// ===============================
// CLOSE BUTTON
// ===============================

closeModalBtn.addEventListener("click", closeModal);

// ===============================
// CANCEL BUTTON
// ===============================

cancelBtn.addEventListener("click", closeModal);

// ===============================
// CLOSE MODAL OUTSIDE
// ===============================

productModal.addEventListener("click", function (event) {
  if (event.target === productModal) {
    closeModal();
  }
});

// ===============================
// CLOSE MODAL WITH ESCAPE
// ===============================

document.addEventListener("keydown", function (event) {
  if (event.key === "Escape" && productModal.classList.contains("show")) {
    closeModal();
  }
});

// ===============================
// ADD / UPDATE PRODUCT
// ===============================

productForm.addEventListener("submit", async function (event) {
  event.preventDefault();

  // ===============================
  // GET PRODUCT ID
  // ===============================

  const id = productId.value;

  // ===============================
  // PRODUCT DATA
  // ===============================

  const productData = {
    product_name: productName.value.trim(),

    sku: productSku.value.trim(),

    category_id: Number(productCategory.value),

    purchase_price: Number(purchasePrice.value),

    selling_price: Number(sellingPrice.value),

    stock_quantity: Number(stockQuantity.value),

    minimum_stock: Number(minimumStock.value),

    description: productDescription.value.trim(),
  };

  // ===============================
  // BASIC VALIDATION
  // ===============================

  if (!productData.product_name || !productData.sku) {
    alert("Product name and SKU are required.");

    return;
  }

  if (!productData.category_id) {
    alert("Please select a category.");

    return;
  }

  if (productData.purchase_price < 0 || productData.selling_price < 0) {
    alert("Prices cannot be negative.");

    return;
  }

  if (productData.stock_quantity < 0 || productData.minimum_stock < 0) {
    alert("Stock values cannot be negative.");

    return;
  }

  try {
    let response;

    // ===============================
    // UPDATE PRODUCT
    // ===============================

    if (id) {
      response = await fetch(`/api/products/${id}`, {
        method: "PUT",

        headers: {
          "Content-Type": "application/json",
        },

        body: JSON.stringify(productData),
      });
    }

    // ===============================
    // ADD PRODUCT
    // ===============================
    else {
      response = await fetch("/api/products", {
        method: "POST",

        headers: {
          "Content-Type": "application/json",
        },

        body: JSON.stringify(productData),
      });
    }

    // ===============================
    // API RESPONSE
    // ===============================

    const result = await response.json();

    if (!response.ok || !result.success) {
      alert(result.message || "Something went wrong.");

      return;
    }

    alert(result.message);

    closeModal();

    await loadProducts();
  } catch (error) {
    console.error("Error saving product:", error);

    alert("Something went wrong while saving the product.");
  }
});

// ===============================
// EDIT PRODUCT
// ===============================

async function editProduct(id) {
  try {
    const response = await fetch(`/api/products/${id}`);

    if (!response.ok) {
      const result = await response.json();

      alert(result.message || "Failed to load product.");

      return;
    }

    const result = await response.json();

    if (!result.success) {
      alert(result.message || "Failed to load product.");

      return;
    }

    const product = result.product;

    // ===============================
    // MODAL TITLE
    // ===============================

    modalTitle.textContent = "Edit Product";

    // ===============================
    // FILL FORM
    // ===============================

    productId.value = product.id;

    productName.value = product.product_name;

    productSku.value = product.sku;

    productCategory.value = product.category_id;

    purchasePrice.value = product.purchase_price;

    sellingPrice.value = product.selling_price;

    stockQuantity.value = product.stock_quantity;

    minimumStock.value = product.minimum_stock;

    productDescription.value = product.description || "";

    // ===============================
    // SHOW MODAL
    // ===============================

    productModal.classList.add("show");
  } catch (error) {
    console.error("Error loading product:", error);

    alert("Failed to load product.");
  }
}

// ===============================
// DELETE PRODUCT
// ===============================

async function deleteProduct(id) {
  const product = products.find(function (item) {
    return item.id === id;
  });

  const productNameValue = product ? product.product_name : "this product";

  const confirmed = confirm(
    `Are you sure you want to delete ${productNameValue}?`,
  );

  if (!confirmed) {
    return;
  }

  try {
    const response = await fetch(`/api/products/${id}`, {
      method: "DELETE",
    });

    const result = await response.json();

    if (!response.ok || !result.success) {
      alert(result.message || "Failed to delete product.");

      return;
    }

    alert(result.message);

    await loadProducts();
  } catch (error) {
    console.error("Error deleting product:", error);

    alert("Failed to delete product.");
  }
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
// INITIALIZE PAGE
// ===============================

document.addEventListener("DOMContentLoaded", function () {
  loadCategories();

  loadProducts();
});
