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
        base_url=f"https://{acc_tok[1]}/admin/api/{API_VERSION}/orders.json?status=any"
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
            if response.status_code == 422:
                return Response({"message":" value must be between 0 and 100"},status=status.HTTP_400_BAD_REQUEST)

                
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
            
            
            influencer=request.data.get("influencer_name")
            if not influencer:
                return Response({'error': 'Influencer name  field is required'}, status=status.HTTP_400_BAD_REQUEST)
            
            amt="-"+amount
            if amount and discount_type=="percentage":
                if int(amount) >100:
                    return Response({'error': 'amount should be less than 100'}, status=status.HTTP_400_BAD_REQUEST)

                    

            
            
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
                    
            
                }
        }

            # Create the price rule in Shopify
            url = f'https://{acc_tok[1]}/admin/api/{API_VERSION}/price_rules.json'
            response = requests.post(url, headers=headers, json=price_rule_payload)
        
            price_rule_id = response.json()['price_rule']['id']
            price_create=json.loads(response.text)["price_rule"]["created_at"]
            z=discount_code1(price_rule_id,acc_tok[1],headers,discount)
            if z.status_code==201:
                print(z.json()["discount_code"])
                inf_obj=influencer_coupon()
                inf_obj.influencer_id_id=influencer
                inf_obj.coupon_name=discount
                inf_obj.amount=amount
                inf_obj.coupon_id=z.json()["discount_code"]["price_rule_id"]
                inf_obj.vendor_id=self.request.user.id
                inf_obj.save()
                
                return Response({"message":"coupon created successfully","title": discount,"created_at":price_create,"id":price_rule_id},status=status.HTTP_201_CREATED)
            else:
               
                return Response({"error":"Coupon already Exists"},status=status.HTTP_401_UNAUTHORIZED)

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
        return discount_code_response
    else:
        print("i mam hererre")
        pp=delete_price_rule(price_id,shop, headers)
        return discount_code_response
      
      
def delete_price_rule(price_rule_id, shop, headers):
   
    
    delete_url = f'https://{shop}/admin/api/{API_VERSION}/price_rules/{price_rule_id}.json'
    response = requests.delete(delete_url, headers=headers)

    if response.status_code == 200:
        return True  # Price rule deleted successfully
    else:
        return False  # Failed to delete price rule

        

# API TO GET LIST OF DISCOUNT
class DiscountCodeView(APIView):
    authentication_classes=[TokenAuthentication]
    permission_classes = [IsAuthenticated] 
    def get(self, request):
        acc_tok=access_token(self,request)
        headers= {"X-Shopify-Access-Token": acc_tok[0]}
        
        
        
        url = f'https://{acc_tok[1]}/admin/api/{API_VERSION}/price_rules.json?status=active'
        
        
    
       
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            price_rules = response.json().get('price_rules', [])
            discount_list=[]
            for rule in price_rules:
                price_rule_id = rule['id']
                discount_codes_url = f"https://{acc_tok[1]}/admin/api/2023-01/price_rules/{price_rule_id}/discount_codes.json"
                discount_codes_response = requests.get(discount_codes_url, headers=headers)
                
                if discount_codes_response.status_code == 200:
                   
                    discount_codes = discount_codes_response.json().get('discount_codes', [])
                    for code in discount_codes:
                        discount_code = code['code']
                        discount_data = {
                        'title': code['code'],
                        'id': code['price_rule_id'],
                        "created_at":code["created_at"]
                        }
                        discount_list.append(discount_data)

            return Response({'coupon': discount_list},status=status.HTTP_200_OK)
        else:
            print(response.json())   
            return Response({'error': 'Failed to fetch discounts'}, status=500)
        
    # def get(self, request, format=None):
    #     acc_tok=access_token(self,request)
    #     headers= {"X-Shopify-Access-Token": acc_tok[0]}
       
    #     url = f'https://{acc_tok[1]}/admin/api/{API_VERSION}/price_rules.json?status=active'
        
        
    
       
    #     response = requests.get(url, headers=headers)
    #     if response.status_code == 200:
    #         price_rules = response.json().get('price_rules', [])
    #         discount_list=[]
    #         for rule in price_rules:
    #             price_rule_id = rule['id']
    #             discount_codes_url = f"{acc_tok[1]}/admin/api/{API_VERSION}/price_rules/{price_rule_id}/discount_codes.json"
    #             discount_codes_response = requests.get(discount_codes_url, headers=headers)
                
    #             if discount_codes_response.status_code == 200:
    #                 discount_codes = discount_codes_response.json().get('discount_codes', [])
    #                 for code in discount_codes:
    #                     discount_code = code['code']
    #                     print(discount_code)
    #                     discount_list.append(discount_code)
        
    #     # if response.status_code == 200:
            
    #     #     coupons = response.json()['price_rules']
            
    #     #     discount_list=[]
    #     #     for discount in coupons:  
    #     #         print(discount['title'])  
    #     #         if discount['title']:
    #     #             discount_data = {
    #     #             'title': discount['title'],
    #     #             'id': discount['id'],
    #     #             "created_at":discount["created_at"]
    #     #             }
    #                 discount_list.append(discount_data)
    
    #         return Response({"coupon":discount_list})
    #     else:
    #         return Response({'message': response.text}, status=response.status_code)


class  ParticularDiscountCodeView(APIView):
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

        if response.status_code == 204:
            delete_dbcoupon=influencer_coupon.objects.filter(coupon_id=price_rule).delete()
            print("checkdddd",delete_dbcoupon)
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
            amount=old_amount
           
        else:
            amt="-"+str(amount)
            amount=amount
            
        data = {
          "price_rule": {
                "title": discount,
                "value_type": discount_type,
                "value":amt,
             

            }
        }
        response = requests.put(url,headers=headers,json=data)

        cop_res=discount_code5(price_rule,acc_tok[1],headers,discount)

  
        if response.status_code == 200 and cop_res == 200:
            return Response({'message': 'Discount Edit successfully','title': discount,"discount_type":discount_type,'amount':amt,"id":price_rule},status=status.HTTP_200_OK)
        else:
            if response.status_code== 422:
      
                return Response({'message': "must be between 0 and 100"}, status=status.HTTP_400_BAD_REQUEST)
            elif cop_res.status_code== 400:
                return Response({'message': "Coupon already exists"}, status=status.HTTP_400_BAD_REQUEST)
        
        
        

      
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
    
    if discount_code_response.status_code == 200:
        return Response({"success":discount_code_response.json()},status=status.HTTP_200_OK)
    else:
        return Response({"error":discount_code_response.json()},status=status.HTTP_400_BAD_REQUEST)
        


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
                infl_data=influencer_coupon.objects.filter(coupon_id=coupon_data["id"]).values("id")
                infl_data_id=influencer_coupon.objects.filter(coupon_id=coupon_data["id"]).values("influencer_id")
                print(infl_data)
                title = coupon_data["title"]
                discount_type = coupon_data["value_type"]
                amount   = coupon_data["value"]   
                id   = coupon_data["id"]   
                infl_id=infl_data_id
                entitle=coupon_data["entitled_product_ids"]
                
                if coupon_data["entitled_product_ids"]:
                    return Response({'title': title,"discount_type":discount_type,'amount':amount,"id":id, "product_name":entitle,"status":2,"indb":infl_data[0]["id"],"infl_id":infl_id})
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
            amount=old_amount
           
        else:
            amt="-"+amount
            amount=amount
            
        infludb_id=request.data.get("influencer_id")
        influencer_id=request.data.get("influ_ids")
        
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
        zzx=discount_code9(price_rule,acc_tok[1],headers,discount)
      

        if zzx.status_code == 200 and response.status_code==200:
            upt_data=influencer_coupon.objects.filter(id=infludb_id).update(influencer_id_id=influencer_id,amount=int(amount),coupon_name=discount,vendor_id=self.request.user.id)

            return Response({'message': 'Discount Edit successfully','title': discount,"discount_type":discount_type,'amount':amt,"id":price_rule})
        else:
            if response.status_code== 422:
                print("entertte")
                return Response({'message': "must be between 0 and 100"}, status=status.HTTP_400_BAD_REQUEST)
            elif zzx.status_code== 400:
                return Response({'message': "Coupon already exists"}, status=status.HTTP_400_BAD_REQUEST)
        
        

      
def discount_code9(price_rule,shop,headers,discount_code):
    discount_code_endpoint = f'https://{SHOPIFY_API_KEY}:{SHOPIFY_API_SECRET}@{shop}/admin/api/{API_VERSION}/price_rules/{price_rule}/discount_codes.json'

    get_response = requests.get(discount_code_endpoint, headers=headers)
  
    discount_code_id=get_response.json()["discount_codes"][0]['id']

    patch_url = f"https://{shop}/admin/api/{API_VERSION}/price_rules/{price_rule}/discount_codes/{discount_code_id}.json"
    

    data = {
    "discount_code": {
        "id": discount_code_id,
        "code": discount_code,
      
    }
}
    discount_code_response = requests.patch(patch_url, json=data,headers=headers)
    if discount_code_response.status_code == 200:
        return Response({"success":discount_code_response.json()},status=status.HTTP_200_OK)
    else:
        return Response({"error":discount_code_response.json()},status=status.HTTP_400_BAD_REQUEST)
        
        
        
    

import requests
from datetime import datetime, timedelta
from django.http import JsonResponse
from datetime import date


class Analytics(APIView):
    authentication_classes=[TokenAuthentication]
    permission_classes = [IsAuthenticated] 
    def get(self,request):
        acc_tok=access_token(self,request)
        
       
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')

        url = f"https://{acc_tok[1]}/admin/api/2023-01/reports.json"
        headers= {"X-Shopify-Access-Token": acc_tok[0]}

        
        now = datetime.now()
        year = now.year
        month = now.month
        print(month)

      
        start_date = date(2023, 1, 1)
        end_date = date(2023, 1, 31)
        payload = {
            "query": {
                "sales": {
                    "metric": {
                        "field": "total_sales",
                        "sum": {}
                    },
                    "time_range": {
                        "start": start_date.isoformat(),
                        "end": end_date.isoformat()
                    }
                }
            }
        }
    
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            data = response.json()
            total_sales = data.get('results', {}).get('sales_over_time', {}).get('rows', [{}])[0].get('total_sales', 0)

            return Response({'total_sales': total_sales})
        else:
            print(response.json())
            return Response({'error': 'Failed to fetch total sales'}, status=500)



from rest_framework.views import APIView
from rest_framework.response import Response
import requests

# class SalesReportAPIView(APIView):
#     def get(self, request):
#         # Shopify API credentials
#         shopify_store = 'marketplacee-app.myshopify.com'  
#         headers= {"X-Shopify-Access-Token": "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"}

#         # Make API request to retrieve sales data
#         url = f"https://{shopify_store}/admin/api/2023-01/orders.json?status=any"
      
#         response = requests.get(url, headers=headers)
#         print(response.json())

#         if response.status_code == 200:
#             sales_data = response.json()['orders']
#             sales_report = {}

#             for order in sales_data:
#                 created_at = order['created_at']
#                 month = created_at.split('-')[1]
#                 total_price = float(order['total_price'])
                
#                 if month in sales_report:
#                     sales_report[month] += total_price
#                 else:
#                     sales_report[month] = total_price

#             return Response(sales_report)
#         else:
#             # Handle API request error
#             return Response({"error": "Failed to retrieve sales data."}, status=response.status_code)


from rest_framework.views import APIView
from rest_framework.response import Response
import requests
import calendar

class SalesReportAPIView(APIView):
    authentication_classes=[TokenAuthentication]
    permission_classes = [IsAuthenticated] 
    def get(self, request):
        acc_tok=access_token(self,request)
        
        headers= {"X-Shopify-Access-Token": acc_tok[0]}

    
        url = f"https://{acc_tok[1]}/admin/api/2023-01/orders.json?status=any"
   
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            sales_data = response.json()['orders']
            sales_report = {}
            
            for month_number in range(1, 13):
                month_name = calendar.month_name[month_number]
                sales_report[month_name] = 0

            for order in sales_data:
                created_at = order['created_at']
                month_number = int(created_at.split('-')[1])
                month_name = calendar.month_name[month_number]
                total_price = float(order['total_price'])
                sales_report[month_name] += total_price
                
               

            return Response(sales_report)
        else:

        
            return Response({"error": "Failed to retrieve sales data."}, status=response.status_code)



class ShopifyCouponView(APIView):
    authentication_classes=[TokenAuthentication]
    permission_classes = [IsAuthenticated] 
    def get(self, request):
        acc_tok=access_token(self,request)
        
        headers= {"X-Shopify-Access-Token": acc_tok[0]}
        endpoint = f"https://{acc_tok[1]}/admin/api/2023-01/price_rules.json"
      

        response = requests.get(endpoint, headers=headers)
        if response.status_code == 200:
            coupons = response.json().get("price_rules", [])

            # Filter coupons with no entitled product attached
            coupons_without_entitlement = [
                coupon for coupon in coupons if not coupon.get("entitled_product_ids")
            ]

            return Response(coupons_without_entitlement)

        return Response("Failed to retrieve coupons", status=response.status_code)