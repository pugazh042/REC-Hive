/** Small DOM helpers */
window.RHUi = {
  el(tag, attrs, children) {
    const node = document.createElement(tag);
    if (attrs) {
      Object.entries(attrs).forEach(([k, v]) => {
        if (k === "class") node.className = v;
        else if (k === "disabled" && v === false) node.removeAttribute("disabled");
        else if (k.startsWith("on") && typeof v === "function") node.addEventListener(k.slice(2).toLowerCase(), v);
        else if (v !== null && v !== undefined && v !== false) node.setAttribute(k, v === true ? "" : v);
      });
    }
    (children || []).forEach((c) => {
      if (typeof c === "string") node.appendChild(document.createTextNode(c));
      else if (c) node.appendChild(c);
    });
    return node;
  },
  money(n) {
    const x = Number(n);
    if (Number.isNaN(x)) return "—";
    return `₹${x.toFixed(0)}`;
  },
  placeholderImg() {
    return "/static/images/placeholder.svg";
  },
};
