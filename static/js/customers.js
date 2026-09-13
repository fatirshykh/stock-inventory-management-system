// ==================== DOM ELEMENTS ====================

const customerTableBody = document.getElementById("customerTableBody");
const searchCustomer = document.getElementById("searchCustomer");
const customerCount = document.getElementById("customerCount");

const customerModal = document.getElementById("customerModal");
const customerModalTitle = document.getElementById("customerModalTitle");

const customerForm = document.getElementById("customerForm");

const customerId = document.getElementById("customerId");
const customerName = document.getElementById("customerName");
const customerPhone = document.getElementById("customerPhone");
const customerEmail = document.getElementById("customerEmail");
const customerAddress = document.getElementById("customerAddress");

const saveCustomerBtn = document.getElementById("saveCustomerBtn");

// ==================== CUSTOMER DATA ====================

let customers = [];

// ==================== LOAD CUSTOMERS ====================

async function loadCustomers() {
  try {
    const response = await fetch("/api/customers");

    const result = await response.json();

    if (result.success) {
      customers = result.customers;

      renderCustomers(customers);
    } else {
      customerTableBody.innerHTML = `
                <tr>
                    <td colspan="7" class="loading">
                        ${result.message}
                    </td>
                </tr>
            `;
    }
  } catch (error) {
    console.error("Error loading customers:", error);

    customerTableBody.innerHTML = `
            <tr>
                <td colspan="7" class="loading">
                    Failed to load customers.
                </td>
            </tr>
        `;
  }
}

// ==================== RENDER CUSTOMERS ====================

function renderCustomers(customerList) {
  customerTableBody.innerHTML = "";

  customerCount.textContent = `${customerList.length} Customer${customerList.length !== 1 ? "s" : ""}`;

  if (customerList.length === 0) {
    customerTableBody.innerHTML = `
            <tr>
                <td colspan="7" class="loading">
                    No customers found.
                </td>
            </tr>
        `;

    return;
  }

  customerList.forEach((customer, index) => {
    const row = document.createElement("tr");

    row.innerHTML = `
            <td>${index + 1}</td>

            <td>
                <strong>${customer.customer_name}</strong>
            </td>

            <td>
                ${customer.phone || "-"}
            </td>

            <td>
                ${customer.email || "-"}
            </td>

            <td>
                ${customer.address || "-"}
            </td>

            <td>
                ${formatDate(customer.created_at)}
            </td>

            <td>

                <button
                    class="edit-btn"
                    onclick="openEditCustomerModal(${customer.id})"
                >
                    Edit
                </button>

                <button
                    class="delete-btn"
                    onclick="deleteCustomer(${customer.id})"
                >
                    Delete
                </button>

            </td>
        `;

    customerTableBody.appendChild(row);
  });
}

// ==================== FORMAT DATE ====================

function formatDate(dateString) {
  if (!dateString) {
    return "-";
  }

  const date = new Date(dateString);

  if (isNaN(date.getTime())) {
    return dateString;
  }

  return date.toLocaleDateString();
}

// ==================== OPEN ADD CUSTOMER MODAL ====================

function openAddCustomerModal() {
  customerForm.reset();

  customerId.value = "";

  customerModalTitle.textContent = "Add Customer";

  saveCustomerBtn.textContent = "Save Customer";

  customerModal.classList.add("active");
}

// ==================== OPEN EDIT CUSTOMER MODAL ====================

function openEditCustomerModal(id) {
  const customer = customers.find((customer) => customer.id === id);

  if (!customer) {
    alert("Customer not found.");

    return;
  }

  customerId.value = customer.id;

  customerName.value = customer.customer_name || "";

  customerPhone.value = customer.phone || "";

  customerEmail.value = customer.email || "";

  customerAddress.value = customer.address || "";

  customerModalTitle.textContent = "Edit Customer";

  saveCustomerBtn.textContent = "Update Customer";

  customerModal.classList.add("active");
}

// ==================== CLOSE MODAL ====================

function closeCustomerModal() {
  customerModal.classList.remove("active");

  customerForm.reset();

  customerId.value = "";
}

// ==================== ADD / UPDATE CUSTOMER ====================

customerForm.addEventListener("submit", async function (event) {
  event.preventDefault();

  const id = customerId.value;

  const name = customerName.value.trim();

  const phone = customerPhone.value.trim();

  const email = customerEmail.value.trim();

  const address = customerAddress.value.trim();

  // ==================== VALIDATION ====================

  if (!name) {
    alert("Customer name is required.");

    return;
  }

  const customerData = {
    customer_name: name,

    phone: phone,

    email: email,

    address: address,
  };

  try {
    let response;

    // ==================== UPDATE ====================

    if (id) {
      response = await fetch(`/api/customers/${id}`, {
        method: "PUT",

        headers: {
          "Content-Type": "application/json",
        },

        body: JSON.stringify(customerData),
      });
    }

    // ==================== ADD ====================
    else {
      response = await fetch("/api/customers", {
        method: "POST",

        headers: {
          "Content-Type": "application/json",
        },

        body: JSON.stringify(customerData),
      });
    }

    const result = await response.json();

    if (result.success) {
      alert(result.message);

      closeCustomerModal();

      loadCustomers();
    } else {
      alert(result.message);
    }
  } catch (error) {
    console.error("Error saving customer:", error);

    alert("Something went wrong.");
  }
});

// ==================== DELETE CUSTOMER ====================

async function deleteCustomer(id) {
  const customer = customers.find((customer) => customer.id === id);

  if (!customer) {
    alert("Customer not found.");

    return;
  }

  const confirmed = confirm(
    `Are you sure you want to delete ${customer.customer_name}?`,
  );

  if (!confirmed) {
    return;
  }

  try {
    const response = await fetch(`/api/customers/${id}`, {
      method: "DELETE",
    });

    const result = await response.json();

    if (result.success) {
      alert(result.message);

      loadCustomers();
    } else {
      alert(result.message);
    }
  } catch (error) {
    console.error("Error deleting customer:", error);

    alert("Something went wrong.");
  }
}

// ==================== SEARCH CUSTOMERS ====================

searchCustomer.addEventListener("input", function () {
  const searchValue = searchCustomer.value.toLowerCase().trim();

  const filteredCustomers = customers.filter((customer) => {
    const name = (customer.customer_name || "").toLowerCase();

    const phone = (customer.phone || "").toLowerCase();

    const email = (customer.email || "").toLowerCase();

    return (
      name.includes(searchValue) ||
      phone.includes(searchValue) ||
      email.includes(searchValue)
    );
  });

  renderCustomers(filteredCustomers);
});

// ==================== CLOSE MODAL WHEN CLICKING OUTSIDE ====================

customerModal.addEventListener("click", function (event) {
  if (event.target === customerModal) {
    closeCustomerModal();
  }
});

// ==================== LOAD DATA WHEN PAGE OPENS ====================

loadCustomers();
