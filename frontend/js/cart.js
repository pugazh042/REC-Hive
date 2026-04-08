const CART_KEY = "rec_cart";

function getCart() {
  return JSON.parse(localStorage.getItem(CART_KEY) || "[]");
}

function saveCart(items) {
  localStorage.setItem(CART_KEY, JSON.stringify(items));
}

function addToCart(product, quantity = 1) {
  const cart = getCart();
  const existing = cart.find((item) => item.product_id === product.id);
  const maxStock = Number(product.stock);
  const hasStockLimit = Number.isFinite(maxStock) && maxStock >= 0;
  if (existing) {
    const nextQty = existing.quantity + quantity;
    existing.quantity = hasStockLimit ? Math.min(nextQty, maxStock) : nextQty;
    if (hasStockLimit) existing.stock = maxStock;
    saveCart(cart);
    return !hasStockLimit || nextQty <= maxStock;
  } else {
    const initialQty = hasStockLimit ? Math.min(quantity, maxStock) : quantity;
    cart.push({
      product_id: product.id,
      name: product.name,
      price: Number(product.price),
      quantity: Math.max(1, initialQty),
      image_url: product.image_url || "",
      shop: product.shop || "",
      shop_id: product.shop_id || null,
      category_name: product.category_name || "",
      product_type: product.product_type,
      stock: hasStockLimit ? maxStock : null,
    });
  }
  saveCart(cart);
  return true;
}

function removeCartItem(productId) {
  const cart = getCart().filter((item) => item.product_id !== productId);
  saveCart(cart);
}

function updateCartQty(productId, quantity) {
  const cart = getCart();
  const item = cart.find((it) => it.product_id === productId);
  if (!item) return;
  const requested = Math.max(1, Number(quantity) || 1);
  const maxStock = Number(item.stock);
  const hasStockLimit = Number.isFinite(maxStock) && maxStock >= 0;
  item.quantity = hasStockLimit ? Math.min(requested, maxStock) : requested;
  saveCart(cart);
}

function clearCart() {
  localStorage.removeItem(CART_KEY);
}

function getCartSummary() {
  const cart = getCart();
  const itemCount = cart.reduce((sum, item) => sum + Number(item.quantity), 0);
  const subtotal = cart.reduce(
    (sum, item) => sum + Number(item.price) * Number(item.quantity),
    0
  );
  return { itemCount, subtotal };
}
