from django.shortcuts import render,redirect
from django.db import connection
import os
from django.conf import settings
from django.http import HttpResponse
import MySQLdb
from django.contrib import messages

# Create your views here.

def admin_login(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        
        with connection.cursor() as cursor:
            cursor.execute("SELECT admin_id,username,name FROM admin WHERE username = %s AND admin_password = %s", [username, password])
            admin = cursor.fetchone()

        if admin:
            request.session['admin_id'] = admin[0]
            request.session['admin_username']=admin[1]
            request.session['admin_name']=admin[2]
            return redirect('admin_dashboard')  # Adjust the redirect to your dashboard route
        else:
            messages.error(request,'Invalid Username or Password !')

    return render(request, 'admin_login.html')

def admin_logout_view(request):
    # Clear the session
    request.session.flush()
    # Redirect to the admin login page
    return redirect('admin_login')

def custom_admin_view(request):
    if 'admin_id' not in request.session:
        return redirect('admin_login')
    username = "Guest"  # Default value for username
    userCount = 0       # Default value for user count
    productCount=0
    recent_activities=[]
    admin_username=request.session.get('admin_username')
    admin_name=request.session.get('admin_name')
    try:
        # Execute raw SQL queries
        with connection.cursor() as cursor:
            # Query 1: Fetch the most recently registered user's username
            cursor.execute("SELECT username FROM users ORDER BY register_date DESC LIMIT 1;")
            result = cursor.fetchone()  # Fetch a single row

            if result:
                username = result[0]  # Extract the username

            # Query 2: Count the total number of users
            cursor.execute("SELECT COUNT(user_id) FROM users;")
            user_count = cursor.fetchone()  # Fetch the count

            if user_count:
                userCount = user_count[0]  # Extract the count from the tuple

            # Query 3: Count the total number of products
            cursor.execute("SELECT COUNT(product_id) FROM product;")
            product_count = cursor.fetchone()  # Fetch the count

            if product_count:
                productCount = product_count[0]  # Extract the count from the tuple

            # Query 4: Fetch recent activities
            cursor.execute("SELECT action FROM activity_log ORDER BY timestamp DESC LIMIT 5;")
            recent_activities = [row[0] for row in cursor.fetchall()]  # Convert tuples to list

           # Query 5: Count the total number of orders
            cursor.execute("SELECT COUNT(order_id) FROM orders;")
            order_count = cursor.fetchone()  # Fetch the count

            if order_count:
                orderCount = order_count[0]  # Extract the count from the tuple


            # Query 6: Count the total number of brands
            cursor.execute("SELECT COUNT(brand_id) FROM brands;")
            brand_count = cursor.fetchone()  # Fetch the count

            if brand_count:
                brandCount = brand_count[0]  # Extract the count from the tuple

    except Exception as e:
        # Handle exceptions gracefully and log the error
        print(f"Error fetching users: {e}")

    # Prepare context with the fetched username and user count
    context = {
        'user': username,
        'usercount': userCount,
        'productCount':productCount,
        'activities':recent_activities,
        'admin_username':admin_username,
        'admin_name':admin_name,
        'brand_count':brandCount,
        'order_count':orderCount
    }

    # Render the template with the context
    return render(request, 'admin_dashboard.html', context)




def user_page(request):
    users = []
    try:
        # Raw SQL Query to fetch users from the MySQL database
        with connection.cursor() as cursor:
            cursor.execute("SELECT user_id, username,name,email,phone_no,address,is_active FROM users")
            rows = cursor.fetchall()
            for row in rows:
                users.append({
                    'user_id': row[0],
                    'username': row[1],
                    'name': row[2],
                    'email': row[3],
                    'phone_no': row[4],
                    'address': row[5],
                    'is_active':row[6],

                })
              
    except Exception as e:
        print(f"Error fetching users: {e}")

    # Pass users data to the template
    return render(request, 'user_page.html', {'users': users})




from django.db import connection, transaction
from django.shortcuts import redirect

def delete_users(request):
    if request.method == "POST":
        # Get user IDs from the POST request
        user_ids = request.POST.getlist('user_ids')  # e.g., ['1', '2', '3']
        
        if user_ids:
            try:
                with transaction.atomic():  # Ensures all queries execute as one transaction
                    with connection.cursor() as cursor:
                        # Convert user_ids to integers to prevent SQL errors
                        user_ids = [int(uid) for uid in user_ids]

                        # Create placeholders for SQL query
                        placeholders = ",".join(["%s"] * len(user_ids))

                        # Fetch usernames BEFORE deleting users
                        cursor.execute(f"SELECT username FROM users WHERE user_id IN ({placeholders})", user_ids)
                        usernames = [row[0] for row in cursor.fetchall()]  # Extract usernames from result

                        if usernames:  # If there are users to delete
                            # Delete users from the database
                            cursor.execute(f"DELETE FROM users WHERE user_id IN ({placeholders})", user_ids)

                            # Log deletion activities for each user
                            activity_logs = [(f"User {username} deleted.",) for username in usernames]
                            cursor.executemany("INSERT INTO activity_log (action) VALUES (%s)", activity_logs)

            except Exception as e:
                print(f"Error deleting users: {e}")

    return redirect('user_page')  # Redirect to users page after deletion

def product_page(request):

    return render(request,'product_page.html')
    
def category_page(request):

    return render(request,'category_page.html')

def brand_page(request):
    return render(request,'brand_page.html')

def color_page(request):
    return render(request,'color_page.html')

from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.db import connection

def add_category(request):

    if request.method=="POST":
        category_name=request.POST['category_name']

        with connection.cursor() as cursor:
            fetch_query="select category_name from category"

            cursor.execute(fetch_query)
            result = [row[0] for row in cursor.fetchall()]
            if category_name in result:
                print("already  exist")
                messages.error(request,'category already Exist !')
            else:
                query="Insert into category(category_name)values(%s)"
                values=(category_name ,)
                cursor.execute(query,values)
                return redirect('show_category')
    return  render(request,'add_category.html')


def add_brand(request):
    if request.method=="POST":
        brand_name=request.POST['brand_name']

        with connection.cursor() as cursor:
            fetch_query="select brand_name from brands"

            cursor.execute(fetch_query)
            result = [row[0] for row in cursor.fetchall()]
            if brand_name in result:
                print("already  exist")
                messages.error(request,'Brand already Exist !')
            else:
                query="Insert into brands(brand_name)values(%s)"
                values=(brand_name ,)
                cursor.execute(query,values)
                return redirect('show_brand')
    return render(request,'add_brand.html')

def add_color(request):
    result=[]
    if request.method=="POST":
        color_name=request.POST['color_name']


        with connection.cursor() as cursor:
            fetch_query="select color_name from colors"

            cursor.execute(fetch_query)
            result = [row[0] for row in cursor.fetchall()]
            if color_name in result:
                print("already  exist")
                messages.error(request,'Color already Exist !')
            else:
                query="Insert into colors(color_name)values(%s)"
                values=(color_name ,)
                cursor.execute(query,values)
                return redirect('show_color')
    return render(request,'add_color.html')


def add_product(request):

    # categories = []
    with connection.cursor() as cursor:
        cursor.execute("SELECT category_id, category_name FROM Category")
        categories = cursor.fetchall()  # Fetch all categories

   
        cursor.execute("SELECT brand_id,brand_name  FROM brands")
        brands = cursor.fetchall()  # Fetch all categories

        cursor.execute("SELECT color_id,color_name  FROM colors")
        colors = cursor.fetchall()  # Fetch all categories

        
        

    
    if request.method == "POST":
        # Get form data
        product_name = request.POST['product_name']
        size = request.POST['size']
        brand_id = request.POST['brand']
        color_id = request.POST['color']
        price = request.POST['price']
        description = request.POST['description']
        category_id = request.POST['category']
        stock_quantity = request.POST['stock_quantity']
        product_image = request.FILES['product_image']

        # Save the uploaded image in the media folder
        image_path = os.path.join(settings.MEDIA_ROOT, 'product_images', product_image.name)
        os.makedirs(os.path.dirname(image_path), exist_ok=True)
        with open(image_path, 'wb+') as destination:
            for chunk in product_image.chunks():
                destination.write(chunk)

        # Save the product details in the database
        try:
            with connection.cursor() as cursor:
                query = """
                    INSERT INTO product (pro_name,size,brand_id,color_id,price,category_id,stock_quantity,description,productURL)
                    VALUES (%s, %s, %s, %s, %s, %s, %s,%s,%s)
                """ 
                cursor.execute(query, (product_name,size,brand_id,color_id,price,category_id, stock_quantity, description, 'product_images/' + product_image.name))

                cursor.execute("INSERT INTO activity_log (action) VALUES (%s)", 
                           [f"Product {product_name} Added."])
        except Exception as e:
            print(f"Error adding product: {e}")
            return render(request, 'add_product.html', {'error': 'Failed to add product.'})

        # Redirect to another page (e.g., product list) after successful addition
        return redirect('product_list')

    return render(request, 'add_product.html', {'categories': categories,'brands':brands,'colors':colors}) 




def product_list(request):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                Product.product_id, 
                Product.pro_name,
                Product.size,
                Product.price,
                Product.description, 
                Product.stock_quantity,
                Product.productURL, 
                Category.category_name, 
                Brands.brand_name, 
                Colors.color_name 
            FROM Product 
            INNER JOIN Category ON Product.category_id = Category.category_id
            INNER JOIN Brands ON Product.brand_id = Brands.brand_id
            INNER JOIN Colors ON Product.color_id = Colors.color_id
        """)
        
        products = [
            dict(zip([column[0] for column in cursor.description], row))
            for row in cursor.fetchall()
        ]
    
    # Prepend MEDIA_URL to the image paths
    for product in products:
        product['image_url'] = settings.MEDIA_URL + product['productURL']
    
    return render(request, 'product_list.html', {'products': products})

def show_category(request):
    with connection.cursor() as cursor:
        cursor.execute("""SELECT category_id, category_name FROM category """)
        
        categories = [
            dict(zip([column[0] for column in cursor.description], row))
            for row in cursor.fetchall()
        ]
    
    
    
    return render(request, 'show_category.html', {'categories': categories})


def show_brand(request):

    with connection.cursor() as cursor:
        cursor.execute("""SELECT brand_id, brand_name FROM brands """)
        
        brands = [
            dict(zip([column[0] for column in cursor.description], row))
            for row in cursor.fetchall()
        ]
    
    
    
    return render(request, 'show_brand.html', {'brands': brands})

def show_color(request):
    
     with connection.cursor() as cursor:
        cursor.execute("""SELECT color_id, color_name FROM colors""")
        
        colors = [
            dict(zip([column[0] for column in cursor.description], row))
            for row in cursor.fetchall()
        ]
    
    
    
        return render(request, 'show_color.html', {'colors': colors})
     

# def delete_product(request, product_id):
#     if request.method == 'POST':
#         with connection.cursor() as cursor:
#             cursor.execute("DELETE FROM product WHERE product_id = %s", [product_id])
#         return redirect('product_list')
    
def update_or_delete_product(request, product_id):
    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'update':
            return redirect('update_productPage', product_id=product_id)

        elif action == 'delete':
                
                
            with connection.cursor() as cursor:
                cursor.execute("select pro_name from product where product_id =%s",[product_id])
                pro_name=cursor.fetchone()

                cursor.execute("INSERT INTO activity_log (action) VALUES (%s)", 
                           [f"Product {pro_name[0]} deleted"])
                cursor.execute("DELETE FROM product WHERE product_id = %s", [product_id])
            return redirect('product_list')

    return redirect('product_list')


def update_or_delete_category(request, category_id):
    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'update':
            return redirect('update_categoryPage', category_id=category_id)

        elif action == 'delete':
            with connection.cursor() as cursor:
                cursor.execute("SELECT category_name FROM category WHERE category_id = %s", [category_id])
                category_name = cursor.fetchone()

                if category_name:  # Check if category exists
                    cursor.execute("INSERT INTO activity_log (action) VALUES (%s)", 
                                   [f"Category {category_name[0]} deleted"])
                
                cursor.execute("DELETE FROM category WHERE category_id = %s", [category_id])

            return redirect('show_category')

    return redirect('show_category')




# def update_products(request, product_id):

#     categories = []
#     with connection.cursor() as cursor:
#         cursor.execute("SELECT category_id, category_name FROM Category")
#         categories = cursor.fetchall()  # Fetch all categories

   
#         cursor.execute("SELECT brand_id,brand_name  FROM brands")
#         brands = cursor.fetchall()  # Fetch all categories

#         cursor.execute("SELECT color_id,color_name  FROM colors")
#         colors = cursor.fetchall()  # Fetch all categories

        
        

    
#     if request.method == "POST":
#         # Get form data
#         product_name = request.POST['pro_name']
#         size = request.POST['size']
#         brand_id = request.POST['brand']
#         color_id = request.POST['color']
#         price = request.POST['price']
#         description = request.POST['description']
#         category_id = request.POST['category']
#         stock_quantity = request.POST['stock_quantity']
#         product_image = request.FILES['product_image']

#         # Save the uploaded image in the media folder
#         image_path = os.path.join(settings.MEDIA_ROOT, 'product_images', product_image.name)
#         os.makedirs(os.path.dirname(image_path), exist_ok=True)
#         with open(image_path, 'wb+') as destination:
#             for chunk in product_image.chunks():
#                 destination.write(chunk)

#         # Save the product details in the database
#         with connection.cursor() as cursor:
#             cursor.execute("""
#                 UPDATE product 
#                 SET pro_name = %s, category_id = %s, price = %s, description = %s,
#                     color_id = %s, size = %s, brand_id  = %s, stock_quantity = %s
#                 WHERE product_id = %s
#              """, [product_name, category_id, price, description, color_id, size, brand_id, stock_quantity, product_id])

#         return redirect('product_list')
    
#     # Fetch existing product data for pre-filling the form
#     with connection.cursor() as cursor:
        
#         cursor.execute("SELECT category_id, category_name FROM category")
#         categories = cursor.fetchall()

#         cursor.execute("""
#             SELECT 
#                 Product.product_id, 
#                 Product.pro_name,
#                 Product.size,
#                 Product.price,
#                 Product.description, 
#                 Product.stock_quantity,
#                 Product.productURL, 
#                 Category.category_name, 
#                 Brands.brand_name, 
#                 Colors.color_name, 
#                 product.category_id
#             FROM Product 
#             INNER JOIN Category ON Product.category_id = Category.category_id
#             INNER JOIN Brands ON Product.brand_id = Brands.brand_id
#             INNER JOIN Colors ON Product.color_id = Colors.color_id
#         """)

#         product=cursor.fetchone()

#     if product:
#         product_data = {
#             'product_id': product[0],
#             'pro_name': product[1],
#             'size': product[2],
#             'price': product[3],
#             'description': product[4],
#             'stock_quantity': product[5],
#             'productURL':product[6],
#             'category_name': product[7],
#             'brand_name': product[8],
#             'color_name': product[9],
#             'category_id':product[10]
#         }
#     else:
#         product_data = None

#     return render(request, 'update_product.html',{'product': product_data, 'categories': categories})    



from django.shortcuts import render, redirect
from django.db import connection

import os
from django.shortcuts import render, redirect
from django.conf import settings
from django.db import connection

def update_productPage(request, product_id):
    # Fetch product details
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM product WHERE product_id = %s", [product_id])
        columns = [col[0] for col in cursor.description]  # Get column names
        product_data = cursor.fetchone()
        product = dict(zip(columns, product_data)) if product_data else None

        # Fetch brands, colors, and categories
        cursor.execute("SELECT brand_id, brand_name FROM brands")
        brands = cursor.fetchall()

        cursor.execute("SELECT color_id, color_name FROM colors")
        colors = cursor.fetchall()

        cursor.execute("SELECT category_id, category_name FROM category")
        categories = cursor.fetchall()

    if request.method == 'POST':
        # Get form data
        pro_name = request.POST.get('pro_name')
        size = request.POST.get('size')
        price = request.POST.get('price')
        stock_quantity = request.POST.get('stock_quantity')
        description = request.POST.get('description')
        brand_id = request.POST.get('brand')
        color_id = request.POST.get('color')
        category_id = request.POST.get('category')
        product_image = request.FILES.get('product_image', None)

        # Handle product image upload if provided
        if product_image:
            image_path = os.path.join(settings.MEDIA_ROOT, 'product_images', product_image.name)
            os.makedirs(os.path.dirname(image_path), exist_ok=True)
            with open(image_path, 'wb+') as destination:
                for chunk in product_image.chunks():
                    destination.write(chunk)
            product_image_url = f'product_images/{product_image.name}'
        else:
            product_image_url = product[8]  # Keep current image if no new image is uploaded

        # Update product using raw SQL
        with connection.cursor() as cursor:
            cursor.execute("""
                UPDATE product 
                SET pro_name = %s, size = %s, price = %s, stock_quantity = %s, description = %s, 
                    brand_id = %s, color_id = %s, category_id = %s, productURL = %s
                WHERE product_id = %s
            """, [pro_name, size, price, stock_quantity, description, brand_id, color_id, category_id, product_image_url, product_id])


            cursor.execute("INSERT INTO activity_log (action) VALUES (%s)", 
                           [f"Product {pro_name} Updated."])
        return redirect('product_list')

     # Render the update page
    return render(request, 'update_product.html', {
        'product': product,  # Now product is a proper dictionary
        'brands': brands,
        'colors': colors,
        'categories': categories
    })

def update_categoryPage(request, category_id):
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM category WHERE category_id = %s", [category_id])
            columns = [col[0] for col in cursor.description]
            category_data = cursor.fetchone()
            category = dict(zip(columns, category_data)) if category_data else None
    except Exception as e:
        return redirect('show_category')  # Handle error gracefully

    if not category:
        return redirect('show_category')

    if request.method == 'POST':
        category_name = request.POST.get('category_name')
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    UPDATE category 
                    SET category_name = %s
                    WHERE category_id = %s
                """, [category_name, category_id])
                cursor.execute("INSERT INTO activity_log (action) VALUES (%s)", 
                               ["Category updated to %s." % category_name])
            return redirect('show_category')
        except Exception as e:
            return redirect('show_category')  # Handle error gracefully

    return render(request, 'update_category.html', {'category': category})



def update_or_delete_color(request, color_id):
    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'update':
            return redirect('update_colorPage', color_id=color_id)

        elif action == 'delete':
            with connection.cursor() as cursor:
                cursor.execute("SELECT color_name FROM colors WHERE color_id = %s", [color_id])
                color_name = cursor.fetchone()

                if color_name:  # Check if category exists
                    cursor.execute("INSERT INTO activity_log (action) VALUES (%s)", 
                                   [f"color {color_name[0]} deleted"])
                
                cursor.execute("DELETE FROM colors WHERE color_id = %s", [color_id])

            return redirect('show_color')

    return redirect('show_color')

def update_colorPage(request, color_id):
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM colors WHERE color_id = %s", [color_id])
            columns = [col[0] for col in cursor.description]
            color_data = cursor.fetchone()
            color = dict(zip(columns, color_data)) if color_data else None
    except Exception as e:
        return redirect('show_color')  # Handle error gracefully

    if not color:
        return redirect('show_color')

    if request.method == 'POST':
        color_name = request.POST.get('color_name')
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    UPDATE colors 
                    SET color_name = %s
                    WHERE color_id = %s
                """, [color_name, color_id])
                cursor.execute("INSERT INTO activity_log (action) VALUES (%s)", 
                               ["color updated to %s." % color_name])
            return redirect('show_color')
        except Exception as e:
            return redirect('show_color')  # Handle error gracefully

    return render(request, 'update_color.html', {'color': color})




def update_or_delete_brand(request, brand_id):
    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'update':
            return redirect('update_brandPage', brand_id=brand_id)

        elif action == 'delete':
            with connection.cursor() as cursor:
                cursor.execute("SELECT brand_name FROM brands WHERE brand_id = %s", [brand_id])
                brand_name = cursor.fetchone()

                if brand_name:  # Check if category exists
                    cursor.execute("INSERT INTO activity_log (action) VALUES (%s)", 
                                   [f"brand {brand_name[0]} deleted"])
                
                cursor.execute("DELETE FROM brands WHERE brand_id = %s", [brand_id])

            return redirect('show_brand')

    return redirect('show_brand')

def update_brandPage(request, brand_id):
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM brands WHERE brand_id = %s", [brand_id])
            columns = [col[0] for col in cursor.description]
            brand_data = cursor.fetchone()
            brand = dict(zip(columns, brand_data)) if brand_data else None
    except Exception as e:
        return redirect('show_color')  # Handle error gracefully

    if not brand:
        return redirect('show_brand')

    if request.method == 'POST':
        brand_name = request.POST.get('brand_name')
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    UPDATE brands 
                    SET brand_name = %s
                    WHERE brand_id = %s
                """, [brand_name, brand_id])
                cursor.execute("INSERT INTO activity_log (action) VALUES (%s)", 
                               ["brand updated to %s." % brand_name])
            return redirect('show_brand')
        except Exception as e:
            return redirect('show_brand')  # Handle error gracefully

    return render(request, 'update_brand.html', {'brand': brand})


# handled orders 


from django.shortcuts import render, redirect
from django.db import connection

# # Function to fetch orders for admin
# def admin_orders(request):
#     with connection.cursor() as cursor:
#         cursor.execute("SELECT order_id, user_id, order_date, total_amount, delivery_address,payment_status,order_status FROM orders")
#         orders = cursor.fetchall()  # Fetch all orders

#     return render(request, 'admin_orders.html', {'orders': orders})

# Function to update order status
def update_order_status(request, order_id):
    if request.method == "POST":
        new_status = request.POST['status']
        
        with connection.cursor() as cursor:
            cursor.execute("UPDATE orders SET status = %s WHERE id = %s", [new_status, order_id])
        
        return redirect('admin_orders')  # Redirect to admin orders page



def admin_base(request):
    return render(request,'admin_base.html')



# Manage Orders ......................................................

from django.shortcuts import render
import MySQLdb

# Admin Orders Page ......

# def admin_orders(request):
#     if 'admin_id' not in request.session:
#         return redirect('admin_login')
#     # Connect to the MySQL database
#     # db = MySQLdb.connect(host="localhost", user="root", password="", database="Stationery_management")
#     # cursor = db.cursor(MySQLdb.cursors.DictCursor)

#     with connection.cursor() as cursor:

#         # Fetch all orders
#         query = "SELECT order_id, user_id, order_date, total_amount, delivery_address, payment_status, order_status, delivery_status, payment_method FROM orders ORDER BY order_date DESC"
#         cursor.execute(query)
#         orders = cursor.fetchall()

#         # db.close()

#     return render(request, "manage_order.html", {"orders": orders})

def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]

def admin_orders(request):
    if 'admin_id' not in request.session:
        return redirect('admin_login')

    with connection.cursor() as cursor:
        cursor.execute("""
           SELECT order_id, user_id, order_date, total_amount, delivery_address, payment_status, order_status, delivery_status, payment_method FROM orders ORDER BY order_date DESC
        """)
        orders = dictfetchall(cursor)

    return render(request, "manage_order.html", {"orders": orders})


from django.shortcuts import redirect
import MySQLdb
def update_status(request):
    if request.method == "POST":
        with connection.cursor() as cursor:
            for key in request.POST:
                if key.startswith("order_id_"):
                    order_id = request.POST[key]
                    order_status = request.POST.get(f"order_status_{order_id}", "")
                    delivery_status = request.POST.get(f"delivery_status_{order_id}", "")
                    payment_status = request.POST.get(f"payment_status_{order_id}", "")

                    update_query = """
                        UPDATE orders 
                        SET order_status = %s, delivery_status = %s, payment_status = %s  
                        WHERE order_id = %s
                    """
                    cursor.execute(update_query, (order_status, delivery_status, payment_status, order_id))

        return redirect("admin_orders")

def delete_order(request):
    if request.method == "POST":
        order_id = request.POST["order_id"]

        # db = MySQLdb.connect(host="localhost", user="root", password="", database="stationery_management")
        # cursor = db.cursor()
        with connection.cursor() as cursor:

            delete_query = "DELETE FROM orders WHERE order_id = %s"
            cursor.execute(delete_query, (order_id,))
            # db.commit()
            # db.close()
        

    return redirect("admin_orders")



# contactUs messages ..................

def admin_contact_messages(request):
    with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM contact_messages ORDER BY created_at DESC")
            messages = cursor.fetchall()

            cursor.close()
           

    return render(request, "admin_contactUs.html", {"messages": messages})


# Handle the reply form
def reply_message(request, message_id):
    if request.method == "POST":
        reply_text = request.POST.get("reply")

    with connection.cursor() as cursor:

            sql = "UPDATE contact_messages SET reply = %s WHERE id = %s"
            cursor.execute(sql, (reply_text, message_id))
            cursor.close()
            return redirect("admin_contact_messages")

    return HttpResponse("Invalid request")


def delete_color(request, color_id):
    if request.method == 'POST':
        action = request.POST.get('action')

    
        if action == 'delete':
                
                
            with connection.cursor() as cursor:
                cursor.execute("select color_name from colors where color_id =%s",[color_id])
                color_name=cursor.fetchone()

                cursor.execute("INSERT INTO activity_log (action) VALUES (%s)", 
                           [f"Product {color_name[0]} deleted"])
                cursor.execute("DELETE FROM colors WHERE color_id = %s", [color_id])
            return redirect('show_color')

    return redirect('show_color')


def delete_brand(request, brand_id):
    if request.method == 'POST':
        action = request.POST.get('action')

    
        if action == 'delete':
                
                
            with connection.cursor() as cursor:
                cursor.execute("select brand_name from brands where brand_id =%s",[brand_id])
                brand_name=cursor.fetchone()

                cursor.execute("INSERT INTO activity_log (action) VALUES (%s)", 
                           [f"Product {brand_name[0]} deleted"])
                cursor.execute("DELETE FROM brands WHERE brand_id = %s", [brand_id])
            return redirect('show_brand')

    return redirect('show_brand')


def delete_category(request, category_id):
    if request.method == 'POST':
        action = request.POST.get('action')

    
        if action == 'delete':
                
                
            with connection.cursor() as cursor:
                cursor.execute("select category_name from category where category_id =%s",[category_id])
                category_name=cursor.fetchone()

                cursor.execute("INSERT INTO activity_log (action) VALUES (%s)", 
                           [f"Product {category_name[0]} deleted"])
                cursor.execute("DELETE FROM category WHERE category_id = %s", [category_id])
            return redirect('show_category')

    return redirect('show_category')




# # manage delivery.........................................................
from django.shortcuts import render, redirect
from django.db import connection
from django.contrib import messages

def manage_deliveries_view(request):
    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        action = request.POST.get('action')

        with connection.cursor() as cursor:
            # Get current order status for validation
            cursor.execute("SELECT order_status, delivery_status FROM orders WHERE ORDER_ID = %s", [order_id])
            current_status = cursor.fetchone()
            if not current_status:
                messages.error(request, f'Order #{order_id} not found.')
                return redirect('manage_deliveries')

            order_status, delivery_status = current_status

            if action == 'process' and order_status == 'Pending':
                cursor.execute("""
                    UPDATE orders 
                    SET order_status = 'Processing'
                    WHERE ORDER_ID = %s
                """, [order_id])
                cursor.execute("""
                    INSERT INTO activity_log (action, timestamp)
                    VALUES (%s, NOW())
                """, [f'Order #{order_id} set to Processing'])
                messages.success(request, f'Order #{order_id} is now being processed.')

            elif action == 'dispatch' and order_status == 'Processing':
                staff_id = request.POST.get('staff_id')
                delivery_address = request.POST.get('delivery_address')
                if not staff_id or not delivery_address:
                    messages.error(request, 'Staff and delivery address are required.')
                else:
                    cursor.execute("""
                        INSERT INTO delivery (order_id, delivery_date, delivery_status, delivery_staff_id, delivery_address)
                        VALUES (%s, CURDATE(), 'Shipped', %s, %s)
                    """, [order_id, staff_id, delivery_address])
                    cursor.execute("""
                        UPDATE orders 
                        SET order_status = 'Shipped', delivery_status = 'Shipped'
                        WHERE ORDER_ID = %s
                    """, [order_id])
                    cursor.execute("""
                        UPDATE product p
                        JOIN order_details od ON p.product_id = od.pro_id
                        SET p.stock_quantity = p.stock_quantity - od.quantity
                        WHERE od.order_id = %s
                    """, [order_id])
                    cursor.execute("""
                        INSERT INTO inventory_log (product_id, quantity_change, change_date, staff_id, change_reason)
                        SELECT pro_id, -quantity, CURDATE(), %s, CONCAT('Order #', %s, ' dispatched')
                        FROM order_details
                        WHERE order_id = %s
                    """, [staff_id, order_id, order_id])
                    cursor.execute("""
                        INSERT INTO activity_log (action, timestamp)
                        VALUES (%s, NOW())
                    """, [f'Order #{order_id} dispatched with staff ID {staff_id}'])
                    messages.success(request, f'Order #{order_id} dispatched.')

            elif action == 'update_status' and order_status in ('Shipped', 'Out for Delivery'):
                new_status = request.POST.get('delivery_status')
                if new_status == 'Delivered' and delivery_status != 'Delivered':
                    cursor.execute("""
                        UPDATE delivery 
                        SET delivery_status = 'Delivered', delivery_date = CURDATE()
                        WHERE order_id = %s
                    """, [order_id])
                    cursor.execute("""
                        UPDATE orders 
                        SET order_status = 'Delivered', delivery_status = 'Delivered'
                        WHERE ORDER_ID = %s
                    """, [order_id])
                    cursor.execute("""
                        UPDATE billing 
                        SET billing_status = 'done'
                        WHERE order_id = %s
                    """, [order_id])
                elif new_status in ('Out for Delivery', 'Cancelled') and delivery_status != new_status:
                    cursor.execute("""
                        UPDATE delivery 
                        SET delivery_status = %s
                        WHERE order_id = %s
                    """, [new_status, order_id])
                    cursor.execute("""
                        UPDATE orders 
                        SET delivery_status = %s
                        WHERE ORDER_ID = %s
                    """, [new_status, order_id])
                    if new_status == 'Cancelled':
                        cursor.execute("""
                            UPDATE orders 
                            SET order_status = 'Cancelled'
                            WHERE ORDER_ID = %s
                        """, [order_id])
                else:
                    messages.error(request, 'Invalid status transition.')
                    return redirect('manage_delivery')

                cursor.execute("""
                    INSERT INTO activity_log (action, timestamp)
                    VALUES (%s, NOW())
                """, [f'Order #{order_id} delivery status updated to {new_status}'])
                messages.success(request, f'Order #{order_id} status updated to {new_status}.')

            else:
                messages.error(request, f'Invalid action for Order #{order_id} in status {order_status}.')

        return redirect('manage_delivery')

    # Fetch orders and staff
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT o.ORDER_ID, o.USER_ID, o.order_date, o.total_amount, o.delivery_address, 
                   o.order_status, o.delivery_status, u.name AS customer_name, 
                   d.delivery_staff_id, s.first_name, s.last_name
            FROM orders o
            JOIN users u ON o.USER_ID = u.user_id
            LEFT JOIN delivery d ON o.ORDER_ID = d.order_id
            LEFT JOIN staff s ON d.delivery_staff_id = s.staff_id
            ORDER BY o.order_date ASC
        """)
        orders = cursor.fetchall()

        cursor.execute("""
            SELECT staff_id, first_name, last_name 
            FROM staff 
            WHERE role = 'Delivery Driver' AND staff_status = 'Active'
        """)
        staff = cursor.fetchall()

    order_list = [
        {
            'order_id': row[0],
            'user_id': row[1],
            'order_date': row[2],
            'total_amount': row[3],
            'delivery_address': row[4],
            'order_status': row[5],
            'delivery_status': row[6] if row[6] else 'Pending',
            'customer_name': row[7],
            'staff_name': f"{row[9]} {row[10]}" if row[9] else 'Not Assigned'
        } for row in orders
    ]
    staff_list = [{'id': row[0], 'name': f"{row[1]} {row[2]}"} for row in staff]

    return render(request, 'manage_delivery.html', {
        'orders': order_list,
        'staff_list': staff_list
    })


# reports page .............................................
# views.py
# views.py
# views.py
from django.shortcuts import render
from django.db import connection, transaction
from datetime import datetime

def reports_view(request):
    with connection.cursor() as cursor:
        # Total Sales Report
        cursor.execute("""
            SELECT 
                COUNT(o.ORDER_ID) as total_orders, 
                SUM(o.total_amount) as total_sales 
            FROM orders o 
            WHERE o.payment_status = 'Completed'
        """)
        sales_data = cursor.fetchone()
        total_orders, total_sales = sales_data if sales_data else (0, 0.00)

        # Top-Selling Products
        cursor.execute("""
            SELECT 
                p.pro_name, 
                SUM(od.quantity) as total_quantity, 
                SUM(od.subtotal) as total_revenue 
            FROM order_details od 
            JOIN product p ON od.pro_id = p.product_id 
            JOIN orders o ON od.order_id = o.ORDER_ID 
            WHERE o.payment_status = 'Completed' 
            GROUP BY p.product_id, p.pro_name 
            ORDER BY total_revenue DESC 
            LIMIT 5
        """)
        top_products = cursor.fetchall()

        # Order Status Summary
        cursor.execute("""
            SELECT 
                order_status, 
                COUNT(ORDER_ID) as count 
            FROM orders 
            GROUP BY order_status
        """)
        order_status = cursor.fetchall()

        # Low Stock Inventory (with reorder_level)
        cursor.execute("""
            SELECT 
                p.product_id,
                p.pro_name, 
                p.stock_quantity, 
                IFNULL(p.reorder_level, 10) as reorder_level 
            FROM product p 
            WHERE p.stock_quantity < IFNULL(p.reorder_level, 10)
            ORDER BY p.stock_quantity ASC
        """)
        low_stock = cursor.fetchall()

        # Recent Activity Log
        cursor.execute("""
            SELECT 
                action, 
                timestamp 
            FROM activity_log 
            ORDER BY timestamp DESC 
            LIMIT 5
        """)
        recent_activity = cursor.fetchall()

        # Top Customers
        cursor.execute("""
            SELECT 
                u.name, 
                COUNT(o.ORDER_ID) as order_count, 
                SUM(o.total_amount) as total_spent 
            FROM orders o 
            JOIN users u ON o.USER_ID = u.user_id 
            WHERE o.payment_status = 'Completed' 
            GROUP BY u.user_id, u.name 
            ORDER BY total_spent DESC 
            LIMIT 5
        """)
        top_customers = cursor.fetchall()

        # Top Staff Performance
        cursor.execute("""
            SELECT 
                CONCAT(s.first_name, ' ', s.last_name) as staff_name, 
                COUNT(d.delivery_id) as delivery_count 
            FROM delivery d 
            JOIN staff s ON d.delivery_staff_id = s.staff_id 
            WHERE d.delivery_status = 'Delivered' 
            GROUP BY s.staff_id, s.first_name, s.last_name 
            ORDER BY delivery_count DESC 
            LIMIT 5
        """)
        top_staff = cursor.fetchall()

        # Handle Restock Action
        restock_message = None
        if request.method == 'POST' and 'restock_product_id' in request.POST:
            product_id = request.POST.get('restock_product_id')
            restock_amount = int(request.POST.get('restock_amount', 50))

            with transaction.atomic():
                cursor.execute("""
                    UPDATE product 
                    SET stock_quantity = stock_quantity + %s 
                    WHERE product_id = %s
                """, [restock_amount, product_id])

                cursor.execute("""
                    INSERT INTO inventory_log (product_id, quantity_change, change_date, staff_id, change_reason)
                    VALUES (%s, %s, CURDATE(), %s, %s)
                """, [product_id, restock_amount, 201, f"Manual restock via reports page"])

                # Refresh low stock after restock
                cursor.execute("""
                    SELECT 
                        p.product_id,
                        p.pro_name, 
                        p.stock_quantity, 
                        IFNULL(p.reorder_level, 10) as reorder_level 
                    FROM product p 
                    WHERE p.stock_quantity < IFNULL(p.reorder_level, 10)
                    ORDER BY p.stock_quantity ASC
                """)
                low_stock = cursor.fetchall()

            restock_message = f"Restocked product ID {product_id} with {restock_amount} units."

    context = {
        'total_orders': total_orders,
        'total_sales': total_sales,
        'top_products': top_products,
        'order_status': order_status,
        'low_stock': low_stock,
        'recent_activity': recent_activity,
        'top_customers': top_customers,
        'top_staff': top_staff,
        'current_date': datetime.now().strftime('%B %d, %Y'),
        'restock_message': restock_message,
    }
    return render(request, 'reports.html', context)




    #   staff side........................................................



from django.shortcuts import render, redirect
from django.db import connection
from django.contrib import messages

def staff_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        with connection.cursor() as cursor:
            cursor.execute("SELECT staff_id, first_name, last_name, role FROM staff WHERE username = %s AND staff_password = %s", [username, password])
            staff = cursor.fetchone()
        
        if staff:
            request.session['staff_id'] = staff[0]
            request.session['staff_name'] = f"{staff[1]} {staff[2]}"
            request.session['staff_role'] = staff[3]
            return redirect('staff_dashboard')
        else:
            messages.error(request, "Invalid credentials")
    
    return render(request, 'staff_login.html')



from django.shortcuts import render
from django.db import connection

def staff_dashboard(request):
    if 'staff_id' not in request.session:
        return redirect('staff_login')
    
    staff_name = request.session['staff_name']
    staff_role = request.session['staff_role']
    
    with connection.cursor() as cursor:
        # Pending orders
        cursor.execute("SELECT COUNT(*) FROM orders WHERE order_status = 'Pending'")
        pending_orders = cursor.fetchone()[0]
        
        # Pending deliveries (role-based)
        if staff_role == 'Delivery Driver':
            cursor.execute("SELECT COUNT(*) FROM delivery WHERE delivery_staff_id = %s AND delivery_status = 'Pending'", [request.session['staff_id']])
        else:
            cursor.execute("SELECT COUNT(*) FROM delivery WHERE delivery_status = 'Pending'")
        pending_deliveries = cursor.fetchone()[0]
    
    context = {
        'staff_name': staff_name,
        'pending_orders': pending_orders,
        'pending_deliveries': pending_deliveries,
        'staff_role': staff_role,
    }
    return render(request, 'staff_dashboard.html', context)


from django.shortcuts import render, redirect
from django.db import connection

def staff_order_management(request):
    if 'staff_id' not in request.session:
        return redirect('staff_login')
    
    with connection.cursor() as cursor:
        cursor.execute("SELECT ORDER_ID, order_date, USER_ID, total_amount, order_status, delivery_status FROM orders")
        orders = cursor.fetchall()
        
        if request.method == 'POST':
            order_id = request.POST.get('order_id')
            action = request.POST.get('action')
            staff_id = request.session['staff_id']
            
            if action == 'process':
                cursor.execute("UPDATE orders SET order_status = 'Processing' WHERE ORDER_ID = %s", [order_id])
                cursor.execute("INSERT INTO activity_log (action, timestamp) VALUES (%s, NOW())", [f"Order #{order_id} set to Processing"])
            elif action == 'assign':
                delivery_staff_id = request.POST.get('delivery_staff_id')
                cursor.execute("INSERT INTO delivery (order_id, delivery_staff_id, delivery_status, delivery_address) SELECT %s, %s, 'Pending', delivery_address FROM orders WHERE ORDER_ID = %s", [order_id, delivery_staff_id, order_id])
                cursor.execute("INSERT INTO activity_log (action, timestamp) VALUES (%s, NOW())", [f"Order #{order_id} dispatched with staff ID {delivery_staff_id}"])
            return redirect('order_management')
    
    return render(request, 'staff_order_manage.html', {'orders': orders})



from django.shortcuts import render, redirect
from django.db import connection

def staff_delivery_management(request):
    if 'staff_id' not in request.session:
        return redirect('staff_login')
    
    staff_id = request.session['staff_id']
    staff_role = request.session['staff_role']
    
    with connection.cursor() as cursor:
        if staff_role == 'Delivery Driver':
            cursor.execute("SELECT delivery_id, order_id, delivery_date, delivery_status, delivery_address FROM delivery WHERE delivery_staff_id = %s", [staff_id])
        else:
            cursor.execute("SELECT delivery_id, order_id, delivery_date, delivery_status, delivery_address FROM delivery")
        deliveries = cursor.fetchall()
        
        if request.method == 'POST':
            delivery_id = request.POST.get('delivery_id')
            action = request.POST.get('action')
            
            if action == 'dispatch':
                cursor.execute("UPDATE delivery SET delivery_status = 'Dispatched' WHERE delivery_id = %s", [delivery_id])
                cursor.execute("INSERT INTO activity_log (action, timestamp) VALUES (%s, NOW())", [f"Delivery #{delivery_id} status updated to Dispatched"])
            elif action == 'out':
                cursor.execute("UPDATE delivery SET delivery_status = 'Out for Delivery' WHERE delivery_id = %s", [delivery_id])
                cursor.execute("INSERT INTO activity_log (action, timestamp) VALUES (%s, NOW())", [f"Delivery #{delivery_id} status updated to Out for Delivery"])
            elif action == 'deliver':
                cursor.execute("UPDATE delivery SET delivery_status = 'Delivered' WHERE delivery_id = %s", [delivery_id])
                cursor.execute("UPDATE orders SET delivery_status = 'Delivered', order_status = 'Delivered' WHERE ORDER_ID = (SELECT order_id FROM delivery WHERE delivery_id = %s)", [delivery_id])
                cursor.execute("INSERT INTO activity_log (action, timestamp) VALUES (%s, NOW())", [f"Delivery #{delivery_id} status updated to Delivered"])
            return redirect('delivery_management')
    
    return render(request, 'staff_delivery_management.html', {'deliveries': deliveries})


from django.shortcuts import render, redirect
from django.db import connection

def staff_inventory_management(request):
    if 'staff_id' not in request.session or request.session['staff_role'] != 'Warehouse Manager':
        return redirect('staff_login')
    
    with connection.cursor() as cursor:
        cursor.execute("SELECT product_id, pro_name, stock_quantity, reorder_level FROM product LEFT JOIN inventory ON product.product_id = inventory.pro_id")
        inventory = cursor.fetchall()
        
        if request.method == 'POST':
            product_id = request.POST.get('product_id')
            quantity_change = int(request.POST.get('quantity_change'))
            reason = request.POST.get('reason')
            staff_id = request.session['staff_id']
            
            cursor.execute("UPDATE product SET stock_quantity = stock_quantity + %s WHERE product_id = %s", [quantity_change, product_id])
            cursor.execute("INSERT INTO inventory_log (product_id, quantity_change, change_date, staff_id, change_reason) VALUES (%s, %s, CURDATE(), %s, %s)", [product_id, quantity_change, staff_id, reason])
            cursor.execute("INSERT INTO activity_log (action, timestamp) VALUES (%s, NOW())", [f"Product #{product_id} stock updated by {quantity_change}"])
            return redirect('inventory_management')
    
    return render(request, 'staff_inventory_management.html', {'inventory': inventory})



from django.shortcuts import render
from django.db import connection

def activity_log(request):
    if 'staff_id' not in request.session:
        return redirect('staff_login')
    
    with connection.cursor() as cursor:
        cursor.execute("SELECT id, action, timestamp FROM activity_log ORDER BY timestamp DESC")
        logs = cursor.fetchall()
    
    return render(request, 'activity_log.html', {'logs': logs})




from django.shortcuts import render, redirect
from django.db import connection

def staff_profile(request):
    if 'staff_id' not in request.session:
        return redirect('staff_login')
    
    staff_id = request.session['staff_id']
    
    with connection.cursor() as cursor:
        cursor.execute("SELECT staff_id, first_name, last_name, email, phone_no, address, hire_date, role, salary FROM staff WHERE staff_id = %s", [staff_id])
        profile = cursor.fetchone()
        
        if request.method == 'POST':
            phone_no = request.POST.get('phone_no')
            address = request.POST.get('address')
            cursor.execute("UPDATE staff SET phone_no = %s, address = %s WHERE staff_id = %s", [phone_no, address, staff_id])
            cursor.execute("INSERT INTO activity_log (action, timestamp) VALUES (%s, NOW())", [f"Staff #{staff_id} updated profile"])
            return redirect('staff_profile')
    
    return render(request, 'staff_profile.html', {'profile': profile})


from django.shortcuts import redirect

def staff_logout(request):
    request.session.flush()
    return redirect('staff_login')