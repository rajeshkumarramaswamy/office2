from django.shortcuts import render
from customer_data.models import *
from django.utils.encoding import smart_str, smart_unicode
import simplejson
import json
import MySQLdb
from django.http import HttpResponse
from django.core.cache import cache, caches

def index(request):
    lines_records = Productlines.objects.all()
    emp_records = Employees.objects.all()

    product_data = []
    productlines_data = []
    prod_and_lines = {}
    emp_records_output = []
    productcode_order = {}

    order_date_vs_orders = {}

    for emp in emp_records:
        emp_records_output.append(' '.join((str(emp.firstname), str(emp.lastname))))

    for pl in lines_records:
        productlines_data.append(str(pl.productline))
        prod_and_lines.setdefault(str(pl.productline), [])
        product_records = Products.objects.filter(productline=pl.productline)

        for pd in product_records:
            try:
                product_data.append(str(pd.productname.replace(u'\u2019', "'")))
            except:
                import pdb;pdb.set_trace()

            prod_and_lines[str(pl.productline)].append(str(pd.productname.replace(u'\u2019', "'")))

            orderdetails_records = Orderdetails.objects.filter(productcode=str(pd.productcode))
            productcode_order.setdefault(str(pd.productcode), [])

            for ordr in orderdetails_records:
                productcode_order[str(pd.productcode)].append(str(ordr.ordernumber.ordernumber))

            orders_records = Orders.objects.filter(ordernumber=str(ordr.ordernumber.ordernumber))
            for orecord in orders_records:
                order_date_vs_orders.setdefault(orecord.orderdate, [])
                order_date_vs_orders[orecord.orderdate].append(str(orecord.ordernumber))
    sales_records = []
    conn, cursor = mysql_connection()
    query = 'select filtername from savefilter;'
    cursor.execute(query)
    records = cursor.fetchall()
    for record in records:
        sales_records.append(record[0].replace(',', ' '))

    return render(request, 'index.html',
                  {'product_data': product_data,
                   'productlines_data': productlines_data, 'prod_and_lines': prod_and_lines,
                   'emp_records_output': emp_records_output, 'productcode_order': productcode_order,
                   'order_date_vs_orders': order_date_vs_orders, 'sales_records': sales_records})


def mysql_connection(db_name='classicmodels'):
    conn = MySQLdb.connect(db=db_name, host='localhost', user='root', passwd='python@123')
    cursor = conn.cursor()
    return conn, cursor

def layout(request):
    layout_rep = []
    layout_product_data = []
    layout_productlines_data = []
    plines = cache_plines()
    product = cache_products()
    l_rep = cache_salesrep()
    for pl in plines:
        layout_productlines_data.append(pl)

    for pd in product:
        try:
            layout_product_data.append(str(pd.replace(u'\u2019', "'")))
        except:
             pass

    for r in l_rep:
        layout_rep.append(r)
    return render(request, 'layout.html', {'layout_productlines_data': layout_productlines_data, 'layout_product_data': layout_product_data, 'layout_rep': layout_rep })

def display(request):
    from_date = request.GET.get('from', '')
    to_date = request.GET.get('to', '')
    input_productline = request.GET.get('json1', '')
    input_product = request.GET.get('json2', '')
    salesmen = json.loads(request.GET['json3'], '[]')
    firstName, lastName  = salesmen[0].split(' ')
    firstName, lastName = firstName.strip(), lastName.strip()

    processed_records = []
    conn, cursor = mysql_connection()
    query = 'select customerName, contactLastName, contactFirstName, employeeNumber, lastName, firstName, jobTitle, customerNumber, customerName from employees, customers where employeeNumber = salesRepEmployeeNumber and lastName = "%s" and firstName = "%s"' % (
    lastName, firstName)
    cursor.execute(query)
    records = cursor.fetchall()
    for record in records:
        customerName, contactLastName, contactFirstName, employeeNumber, lastName, firstName, jobTitle, customerNumber, customerName = record
        query = 'select orderDate, status, productCode from orderdetails D, orders O where O.orderNumber=D.orderNumber and customerNumber = "%s" and orderDate between %s and %s' % (
        customerNumber, from_date, to_date)
        cursor.execute(query)
        order_records = cursor.fetchall()
        for o_record in order_records:
            orderDate, status, productCode = o_record
            orderDate = str(orderDate)
            query = 'select productName from productlines L, products P where L.productLine = P.productLine and productCode = "%s" and productName=%s and P.productLine=%s' % (
            productCode, input_product, input_productline)
            cursor.execute(query)
            p_records = cursor.fetchall()

            for p_record in p_records:
                productName = p_record[0]

                output = {'lastName': lastName, 'firstName': firstName,
                          'productCode': productCode, 'customerName': customerName, 'jobTitle': jobTitle,
                          'customerName': customerName, 'contactLastName': contactLastName,
                          'contactFirstName': contactFirstName, 'orderDate': orderDate, 'status': status,
                          }
                processed_records.append(output)
    # import pdb;pdb.set_trace()

    return HttpResponse(simplejson.dumps({'dtable': processed_records}), content_type="application/json")


def react(request):
    return render(request, 'react.html')

def cache_plines(plines=[]):
    cached_data_plines = cache.get(plines)
    conn, cursor = mysql_connection()
    if not cached_data_plines:
        query = 'select productLine from productLines'
        cursor.execute(query)
        record_plines = cursor.fetchall()
        for pl in record_plines:
            plines.append(pl[0])
            #import pdb; pdb.set_trace()
    else:
        cached_data_plines = cache.set('plines', plines, 60)
    return plines

def cache_products(product=[]):
    cached_data_products = cache.get(product)
    conn, cursor = mysql_connection()
    if not cached_data_products:
        query = 'select productName from products'
        cursor.execute(query)
        record_product = cursor.fetchall()
        for pd in record_product:
            product.append(pd[0])
    else:
        cached_data_products = cache.set('products', product, 60)
    return product

def cache_salesrep(rep=[]):
    cached_data_rep = cache.get(rep)
    conn, cursor = mysql_connection()
    if not cached_data_rep:
        query = 'select firstName, lastName from employees'
        cursor.execute(query)
        record_rep = cursor.fetchall()
        for r in record_rep:
            rep.append(' '.join((str(r[0]), str(r[1]))))
    else:
        cached_data_rep = cache.set('rep', rep, 60)
    return rep

def savefilter(request):
    input_productline = request.GET.get('json1', '')
    input_product = request.GET.get('json2', '')
    salesmen = json.loads(request.GET['json3'], '[]')
    #firstName, lastName  = salesmen[0].split(' ')
    conn, cursor = mysql_connection()
    query = "INSERT INTO savefilter(filtername, Productlines, Product, salesrep) VALUES (%s, %s, %s, %s)"
    query += 'on duplicate key update filtername=%s'
    values = (salesmen[0], input_productline.replace('"', ''), input_product.replace('"', ''), salesmen[0], salesmen[0])
    cursor.execute(query, values)
    conn.commit()
    return  HttpResponse(simplejson.dumps({'status': '1'}), content_type="application/json")

def deletefilter(request):
    input_productline = request.GET.get('json1', '')
    input_product = request.GET.get('json2', '')
    salesmen = json.loads(request.GET['json3'], '[]')
    conn, cursor = mysql_connection()
    query = "DELETE FROM savefilter(filtername, Productlines, Product, salesrep) VALUES (%s, %s, %s, %s)"
    values = (salesmen[0], input_productline.replace('"', ''), input_product.replace('"', ''), salesmen[0], salesmen[0])
    cursor.execute(query, values)
    conn.commit()
    return  HttpResponse(simplejson.dumps({'status': '3'}), content_type="application/json")