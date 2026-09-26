# Grocery Management System

products = {
    "apple": {"price": 100, "quantity": 20},
    "milk": {"price": 60, "quantity": 15},
    "bread": {"price": 40, "quantity": 10},
    "rice": {"price": 80, "quantity": 25}
}


while True:

    print("\n========== GROCERY MANAGEMENT SYSTEM ==========")
    print("1. View Products")
    print("2. Add Product")
    print("3. Search Product")
    print("4. Update Product")
    print("5. Delete Product")
    print("6. Buy Product")
    print("7. Exit")

    choice = input("Enter your choice: ")

    # 1. View Products
    if choice == "1":

        print("\n--------------- PRODUCTS ----------------")

        for name, details in products.items():
            print(
                name,
                "- Price: ₹", details["price"],
                "- Quantity:", details["quantity"]
            )

    # 2. Add Product
    elif choice == "2":

        name = input("Enter product name: ").lower()

        if name in products:
            print("Product already exists!")

        else:
            price = float(input("Enter price: ₹"))
            quantity = int(input("Enter quantity: "))

            products[name] = {
                "price": price,
                "quantity": quantity
            }

            print("Product added successfully!")

    # 3. Search Product
    elif choice == "3":

        name = input("Enter product name: ").lower()

        if name in products:

            print("\nProduct Found!")
            print("Name:", name)
            print("Price: ₹", products[name]["price"])
            print("Quantity:", products[name]["quantity"])

        else:
            print("Product not found!")

    # 4. Update Product
    elif choice == "4":

        name = input("Enter product name: ").lower()

        if name in products:

            price = float(input("Enter new price: ₹"))
            quantity = int(input("Enter new quantity: "))

            products[name]["price"] = price
            products[name]["quantity"] = quantity

            print("Product updated successfully!")

        else:
            print("Product not found!")

    # 5. Delete Product
    elif choice == "5":

        name = input("Enter product name: ").lower()

        if name in products:
            del products[name]
            print("Product deleted successfully!")

        else:
            print("Product not found!")

    # 6. Buy Product
    elif choice == "6":

        total = 0

        print("\n========== BILL ==========")

        while True:

            name = input("Enter product name (or 'done' to finish): ").lower()

            if name == "done":
                break

            if name not in products:
                print("Product not found!")
                continue

            quantity = int(input("Enter quantity: "))

            if quantity > products[name]["quantity"]:
                print("Not enough stock!")

            else:

                price = products[name]["price"]
                amount = price * quantity

                products[name]["quantity"] -= quantity
                total += amount

                print(name, "x", quantity, "=", "₹", amount)

        print("--------------------------")
        print("Total Bill: ₹", total)
        print("==========================")

    # 7. Exit
    elif choice == "7":

        print("Thank you for using Grocery Management System!")
        break

    else:
        print("Invalid choice! Please try again.")
        