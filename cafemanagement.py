import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

BG, BROWN, TERRA, WHITE = "#F7F0E6", "#3B2924", "#B96F50", "#FFFDF9"
MUTED, BORDER, STRIPE, DANGER, GREY = "#8B786F", "#E8D8C9", "#FBF5EC", "#79554A", "#A8968A"
GST_RATE, FONT = 5, "Segoe UI"
PAGES = [("Dashboard", "◧"), ("Menu Management", "☰"), ("Orders", "✎"), ("Billing", "₹"), ("Sales Report", "▤")]
menu = [{"name": n, "category": c, "price": p} for n, c, p in [
    ("Cappuccino", "Coffee", 160), ("Latte", "Coffee", 180), ("Americano", "Coffee", 140),
    ("Mocha", "Coffee", 200), ("Masala Chai", "Tea", 90), ("Iced Tea", "Tea", 120),
    ("Chocolate Brownie", "Dessert", 150), ("Cheesecake", "Dessert", 220), ("Croissant", "Bakery", 130)]]
cart, orders, total_sales = [], [], 0.0

def money(amount): return f"Rs. {amount:,.2f}"
def alive(widget): return widget is not None and widget.winfo_exists()

def darker(c): return "#%02x%02x%02x" % tuple(int(int(c[i:i + 2], 16) * .85) for i in (1, 3, 5))

def totals():
    sub = sum(x["price"] * x["qty"] for x in cart)
    return sub, sub * GST_RATE / 100, sub * (1 + GST_RATE / 100)  # subtotal, GST, final total

def put(widget, **pack):
    widget.pack(**pack)
    return widget

def frame(parent, bg=BG, **pack): return put(tk.Frame(parent, bg=bg), **pack)

def make_button(parent, text, command, color=TERRA):
    btn = tk.Button(parent, text=text, command=command, bg=color, fg="white", activebackground=darker(color),
                    activeforeground="white", relief="flat", bd=0, font=(FONT, 10, "bold"), padx=14, pady=8, cursor="hand2")
    btn.bind("<Enter>", lambda e: btn.config(bg=darker(color)))
    btn.bind("<Leave>", lambda e: btn.config(bg=color))
    return btn

def make_label(parent, text, size=11, color=BROWN, bold=False): return tk.Label(parent, text=text, bg=parent.cget("bg"), fg=color, font=(FONT, size, "bold" if bold else "normal"))

def make_entry(parent, **kw):
    return tk.Entry(parent, font=(FONT, 11), relief="flat", bg=WHITE, fg=BROWN, insertbackground=BROWN,
                    highlightthickness=1, highlightbackground=BORDER, highlightcolor=TERRA, **kw)

def card_row(parent, items, gap=8):
    row = frame(parent, fill="x")
    for i, (title, value) in enumerate(items):
        inner = put(tk.Frame(row, bg=WHITE, padx=18, pady=16, highlightthickness=1, highlightbackground=BORDER),
                    side="left", fill="both", expand=True, padx=(0 if i == 0 else gap, 0))
        tk.Frame(inner, bg=TERRA, height=3, width=34).pack(anchor="w", pady=(0, 10))
        make_label(inner, title.upper(), 9, MUTED, True).pack(anchor="w")
        make_label(inner, value, 20, BROWN, True).pack(anchor="w", pady=(6, 0))

def tree(parent, columns, headings, widths):
    wrap = frame(parent, BORDER, fill="both", expand=True, pady=8)
    widget = ttk.Treeview(wrap, columns=columns, show="headings", height=9, selectmode="browse")
    scroll = ttk.Scrollbar(wrap, orient="vertical", command=widget.yview)
    widget.configure(yscrollcommand=scroll.set)
    for col, heading, w in zip(columns, headings, widths):
        widget.heading(col, text=heading)
        widget.column(col, width=w, minwidth=60, anchor="center")
    widget.tag_configure("odd", background=STRIPE)
    widget.tag_configure("empty", foreground=MUTED)
    put(scroll, side="right", fill="y", padx=(0, 1), pady=1)
    return put(widget, side="left", fill="both", expand=True, padx=(1, 0), pady=1)

def fill_tree(widget, rows, empty_text, iids=None):
    widget.delete(*widget.get_children())
    if not rows:
        widget.insert("", "end", values=["", empty_text] + [""] * (len(widget["columns"]) - 2), tags=("empty",))
    for i, row in enumerate(rows):
        widget.insert("", "end", values=row, tags=("odd",) if i % 2 else (), **({"iid": iids[i]} if iids else {}))

class CafeApp:
    def __init__(self, root):
        self.root, self.page_title, self.nav, self.status = root, "", {}, None
        root.title("Noir & Cream | Cafe Management")
        root.geometry("1100x720")
        root.configure(bg=BG)
        self.setup_style()
        self.login_page()

    def setup_style(self):
        s = ttk.Style()
        s.theme_use("clam")
        s.configure("Treeview", background=WHITE, foreground=BROWN, rowheight=32, fieldbackground=WHITE,
                    borderwidth=0, font=(FONT, 10))
        s.configure("Treeview.Heading", background=BROWN, foreground="white", font=(FONT, 10, "bold"),
                    relief="flat", padding=(6, 8))
        s.map("Treeview", background=[("selected", TERRA)], foreground=[("selected", "white")])

    def clear(self):
        [w.destroy() for w in self.root.winfo_children()]

    def flash(self, text, color="#3E7C4F"):
        if alive(self.status):
            self.status.config(text="●  " + text, fg=color)
            self.root.after(2500, lambda: alive(self.status) and self.status.config(text=""))

    def login_page(self):
        self.clear()
        box = tk.Frame(self.root, bg=WHITE, padx=52, pady=40, highlightthickness=1, highlightbackground=BORDER)
        box.place(relx=0.5, rely=0.5, anchor="center")
        tk.Label(box, text="NOIR & CREAM", bg=WHITE, fg=BROWN, font=("Georgia", 25, "bold")).pack(pady=(0, 4))
        tk.Label(box, text="YOUR CORNER OF CALM", bg=WHITE, fg=TERRA, font=(FONT, 10, "bold")).pack(pady=(0, 24))
        entries = []
        for label, kw in (("Username", {}), ("Password", {"show": "*"})):
            make_label(box, label, 10, MUTED, True).pack(anchor="w")
            entries.append(put(make_entry(box, width=30, **kw), pady=(6, 16), ipady=8, fill="x"))
        self.username, self.password = entries
        self.password.bind("<Return>", lambda e: self.login())
        self.username.bind("<Return>", lambda e: self.password.focus_set())
        make_button(box, "LOGIN TO YOUR CAFE", self.login).pack(fill="x")
        self.login_error = put(make_label(box, "", 10, "#B33A3A"), pady=(12, 0))
        self.username.focus_set()

    def login(self):
        if self.username.get().strip().upper() == "ADMIN" and self.password.get() == "1328":
            return self.main_layout()
        self.login_error.config(text="Incorrect username or password.")
        self.password.delete(0, tk.END)
        self.password.focus_set()

    def main_layout(self):
        self.clear()
        self.nav = {}
        sidebar = put(tk.Frame(self.root, bg=BROWN, width=230), side="left", fill="y")
        sidebar.pack_propagate(False)
        tk.Label(sidebar, text="NOIR & CREAM", bg=BROWN, fg="#F7E9D8", font=("Georgia", 17, "bold")).pack(pady=(28, 4))
        tk.Label(sidebar, text="CAFE MANAGEMENT", bg=BROWN, fg="#D5B7A3", font=(FONT, 9)).pack(pady=(0, 26))
        self.content = put(tk.Frame(self.root, bg=BG, padx=28, pady=22), side="right", fill="both", expand=True)
        for name, icon in PAGES:
            self.nav[name] = put(tk.Button(sidebar, text=f"  {icon}   {name}", anchor="w", command=lambda n=name: self.show_page(n),
                                bg=BROWN, fg="#EBDCCB", activebackground=TERRA, activeforeground="white", relief="flat",
                                bd=0, font=(FONT, 11), padx=16, pady=12, cursor="hand2"), fill="x", pady=2)
        make_button(sidebar, "LOG OUT", self.login_page, "#715449").pack(fill="x", padx=18, pady=(22, 8))
        self.show_page("Dashboard")

    def show_page(self, name):
        [w.destroy() for w in self.content.winfo_children()]
        self.page_title = name
        for key, btn in self.nav.items():
            on = key == name
            btn.config(bg=TERRA if on else BROWN, fg="white" if on else "#EBDCCB", font=(FONT, 11, "bold" if on else "normal"))
        header = frame(self.content, fill="x", pady=(0, 16))
        left, right = frame(header, side="left"), frame(header, side="right", anchor="s")
        make_label(left, name, 23, BROWN, True).pack(anchor="w")
        tk.Frame(left, bg=TERRA, height=3, width=70).pack(anchor="w", pady=(6, 0))
        make_label(right, datetime.now().strftime("%A, %d %B %Y"), 10, MUTED).pack(anchor="e")
        self.status = put(make_label(right, "", 10, "#3E7C4F", True), anchor="e")
        getattr(self, "page_" + name.lower().replace(" ", "_"))()

    def page_dashboard(self):
        card_row(self.content, [("Total Sales", money(total_sales)), ("Number of Orders", str(len(orders))),
                                ("Menu Items", str(len(menu))), ("Items in Cart", str(sum(x["qty"] for x in cart)))])
        top = frame(self.content, fill="x", pady=(24, 0))
        make_label(top, "Recent Orders", 14, BROWN, True).pack(side="left")
        make_button(top, "+ New Order", lambda: self.show_page("Orders")).pack(side="right")
        self.recent_tree = tree(self.content, ("id", "date", "items", "total"),
                                ("Order ID", "Date & Time", "Items", "Total"), (90, 140, 330, 110))
        fill_tree(self.recent_tree, [(o["id"], o["date"], o["items"], money(o["total"]))
                                     for o in orders[-5:][::-1]], "No orders yet")

    def page_sales_report(self): card_row(self.content, [("Number of Orders", str(len(orders))), ("Total Revenue", money(total_sales))], gap=10)

    def page_menu_management(self):
        self.m_name, self.m_price = tk.StringVar(), tk.StringVar()
        self.m_category, self.m_search = tk.StringVar(value="Coffee"), tk.StringVar()
        form = frame(self.content, fill="x", pady=(0, 10))
        for label, var, width in [("Item Name", self.m_name, 20), ("Category", self.m_category, 14), ("Price (Rs.)", self.m_price, 12)]:
            field = frame(form, side="left", padx=(0, 12))
            make_label(field, label, 10, MUTED, True).pack(anchor="w")
            if label == "Category":
                ttk.Combobox(field, textvariable=var, width=width,
                             values=["Coffee", "Tea", "Dessert", "Bakery", "Snacks", "Other"]).pack(pady=5, ipady=3)
            else:
                put(make_entry(field, textvariable=var, width=width), pady=5, ipady=6)
        actions = frame(self.content, fill="x", pady=5)
        for text, cmd, color in [("Add Item", self.add_menu_item, TERRA), ("Edit Selected", self.edit_menu_item, TERRA),
                                 ("Delete Selected", self.delete_menu_item, DANGER), ("Clear Form", self.clear_menu_form, GREY)]:
            make_button(actions, text, cmd, color).pack(side="left", padx=(0, 8))
        search = frame(self.content, fill="x", pady=(14, 0))
        make_label(search, "Search", 10, MUTED, True).pack(side="left")
        make_entry(search, textvariable=self.m_search, width=28).pack(side="left", ipady=5, padx=8)
        self.menu_tree = tree(self.content, ("name", "category", "price"), ("Item Name", "Category", "Price"), (260, 160, 120))
        self.menu_tree.bind("<<TreeviewSelect>>", self.select_menu_item)
        self.m_search.trace_add("write", lambda *a: self.refresh_menu())
        self.refresh_menu()

    def refresh_menu(self):
        if alive(getattr(self, "menu_tree", None)):
            q = self.m_search.get().strip().lower()
            shown = [x for x in menu if q in x["name"].lower() or q in x["category"].lower()]
            fill_tree(self.menu_tree, [(x["name"], x["category"], money(x["price"])) for x in shown],
                      "No matching items", [x["name"] for x in shown])

    def selected_name(self, widget, source, verb):
        sel = widget.selection()
        if sel and any(x["name"] == sel[0] for x in source):
            return sel[0]
        messagebox.showwarning("Select Item", f"Select an item to {verb}.")

    def select_menu_item(self, event=None):
        sel = self.menu_tree.selection()
        item = next((x for x in menu if sel and x["name"] == sel[0]), None)
        if item:
            self.m_name.set(item["name"])
            self.m_category.set(item["category"])
            self.m_price.set(str(item["price"]))

    def read_form(self, ignore=None):
        name = self.m_name.get().strip()
        try:
            price = float(self.m_price.get())
        except ValueError:
            price = 0
        if not name or price <= 0:
            messagebox.showerror("Invalid Input", "Enter a name and positive price.")
        elif any(x["name"].lower() == name.lower() and x["name"] != ignore for x in menu):
            messagebox.showerror("Duplicate Item", "That item already exists.")
        else:
            return name, price

    def menu_changed(self):
        for refresh in (self.refresh_menu, self.update_orders_menu, self.refresh_cart, self.clear_menu_form):
            refresh()

    def add_menu_item(self):
        data = self.read_form()
        if data:
            menu.append({"name": data[0], "category": self.m_category.get().strip(), "price": data[1]})
            self.menu_changed()
            self.flash(f"{data[0]} added to menu")

    def edit_menu_item(self):
        old = self.selected_name(self.menu_tree, menu, "edit")
        data = old and self.read_form(ignore=old)
        if data:
            next(x for x in menu if x["name"] == old).update(name=data[0], category=self.m_category.get(), price=data[1])
            for line in (x for x in cart if x["name"] == old):
                line.update(name=data[0], price=data[1])
            self.menu_changed()
            self.flash(f"{data[0]} updated")

    def delete_menu_item(self):
        name = self.selected_name(self.menu_tree, menu, "delete")
        if name and messagebox.askyesno("Confirm", f"Delete {name}?"):
            menu[:] = [x for x in menu if x["name"] != name]
            cart[:] = [x for x in cart if x["name"] != name]
            self.menu_changed()
            self.flash(f"{name} deleted", "#B33A3A")

    def clear_menu_form(self):
        for var, val in ((self.m_name, ""), (self.m_category, "Coffee"), (self.m_price, "")):
            var.set(val)

    def page_orders(self):
        panel = frame(self.content, fill="x", pady=(0, 10))
        make_label(panel, "Menu Item", 10, MUTED, True).pack(side="left", padx=(0, 8))
        self.order_item, self.order_qty = tk.StringVar(), tk.StringVar(value="1")
        self.order_combo = put(ttk.Combobox(panel, textvariable=self.order_item, state="readonly", width=28), side="left", padx=5)
        self.update_orders_menu()
        make_label(panel, "Qty", 10, MUTED, True).pack(side="left", padx=(14, 5))
        tk.Spinbox(panel, from_=1, to=99, textvariable=self.order_qty, width=5, font=(FONT, 11), relief="flat",
                   highlightthickness=1, highlightbackground=BORDER).pack(side="left", padx=5, ipady=4)
        make_button(panel, "Add to Cart", self.add_to_cart).pack(side="left", padx=12)
        self.cart_tree = tree(self.content, ("name", "price", "qty", "total"),
                              ("Item", "Unit Price", "Quantity", "Line Total"), (220, 120, 90, 130))
        footer = frame(self.content, fill="x", pady=6)
        self.cart_total_label = put(make_label(footer, "", 12, TERRA, True), side="left")
        make_button(footer, "Go to Billing →", lambda: self.show_page("Billing")).pack(side="right")
        make_button(footer, "Remove Selected", self.remove_from_cart, DANGER).pack(side="right", padx=8)
        self.refresh_cart()

    def update_orders_menu(self):
        if alive(getattr(self, "order_combo", None)):
            self.order_combo["values"] = names = [x["name"] for x in menu]
            if self.order_item.get() not in names:
                self.order_item.set(names[0] if names else "")

    def add_to_cart(self):
        name = self.order_item.get()
        item = next((x for x in menu if x["name"] == name), None)
        qty = self.order_qty.get()
        if not qty.isdigit() or int(qty) < 1:
            return messagebox.showerror("Invalid Quantity", "Enter a quantity of 1 or more.")
        qty = int(qty)
        if not item:
            return messagebox.showwarning("No Item", "Please select a menu item.")
        existing = next((x for x in cart if x["name"] == name), None)
        if existing:
            existing["qty"] += qty
        else:
            cart.append({"name": name, "price": item["price"], "qty": qty})
        self.order_qty.set("1")
        self.refresh_cart()
        self.flash(f"{qty} x {name} added to cart")

    def refresh_cart(self):
        if alive(getattr(self, "cart_tree", None)):
            fill_tree(self.cart_tree, [(i["name"], money(i["price"]), i["qty"], money(i["price"] * i["qty"]))
                                       for i in cart], "Cart is empty", [i["name"] for i in cart])
            self.cart_total_label.config(text=f"Subtotal: {money(totals()[0])}")

    def remove_from_cart(self):
        name = self.selected_name(self.cart_tree, cart, "remove")
        if name:
            cart[:] = [x for x in cart if x["name"] != name]
            self.refresh_cart()

    def page_billing(self):
        self.bill_text = put(tk.Text(self.content, height=10, bg=WHITE, fg=BROWN, font=("Consolas", 10), relief="flat",
                                     padx=16, pady=12, highlightthickness=1, highlightbackground=BORDER),
                             fill="both", expand=True, pady=10)
        make_button(self.content, "Complete Order", self.complete_order).pack(anchor="w")
        make_label(self.content, f"Last Receipt: {orders[-1]['id'] if orders else 'None'}", 10, MUTED).pack(anchor="w", pady=5)
        self.refresh_bill()

    def refresh_bill(self):
        if alive(getattr(self, "bill_text", None)):
            sub, gst, total = totals()
            line = "-" * 42
            rows = ["           NOIR & CREAM", "              BILL PREVIEW", line, f"{'Item':18} {'Qty':>4} {'Amount':>12}", line]
            rows += [f"{i['name'][:18]:18} {i['qty']:>4} {i['price'] * i['qty']:>12.2f}" for i in cart] or ["                Cart is empty"]
            rows += [line, f"{'Subtotal':23}{sub:>13.2f}", f"{f'GST ({GST_RATE}%)':23}{gst:>13.2f}", f"{'TOTAL':23}{total:>13.2f}"]
            self.bill_text.config(state="normal")
            self.bill_text.delete("1.0", tk.END)
            self.bill_text.insert(tk.END, "\n".join(rows) + "\n")
            self.bill_text.config(state="disabled")

    def complete_order(self):
        global total_sales
        if not cart:
            return messagebox.showwarning("Empty Cart", "Add items before billing.")
        sub, gst, total = totals()
        order_id, date = f"NC{len(orders) + 1:03d}", datetime.now().strftime("%d-%m-%Y %H:%M")
        lines = "\n".join(f"{x['name']} x{x['qty']} = {money(x['price'] * x['qty'])}" for x in cart)
        receipt = (f"NOIR & CREAM\nOrder: {order_id}\nDate: {date}\n\n{lines}\n\nSubtotal: {money(sub)}\n"
                   f"GST ({GST_RATE}%): {money(gst)}\nTOTAL: {money(total)}\n\nThank you for visiting!")
        orders.append({"id": order_id, "date": date, "total": total, "receipt": receipt,
                       "items": ", ".join(f"{x['name']} x{x['qty']}" for x in cart)})
        total_sales += total
        cart.clear()
        self.show_page("Billing")
        self.flash(f"Order {order_id} completed")
        messagebox.showinfo("Order Completed", receipt)

if __name__ == "__main__":
    root = tk.Tk()
    app = CafeApp(root)
    root.mainloop()