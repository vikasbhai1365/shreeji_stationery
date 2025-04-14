
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


from django.shortcuts import render, redirect
from django.db import connection

def staff_dashboard(request):
    if 'staff_id' not in request.session:
        return redirect('staff_login')
    
    staff_id = request.session['staff_id']
    staff_role = request.session['staff_role']
    staff_name = request.session.get('staff_name', 'Staff Member')  # Set during login
    
    with connection.cursor() as cursor:
        # # Pending Orders
        # cursor.execute("SELECT COUNT(*) FROM orders WHERE order_status = 'Pending'")
        # pending_orders = cursor.fetchone()[0]

        # Pending Deliveries
        if staff_role == 'Delivery Driver':
            cursor.execute("""
                SELECT COUNT(*) 
                FROM delivery 
                WHERE delivery_status IN ('Pending', 'Dispatched', 'Out for Delivery') 
                AND delivery_staff_id = %s
            """, [staff_id])
        else:
            cursor.execute("""
                SELECT COUNT(*) 
                FROM delivery 
                WHERE delivery_status IN ('Pending', 'Dispatched', 'Out for Delivery')
            """)
        pending_deliveries = cursor.fetchone()[0]

        # Total Completed Deliveries
        if staff_role == 'Delivery Driver':
            cursor.execute("""
                SELECT COUNT(*) 
                FROM delivery 
                WHERE delivery_status = 'Delivered' 
                AND delivery_staff_id = %s
            """, [staff_id])
        else:
            cursor.execute("SELECT COUNT(*) FROM delivery WHERE delivery_status = 'Delivered'")
        completed_deliveries = cursor.fetchone()[0]

        # # Orders Processed Today (April 3, 2025)
        # if staff_role == 'Delivery Driver':
        #     cursor.execute("""
        #         SELECT COUNT(*) 
        #         FROM orders o
        #         JOIN delivery d ON o.ORDER_ID = d.order_id
        #         WHERE o.order_status = 'Processing' 
        #         AND DATE(o.order_date) = '2025-04-03'
        #         AND d.delivery_staff_id = %s
        #     """, [staff_id])
        # else:
        #     cursor.execute("""
        #         SELECT COUNT(*) 
        #         FROM orders 
        #         WHERE order_status = 'Processing' 
        #         AND DATE(order_date) = '2025-04-03'
        #     """)
        # orders_processed_today = cursor.fetchone()[0]

        # # Active Staff Members
        # cursor.execute("SELECT COUNT(*) FROM staff WHERE staff_status = 'active'")
        # active_staff = cursor.fetchone()[0]

        # # Recent Activities (last 5 from staff_activity_log)
        # if staff_role == 'Delivery Driver':
        #     cursor.execute("""
        #         SELECT action, timestamp, user_name 
        #         FROM staff_activity_log 
        #         WHERE staff_id = %s 
        #         ORDER BY timestamp DESC 
        #         LIMIT 5
        #     """, [staff_id])
        # else:
        #     cursor.execute("""
        #         SELECT action, timestamp, user_name 
        #         FROM staff_activity_log 
        #         ORDER BY timestamp DESC 
        #         LIMIT 5
        #     """)
        # recent_activities = cursor.fetchall()

    context = {
        'staff_name': staff_name,
        'staff_role': staff_role,
        # 'pending_orders': pending_orders,
        'pending_deliveries': pending_deliveries,
        'completed_deliveries': completed_deliveries,
        # 'orders_processed_today': orders_processed_today,
        # 'active_staff': active_staff,
        # 'recent_activities': [{'action': row[0], 'timestamp': row[1], 'user_name': row[2]} for row in recent_activities],
    }
    return render(request, 'staff_dashboard.html', context)

from django.shortcuts import render, redirect
from django.db import connection
from django.contrib import messages

def staff_order_management(request):
    if 'staff_id' not in request.session:
        return redirect('staff_login')
    
    staff_id = request.session['staff_id']
    staff_role = request.session.get('staff_role', 'Delivery Driver')  # Default to Delivery Driver
    
    with connection.cursor() as cursor:
        if staff_role == 'Warehouse Manager':
            # Fetch all orders for Warehouse Manager
            cursor.execute("""
                SELECT ORDER_ID, order_date, USER_ID, total_amount, order_status, delivery_status, delivery_address
                FROM orders
                ORDER BY order_date DESC
            """)
            orders = cursor.fetchall()
        else:  # Delivery Driver
            # Fetch orders assigned to this Delivery Driver
            cursor.execute("""
                SELECT o.ORDER_ID, o.order_date, o.USER_ID, o.total_amount, o.order_status, 
                       o.delivery_status, o.delivery_address
                FROM orders o
                JOIN delivery d ON o.ORDER_ID = d.order_id
                WHERE d.delivery_staff_id = %s
                ORDER BY o.order_date DESC
            """, [staff_id])
            orders = cursor.fetchall()
        
        # Warehouse Manager actions
        if request.method == 'POST' and staff_role == 'Warehouse Manager':
            order_id = request.POST.get('order_id')
            action = request.POST.get('action')
            
            if action in ['process', 'ship'] and order_id:
                new_status = 'Processing' if action == 'process' else 'Shipped'
                cursor.execute("""
                    UPDATE orders
                    SET order_status = %s
                    WHERE ORDER_ID = %s AND order_status IN ('Pending', 'Processing')
                """, [new_status, order_id])
                if cursor.rowcount > 0:
                    cursor.execute("""
                        INSERT INTO activity_log (action, timestamp)
                        VALUES (%s, NOW())
                    """, [f"Order #{order_id} set to {new_status}"])
                    messages.success(request, f"Order #{order_id} set to {new_status}.")
                else:
                    messages.error(request, f"Order #{order_id} could not be updated.")
                return redirect('staff_order_management')
    
    context = {
        'orders': orders,
        'staff_role': staff_role,
    }
    return render(request, 'staff_order_manage.html', context)

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