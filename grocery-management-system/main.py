"""FreshCart grocery inventory desktop application."""

import csv
from pathlib import Path
import tkinter as tk
from tkinter import messagebox, ttk


BG = "#F3F6FB"
NAVY = "#172554"
BLUE = "#3157D5"
TEXT = "#172033"
MUTED = "#75819A"
GREEN = "#16845B"
RED = "#C2414B"
WHITE = "#FFFFFF"

CSV_FILE = Path(__file__).with_name("products.csv")
DEFAULT_PRODUCTS = {
    "apple": {"price": 100, "quantity": 20},
    "milk": {"price": 60, "quantity": 15},
    "bread": {"price": 40, "quantity": 10},
    "rice": {"price": 80, "quantity": 25},
}


def load_products():
    """Load inventory from the CSV file beside this script."""
    if not CSV_FILE.exists():
        return {name: item.copy() for name, item in DEFAULT_PRODUCTS.items()}

    inventory = {}
    try:
        with CSV_FILE.open("r", newline="", encoding="utf-8-sig") as csv_file:
            for row in csv.DictReader(csv_file):
                name = (row.get("name") or "").strip().lower()
                if not name:
                    continue
                try:
                    price = float(row["price"])
                    quantity = int(row["quantity"])
                    if price < 0 or quantity < 0:
                        continue
                except (KeyError, TypeError, ValueError):
                    continue
                inventory[name] = {"price": price, "quantity": quantity}
    except OSError:
        return {name: item.copy() for name, item in DEFAULT_PRODUCTS.items()}
    return inventory


products = load_products()


class GroceryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("FreshCart | Grocery Management")
        self.root.geometry("1180x760")
        self.root.minsize(900, 620)
        self.root.configure(bg=BG)
        self.setup_styles()
        self.build_ui()
        self.refresh_products()

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Treeview", background=WHITE, foreground=TEXT,
            fieldbackground=WHITE, rowheight=42, borderwidth=0,
            font=("Segoe UI", 10),
        )
        style.configure(
            "Treeview.Heading", background="#F7F9FC", foreground=MUTED,
            relief="flat", font=("Segoe UI", 9, "bold"), padding=(12, 12),
        )
        style.map("Treeview", background=[("selected", "#E5ECFF")])
        style.map("Treeview", foreground=[("selected", TEXT)])

    def build_ui(self):
        sidebar = tk.Frame(self.root, bg=NAVY, width=220)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        tk.Label(
            sidebar, text="F  FreshCart", bg=NAVY, fg=WHITE,
            font=("Segoe UI", 18, "bold"),
        ).pack(anchor="w", padx=23, pady=(30, 3))
        tk.Label(
            sidebar, text="GROCERY MANAGER", bg=NAVY, fg="#AAB8D4",
            font=("Segoe UI", 8, "bold"),
        ).pack(anchor="w", padx=25, pady=(0, 38))
        tk.Label(
            sidebar, text="WORKSPACE", bg=NAVY, fg="#8190AE",
            font=("Segoe UI", 8, "bold"),
        ).pack(anchor="w", padx=24, pady=(0, 12))

        self.nav_buttons = {}
        for page, label, command in (
            ("overview", "▦   Overview", self.show_overview),
            ("inventory", "▤   Inventory", self.show_inventory),
            ("add", "＋   Add product", self.add_product),
        ):
            button = tk.Button(
                sidebar, text=label, command=command, anchor="w",
                bg="#2A3B66" if page == "overview" else NAVY,
                fg=WHITE if page == "overview" else "#C5CEE0",
                activebackground="#2A3B66", activeforeground=WHITE,
                relief="flat", cursor="hand2", font=("Segoe UI", 10),
                padx=18, pady=12,
            )
            button.pack(fill="x", padx=14, pady=3)
            self.nav_buttons[page] = button

        tk.Frame(sidebar, bg="#344366", height=1).pack(fill="x", padx=22, pady=25)
        tk.Label(
            sidebar, text="Everything fresh,\nin one place.", bg=NAVY,
            fg="#C5CEE0", justify="left", font=("Segoe UI", 11),
        ).pack(anchor="w", padx=25)
        tk.Label(
            sidebar, text="Local inventory dashboard", bg=NAVY,
            fg="#8190AE", font=("Segoe UI", 8),
        ).pack(anchor="w", padx=25, pady=(8, 0))

        main = tk.Frame(self.root, bg=BG)
        main.pack(side="left", fill="both", expand=True)

        header = tk.Frame(main, bg=BG)
        header.pack(fill="x", padx=32, pady=(26, 20))
        title_area = tk.Frame(header, bg=BG)
        title_area.pack(side="left")
        self.page_title = tk.Label(
            title_area, text="Inventory overview", bg=BG, fg=TEXT,
            font=("Segoe UI", 23, "bold"),
        )
        self.page_title.pack(anchor="w")
        self.page_subtitle = tk.Label(
            title_area, text="Manage products and keep your stock up to date.",
            bg=BG, fg=MUTED, font=("Segoe UI", 10),
        )
        self.page_subtitle.pack(anchor="w", pady=(5, 0))
        tk.Button(
            header, text="＋  Add product", command=self.add_product,
            bg=BLUE, fg=WHITE, activebackground="#2446BD", activeforeground=WHITE,
            relief="flat", cursor="hand2", font=("Segoe UI", 10, "bold"),
            padx=17, pady=11,
        ).pack(side="right")

        self.cards = tk.Frame(main, bg=BG)
        self.cards.pack(fill="x", padx=32, pady=(0, 20))
        self.card_values = {}
        self.make_card("products", "TOTAL PRODUCTS", "0", "In your catalog", BLUE)
        self.make_card("units", "UNITS IN STOCK", "0", "Across all products", GREEN)
        self.make_card("value", "INVENTORY VALUE", "₹0", "At current prices", "#9B6ACB")
        self.make_card("low", "LOW STOCK ITEMS", "0", "5 units or fewer", "#D58A26")

        self.inventory_panel = tk.Frame(main, bg=WHITE, highlightthickness=1,
                        highlightbackground="#E7EBF2")
        panel = self.inventory_panel
        panel.pack(fill="both", expand=True, padx=32, pady=(0, 16))
        panel_header = tk.Frame(panel, bg=WHITE)
        panel_header.pack(fill="x", padx=20, pady=18)
        tk.Label(
            panel_header, text="Product inventory", bg=WHITE, fg=TEXT,
            font=("Segoe UI", 14, "bold"),
        ).pack(side="left")

        search_box = tk.Frame(panel_header, bg="#F7F9FC", highlightthickness=1,
                              highlightbackground="#E5EAF2")
        search_box.pack(side="right")
        tk.Label(search_box, text="⌕", bg="#F7F9FC", fg=MUTED,
                 font=("Segoe UI", 15)).pack(side="left", padx=(10, 3))
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *_: self.refresh_products())
        tk.Entry(
            search_box, textvariable=self.search_var, width=22,
            bg="#F7F9FC", fg=TEXT, insertbackground=TEXT,
            relief="flat", font=("Segoe UI", 10),
        ).pack(side="left", ipady=9, padx=(2, 10))

        table_area = tk.Frame(panel, bg=WHITE)
        table_area.pack(fill="both", expand=True, padx=20, pady=(0, 8))
        self.table = ttk.Treeview(
            table_area, columns=("name", "price", "stock", "status"),
            show="headings", selectmode="browse",
        )
        for column, label, width in (
            ("name", "PRODUCT", 280), ("price", "PRICE", 150),
            ("stock", "STOCK", 140), ("status", "STATUS", 160),
        ):
            self.table.heading(column, text=label)
            self.table.column(column, width=width, anchor="w")
        scrollbar = ttk.Scrollbar(table_area, orient="vertical", command=self.table.yview)
        self.table.configure(yscrollcommand=scrollbar.set)
        self.table.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        self.table.tag_configure("low", foreground=RED)

        actions = tk.Frame(panel, bg="#FAFBFD")
        actions.pack(fill="x", side="bottom")
        tk.Frame(actions, bg="#E9EDF4", height=1).pack(fill="x")
        row = tk.Frame(actions, bg="#FAFBFD")
        row.pack(fill="x", padx=20, pady=12)
        self.action_button(row, "Edit product", self.edit_product)
        self.action_button(row, "Delete", self.delete_product, danger=True)
        tk.Label(
            row, text="Select a product to edit, delete, or sell.",
            bg="#FAFBFD", fg=MUTED, font=("Segoe UI", 9),
        ).pack(side="left", padx=8)
        tk.Button(
            row, text="Sell selected  →", command=self.sell_product,
            bg="#E1F4EA", fg=GREEN, activebackground="#D1EBDD",
            relief="flat", cursor="hand2", font=("Segoe UI", 9, "bold"),
            padx=14, pady=9,
        ).pack(side="right")

        tk.Label(
            main, text="FreshCart  •  Inventory management", bg=BG,
            fg="#98A2B3", font=("Segoe UI", 8),
        ).pack(anchor="w", padx=32, pady=(0, 10))

    def make_card(self, key, heading, value, note, accent):
        card = tk.Frame(self.cards, bg=WHITE, highlightthickness=1, highlightbackground="#E7EBF2")
        card.pack(side="left", fill="both", expand=True, padx=(0, 10))
        tk.Frame(card, bg=accent, width=4).pack(side="left", fill="y")
        body = tk.Frame(card, bg=WHITE)
        body.pack(fill="both", expand=True, padx=13, pady=12)
        tk.Label(body, text=heading, bg=WHITE, fg=MUTED,
                 font=("Segoe UI", 8, "bold")).pack(anchor="w")
        number = tk.Label(body, text=value, bg=WHITE, fg=TEXT,
                          font=("Segoe UI", 18, "bold"))
        number.pack(anchor="w", pady=(5, 1))
        tk.Label(body, text=note, bg=WHITE, fg=MUTED,
                 font=("Segoe UI", 8)).pack(anchor="w")
        self.card_values[key] = number

    @staticmethod
    def action_button(parent, text, command, danger=False):
        tk.Button(
            parent, text=text, command=command,
            bg="#FCEBEC" if danger else WHITE,
            fg=RED if danger else TEXT,
            activebackground="#F7DCDD" if danger else "#F1F4F8",
            relief="flat", cursor="hand2", font=("Segoe UI", 9, "bold"),
            padx=13, pady=9,
        ).pack(side="left", padx=(0, 8))

    def refresh_products(self):
        if not hasattr(self, "table"):
            return
        query = self.search_var.get().strip().lower()
        for row in self.table.get_children():
            self.table.delete(row)
        for name, item in sorted(products.items()):
            if query and query not in name.lower():
                continue
            self.table.insert(
                "", "end", iid=name,
                values=(name.title(), f"₹{item['price']:,.2f}", item["quantity"],
                        "Low stock" if item["quantity"] <= 5 else "In stock"),
                tags=("low" if item["quantity"] <= 5 else "",),
            )
        self.card_values["products"].config(text=str(len(products)))
        self.card_values["units"].config(text=str(sum(p["quantity"] for p in products.values())))
        value = sum(p["price"] * p["quantity"] for p in products.values())
        self.card_values["value"].config(text=f"₹{value:,.0f}")
        low_count = sum(p["quantity"] <= 5 for p in products.values())
        self.card_values["low"].config(text=str(low_count))

    def save_products(self):
        """Write the latest inventory to products.csv."""
        try:
            with CSV_FILE.open("w", newline="", encoding="utf-8") as csv_file:
                writer = csv.DictWriter(csv_file, fieldnames=("name", "price", "quantity"))
                writer.writeheader()
                for name, item in sorted(products.items()):
                    writer.writerow({
                        "name": name,
                        "price": item["price"],
                        "quantity": item["quantity"],
                    })
        except OSError as error:
            messagebox.showerror(
                "Could not save inventory",
                f"The change could not be written to products.csv.\n\n{error}",
                parent=self.root,
            )

    def show_overview(self):
        self.cards.pack(fill="x", padx=32, pady=(0, 20), before=self.inventory_panel)
        self.page_title.config(text="Inventory overview")
        self.page_subtitle.config(text="Manage products and keep your stock up to date.")
        self.set_active_page("overview")
        self.search_var.set("")
        self.refresh_products()

    def show_inventory(self):
        self.cards.pack_forget()
        self.page_title.config(text="Product inventory")
        self.page_subtitle.config(text="View, search, update, sell, or remove your products.")
        self.set_active_page("inventory")
        self.search_var.set("")
        self.refresh_products()
        self.table.focus_set()

    def set_active_page(self, page):
        for name, button in self.nav_buttons.items():
            active = name == page
            button.config(
                bg="#2A3B66" if active else NAVY,
                fg=WHITE if active else "#C5CEE0",
            )

    def selected_product(self):
        selection = self.table.selection()
        if not selection:
            messagebox.showinfo("Select a product", "Choose a product from the list first.", parent=self.root)
            return None
        return selection[0]

    def product_dialog(self, title, name="", price="", quantity="", original_name=None):
        dialog = tk.Toplevel(self.root)
        dialog.title(title)
        dialog.configure(bg=WHITE)
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()
        tk.Label(dialog, text=title, bg=WHITE, fg=TEXT,
                 font=("Segoe UI", 17, "bold")).pack(anchor="w", padx=24, pady=(22, 4))
        tk.Label(dialog, text="Enter the product details below.", bg=WHITE, fg=MUTED,
                 font=("Segoe UI", 9)).pack(anchor="w", padx=24, pady=(0, 12))
        fields = tk.Frame(dialog, bg=WHITE)
        fields.pack(fill="x", padx=24)
        entries = {}
        for key, label, value in (
            ("name", "Product name", name),
            ("price", "Price (₹)", price),
            ("quantity", "Quantity in stock", quantity),
        ):
            tk.Label(fields, text=label, bg=WHITE, fg=TEXT,
                     font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(8, 4))
            entry = tk.Entry(fields, font=("Segoe UI", 10), relief="solid", bd=1)
            entry.pack(fill="x", ipady=7)
            entry.insert(0, value)
            entries[key] = entry

        def save():
            new_name = entries["name"].get().strip().lower()
            try:
                new_price = float(entries["price"].get())
                new_quantity = int(entries["quantity"].get())
                if not new_name or new_price < 0 or new_quantity < 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror(
                    "Invalid details", "Enter a name, a non-negative price, and a whole-number quantity.",
                    parent=dialog,
                )
                return
            if new_name in products and new_name != original_name:
                messagebox.showerror("Product exists", "Choose a different product name.", parent=dialog)
                return
            if original_name and original_name != new_name:
                del products[original_name]
            products[new_name] = {"price": new_price, "quantity": new_quantity}
            self.save_products()
            dialog.destroy()
            self.refresh_products()

        buttons = tk.Frame(dialog, bg=WHITE)
        buttons.pack(fill="x", padx=24, pady=20)
        tk.Button(buttons, text="Cancel", command=dialog.destroy, bg="#F1F4F8", fg=TEXT,
                  relief="flat", cursor="hand2", padx=14, pady=9).pack(side="right", padx=(8, 0))
        tk.Button(buttons, text="Save product", command=save, bg=BLUE, fg=WHITE,
                  activebackground="#2446BD", relief="flat", cursor="hand2",
                  font=("Segoe UI", 9, "bold"), padx=14, pady=9).pack(side="right")
        dialog.update_idletasks()
        x = self.root.winfo_rootx() + (self.root.winfo_width() - dialog.winfo_width()) // 2
        y = self.root.winfo_rooty() + (self.root.winfo_height() - dialog.winfo_height()) // 2
        dialog.geometry(f"+{x}+{y}")
        entries["name"].focus_set()

    def add_product(self):
        self.product_dialog("Add a product")

    def edit_product(self):
        name = self.selected_product()
        if name:
            item = products[name]
            self.product_dialog("Edit product", name, str(item["price"]),
                                str(item["quantity"]), original_name=name)

    def delete_product(self):
        name = self.selected_product()
        if name and messagebox.askyesno(
            "Delete product", f"Remove {name.title()} from your inventory?", parent=self.root
        ):
            del products[name]
            self.save_products()
            self.refresh_products()

    def sell_product(self):
        name = self.selected_product()
        if not name:
            return
        item = products[name]
        if item["quantity"] < 1:
            messagebox.showwarning("Out of stock", f"{name.title()} is out of stock.", parent=self.root)
            return

        dialog = tk.Toplevel(self.root)
        dialog.title("Sell product")
        dialog.configure(bg=WHITE)
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()
        tk.Label(dialog, text=f"Sell {name.title()}", bg=WHITE, fg=TEXT,
                 font=("Segoe UI", 17, "bold")).pack(anchor="w", padx=24, pady=(22, 4))
        tk.Label(dialog, text=f"₹{item['price']:,.2f} each  •  {item['quantity']} in stock",
                 bg=WHITE, fg=MUTED, font=("Segoe UI", 10)).pack(anchor="w", padx=24, pady=(0, 16))
        tk.Label(dialog, text="Quantity", bg=WHITE, fg=TEXT,
                 font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=24)
        quantity_entry = tk.Entry(dialog, font=("Segoe UI", 11), relief="solid", bd=1)
        quantity_entry.pack(fill="x", padx=24, pady=(6, 15), ipady=8)
        quantity_entry.insert(0, "1")

        def complete_sale():
            try:
                count = int(quantity_entry.get())
                if count < 1 or count > item["quantity"]:
                    raise ValueError
            except ValueError:
                messagebox.showerror(
                    "Invalid quantity", f"Enter a whole number from 1 to {item['quantity']}.", parent=dialog
                )
                return
            total = item["price"] * count
            item["quantity"] -= count
            self.save_products()
            dialog.destroy()
            self.refresh_products()
            messagebox.showinfo(
                "Sale complete",
                f"FRESHCART RECEIPT\n\n{name.title()}  ×  {count}\n"
                f"Price each:  ₹{item['price']:,.2f}\nTotal:       ₹{total:,.2f}\n\nThank you for shopping!",
                parent=self.root,
            )

        buttons = tk.Frame(dialog, bg=WHITE)
        buttons.pack(fill="x", padx=24, pady=(0, 22))
        tk.Button(buttons, text="Cancel", command=dialog.destroy, bg="#F1F4F8", fg=TEXT,
                  relief="flat", cursor="hand2", padx=14, pady=9).pack(side="right", padx=(8, 0))
        tk.Button(buttons, text="Complete sale", command=complete_sale, bg=GREEN, fg=WHITE,
                  activebackground="#116D4A", relief="flat", cursor="hand2",
                  font=("Segoe UI", 9, "bold"), padx=14, pady=9).pack(side="right")
        dialog.update_idletasks()
        x = self.root.winfo_rootx() + (self.root.winfo_width() - dialog.winfo_width()) // 2
        y = self.root.winfo_rooty() + (self.root.winfo_height() - dialog.winfo_height()) // 2
        dialog.geometry(f"+{x}+{y}")
        quantity_entry.focus_set()


if __name__ == "__main__":
    window = tk.Tk()
    GroceryApp(window)
    window.mainloop()
