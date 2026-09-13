// =========================
// MOBILE SIDEBAR
// =========================

const menuBtn = document.getElementById("menuBtn");
const sidebar = document.getElementById("sidebar");

menuBtn.addEventListener("click", () => {
  sidebar.classList.toggle("show");
});

// =========================
// CLOSE SIDEBAR
// WHEN CLICKING OUTSIDE
// =========================

document.addEventListener("click", (event) => {
  if (
    window.innerWidth <= 768 &&
    sidebar.classList.contains("show") &&
    !sidebar.contains(event.target) &&
    !menuBtn.contains(event.target)
  ) {
    sidebar.classList.remove("show");
  }
});

// =========================
// SEARCH UI
// =========================

const searchInput = document.getElementById("searchInput");

searchInput.addEventListener("input", () => {
  const searchValue = searchInput.value.trim();

  console.log("Searching:", searchValue);
});

// =========================
// NAVIGATION
// =========================

const navLinks = document.querySelectorAll(".nav-link");

navLinks.forEach((link) => {
  link.addEventListener("click", () => {
    navLinks.forEach((item) => {
      item.classList.remove("active");
    });

    if (!link.classList.contains("logout")) {
      link.classList.add("active");
    }
  });
});

// ======================================================
// DASHBOARD DATA
// ======================================================

async function loadDashboardData() {
  try {
    // ==========================================
    // GET DASHBOARD DATA FROM FLASK
    // ==========================================

    const response = await fetch("/api/dashboard/stats");

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.message || "Failed to load dashboard data.");
    }

    // ==========================================
    // TOTAL PRODUCTS
    // ==========================================

    document.getElementById("totalProducts").textContent =
      data.total_products ?? 0;

    // ==========================================
    // TOTAL CATEGORIES
    // ==========================================

    document.getElementById("totalCategories").textContent =
      data.total_categories ?? 0;

    // ==========================================
    // LOW STOCK
    // ==========================================

    document.getElementById("lowStock").textContent = data.low_stock ?? 0;

    // ==========================================
    // TODAY'S SALES
    // ==========================================

    document.getElementById("todaySales").textContent = data.today_sales ?? 0;

    // ==========================================
    // CUSTOMERS
    // ==========================================

    const customerElement = document.getElementById("totalCustomers");

    if (customerElement) {
      customerElement.textContent = data.total_customers ?? 0;
    }

    // ==========================================
    // RECENT SALES
    // ==========================================

    if (data.recent_sales) {
      displayRecentSales(data.recent_sales);
    }

    // ==========================================
    // LOW STOCK PRODUCTS
    // ==========================================

    if (data.low_stock_products) {
      displayLowStockProducts(data.low_stock_products);
    }
  } catch (error) {
    console.error("Dashboard data error:", error);
  }
}

// ======================================================
// DISPLAY RECENT SALES
// ======================================================

function displayRecentSales(sales) {
  const tableBody = document.querySelector(".recent-sales tbody");

  if (!tableBody) {
    return;
  }

  // ==========================================
  // NO SALES
  // ==========================================

  if (!sales || sales.length === 0) {
    tableBody.innerHTML = `
      <tr>
        <td colspan="5" class="empty-state">
          No sales available yet.
        </td>
      </tr>
    `;

    return;
  }

  // ==========================================
  // DISPLAY SALES
  // ==========================================

  tableBody.innerHTML = "";

  sales.forEach((sale) => {
    const row = document.createElement("tr");

    row.innerHTML = `

      <td>
        #${sale.invoice}
      </td>

      <td>
        ${sale.customer}
      </td>

      <td>
        ${sale.date}
      </td>

      <td>
        ${sale.amount}
      </td>

      <td>
        ${sale.status}
      </td>

    `;

    tableBody.appendChild(row);
  });
}

// ======================================================
// DISPLAY LOW STOCK PRODUCTS
// ======================================================

function displayLowStockProducts(products) {
  const stockList = document.querySelector(".stock-list");

  if (!stockList) {
    return;
  }

  // ==========================================
  // NO LOW STOCK PRODUCTS
  // ==========================================

  if (!products || products.length === 0) {
    stockList.innerHTML = `
      <div class="empty-stock">

        <div class="empty-icon">
          📦
        </div>

        <p>
          No low-stock products.
        </p>

      </div>
    `;

    return;
  }

  // ==========================================
  // DISPLAY LOW STOCK PRODUCTS
  // ==========================================

  stockList.innerHTML = "";

  products.forEach((product) => {
    const item = document.createElement("div");

    item.className = "stock-item";

    item.innerHTML = `

      <div>
        <strong>
          ${product.name}
        </strong>

        <small>
          ${product.quantity} units remaining
        </small>
      </div>

    `;

    stockList.appendChild(item);
  });
}

// ======================================================
// INITIAL DASHBOARD LOAD
// ======================================================

loadDashboardData();
