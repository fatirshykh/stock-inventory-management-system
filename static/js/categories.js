// ==========================================
// ELEMENTS
// ==========================================

const categoryTableBody = document.getElementById("categoryTableBody");

const categoryModal = document.getElementById("categoryModal");

const deleteModal = document.getElementById("deleteModal");

const categoryForm = document.getElementById("categoryForm");

const categoryId = document.getElementById("categoryId");

const categoryName = document.getElementById("categoryName");

const categoryDescription = document.getElementById("categoryDescription");

const categoryStatus = document.getElementById("categoryStatus");

const modalTitle = document.getElementById("modalTitle");

const modalDescription = document.getElementById("modalDescription");

const saveCategoryBtn = document.getElementById("saveCategoryBtn");

const deleteCategoryName = document.getElementById("deleteCategoryName");

// ==========================================
// OPEN ADD CATEGORY MODAL
// ==========================================

document.getElementById("openAddModal").addEventListener("click", () => {
  categoryForm.reset();

  categoryId.value = "";

  modalTitle.textContent = "Add Category";

  modalDescription.textContent = "Create a new product category.";

  saveCategoryBtn.textContent = "Add Category";

  categoryModal.classList.add("show");

  categoryName.focus();
});

// ==========================================
// CLOSE CATEGORY MODAL
// ==========================================

function closeCategoryModal() {
  categoryModal.classList.remove("show");

  categoryForm.reset();
}

document
  .getElementById("closeModal")
  .addEventListener("click", closeCategoryModal);

document
  .getElementById("cancelBtn")
  .addEventListener("click", closeCategoryModal);

// ==========================================
// LOAD CATEGORIES FROM FLASK
// ==========================================

async function loadCategories() {
  try {
    const response = await fetch("/api/categories");

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.message || "Failed to load categories.");
    }

    displayCategories(data.categories);
  } catch (error) {
    console.error(error);

    showToast("Error", error.message);
  }
}

// ==========================================
// DISPLAY DATABASE CATEGORIES
// ==========================================

function displayCategories(categories) {
  // ==========================================
  // UPDATE CATEGORY STATISTICS
  // ==========================================

  const totalCategories = categories.length;

  const activeCategories = categories.filter(
    (category) => category.status === "active",
  ).length;

  document.getElementById("totalCategories").textContent = totalCategories;

  document.getElementById("activeCategories").textContent = activeCategories;

  // ==========================================
  // DISPLAY CATEGORIES IN TABLE
  // ==========================================

  categoryTableBody.innerHTML = "";

  categories.forEach((category) => {
    const row = document.createElement("tr");

    row.innerHTML = `

            <td>#${category.id}</td>

            <td>
                <strong>${category.name}</strong>
            </td>

            <td>
                ${category.description || "No description"}
            </td>

            <td>
                <span class="status ${category.status}">
                    ${category.status}
                </span>
            </td>

            <td>
                ${category.created_at}
            </td>

            <td>

                <div class="action-buttons">

                    <button
                        class="action-btn"
                        onclick="editCategory(${category.id})"
                    >
                        ✎
                    </button>

                    <button
                        class="action-btn delete"
                        onclick="openDeleteModal(
                            ${category.id},
                            '${escapeHtml(category.name)}'
                        )"
                    >
                        ×
                    </button>

                </div>

            </td>
        `;

    categoryTableBody.appendChild(row);
  });
}

// ==========================================
// ADD / UPDATE CATEGORY
// ==========================================

categoryForm.addEventListener("submit", async (event) => {
  event.preventDefault();

  const name = categoryName.value.trim();

  const description = categoryDescription.value.trim();

  const status = categoryStatus.value;

  const id = categoryId.value;

  // Basic frontend validation

  if (!name) {
    showToast("Error", "Category name is required.");

    categoryName.focus();

    return;
  }

  const categoryData = {
    name: name,

    description: description,

    status: status,
  };

  try {
    let response;

    // UPDATE

    if (id) {
      response = await fetch(`/api/categories/${id}`, {
        method: "PUT",

        headers: {
          "Content-Type": "application/json",
        },

        body: JSON.stringify(categoryData),
      });
    }

    // CREATE
    else {
      response = await fetch("/api/categories", {
        method: "POST",

        headers: {
          "Content-Type": "application/json",
        },

        body: JSON.stringify(categoryData),
      });
    }

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.message || "Something went wrong.");
    }

    closeCategoryModal();

    showToast("Success", data.message);

    // Reload database data

    loadCategories();
  } catch (error) {
    console.error(error);

    showToast("Error", error.message);
  }
});

// ==========================================
// EDIT CATEGORY
// ==========================================

async function editCategory(id) {
  try {
    const response = await fetch(`/api/categories/${id}`);

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.message || "Failed to load category.");
    }

    const category = data.category;

    categoryId.value = category.id;

    categoryName.value = category.name;

    categoryDescription.value = category.description || "";

    categoryStatus.value = category.status;

    modalTitle.textContent = "Edit Category";

    modalDescription.textContent = "Update category information.";

    saveCategoryBtn.textContent = "Update Category";

    categoryModal.classList.add("show");

    categoryName.focus();
  } catch (error) {
    console.error(error);

    showToast("Error", error.message);
  }
}

// ==========================================
// DELETE MODAL
// ==========================================

let categoryToDelete = null;

function openDeleteModal(id, name) {
  categoryToDelete = id;

  deleteCategoryName.textContent = name;

  deleteModal.classList.add("show");
}

// ==========================================
// CANCEL DELETE
// ==========================================

document.getElementById("cancelDelete").addEventListener("click", () => {
  categoryToDelete = null;

  deleteModal.classList.remove("show");
});

// ==========================================
// DELETE CATEGORY
// ==========================================

document.getElementById("confirmDelete").addEventListener("click", async () => {
  if (!categoryToDelete) {
    return;
  }

  try {
    const response = await fetch(`/api/categories/${categoryToDelete}`, {
      method: "DELETE",
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.message || "Failed to delete category.");
    }

    deleteModal.classList.remove("show");

    categoryToDelete = null;

    showToast("Success", data.message);

    // Reload from database

    loadCategories();
  } catch (error) {
    console.error(error);

    showToast("Error", error.message);
  }
});

// ==========================================
// TOAST
// ==========================================

function showToast(title, message) {
  const toast = document.getElementById("toast");

  const toastTitle = document.getElementById("toastTitle");

  const toastMessage = document.getElementById("toastMessage");

  toastTitle.textContent = title;

  toastMessage.textContent = message;

  toast.classList.add("show");

  setTimeout(() => {
    toast.classList.remove("show");
  }, 3000);
}

// ==========================================
// HTML ESCAPE
// ==========================================

function escapeHtml(value) {
  return String(value)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

// ==========================================
// INITIAL LOAD
// ==========================================

loadCategories();
