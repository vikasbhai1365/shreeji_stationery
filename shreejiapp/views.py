from django.shortcuts import render,redirect
from django.contrib.auth import logout
import hashlib
import mysql.connector
from django.contrib import messages
from django.db import connection
from django.conf import settings



# Create your views here.
def homepage(request):
    if 'admin_id' not in request.session:
        return redirect('admin_login')
    
    user_name = request.session.get('name')

    first_letter_of_name = ''
    cartItemCount = 0  # Default value if no cart items exist

    if 'user_id' in request.session:
        user_id=request.session.get('user_id')
        with connection.cursor() as cursor:
            cursor.execute("SELECT name FROM Users WHERE user_id = %s", [request.session['user_id']])
            user = cursor.fetchone()

            if user and user[0]:  
                first_letter_of_name = user[0][0]  # Get the first letter of the user's name
            
            cursor.execute("SELECT COUNT(cart_id) FROM cart WHERE user_id = %s", [user_id])
            cartItem = cursor.fetchone()
            
            if cartItem and cartItem[0] is not None:
                cartItemCount = cartItem[0]  # Ensure it's a valid integer

    categories = get_categories()  # Fetch categories

    context = {
        'user_name': user_name,
        'categories': categories,
        'first_letter_of_name': first_letter_of_name,
        'cartItemCount': cartItemCount
    }

    return render(request, 'Homepage.html', context)



def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def  register(request):

    if  request.method=='POST':
        name=request.POST['name']
        email=request.POST['email']
        phone_no=request.POST['phone_no']
        address=request.POST['address']
        username=request.POST['username']
        password=request.POST['password']
        confirm_password=request.POST['confirm_password']
        
        if password==confirm_password:
            # conn=mysql.connector.connect(host="localhost",user="jignesh_gandhi",password="jignesh12",database="stationery_management")
            with connection.cursor() as cursor:
            # cursor=conn.cursor()

                query="insert into users(name,email,phone_no,address,username,user_password) values  (%s,%s,%s,%s,%s,%s)"
                values=(name,email,phone_no,address,username,password)
                cursor.execute(query,values)
                # conn.commit()

                
                # conn.close()

                cursor.execute("INSERT INTO activity_log (action) VALUES (%s)", 
                            [f"User {username} registered"])
                cursor.close()
                    
                return redirect('login')
        else:
                messages.error(request,"Password doesn't match")
    return render(request,'register.html')



# def  login(request):
#     if request.method=='POST':
#         username=request.POST['username']
#         password=request.POST['password']


#         conn=mysql.connector.connect(host="localhost",user="jignesh_gandhi",password="jignesh12",database="stationery_management")
#         cursor = conn.cursor(dictionary=True)

#         cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
#         user = cursor.fetchone()

#         cursor.close()
#         conn.close()

#         if  user:
#             if password==user['user_password']:
#                 request.session['user_id']=user['user_id']
#                 request.session['name']=user['name']
#                 return redirect('homepage')
#             else:
#                 messages.error(request,'Invalid password.please try again.')
 
#         else: 
#             messages.error(request,'Username not found. please register')


#     return render(request,'login.html')


from django.shortcuts import render, redirect
from django.db import connection
from django.contrib import messages

def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        with connection.cursor() as cursor:
            cursor.execute("SELECT user_id, name, user_password FROM users WHERE username = %s", [username])
            user = cursor.fetchone()  # returns a tuple: (user_id, name, user_password)

        if user:
            user_id, name, db_password = user
            if password == db_password:
                request.session['user_id'] = user_id
                request.session['name'] = name
                return redirect('homepage')
            else:
                messages.error(request, 'Invalid password. Please try again.')
        else:
            messages.error(request, 'Username not found. Please register.')

    return render(request, 'login.html')





# from django.contrib.auth.hashers import make_password, check_password
# import mysql.connector

# def register(request):
#     if request.method == 'POST':
#         name = request.POST['name']
#         email = request.POST['email']
#         phone_no = request.POST['phone_no']
#         address = request.POST['address']
#         username = request.POST['username']
#         password = request.POST['password']
#         confirm_password = request.POST['confirm_password']
        
#         if password == confirm_password:
#             hashed_password = make_password(password)  # Hash the password
            
#             conn = mysql.connector.connect(host="localhost", user="root", password="", database="stationery_management")
#             cursor = conn.cursor()
            
#             query = "INSERT INTO users (name, email, phone_no, address, username, user_password) VALUES (%s, %s, %s, %s, %s, %s)"
#             values = (name, email, phone_no, address, username, hashed_password)
#             cursor.execute(query, values)
#             conn.commit()
            
#             cursor.close()
#             conn.close()
            
#             return redirect('login')
#         else:
#             messages.error(request, "Password doesn't match")
    
#     return render(request, 'register.html')
# from django.contrib.auth.hashers import check_password
# from django.shortcuts import render, redirect
# from django.contrib import messages
# import mysql.connector
# def login(request):
#     if request.method == 'POST':
#         username = request.POST.get('username', '').strip()
#         password = request.POST.get('password', '').strip()
        
#         if not username or not password:
#             messages.error(request, 'Both fields are required')
#             return render(request, 'login.html')

#         try:
#             conn = mysql.connector.connect(
#                 host="localhost",
#                 user="root",
#                 password="",
#                 database="stationery_management"
#             )
#             cursor = conn.cursor(dictionary=True)
            
#             cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
#             user = cursor.fetchone()
            
#             if user:
#                 stored_hash = user['user_password'].strip()
#                 print("Debug - Stored hash:", stored_hash)  # Check this output
                
#                 # Temporary debug - compare raw strings
#                 print("Debug - Password match:", password == stored_hash)
                
#                 try:
#                     if check_password(password, stored_hash):
#                         request.session['user_id'] = user['user_id']
#                         request.session['name'] = user['name']
#                         return redirect('homepage')
#                     else:
#                         messages.error(request, 'Invalid password')
#                 except Exception as e:
#                     print("Hash verification error:", str(e))
#                     messages.error(request, 'System error during login')
#             else:
#                 messages.error(request, 'User not found')
                
#         except mysql.connector.Error as err:
#             messages.error(request, 'Database error')
#             print("Database error:", err)
            
#         finally:
#             if 'cursor' in locals(): cursor.close()
#             if 'conn' in locals(): conn.close()
    
#     return render(request, 'login.html')

def user_logout_view(request):
    if 'user_id' in request.session:
        del request.session['user_id']
    return redirect('homepage')


# def user_logout_view(request):
#     # Clear the session
#     request.session.flush()
#     # Redirect to the admin login page
#     return redirect('login')



# Fetch categories directly, without rendering a template
def get_categories():
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT c.category_id, c.category_name, p.productURL
            FROM Category c
            LEFT JOIN Product p ON c.category_id = p.category_id
            WHERE p.product_id = (
            SELECT MIN(product_id)
            FROM Product
            WHERE Product.category_id = c.category_id
)


        """)
        categories = [
            {
                'category_id': row[0],
                'category_name': row[1],
                'productURL': settings.MEDIA_URL + (row[2] if row[2] else 'default_image.jpg')
            }
            for row in cursor.fetchall()
        ]
    return categories


def get_products():
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
        
        # Convert query result to a list of dictionaries
        products = [
            dict(zip([column[0] for column in cursor.description], row))
            for row in cursor.fetchall()
        ]
    
    # Prepend MEDIA_URL to image paths
    for product in products:
        product['image_url'] = settings.MEDIA_URL + product['productURL']

    # Return the list of products
    return products


# def userside_productPage(request):
#     with connection.cursor() as cursor:
#         # Fetch products grouped by categories
#         cursor.execute("""
#             SELECT c.category_name, p.pro_name, p.price, p.description, p.productURL
#             FROM product p
#             JOIN category c ON p.category_id = c.category_id
#             ORDER BY c.category_name
#         """)
        
#         # Organize data into a category-wise structure
#         products_by_category = {}
#         for row in cursor.fetchall():
#             category_name = row[0]
#             product = {
#                 'pro_name': row[1],
#                 'price': row[2],
#                 'description': row[3],
#                 'productURL': settings.MEDIA_URL + (row[4] if row[4] else 'default_image.jpg')
#             }
#             if category_name not in products_by_category:
#                 products_by_category[category_name] = []
#             products_by_category[category_name].append(product)

#     # Pass the data to the template
#     return render(request, 'userside_productPage.html', {'products_by_category': products_by_category})






def userside_productPage(request):
    category_id = request.GET.get('category_id')

    with connection.cursor() as cursor:
        # Fetch all categories for the sidebar
        cursor.execute("SELECT category_id, category_name FROM category;")
        categories = [
            {'category_id': row[0], 'category_name': row[1]} 
            for row in cursor.fetchall()
        ]
        # Fetch all brands, regardless of category selection
        cursor.execute("SELECT brand_id, brand_name FROM brands;")
        brands = [
            {'brand_id': row[0], 'brand_name': row[1]}
            for row in cursor.fetchall()
        ]

        # Fetch all colors, for filter option
        cursor.execute("SELECT color_id, color_name FROM colors;")
        colors = [
            {'color_id': row[0], 'color_name': row[1]}
            for row in cursor.fetchall()
        ]
        # Fetch all sizes, for filter option
        cursor.execute("SELECT distinct size FROM product;")
        sizes = [
            {'size': row[0]}
            for row in cursor.fetchall()
        ]

        # Fetch products only if category_id is provided
        products = []
        if category_id:
            cursor.execute("""
                SELECT pro_name, price, description, productURL,product_id,category_id,stock_quantity
                FROM product
                WHERE category_id = %s
            """, [category_id])
            products = [
                {
                    'pro_name': row[0],
                    'price': row[1],
                    'description': row[2],
                    'productURL': settings.MEDIA_URL + (row[3] if row[3] else 'default_image.jpg'),
                    'product_id':row[4],
                    'category_id':row[5],
                    'stock_quantity':row[6],
                }
                for row in cursor.fetchall()
            ]
        if request.method == 'POST':
            brand_id = request.POST.get('brand_name')
            color_id = request.POST.get('color_name')
            size = request.POST.get('size')
            price_range = request.POST.get('price_range')


            query = """
                SELECT pro_name, price, description, productURL,product_id,category_id
                FROM product
                 WHERE 1=1
                """
            params = []

            if category_id:
                query += " AND category_id = %s"
                params.append(category_id)
            if brand_id:
                query += " AND brand_id = %s"
                params.append(brand_id)
            if color_id:
                query += " AND color_id = %s"
                params.append(color_id)
            if size:
                query += " AND size = %s"
                params.append(size)
            if price_range:
                query += " AND price <= %s"
                params.append(price_range)

            with connection.cursor() as cursor:
                cursor.execute(query, params)
                products = [
                    {
                    'pro_name': row[0],
                    'price': row[1],
                    'description': row[2],
                    'productURL': settings.MEDIA_URL + (row[3] if row[3] else 'default_image.jpg'),
                    'product_id':row[4],
                    'category_id':row[5]
                    }
                for row in cursor.fetchall()
            ]


                return render(request, 'userside_productPage.html', {
                'categories': categories,
                'products': products,
                'colors':colors,
                'brands':brands,
                'selected_category_id': category_id,
                'sizes':sizes
                })
    return render(request, 'userside_productPage.html', {
        'categories': categories,
        'products': products,
        'colors':colors,
        'brands':brands,
        'selected_category_id': category_id,
        'sizes':sizes
    })


# def userside_productPage(request):
#     category_id = request.GET.get('category_id')
#     brand_id = request.GET.get('brand_name')
#     color_id = request.GET.get('color_name')
#     size = request.GET.get('size')
#     price = request.GET.get('price')

#     with connection.cursor() as cursor:
#         # Fetch all categories for the sidebar
#         cursor.execute("SELECT category_id, category_name FROM category;")
#         categories = [
#             {'category_id': row[0], 'category_name': row[1]} 
#             for row in cursor.fetchall()
#         ]
        
#         # Fetch all brands
#         cursor.execute("SELECT brand_id, brand_name FROM brands;")
#         brands = [
#             {'brand_id': row[0], 'brand_name': row[1]}
#             for row in cursor.fetchall()
#         ]

#         # Fetch all colors
#         cursor.execute("SELECT color_id, color_name FROM colors;")
#         colors = [
#             {'color_id': row[0], 'color_name': row[1]}
#             for row in cursor.fetchall()
#         ]
        
#         # Fetch all sizes
#         cursor.execute("SELECT DISTINCT size FROM product;")
#         sizes = [
#             {'size': row[0]}
#             for row in cursor.fetchall()
#         ]

#         # Construct the query for filtered products
#         query = """
#             SELECT pro_name, price, description, productURL
#             FROM product
#             WHERE 1=1
#         """
#         params = []

#         if category_id:
#             query += " AND category_id = %s"
#             params.append(category_id)
#         if brand_id:
#             query += " AND brand_id = %s"
#             params.append(brand_id)
#         if color_id:
#             query += " AND color_id = %s"
#             params.append(color_id)
#         if size:
#             query += " AND size = %s"
#             params.append(size)
#         if price:
#             query += " AND price <= %s"
#             params.append(price)
        
#         cursor.execute(query, params)
#         products = [
#             {
#                 'pro_name': row[0],
#                 'price': row[1],
#                 'description': row[2],
#                 'productURL': settings.MEDIA_URL + (row[3] if row[3] else 'default_image.jpg')
#             }
#             for row in cursor.fetchall()
#         ]

#     return render(request, 'userside_productPage.html', {
#         'categories': categories,
#         'products': products,
#         'colors': colors,
#         'brands': brands,
#         'selected_category_id': category_id,
#         'sizes': sizes
#     })





# def userside_orderPage(request):
#     product_id = request.GET.get('product_id')
#     category_id = request.GET.get('category_id')
#     print("Received product_id:", product_id)
#     print("Received category_id:", category_id)

#     product = None
#     if product_id and category_id:
#         with connection.cursor() as cursor:
#             cursor.execute("""
#                 SELECT product.product_id, product.pro_name, product.price, product.description, product.productURL, category.category_name
#                 FROM product
#                 INNER JOIN category ON product.category_id = category.category_id
#                 WHERE product.product_id = %s AND product.category_id = %s
#             """, [product_id, category_id])

#             row = cursor.fetchone()  # Get a single row
            
#         if row:
#             product = {
#                 'product_id': row[0],
#                 'product_name': row[1],
#                 'price': row[2],
#                 'description': row[3],
#                 'productURL': settings.MEDIA_URL + (row[4] if row[4] else 'default_image.jpg'),
#                 'category_name': row[5]
#             }
#         else:
#             product = None
#         print("Query result:", product)
    
#     if not product:
#         print("Product not found!")
#         return redirect('userside_productPage')
    
    
#     return render(request, 'userside_orderPage.html',{'product':product})



from django.db import connection
from django.conf import settings
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt

# @csrf_exempt
# def userside_orderPage(request):
#     product_id = request.GET.get('product_id')
#     category_id = request.GET.get('category_id')
#     message = None
#     success = False

#     # Get the logged-in user ID
#     user_id = request.session.get('user_id')
#     if not user_id:
#         # return render(request, 'userside_orderPage.html', {"message": "❌ User not logged in.", "success": False})
#         return redirect('login')

#     product = None
#     delivery_address = ""

#     # Fetch user delivery address
#     with connection.cursor() as cursor:
#         cursor.execute("SELECT address FROM users WHERE user_id = %s", [user_id])
#         row = cursor.fetchone()
#         if row:
#             delivery_address = row[0]


#     # Fetch product details
#     if product_id and category_id:
#         with connection.cursor() as cursor:
#             cursor.execute("""
#                 SELECT p.product_id, p.pro_name, p.price, p.description, p.productURL, 
#                        c.category_name, p.stock_quantity
#                 FROM product p
#                 INNER JOIN category c ON p.category_id = c.category_id
#                 WHERE p.product_id = %s AND p.category_id = %s
#             """, [product_id, category_id])
#             row = cursor.fetchone()

#         if row:
#             product = {
#                 'product_id': row[0],
#                 'product_name': row[1],
#                 'price': row[2],
#                 'description': row[3],
#                 'productURL': settings.MEDIA_URL + (row[4] if row[4] else 'default_image.jpg'),
#                 'category_name': row[5],
#                 'stock': row[6]
#             }
#         else:
#             return redirect('userside_productPage')

#     # Process order on form submission
#     if request.method == "POST":
#         try:
#             quantity = int(request.POST.get("quantity"))
#             print("Quantity is :",quantity)
#             delivery_address = request.POST.get("delivery_address")
#             payment_mode = request.POST.get("payment_mode")
#             payment_method_detail = request.POST.get("payment_method_detail", "Cash On Delivery")

#             # Check if stock is available
#             if product["stock"] < quantity:
#                 return render(request, 'userside_orderPage.html', {"message": "❌ Insufficient stock available.", "success": False, "product": product})

#             total_amount = product["price"] * quantity

#             with connection.cursor() as cursor:
#                 # Insert into orders table
#                 cursor.execute("""
#                     INSERT INTO orders (user_id, order_date, total_amount, delivery_address, payment_status, order_status,delivery_status,payment_method)
#                     VALUES (%s, NOW(), %s, %s, 'Pending', 'Pending','processing','cash on delivery')
#                 """, [user_id, total_amount, delivery_address])

#                 cursor.execute("SELECT LAST_INSERT_ID()")
#                 order_id = cursor.fetchone()[0]

#                 # Insert into order_details table
#                 cursor.execute("""
#                     INSERT INTO order_details (order_id, pro_id, quantity, price, subtotal)
#                     VALUES (%s, %s, %s, %s, %s)
#                 """, [order_id, product_id, quantity, product["price"], total_amount])

#                    # Insert into billing table
#                 cursor.execute("""
#                     INSERT INTO billing (order_id, bill_date, total_amount, discount_amount, net_amount, billing_status)
#                         VALUES (%s, NOW(), %s, 0, %s, 'Pending')
#                         """, [order_id, total_amount, total_amount])

#                 cursor.execute("SELECT LAST_INSERT_ID()")  # Fetch newly created bill_id
#                 bill_id = cursor.fetchone()[0]

#                 # Insert into payment table
#                 cursor.execute("""
#                     INSERT INTO payment (order_id, payment_mode, payment_method_details, transaction_status, total_amount, payment_date,bill_id)
#                     VALUES (%s, %s, %s, 'Pending', %s, NOW(),%s)
#                 """, [order_id, payment_mode, payment_method_detail, total_amount,bill_id])

              

#                 # Update product stock
#                 cursor.execute("UPDATE product SET stock_quantity = stock_quantity - %s WHERE product_id = %s", [quantity, product_id])

#             message = "✅ Order Confirmed! Your order has been placed successfully."
#             success = True
          

#         except Exception as e:
#             message = f"❌ Order processing failed: {str(e)}"
#             success = False

#     return render(request, 'userside_orderPage.html', {'product': product, 'message': message, 'success': success, 'delivery_address': delivery_address})

@csrf_exempt
def userside_orderPage(request):
    product_id = request.GET.get('product_id')
    category_id = request.GET.get('category_id')
    message = None
    success = False

    # Get the logged-in user ID
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')

    product = None
    delivery_address = ""
    order_details = None

    # Fetch user delivery address and details
    with connection.cursor() as cursor:
        cursor.execute("SELECT address, name, email, phone_no FROM users WHERE user_id = %s", [user_id])
        row = cursor.fetchone()
        if row:
            delivery_address = row[0]
            user_name = row[1]
            user_email = row[2]
            user_phone = row[3]

    # Fetch product details
    if product_id and category_id:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT p.product_id, p.pro_name, p.price, p.description, p.productURL, 
                       c.category_name, p.stock_quantity
                FROM product p
                INNER JOIN category c ON p.category_id = c.category_id
                WHERE p.product_id = %s AND p.category_id = %s
            """, [product_id, category_id])
            row = cursor.fetchone()

        if row:
            product = {
                'product_id': row[0],
                'product_name': row[1],
                'price': row[2],
                'description': row[3],
                'productURL': settings.MEDIA_URL + (row[4] if row[4] else 'default_image.jpg'),
                'category_name': row[5],
                'stock': row[6]
            }
        else:
            return redirect('userside_productPage')

    # Process order on form submission
    if request.method == "POST":
        try:
            quantity = int(request.POST.get("quantity"))
            delivery_address = request.POST.get("delivery_address")
            payment_mode = request.POST.get("payment_mode")
            payment_method_detail = request.POST.get("payment_method_detail", "Cash On Delivery")

            # Check if stock is available
            if product["stock"] < quantity:
                return render(request, 'userside_orderPage.html', {
                    "message": "❌ Insufficient stock available.", 
                    "success": False, 
                    "product": product
                })

            total_amount = product["price"] * quantity

            with connection.cursor() as cursor:
                # Insert into orders table
                cursor.execute("""
                    INSERT INTO orders (user_id, order_date, total_amount, delivery_address, 
                    payment_status, order_status, delivery_status, payment_method)
                    VALUES (%s, NOW(), %s, %s, 'Pending', 'Pending', 'processing', %s)
                """, [user_id, total_amount, delivery_address, payment_mode])

                cursor.execute("SELECT LAST_INSERT_ID()")
                order_id = cursor.fetchone()[0]

                # Insert into order_details table
                cursor.execute("""
                    INSERT INTO order_details (order_id, pro_id, quantity, price, subtotal)
                    VALUES (%s, %s, %s, %s, %s)
                """, [order_id, product_id, quantity, product["price"], total_amount])

                # Insert into billing table
                cursor.execute("""
                    INSERT INTO billing (order_id, bill_date, total_amount, discount_amount, net_amount, billing_status)
                    VALUES (%s, NOW(), %s, 0, %s, 'Pending')
                """, [order_id, total_amount, total_amount])

                cursor.execute("SELECT LAST_INSERT_ID()")  # Fetch newly created bill_id
                bill_id = cursor.fetchone()[0]

                # Insert into payment table
                cursor.execute("""
                    INSERT INTO payment (order_id, payment_mode, payment_method_details, 
                    transaction_status, total_amount, payment_date, bill_id)
                    VALUES (%s, %s, %s, 'Pending', %s, NOW(), %s)
                """, [order_id, payment_mode, payment_method_detail, total_amount, bill_id])

                # Update product stock
                cursor.execute("""
                    UPDATE product SET stock_quantity = stock_quantity - %s 
                    WHERE product_id = %s
                """, [quantity, product_id])

                # Get complete order details for confirmation page
                cursor.execute("""
                    SELECT o.order_id, o.order_date, o.total_amount, o.delivery_address, 
                           o.payment_method, od.quantity, p.pro_name, p.productURL, p.price
                    FROM orders o
                    JOIN order_details od ON o.order_id = od.order_id
                    JOIN product p ON od.pro_id = p.product_id
                    WHERE o.order_id = %s
                """, [order_id])
                order_row = cursor.fetchone()
                print("total cmounnt :",order_row[2])
                if order_row:
                    order_details = {
                        'order_id': order_row[0],
                        'order_date': order_row[1],
                        'total_amount': order_row[2],
                        'delivery_address': order_row[3],
                        'payment_mode': order_row[4],
                        'quantity': order_row[5],
                        'product_name': order_row[6],
                        'productURL': settings.MEDIA_URL + (order_row[7] if order_row[7] else 'default_image.jpg'),
                        'price': order_row[8]
                    }

            # Prepare data for confirmation page
            confirmation_data = {
                'order': order_details,
                'product': product,
                'user': {
                    'name': user_name,
                    'email': user_email,
                    'phone_number': user_phone
                },
                'message': "✅ Order Confirmed! Your order has been placed successfully.",
                'success': True
            }

            return render(request, 'order_confirmation.html', confirmation_data)

        except Exception as e:
            message = f"❌ Order processing failed: {str(e)}"
            success = False

    return render(request, 'userside_orderPage.html', {
        'product': product, 
        'message': message, 
        'success': success, 
        'delivery_address': delivery_address
    })


# my order page

from django.shortcuts import render
from django.db import connection

def user_orders(request):
    user_id = request.session.get('user_id')  # Ensure user is logged in
    if not user_id:
        return render(request, 'login.html', {'message': 'Please log in first'})

    query = """
    SELECT o.order_id, o.order_date, o.total_amount, o.order_status, 
           p.pro_name, p.price, p.productURL, od.quantity 
    FROM orders o
    JOIN order_details od ON o.order_id = od.order_id
    JOIN product p ON od.pro_id = p.product_id
    WHERE o.user_id = %s
    ORDER BY o.order_id DESC
    """
    
    with connection.cursor() as cursor:
        cursor.execute(query, [user_id])
        orders = cursor.fetchall()

    order_list = []
    for order in orders:
        order_dict = {
            'order_id': order[0],
            'order_date': order[1],
            'total_amount': order[2],
            'order_status': order[3],
            'product_name': order[4],
            'price': order[5],
            # 'product_url': order[6],
            'productURL': settings.MEDIA_URL + (order[6] if order[6] else 'default_image.jpg'),

            'quantity': order[7],
        }
        order_list.append(order_dict)

    return render(request, 'user_orders.html', {'orders': order_list})




from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import connection

@csrf_exempt
def add_to_cart(request):
    if request.method == "POST":
        product_id = request.POST.get("product_id")
        user_id = request.session.get("user_id")

        if not user_id:
            # For AJAX requests, return a special response
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return HttpResponse("login_required", status=401)
            # For normal requests, redirect
            return redirect('login')

        with connection.cursor() as cursor:
            # Check if the product is already in the cart
            cursor.execute("SELECT * FROM cart WHERE user_id = %s AND product_id = %s", (user_id, product_id))
            cart_item = cursor.fetchone()

            if cart_item:
                cursor.execute("UPDATE cart SET quantity = quantity + 1 WHERE user_id = %s AND product_id = %s",
                               (user_id, product_id))
            else:
                cursor.execute("INSERT INTO cart (user_id, product_id, quantity) VALUES (%s, %s, %s)",
                               (user_id, product_id, 1))

            connection.commit()

        return HttpResponse("success")

    return HttpResponse("error", status=400)

def cart_page(request):
    user_id = request.session.get("user_id")
    if not user_id:
        return redirect('login')

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT p.pro_name, p.price, c.quantity, p.productURL,c.product_id
            FROM cart c
            JOIN product p ON c.product_id = p.product_id
            WHERE c.user_id = %s
        """, [user_id])
        cart_items = cursor.fetchall()

    return render(request, "cart.html", {"cart_items": cart_items})


@csrf_exempt  # If CSRF protection causes issues, you can remove this if you have {% csrf_token %}
def remove_from_cart(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')

        if product_id:
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM cart WHERE product_id = %s", [product_id])

        return redirect('cart')  # Redirect back to cart page

    return redirect('cart')  # If invalid request, just refresh cart page




#checkout page ...............

import MySQLdb
from django.shortcuts import render, redirect
import MySQLdb
from django.shortcuts import render, redirect

# def checkout(request):
#     user_id = request.session.get("user_id")

#     if not user_id:
#         return redirect('login')

#     selected_items = request.GET.getlist("selected_items")  # Get selected product IDs

#     if not selected_items:
#         return redirect('cart')  # Redirect if no items selected

#     db = MySQLdb.connect("localhost", "root", "", "stationery_management")
#     cursor = db.cursor()

#     # Fetch user details
#     cursor.execute("SELECT address, phone_no, name FROM users WHERE user_id = %s", (user_id,))
#     user_data = cursor.fetchone()

#     # Safe unpacking
#     if user_data:
#         user_address, user_phone, user_name = user_data
#     else:
#         user_address, user_phone, user_name = "", "", ""

#     # Fetch subtotal only for selected items
#     format_strings = ",".join(["%s"] * len(selected_items))  # Prepare for IN clause
#     query = f"""
#         SELECT SUM(p.price * c.quantity)
#         FROM cart c
#         JOIN product p ON c.product_id = p.product_id
#         WHERE c.user_id = %s AND c.product_id IN ({format_strings})
#     """
#     cursor.execute(query, [user_id] + selected_items)
#     subtotal = cursor.fetchone()[0] or 0

#     db.close()
#     return render(request, "checkout_page.html", {
#         "user_address": user_address,
#         "user_phone": user_phone,
#         "user_name":user_name,
#         "subtotal": subtotal
#     })


# def process_order(request):
#     if request.method == "POST":
#         address = request.POST["address"]
#         phone = request.POST["phone"]
#         payment_method = request.POST["payment_method"]

#         db = MySQLdb.connect("localhost", "root", "", "stationery_management")
#         cursor = db.cursor()
        
#         # Create order
#         cursor.execute(
#             "INSERT INTO orders (user_id, delivery_address, phone, payment_method, order_status) VALUES (%s, %s, %s, %s, %s)",
#             (request.user.id, address, phone, payment_method, "Pending")
#         )
#         order_id = cursor.lastrowid

#         # Move items from cart to order_details
#         cursor.execute(
#             "INSERT INTO order_details (order_id, product_id, quantity, price) "
#             "SELECT %s, product_id, quantity, price FROM cart WHERE user_id = %s",
#             (order_id, request.user.id)
#         )

#         # Clear the cart
#         cursor.execute("DELETE FROM cart WHERE user_id = %s", (request.user.id,))
#         db.commit()
#         db.close()

#         return redirect("payment")



def checkout(request):
    user_id = request.session.get("user_id")
    
    if not user_id:
        return redirect('login')

    # Handle both GET (from cart) and POST (form submission) methods
    if request.method == 'GET':
        selected_items = request.GET.getlist("selected_items")
        quantities = request.GET.getlist("quantities")
        
        # Store in session for process_order to use
        request.session['checkout_items'] = list(zip(selected_items, quantities))
    elif request.method == 'POST':
        # If coming from form submission, get from session
        checkout_data = request.session.get('checkout_items', [])
        selected_items = [item[0] for item in checkout_data]
        quantities = [item[1] for item in checkout_data]
    else:
        return redirect('cart')

    if not selected_items or not quantities:
        return redirect('cart')

    try:
        with connection.cursor() as cursor:
            # Fetch user details
            cursor.execute("SELECT address, phone_no, name FROM users WHERE user_id = %s", [user_id])
            user_data = cursor.fetchone()

            if not user_data:
                messages.error(request, "User not found")
                return redirect('cart')

            user_address, user_phone, user_name = user_data

            # Calculate subtotal for selected items
            total_amount = 0
            products = []
            
            for item_id, qty in zip(selected_items, quantities):
                try:
                    cursor.execute("""
                        SELECT product_id, pro_name, price 
                        FROM product 
                        WHERE product_id = %s
                    """, [item_id])
                    product = cursor.fetchone()
                    
                    if not product:
                        continue
                        
                    product_id, product_name, price = product
                    quantity = int(qty)
                    subtotal = price * quantity
                    total_amount += subtotal
                    
                    products.append({
                        'id': product_id,
                        'name': product_name,
                        'price': price,
                        'quantity': quantity,
                        'subtotal': subtotal
                    })
                    
                except (ValueError, TypeError):
                    continue

            if not products:
                messages.error(request, "No valid products in cart")
                return redirect('cart')

            return render(request, "checkout_page.html", {
                "user_address": user_address,
                "user_phone": user_phone,
                "user_name": user_name,
                "subtotal": total_amount,
                "products": products,
                "selected_items": selected_items,
                "quantities": quantities
            })

    except Exception as e:
        messages.error(request, f"Error during checkout: {str(e)}")
        return redirect('cart')
    


import datetime
from django.db import connection
from django.shortcuts import render, redirect
from django.contrib import messages
import datetime
from django.db import connection
from django.shortcuts import redirect
from django.contrib import messages

def process_order(request):
    if request.method == 'POST':
        try:
            # Get user and form data
            user_id = request.session.get('user_id')
            if not user_id:
                messages.error(request, "Please login to complete your order")
                return redirect('login')

            # Get items from session (set during checkout)
            checkout_items = request.session.get('checkout_items', [])
            if not checkout_items:
                messages.error(request, "Your session expired or no items selected")
                return redirect('cart')

            # Get form data
            address = request.POST.get('address')
            payment_method = request.POST.get('payment_method')
            
            if not address or not payment_method:
                messages.error(request, "Please fill all required fields")
                return redirect('checkout')

            with connection.cursor() as cursor:
                # Verify all products still exist and have stock
                valid_items = []
                total_amount = 0
                
                for item_id, qty_str in checkout_items:
                    try:
                        qty = int(qty_str)
                        if qty <= 0:
                            continue
                            
                        cursor.execute("""
                            SELECT price, stock_quantity 
                            FROM product 
                            WHERE product_id = %s
                            FOR UPDATE  # Lock row for update
                        """, [item_id])
                        result = cursor.fetchone()
                        
                        if not result:
                            messages.error(request, f"Product {item_id} no longer available")
                            continue
                            
                        price, stock = result
                        
                        if stock < qty:
                            messages.error(request, f"Not enough stock for product {item_id}")
                            continue
                            
                        total_amount += price * qty
                        valid_items.append((item_id, qty, price))
                        
                    except (ValueError, TypeError):
                        continue

                if not valid_items:
                    messages.error(request, "No valid items available for purchase")
                    return redirect('cart')

                # Start transaction
                cursor.execute("START TRANSACTION")

                try:
                    # Create order
                    current_date = datetime.datetime.now().date()
                    cursor.execute(
                        """INSERT INTO orders 
                        (USER_ID, order_date, total_amount, delivery_address, 
                         payment_status, order_status, delivery_status, payment_method) 
                        VALUES (%s, %s, %s, %s, 'Pending', 'Pending', 'Processing', %s)
                        """,
                        [user_id, current_date, total_amount, address, payment_method]
                    )
                    order_id = cursor.lastrowid
                    
                    # Create order details
                    for item_id, qty, price in valid_items:
                        subtotal = price * qty
                        cursor.execute(
                            """INSERT INTO order_details 
                            (order_id, pro_id, quantity, price, subtotal) 
                            VALUES (%s, %s, %s, %s, %s)
                            """,
                            [order_id, item_id, qty, price, subtotal]
                        )
                        
                        # Update stock
                        cursor.execute(
                            """UPDATE product 
                            SET stock_quantity = stock_quantity - %s 
                            WHERE product_id = %s
                            """,
                            [qty, item_id]
                        )
                    
                    # Create billing record
                    cursor.execute(
                        """INSERT INTO billing 
                        (order_id, bill_date, total_amount, discount_amount, net_amount, billing_status) 
                        VALUES (%s, %s, %s, 0, %s, 'pending')
                        """,
                        [order_id, datetime.datetime.now(), total_amount, total_amount]
                    )
                    bill_id = cursor.lastrowid
                    
                    # Create payment record
                    payment_mode = 'Cash on delivery' if payment_method == 'Cash On delivery' else 'Online Payment'
                    cursor.execute(
                        """INSERT INTO payment 
                        (order_id, payment_mode, payment_method_details, transaction_status, 
                         total_amount, payment_date, bill_id) 
                        VALUES (%s, %s, %s, 'Pending', %s, %s, %s)
                        """,
                        [order_id, payment_mode, payment_method, total_amount, 
                         datetime.datetime.now(), bill_id]
                    )
                    
                    # Clear cart
                    for item_id, _, _ in valid_items:
                        cursor.execute(
                            """DELETE FROM cart 
                            WHERE user_id = %s AND product_id = %s
                            """,
                            [user_id, item_id]
                        )
                    
                    # Log activity
                    cursor.execute(
                        "INSERT INTO activity_log (action) VALUES (%s)",
                        [f"Order #{order_id} placed by user {user_id}"]
                    )
                    
                    # Commit transaction
                    cursor.execute("COMMIT")
                    
                    # Clear checkout session data
                    if 'checkout_items' in request.session:
                        del request.session['checkout_items']
                    
                    messages.success(request, 'Order placed successfully!')
                    return redirect('order_confirmation', order_id=order_id)
                    
                except Exception as e:
                    cursor.execute("ROLLBACK")
                    raise e

        except Exception as e:
            messages.error(request, f'Error processing order: {str(e)}')
            return redirect('checkout')
    
    return redirect('cart')

    
def contact_us(request):
    user_id = request.session.get("user_id")  # Fetch logged-in user ID
    print("id:", user_id)

    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        subject = request.POST.get("subject")
        message = request.POST.get("message")

        with connection.cursor() as cursor:
            # Insert raw SQL query
            sql = "INSERT INTO contact_messages (name, email, phone, subject, message, user_id) VALUES (%s, %s, %s, %s, %s, %s)"
            values = (name, email, phone, subject, message, user_id)  # ✅ Corrected order

            try:
                cursor.execute(sql, values)
                messages.success(request, "Request Sent Successfully!")
            except Exception as e:
                messages.error(request, f"Database Error: {str(e)}")

    return render(request, "contact_us.html")



def aboutUs(request):
    return render(request,'aboutUs.html')





def user_messages(request):
    user_id = request.session.get("user_id")  # Fetch logged-in user ID

    with connection.cursor() as cursor:

        query = "SELECT subject, message, reply, created_at FROM contact_messages WHERE user_id=%s ORDER BY created_at DESC"
        cursor.execute(query, (user_id,))
        messages = cursor.fetchall()

    return render(request, 'user_messages.html', {'messages': messages})



#search operation .....................
# views.py
from django.shortcuts import render
from django.db import connection
from django.conf import settings
from django.conf import settings
from django.db import connection

def search_products(request):
    query = request.GET.get('q', '')  # Get the search query from the input field
    products = []
    
    if query:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT p.product_id, p.pro_name, p.price, CONCAT(%s, p.productURL), 
                       c.category_name, b.brand_name, col.color_name,p.stock_quantity
                FROM product p
                JOIN category c ON p.category_id = c.category_id
                JOIN brands b ON p.brand_id = b.brand_id
                JOIN colors col ON p.color_id = col.color_id
                WHERE p.pro_name LIKE %s OR p.description LIKE %s
            """, [settings.MEDIA_URL, f'%{query}%', f'%{query}%'])
            products = cursor.fetchall()
    
    print("Fetched Products:", products)  # Debugging Line

    return render(request, 'search_results.html', {'products': products, 'query': query})



#  for downlod the pdfs
import io
import os
from django.http import HttpResponse
from django.db import connection
from django.conf import settings
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

def generate_invoice(request, order_id):
    # Fetch order details using raw SQL
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT order_id, total_amount, order_date, delivery_address, payment_method 
            FROM orders WHERE order_id = %s
        """, [order_id])
        order = cursor.fetchone()

        cursor.execute("""
            SELECT p.pro_name, p.price, od.quantity, p.productURL
            FROM order_details od
            JOIN product p ON od.pro_id = p.product_id
            WHERE od.order_id = %s
        """, [order_id])
        products = cursor.fetchall()

    if not order:
        return HttpResponse("Order not found.", status=404)

    # Create PDF
    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer)
    pdf.setTitle(f"Invoice_{order[0]}.pdf")

    # Add content to the PDF
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(200, 800, "Invoice")

    pdf.setFont("Helvetica", 12)
    pdf.drawString(50, 770, f"Order ID: {order[0]}")
    pdf.drawString(50, 750, f"Order Date: {order[2]}")
    pdf.drawString(50, 730, f"Delivery Address: {order[3]}")
    pdf.drawString(50, 710, f"Payment Mode: {order[4]}")
    pdf.drawString(50, 690, f"Total Amount: {order[1]} Rupees")

    # Add products
    y_position = 650
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(50, y_position, "Product:")
    pdf.setFont("Helvetica", 10)
    
    y_position -= 30
    for product in products:
        product_name = product[0]
        price = product[1]
        quantity = product[2]
        image_path = product[3]  # Image filename stored in DB
        
        # Construct full image path
        image_full_path = os.path.join(settings.MEDIA_ROOT, image_path)

        # Add product details
        # pdf.drawString(50, y_position, f"{product_name} - {price} x {quantity}")
        
        # Add product image
        if os.path.exists(image_full_path):
            img = ImageReader(image_full_path)
            pdf.drawImage(img, 150, y_position -250, width=250, height=250, preserveAspectRatio=True, mask='auto')
        
        y_position -= 70  # Move further down for the next product

    pdf.showPage()
    pdf.save()

    # Return PDF as response
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Invoice_{order[0]}.pdf"'
    return response





# manage profile page ..........................................


from django.contrib.auth.hashers import make_password, check_password

def get_user_profile(user_id):
    with connection.cursor() as cursor:
        cursor.execute("SELECT user_id, name, email, phone_no,username, user_password,address FROM users WHERE user_id = %s", [user_id])
        user = cursor.fetchone()
    
    if user:
        return {
            "id": user[0],
            "name": user[1],
            "email": user[2],
            "phone_no": user[3],
            "username": user[4],
            "password": user[5],
            "address":user[6]
        }
    return None

def profile_view(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('/login')
    
    user = get_user_profile(user_id)
    if not user:
        return redirect('/login')
    
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        username = request.POST.get('username')
        new_password = request.POST.get('password')
        confirm_password = request.POST.get('confirmPassword')
        address=request.POST.get('address')
        
        if new_password and new_password == confirm_password:
            # hashed_password = make_password(new_password)
            with connection.cursor() as cursor:
                cursor.execute("""
                    UPDATE users 
                    SET name = %s, email = %s, phone_no = %s, username = %s, user_password = %s ,address = %s
                    WHERE user_id = %s
                """, [name, email, phone, username, new_password,address,user_id])
        else:
            with connection.cursor() as cursor:
                cursor.execute("""
                    UPDATE users 
                    SET name = %s, email = %s, phone_no = %s, username = %s ,address = %s
                    WHERE user_id = %s
                """, [name, email, phone, username, address, user_id])
        
        # return JsonResponse({"message": "Profile updated successfully!"})
    
    return render(request, 'manageProfile.html', {'user': user})
