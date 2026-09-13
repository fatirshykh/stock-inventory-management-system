// ========================================
// SIMS - SETTINGS JAVASCRIPT
// ========================================

// ========================================
// ELEMENTS
// ========================================

const menuBtn = document.getElementById("menuBtn");
const sidebar = document.querySelector(".sidebar");

const profileForm = document.getElementById("profileForm");
const passwordForm = document.getElementById("passwordForm");
const businessForm = document.getElementById("businessForm");

// ========================================
// MOBILE SIDEBAR
// ========================================

if (menuBtn && sidebar) {
  menuBtn.addEventListener("click", function () {
    sidebar.classList.toggle("show");
  });
}

// Close sidebar when clicking outside on mobile

document.addEventListener("click", function (event) {
  if (!sidebar || !menuBtn) {
    return;
  }

  const clickedInsideSidebar = sidebar.contains(event.target);
  const clickedMenuButton = menuBtn.contains(event.target);

  if (window.innerWidth <= 768 && !clickedInsideSidebar && !clickedMenuButton) {
    sidebar.classList.remove("show");
  }
});

// ========================================
// LOAD PROFILE
// ========================================

async function loadProfile() {
  try {
    const response = await fetch("/api/settings/profile");

    const data = await response.json();

    if (!response.ok || !data.success) {
      alert(data.message || "Failed to load profile.");

      return;
    }

    const user = data.user;

    document.getElementById("fullName").value = user.fullname || "";

    document.getElementById("username").value = user.username || "";

    document.getElementById("email").value = user.email || "";

    document.getElementById("phone").value = user.phone || "";
  } catch (error) {
    console.error("Profile loading error:", error);

    alert("Unable to load profile information.");
  }
}

// ========================================
// PROFILE FORM
// ========================================

if (profileForm) {
  profileForm.addEventListener("submit", async function (event) {
    event.preventDefault();

    const fullName = document.getElementById("fullName").value.trim();

    const username = document.getElementById("username").value.trim();

    const email = document.getElementById("email").value.trim();

    const phone = document.getElementById("phone").value.trim();

    if (!fullName || !username || !email) {
      alert("Please fill in all required profile fields.");

      return;
    }

    const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    if (!emailPattern.test(email)) {
      alert("Please enter a valid email address.");

      return;
    }

    try {
      const response = await fetch("/api/settings/profile", {
        method: "PUT",

        headers: {
          "Content-Type": "application/json",
        },

        body: JSON.stringify({
          fullName: fullName,
          username: username,
          email: email,
          phone: phone,
        }),
      });

      const data = await response.json();

      if (!response.ok || !data.success) {
        alert(data.message || "Failed to update profile.");

        return;
      }

      // Update topbar username

      const topbarUserName = document.getElementById("topbarUserName");

      if (topbarUserName) {
        topbarUserName.textContent = username;
      }

      alert("Profile updated successfully.");
    } catch (error) {
      console.error("Profile update error:", error);

      alert("Unable to update profile.");
    }
  });
}

// Load profile when page opens

loadProfile();

// ========================================
// PASSWORD FORM
// ========================================

if (passwordForm) {
  passwordForm.addEventListener("submit", async function (event) {
    event.preventDefault();

    const currentPassword = document.getElementById("currentPassword").value;

    const newPassword = document.getElementById("newPassword").value;

    const confirmPassword = document.getElementById("confirmPassword").value;

    // Required fields

    if (!currentPassword || !newPassword || !confirmPassword) {
      alert("Please fill in all password fields.");

      return;
    }

    // Password length

    if (newPassword.length < 7) {
      alert("New password must be at least 7 characters long.");

      return;
    }

    // Confirm password

    if (newPassword !== confirmPassword) {
      alert("New password and confirm password do not match.");

      return;
    }

    try {
      const response = await fetch("/api/settings/password", {
        method: "PUT",

        headers: {
          "Content-Type": "application/json",
        },

        body: JSON.stringify({
          currentPassword: currentPassword,
          newPassword: newPassword,
          confirmPassword: confirmPassword,
        }),
      });

      const data = await response.json();

      if (!response.ok || !data.success) {
        alert(data.message || "Failed to change password.");

        return;
      }

      alert("Password changed successfully.");

      // Clear password fields

      document.getElementById("currentPassword").value = "";

      document.getElementById("newPassword").value = "";

      document.getElementById("confirmPassword").value = "";
    } catch (error) {
      console.error("Password change error:", error);

      alert("Unable to change password.");
    }
  });
}

// ========================================
// LOAD BUSINESS INFORMATION
// ========================================

async function loadBusinessSettings() {
  try {
    const response = await fetch("/api/settings/business");

    const data = await response.json();

    if (!response.ok || !data.success) {
      console.error(data.message || "Failed to load business settings.");

      return;
    }

    const business = data.business;

    document.getElementById("businessName").value =
      business.business_name || "";

    document.getElementById("businessPhone").value =
      business.business_phone || "";

    document.getElementById("businessEmail").value =
      business.business_email || "";

    document.getElementById("currency").value = business.currency || "PKR";

    document.getElementById("businessAddress").value =
      business.business_address || "";
  } catch (error) {
    console.error("Business settings loading error:", error);
  }
}

// ========================================
// BUSINESS FORM
// ========================================

if (businessForm) {
  businessForm.addEventListener("submit", async function (event) {
    event.preventDefault();

    const businessName = document.getElementById("businessName").value.trim();

    const businessPhone = document.getElementById("businessPhone").value.trim();

    const businessEmail = document.getElementById("businessEmail").value.trim();

    const currency = document.getElementById("currency").value;

    const businessAddress = document
      .getElementById("businessAddress")
      .value.trim();

    if (!businessName) {
      alert("Please enter your business name.");

      return;
    }

    if (businessEmail) {
      const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

      if (!emailPattern.test(businessEmail)) {
        alert("Please enter a valid business email.");

        return;
      }
    }

    try {
      const response = await fetch("/api/settings/business", {
        method: "PUT",

        headers: {
          "Content-Type": "application/json",
        },

        body: JSON.stringify({
          businessName: businessName,
          businessPhone: businessPhone,
          businessEmail: businessEmail,
          currency: currency,
          businessAddress: businessAddress,
        }),
      });

      const data = await response.json();

      if (!response.ok || !data.success) {
        alert(data.message || "Failed to update business information.");

        return;
      }

      alert("Business information updated successfully.");
    } catch (error) {
      console.error("Business settings update error:", error);

      alert("Unable to update business information.");
    }
  });
}

// Load business settings when page opens

loadBusinessSettings();
