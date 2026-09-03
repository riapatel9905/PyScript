// ---------- helpers ----------
async function postJSON(url, data) {
  const res = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  return res.json();
}

function updateCartBadge(count) {
  document.querySelectorAll(".cart-badge").forEach((el) => (el.textContent = count));
}

// ---------- add to cart (menu / home pages) ----------
document.addEventListener("click", async (e) => {
  const btn = e.target.closest(".add-btn");
  if (!btn) return;
  const itemId = btn.dataset.itemId;
  const original = btn.textContent;
  btn.disabled = true;
  btn.textContent = "Adding…";
  try {
    const data = await postJSON("/api/cart/add", { menu_item_id: itemId, quantity: 1 });
    if (data.count !== undefined) updateCartBadge(data.count);
    btn.textContent = "Added ✓";
    setTimeout(() => {
      btn.textContent = original;
      btn.disabled = false;
    }, 900);
  } catch (err) {
    btn.textContent = original;
    btn.disabled = false;
    alert("Could not add item to cart.");
  }
});

// ---------- cart page: qty change / delete ----------
function renderCart(data) {
  const list = document.getElementById("cart-list");
  const emptyState = document.getElementById("cart-empty");
  const summary = document.getElementById("cart-summary");
  if (!list) return;

  updateCartBadge(data.count);

  if (!data.items.length) {
    list.innerHTML = "";
    if (emptyState) emptyState.style.display = "block";
    if (summary) summary.style.display = "none";
    return;
  }
  if (emptyState) emptyState.style.display = "none";
  if (summary) summary.style.display = "block";

  list.innerHTML = data.items
    .map(
      (ci) => `
    <div class="cart-row" data-cart-item-id="${ci.cart_item_id}">
      <img src="/static/img/${ci.image}" alt="${ci.name}">
      <div class="info">
        <h4>${ci.name}</h4>
        <div class="unit-price">₹${ci.price} each</div>
      </div>
      <div class="qty-box">
        <button class="qty-minus" data-id="${ci.cart_item_id}">−</button>
        <span>${ci.quantity}</span>
        <button class="qty-plus" data-id="${ci.cart_item_id}">+</button>
      </div>
      <div class="row-subtotal">₹${ci.subtotal}</div>
      <button class="remove-btn" data-id="${ci.cart_item_id}" title="Remove"><i class="fas fa-trash"></i></button>
    </div>`
    )
    .join("");

  document.getElementById("subtotal-amount").textContent = "₹" + data.subtotal;
  const feeEl = document.getElementById("delivery-fee-amount");
  const fee = data.subtotal >= 500 ? 0 : 40;
  if (feeEl) feeEl.textContent = fee === 0 ? "FREE" : "₹" + fee;
  const totalEl = document.getElementById("total-amount");
  if (totalEl) totalEl.textContent = "₹" + (data.subtotal + fee);
}

document.addEventListener("click", async (e) => {
  const minus = e.target.closest(".qty-minus");
  const plus = e.target.closest(".qty-plus");
  const remove = e.target.closest(".remove-btn");
  if (!minus && !plus && !remove) return;

  const id = (minus || plus || remove).dataset.id;
  const row = document.querySelector(`[data-cart-item-id="${id}"]`);
  const currentQty = row ? parseInt(row.querySelector(".qty-box span").textContent) : 1;

  let data;
  if (remove) {
    data = await postJSON("/api/cart/delete", { cart_item_id: id });
  } else {
    const newQty = plus ? currentQty + 1 : currentQty - 1;
    data = await postJSON("/api/cart/update", { cart_item_id: id, quantity: newQty });
  }
  renderCart(data);
});

// ---------- checkout: nearest store via geolocation ----------
function initNearestStore() {
  const btn = document.getElementById("locate-btn");
  const statusEl = document.getElementById("locate-status");
  if (!btn) return;

  btn.addEventListener("click", () => {
    if (!navigator.geolocation) {
      statusEl.textContent = "Geolocation isn't supported on this browser — pick a branch manually below.";
      return;
    }
    statusEl.textContent = "Locating you…";
    navigator.geolocation.getCurrentPosition(
      async (pos) => {
        const { latitude, longitude } = pos.coords;
        try {
          const res = await fetch(`/api/nearest-store?lat=${latitude}&lng=${longitude}`);
          const data = await res.json();
          if (data.id) {
            const radio = document.querySelector(`input[name="store_id"][value="${data.id}"]`);
            if (radio) radio.checked = true;
            document.querySelectorAll(".store-option").forEach((el) => el.classList.remove("nearest"));
            document.querySelectorAll(".badge-nearest").forEach((el) => el.remove());
            const label = document.querySelector(`label[data-store-id="${data.id}"]`);
            if (label) {
              label.closest(".store-option").classList.add("nearest");
              const badge = document.createElement("span");
              badge.className = "badge-nearest";
              badge.textContent = `Nearest • ${data.distance_km} km`;
              label.appendChild(badge);
            }
            statusEl.textContent = `Selected nearest branch: ${data.name} (${data.distance_km} km away).`;
          }
        } catch (err) {
          statusEl.textContent = "Couldn't determine nearest branch — pick one manually.";
        }
      },
      () => {
        statusEl.textContent = "Location access denied — pick a branch manually below.";
      }
    );
  });
}

// ---------- checkout: payment method tabs ----------
function initPaymentTabs() {
  const tabs = document.querySelectorAll(".payment-tab");
  const panels = document.querySelectorAll(".payment-panel");
  if (!tabs.length) return;

  function activate(method) {
    tabs.forEach((t) => t.classList.toggle("active", t.dataset.method === method));
    panels.forEach((p) => p.classList.toggle("active", p.dataset.panel === method));
  }

  tabs.forEach((tab) => {
    tab.addEventListener("click", () => {
      const radio = tab.querySelector("input[type=radio]");
      if (radio) radio.checked = true;
      activate(tab.dataset.method);
    });
  });

  const checked = document.querySelector(".payment-tab input[type=radio]:checked");
  activate(checked ? checked.closest(".payment-tab").dataset.method : tabs[0].dataset.method);
}

document.addEventListener("DOMContentLoaded", () => {
  initNearestStore();
  initPaymentTabs();
});
