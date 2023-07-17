from django.core.mail import send_mail
from django.conf import settings
import requests

def send_forget_password_mail(email,token):

    subject="your forget password link"
    message=f'Hi,click on the link to reset your passord http://127.0.0.1:8000/isadmin/change_password_link/{email}/{token}'
    email_from=settings.EMAIL_HOST_USER
    recipient_list=[email]
    send_mail(subject,message,email_from,recipient_list)
    return True



def dashboard_value(request,get_tok,sales_reports1,vendor_store,sale_val,total_order_count,total_sales):
    if get_tok:
        for token in get_tok:
            headers = {"X-Shopify-Access-Token": token["access_token"]}
            store_name = token["store_name"]

            url = f"https://{store_name}/admin/api/2022-10/orders.json?status=active"
            response = requests.get(url, headers=headers)
            sales_data = response.json().get('orders', [])
            sales_report = 0 
            order_count=0
        
            for order in sales_data:
                total_price = float(order['total_price'])
                discount_codes = order.get("discount_codes", [])

                if discount_codes:
                    sales_report += total_price
                    total_sales += total_price
                    order_count += 1  
            sales_reports1.append({"store_name": store_name, "sales_report": sales_report,"order_count":order_count})

    for i in sales_reports1:
        total_order_count+=i["order_count"]
        vendor_store.append(i["store_name"])
        sale_val.append(i["sales_report"])
    rouded_value=round(total_sales,2)
    
    return rouded_value,sales_reports1,total_order_count,vendor_store,sale_val
    