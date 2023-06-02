from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import redirect
import requests

import json
from Affilate_Marketing.settings import base_url ,headers ,SHOPIFY_API_KEY,SHOPIFY_API_SECRET,API_VERSION
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from AdminApp.models import *
from StoreApp.models import *
from ShopifyApp.models import *
from ShopifyApp.serializers import *
from CampaignApp.models import *

# Create your views here.

#FUNCTION TO GET ACCESS TOKEN
def access_token(self,request):
    user_obj=User.objects.filter(id=self.request.user.id)
    shop=user_obj.values("shopify_url")[0]["shopify_url"]
    acc_tok=Store.objects.filter(store_name=shop).values("access_token")[0]["access_token"]
   
    return acc_tok,shop
    
    
#API TO FET PRODUCT LIST    
class ProductList(APIView):
    def get(self,request):
        response = requests.get(base_url, headers=headers)
        return Response({"success":json.loads(response.text)})    



# API TO CREATE A PRODUCT
class CreateProduct(APIView):
    def post(self,request):
        title=request.data.get("product")
        body = {"product":title}
        response = requests.post(base_url,headers=headers,json=body)
        return Response({"success":json.loads(response.text)})
    
    



#API TO GET ORDER LIST
class OrderList(APIView):
    authentication_classes=[TokenAuthentication]
    permission_classes = [IsAuthenticated]  
    def get(self,request):
        acc_tok=access_token(self,request)
        headers= {"X-Shopify-Access-Token": acc_tok[0]}
        base_url=f"https://{acc_tok[1]}/admin/api/{API_VERSION}/orders.json?status=anyn"
        response = requests.get(base_url, headers=headers)
        return Response({"success":json.loads(response.text)},status=status.HTTP_200_OK)




#API TO CREATE DISCOUNT
class CreateDiscountCodeView(APIView):
    
    authentication_classes=[TokenAuthentication]
    permission_classes = [IsAuthenticated]  
    def post(self, request):
        vendor_status1=User.objects.filter(id=self.request.user.id).values("vendor_status")
        if vendor_status1[0]["vendor_status"] == True:
            acc_tok=access_token(self,request)
            headers= {"X-Shopify-Access-Token": acc_tok[0]}
            base_url = f'https://{acc_tok[1]}/admin/api/{API_VERSION}'
            discount = request.data.get('discount_code')
            if not discount:
                return Response({'error': 'Coupon field is required'}, status=status.HTTP_400_BAD_REQUEST)
                    
            discount_type=request.data.get("discount_type")
            if not discount_type:
                return Response({'error': 'discount_type field is required'}, status=status.HTTP_400_BAD_REQUEST)
                
            amount=request.data.get("amount")
            if not amount:
                return Response({'error': 'Amount field is required'}, status=status.HTTP_400_BAD_REQUEST)
            
            amt_val="-"+amount
        
            
            data = {
            "price_rule": {
                    "title": discount,
                    "target_type": "line_item",
                    "target_selection": "all",
                    "allocation_method": "across",
                    "value_type":discount_type ,
                    "value": amt_val, 
                    "customer_selection": "all",
                    "once_per_customer": True, 
                    'starts_at': '2023-04-06T00:00:00Z',
                    'ends_at': '2023-08-30T23:59:59Z'
                }
            }

            response = requests.post(f"{base_url}/price_rules.json", headers=headers, json=data)
            price_id=json.loads(response.text)["price_rule"]["id"]
            price_create=json.loads(response.text)["price_rule"]["created_at"]
            
            discount_status=self.one_time_discount(price_id,acc_tok[1],headers,discount)
            
            if response.ok and discount_status == None:
                return Response({"message":"coupon created successfully","title": discount,"created_at":price_create,"id":price_id,},status=status.HTTP_201_CREATED)
            else:
                return Response({"response":"Coupon name already taken"},status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error":"Admin Deactive your shop"},status=status.HTTP_401_UNAUTHORIZED)

 
        
    def one_time_discount(self,price_id,shop,headers,discount_code):
    
        discount_code_endpoint = f'https://{SHOPIFY_API_KEY}:{SHOPIFY_API_SECRET}@{shop}/admin/api/{API_VERSION}/price_rules/{price_id}/discount_codes.json'

        discount_code_data = {
            'discount_code': {
                'code': discount_code,
                'usage_limit': 1,
                'customer_selection': 'all',
                'starts_at': '2023-04-06T00:00:00Z',
                'ends_at': '2023-04-30T23:59:59Z'
            }
        }


        discount_code_response = requests.post(discount_code_endpoint, json=discount_code_data,headers=headers)
    
    

        if discount_code_response.status_code == 201:
            print('Discount code created successfully!')
        else:
           
            return Response({"error":f'Error creating discount code: {discount_code_response.text}'},status=status.HTTP_400_BAD_REQUEST) 
        
    

#API TO CREATE DISCOUNT
class DiscountCodeMultiple(APIView):
    authentication_classes=[TokenAuthentication]
    permission_classes = [IsAuthenticated]  
    def post(self, request):
      
        acc_tok=access_token(self,request)
        headers= {"X-Shopify-Access-Token": acc_tok[0]}
        base_url = f'https://{acc_tok[1]}/admin/api/{API_VERSION}'
   
        discount = request.data.get('discount_code')
        discount_type=request.data.get("discount_type")
        amount=request.data.get("amount")
  
        data = {
          "price_rule": {
                "title": discount,
                "target_type": "line_item",
                "target_selection": "all",
                "allocation_method": "across",
                "value_type": discount_type,
                "value":amount,
                "customer_selection": "all",
                'starts_at': '2023-04-06T00:00:00Z',
                'ends_at': '2023-04-30T23:59:59Z'

            }
        }
        
    
        response = requests.post(f"{base_url}/price_rules.json", headers=headers, json=data)
        price_id=json.loads(response.text)["price_rule"]["id"]
        discount_value=self.multiple_discount_code(price_id,acc_tok[1],headers,discount)
        if response.ok and discount_value == None:
            return Response({"coupon": discount},status=status.HTTP_201_CREATED)
        else:
            return Response({"error":"Coupon name already taken"},status=status.HTTP_400_BAD_REQUEST)
        
        
    def multiple_discount_code(self,price_id,shop,headers,discount_code):
        
        discount_code_endpoint = f'https://{SHOPIFY_API_KEY}:{SHOPIFY_API_SECRET}@{shop}/admin/api/{API_VERSION}/price_rules/{price_id}/discount_codes.json'

        # Set up the data for the discount code
        discount_code_data = {
            'discount_code': {
                'code': discount_code,
                'usage_limit': None,
                'customer_selection': 'all',
                'starts_at': '2023-04-06T00:00:00Z',
                'ends_at': '2023-04-30T23:59:59Z'
            }
        }

        
        discount_code_response = requests.post(discount_code_endpoint, json=discount_code_data,headers=headers)
        
        
     
        if discount_code_response.status_code == 201:
            print('Discount code created successfully!')
        else:
            print(f'Error creating discount code: {discount_code_response.text}')
        


    


#API TO CREATE DISCOUNT
class ParticularProduct(APIView):
    
    authentication_classes=[TokenAuthentication]
    permission_classes = [IsAuthenticated]  
    def post(self, request):
        vendor_status1=User.objects.filter(id=self.request.user.id).values("vendor_status")
        if vendor_status1[0]["vendor_status"] == True:
        
            acc_tok=access_token(self,request)  
            headers= {"X-Shopify-Access-Token": acc_tok[0]}
        
        
        
            product_name=request.data.get("product_id")
            if not product_name:     
                return Response({'error': 'Product  field is required'}, status=status.HTTP_400_BAD_REQUEST)
            my_list = list(map(int, product_name.split(",")))
            
            discount = request.data.get('discount_code')
            if not discount:
                return Response({'error': 'discount code  field is required'}, status=status.HTTP_400_BAD_REQUEST)

           
            
            
            discount_type=request.data.get("discount_type")
            if not discount_type:
                return Response({'error': 'discount type field is required'}, status=status.HTTP_400_BAD_REQUEST)
            
            amount=request.data.get("amount")
            if not amount:
                return Response({'error': 'Amount field is required'}, status=status.HTTP_400_BAD_REQUEST)
            
            amt="-"+amount
        
            price_rule_payload = {
                "price_rule": {
                    "title": discount,
                    "target_type": "line_item",
                    "target_selection": "entitled",
                    "allocation_method": "across",
                    "value_type": discount_type,
                    "value": amt,
                    "customer_selection": "all",
                    'starts_at': '2023-04-06T00:00:00Z',
                    'ends_at': '2023-08-30T23:59:59Z',
                    "entitled_product_ids": my_list,
                    "once_per_customer": True,
            
                }
        }

            # Create the price rule in Shopify
            url = f'https://{acc_tok[1]}/admin/api/{API_VERSION}/price_rules.json'
            response = requests.post(url, headers=headers, json=price_rule_payload)
        
            price_rule_id = response.json()['price_rule']['id']
            price_create=json.loads(response.text)["price_rule"]["created_at"]
            discount_code1(price_rule_id,acc_tok[1],headers,discount)
            print("--------------",discount_code1)
            if response.ok:
                return Response({"message":"coupon created successfully","title": discount,"created_at":price_create,"id":price_rule_id},status=status.HTTP_201_CREATED)
            else:
                return Response({"response":response},status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error":"Admin Deactivate your shop"},status=status.HTTP_401_UNAUTHORIZED)

            

        
    
#API for particular product
def discount_code1(price_id,shop,headers,discount_code):
    
    
    discount_code_endpoint = f'https://{SHOPIFY_API_KEY}:{SHOPIFY_API_SECRET}@{shop}/admin/api/{API_VERSION}/price_rules/{price_id}/discount_codes.json'

    # Set up the data for the discount code
    discount_code_data = {
        'discount_code': {
            'code': discount_code,
            'usage_limit': None,
            'customer_selection': 'all',
            'starts_at': '2023-04-06T00:00:00Z',
            'ends_at': '2023-04-30T23:59:59Z',
            

        }
    }


    discount_code_response = requests.post(discount_code_endpoint, json=discount_code_data,headers=headers)
   
    
    if discount_code_response.status_code == 201:
        print('Discount code created successfully!')
    else:
        print("emnterter")
        return Response({"coupon":discount_code_response.text})
        # print(f'Error creating discount code: {discount_code_response.text}')
        

# API TO GET LIST OF DISCOUNT
class DiscountCodeView(APIView):
    authentication_classes=[TokenAuthentication]
    permission_classes = [IsAuthenticated] 
    def get(self, request, format=None):
        acc_tok=access_token(self,request)
        headers= {"X-Shopify-Access-Token": acc_tok[0]}
       
        url = f'https://{acc_tok[1]}/admin/api/{API_VERSION}/price_rules.json?status=active'
        
        
        
       
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            
            coupons = response.json()['price_rules']
            
            discount_list=[]
            for discount in coupons:    
                discount_data = {
                'title': discount['title'],
                'id': discount['id'],
                "created_at":discount["created_at"]
                }
                discount_list.append(discount_data)

           
    
            return Response({"coupon":discount_list})
        else:
            return Response({'message': response.text}, status=response.status_code)


class ParticularDiscountCodeView(APIView):
    authentication_classes=[TokenAuthentication]
    permission_classes = [IsAuthenticated] 
    def get(self, request, format=None):
        acc_tok=access_token(self,request)
        headers= {"X-Shopify-Access-Token":acc_tok[0]}
        url = f'https://{acc_tok[1]}/admin/api/{API_VERSION}/price_rules.json?status=active'
        
        
      
        lst=[]
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            
            coupons = response.json()['price_rules']
            
        
            for discount in coupons:   
            
                
                coupon_data=requests.get(f'https://{acc_tok[1]}/admin/api/2023-01/price_rules/{discount["id"]}/discount_codes.json',headers=headers)
            
                if coupon_data.json()["discount_codes"]:
                    discount_data = {
                    'title': coupon_data.json()["discount_codes"][0]["code"],
                    'id': coupon_data.json()["discount_codes"][0]["id"],
                    "created_at":coupon_data.json()["discount_codes"][0]["created_at"]
                    }
                    lst.append(discount_data)
    
            return Response({"coupon":lst})
        else:
            return Response({'message': response.text}, status=response.status_code)


#API TO DELETE DISCOUNT CODE
class DeleteCodeView(APIView):
    authentication_classes=[TokenAuthentication]
    permission_classes = [IsAuthenticated] 
    def get(self, request, format=None):
        acc_tok=access_token(self,request)
      
        headers= {"X-Shopify-Access-Token": acc_tok[0]}
        price_rule=request.query_params.get('price')
       
        url =f'https://{SHOPIFY_API_KEY}:{SHOPIFY_API_SECRET}@{acc_tok[1]}/admin/api/{API_VERSION}/price_rules/{price_rule}.json'
        
     
        response = requests.delete(url,headers=headers)


        if response.status_code == 200:
            return Response({'message': 'Discount deleted successfully'})
        else:
            return Response({'message': response.text}, status=response.status_code)
        

        

#API TO EDIT DISCOUNT CODE
class EditCodeView(APIView):
    authentication_classes=[TokenAuthentication]
    permission_classes = [IsAuthenticated] 
    def post(self, request, format=None):
        acc_tok=access_token(self,request)
        
        headers= {"X-Shopify-Access-Token": acc_tok[0]}
        price_rule=request.query_params.get('price')
     
        
        get_url = f'https://{SHOPIFY_API_KEY}:{SHOPIFY_API_SECRET}@{acc_tok[1]}/admin/api/{API_VERSION}/price_rules/{price_rule}.json'
            
        get_response = requests.get(get_url, headers=headers)
        if get_response.status_code == 200:
            coupon_data = get_response.json()["price_rule"]

        
            old_title = coupon_data["title"]
            old_discount_type = coupon_data["value_type"]
            old_amount = coupon_data["value"]   
        else:
            return Response({'message':get_response.text})
        url =f'https://{SHOPIFY_API_KEY}:{SHOPIFY_API_SECRET}@{acc_tok[1]}/admin/api/{API_VERSION}/price_rules/{price_rule}.json'
      
      
    
            
        discount = request.data.get('discount_code')
      
        if discount == None:
            discount=old_title
            
            
            
        discount_type=request.data.get("discount_type")
 
        if discount_type == None:
            discount_type =old_discount_type
           
        amount=request.data.get("amount")
       
        if amount == None:
            amt=old_amount
            
        else:
            amt="-"+amount
            
        data = {
          "price_rule": {
                "title": discount,
                "value_type": discount_type,
                "value":amt,
             

            }
        }
        response = requests.put(url,headers=headers,json=data)
       
        discount_code5(price_rule,acc_tok[1],headers,discount)

    # Check if the discount was successfully deleted and return a DRF response
        if response.status_code == 200:
            return Response({'message': 'Discount Edit successfully','title': discount,"discount_type":discount_type,'amount':amt,"id":price_rule})
        else:
            return Response({'message': response.text}, status=response.status_code)
        

      
def discount_code5(price_rule,shop,headers,discount_code):
    discount_code_endpoint = f'https://{SHOPIFY_API_KEY}:{SHOPIFY_API_SECRET}@{shop}/admin/api/{API_VERSION}/price_rules/{price_rule}/discount_codes.json'
    
    get_response = requests.get(discount_code_endpoint, headers=headers)
    discount_code_id=get_response.json()["discount_codes"][0]['id']

    patch_url = f"https://{shop}/admin/api/2021-10/price_rules/{price_rule}/discount_codes/{discount_code_id}.json"
    

    data = {
    "discount_code": {
        "id": discount_code_id,
        "code": discount_code,
      
    }
}
    discount_code_response = requests.patch(patch_url, json=data,headers=headers)
    # Check if the discount code was created successfully
    if discount_code_response.status_code == 200:
        print('Discount code created successfully!')
    else:
        print(f'Error creating discount code: {discount_code_response}')
        


#API TO GET SINGLE COUPON DATA
class SingleCoupon(APIView):
    authentication_classes=[TokenAuthentication]
    permission_classes = [IsAuthenticated]  
    
    def get(self,request):
        acc_tok=access_token(self,request)
        
        headers= {"X-Shopify-Access-Token": acc_tok[0]}
        price_rule=request.query_params.get('price')
     
        
        get_url = f'https://{SHOPIFY_API_KEY}:{SHOPIFY_API_SECRET}@{acc_tok[1]}/admin/api/{API_VERSION}/price_rules/{price_rule}.json'
            
        get_response = requests.get(get_url, headers=headers)
        if get_response.status_code == 200:
         
                coupon_data = get_response.json()["price_rule"]
                
                title = coupon_data["title"]
                discount_type = coupon_data["value_type"]
                amount   = coupon_data["value"]   
                id   = coupon_data["id"]   
                entitle=coupon_data["entitled_product_ids"]
                
                if coupon_data["entitled_product_ids"]:
                    return Response({'title': title,"discount_type":discount_type,'amount':amount,"id":id, "product_name":entitle,"status":2})
                else:
                    
                    return Response({'title': title,"discount_type":discount_type,'amount':amount,"id":id,"status":1})

        else:
            return Response({'message': get_response.text}, status=400)





        
        
#API TO EDIT DISCOUNT CODE
class ProductEditCodeView(APIView):
    authentication_classes=[TokenAuthentication]
    permission_classes = [IsAuthenticated] 
    def post(self, request, format=None):
        acc_tok=access_token(self,request)
        
        headers= {"X-Shopify-Access-Token": acc_tok[0]}
        price_rule=request.query_params.get('price')
        
        
        get_url = f'https://{SHOPIFY_API_KEY}:{SHOPIFY_API_SECRET}@{acc_tok[1]}/admin/api/{API_VERSION}/price_rules/{price_rule}.json'
            
        get_response = requests.get(get_url, headers=headers)
        if get_response.status_code == 200:
           
            coupon_data = get_response.json()["price_rule"]
            old_title = coupon_data["title"]
            old_discount_type = coupon_data["value_type"]
            old_amount = coupon_data["value"]   
            old_entitled_product_ids = coupon_data['entitled_product_ids']
            
        else:
            return Response({'message':get_response.text})
        url =f'https://{SHOPIFY_API_KEY}:{SHOPIFY_API_SECRET}@{acc_tok[1]}/admin/api/{API_VERSION}/price_rules/{price_rule}.json'
      
      
        product_name = request.data.get('product_id')
        
       
        if product_name == None:
           
            my_list=old_entitled_product_ids
           
        else:    
            my_list = list(map(int, product_name.split(",")))
           
            
            
        discount = request.data.get('discount_code')
        
        if discount == None:
            discount=old_title
               
      
        discount = request.data.get('discount_code')
       
        if discount == None:
            discount=old_title
            
            
            
        discount_type=request.data.get("discount_type")
 
        if discount_type == None:
            discount_type =old_discount_type
          
        amount=request.data.get("amount")
       
        if amount == None:
            amt=old_amount
           
        else:
            amt="-"+amount
        
        
        data = {
            "price_rule": {
                "title": discount,
                "value_type": discount_type,
                "value": amt,
                "entitled_product_ids": my_list,
           
          
            }
    }
        response = requests.put(url,headers=headers,json=data)
        print(acc_tok[1])
        discount_code9(price_rule,acc_tok[1],headers,discount)

    # Check if the discount was successfully deleted and return a DRF response
        if response.status_code == 200:
            return Response({'message': 'Discount Edit successfully','title': discount,"discount_type":discount_type,'amount':amt,"id":price_rule})
        else:
            return Response({'message': response.text}, status=response.status_code)
        
        

      
def discount_code9(price_rule,shop,headers,discount_code):
    discount_code_endpoint = f'https://{SHOPIFY_API_KEY}:{SHOPIFY_API_SECRET}@{shop}/admin/api/{API_VERSION}/price_rules/{price_rule}/discount_codes.json'
    print("-0---------------------",discount_code_endpoint)
    get_response = requests.get(discount_code_endpoint, headers=headers)
    print("---------------------",get_response.json()["discount_codes"])
    discount_code_id=get_response.json()["discount_codes"][0]['id']

    patch_url = f"https://{shop}/admin/api/{API_VERSION}/price_rules/{price_rule}/discount_codes/{discount_code_id}.json"
    

    data = {
    "discount_code": {
        "id": discount_code_id,
        "code": discount_code,
      
    }
}
    discount_code_response = requests.patch(patch_url, json=data,headers=headers)
    # Check if the discount code was created successfully
    if discount_code_response.status_code == 200:
        print('Discount code created successfully!')
    else:
        
        print(f'Error creating discount code: {discount_code_response}')
        
        
        
    

        