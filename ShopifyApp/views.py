from rest_framework.views import APIView
from rest_framework.response import Response
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
import requests
from datetime import datetime, timedelta
from datetime import date
from ShopifyApp.utils import *
import ast  
# Create your views here.

#FUNCTION TO GET ACCESS TOKEN

    




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
            
            product_name=request.data.get("product_id")
            if not product_name:     
                return Response({'error': 'Product  field is required'}, status=status.HTTP_400_BAD_REQUEST)
            my_list = list(map(int, product_name.split(",")))
           
            
            
            discount = request.data.get('discount_code')
          
            if discount:
                if len(discount)<3:
                    return Response({'error': 'discount code must be three or more than three character long'}, status=status.HTTP_400_BAD_REQUEST)

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
                    "target_selection": "entitled",
                    "allocation_method": "across",
                    "value_type":discount_type ,
                    "value": amt_val, 
                    "customer_selection": "all",
                    "once_per_customer": True, 
                    'starts_at': '2023-04-06T00:00:00Z',
                    'ends_at': '2023-08-30T23:59:59Z',
                    "entitled_product_ids": my_list,
                }
            }

            response = requests.post(f"{base_url}/price_rules.json", headers=headers, json=data)
          
            if response.status_code == 422:
                return Response({"message":" value must be between 0 and 100"},status=status.HTTP_400_BAD_REQUEST)

            if response.ok:
                price_id=json.loads(response.text)["price_rule"]["id"]
                
                price_create=json.loads(response.text)["price_rule"]["created_at"]
                
                discount_status=one_time_discount(price_id,acc_tok[1],headers,discount)
                
                if discount_status.status_code==201:
                    inf_obj=Marketplace_coupon()
                    inf_obj.coupon_name=discount
                    inf_obj.amount=amount
                    inf_obj.coupon_id=discount_status.json()["discount_code"]["price_rule_id"]
                    inf_obj.vendor_id=self.request.user.id
                    inf_obj.save()
                    return Response({"message":"coupon created successfully","title": discount,"created_at":price_create,"id":price_id,},status=status.HTTP_201_CREATED)
                else:
                    return Response({"response":"Coupon name already taken"},status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"error":"Amount should be in positive"},status=status.HTTP_400_BAD_REQUEST)
        return Response({"error":"Admin Deactive your shop"},status=status.HTTP_401_UNAUTHORIZED)
   



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
            if discount:
                if len(discount)<3:
                    return Response({'error': 'discount code must be three or more than three character long'}, status=status.HTTP_400_BAD_REQUEST)

                    
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
                if float(amount) >100:
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
                    "once_per_customer": True, 
                    'starts_at': '2023-04-06T00:00:00Z',
                    'ends_at': '2023-08-30T23:59:59Z',
                    "entitled_product_ids": my_list,
                    
            
                }
        }

            # Create the price rule in Shopify
            url = f'https://{acc_tok[1]}/admin/api/{API_VERSION}/price_rules.json'
            response = requests.post(url, headers=headers, json=price_rule_payload)
            if response.ok:
                price_rule_id = response.json()['price_rule']['id']
                price_create=json.loads(response.text)["price_rule"]["created_at"]
                z=discount_code1(price_rule_id,acc_tok[1],headers,discount)
                if z.status_code==201:
                
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
                return Response({"error":"Amount should be in positive"},status=status.HTTP_400_BAD_REQUEST)
                
        else:
            return Response({"error":"Admin Deactivate your shop"},status=status.HTTP_401_UNAUTHORIZED)
        
        

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
                title = rule['title']
                created_at=rule["created_at"]
                split_date=created_at.split("T")[0]
                discount_data = {
                'title':title,
                'id': price_rule_id,
                "created_at":split_date
                }
                discount_list.append(discount_data)
              
   
            sorted_data = sorted(discount_list, key=lambda x: x['created_at'], reverse=True)
           
            return Response({'coupon': sorted_data},status=status.HTTP_200_OK)
        else:
               
            return Response({'error': 'Failed to fetch discounts'}, status=500)
        



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
            
                
                coupon_data=requests.get(f'https://{acc_tok[1]}/admin/api/{API_VERSION}/price_rules/{discount["id"]}/discount_codes.json',headers=headers)
            
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
        if discount:
            if len(discount)<3:
                return Response({'error': 'discount code must be three or more than three character long'}, status=status.HTTP_400_BAD_REQUEST)

      
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
            
            
       
    
        influencer_id=request.data.get("influ_ids")
        
            
        data = {
            "price_rule": {
                "title": discount,
                "value_type": discount_type,
                "value": amt,
                "entitled_product_ids": my_list,
           
          
            }
    }
      
        cop_res=discount_code5(price_rule,acc_tok[1],headers,discount)
        
        if cop_res.status_code == 200:

            response = requests.put(url,headers=headers,json=data)
            
            if response.status_code == 200: 
                cop_data=Product_information.objects.all()
            
                
                for k in cop_data:
                   
                    if k.coupon_id:
                       
                        if int(price_rule) in ast.literal_eval(k.coupon_id):
                         
                            cop_id=ast.literal_eval(k.coupon_id)
                            
                            edit_index=cop_id.index(int(price_rule))
                           
                          
                            cop_name=ast.literal_eval(k.coupon_name)
                            cop_name[edit_index] = discount
                            k.coupon_name=str(cop_name)
                           
                            cop_amount=ast.literal_eval(k.amount)   
                            flt_val=float(amount)
                            cop_amount[edit_index] = str(flt_val)
                            k.amount=str(cop_amount)
                            
                            cop_type=ast.literal_eval(k.discount_type)   
                           
                            cop_type[edit_index] = str(discount_type)
                            k.discount_type=str(cop_type)
                            
    
                            
                            Product_information.objects.filter(coupon_id=k.coupon_id).update(coupon_name=k.coupon_name,amount= k.amount,discount_type=k.discount_type)
                
                return Response({'message': 'Discount Edit successfully','title': discount,"discount_type":discount_type,'amount':amt,"id":price_rule},status=status.HTTP_200_OK)
            if response.status_code== 422:
                return Response({'message': "must be between 0 and 100"}, status=status.HTTP_400_BAD_REQUEST)   
        else:
            if cop_res.status_code== 400:
                return Response({'message': "Coupon already exists"}, status=status.HTTP_400_BAD_REQUEST)
        
        
    


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
               
                if infl_data_id and infl_data:
                    title = coupon_data["title"]
                    discount_type = coupon_data["value_type"]
                    amount   = coupon_data["value"]   
                    id   = coupon_data["id"]   
                    infl_id=infl_data_id
                
                    main_id=infl_id[0]["influencer_id"]
                    entitle=coupon_data["entitled_product_ids"]
                    
                    if coupon_data["entitled_product_ids"]:
                        return Response({'title': title,"discount_type":discount_type,'amount':amount,"id":id, "product_name":entitle,"status":2,"indb":infl_data[0]["id"],"infl_id":main_id})
                    else:
                        return Response({'title': title,"discount_type":discount_type,'amount':amount,"id":id,"status":1})
                else:
                    title = coupon_data["title"]
                    discount_type = coupon_data["value_type"]
                    amount   = coupon_data["value"]   
                    id  = coupon_data["id"]   
                    entitle=coupon_data["entitled_product_ids"]
                    return Response({'title': title,"discount_type":discount_type,'amount':amount,"id":id,"status":1,"product_name":entitle})

                    
        else:
            return Response({'message': get_response.text}, status=400)





        
        
#API TO EDIT DISCOUNT CODE
class ProductEditCodeView(APIView):
    authentication_classes=[TokenAuthentication]
    permission_classes = [IsAuthenticated] 
    def post(self, request, format=None):
        
        coupon_value=VendorCampaign.objects.filter(vendor=self.request.user.id,campaign_status=2).values("campaignid")
      
        for ids in coupon_value:
            print(ids["campaignid"])
            pre_val=Campaign.objects.filter(id=ids["campaignid"]).prefetch_related("product_information__set").all()
            print(pre_val)
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
        if discount:
                if len(discount)<3:
                    return Response({'error': 'discount code must be three or more than three character long'}, status=status.HTTP_400_BAD_REQUEST)

        
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
        
       
      
        zzx=discount_code9(price_rule,acc_tok[1],headers,discount)
      

        if zzx.status_code == 200:
            response = requests.put(url,headers=headers,json=data)
            if  response.status_code==200:
               
                cccc=Product_information.objects.all()
            
                
                for k in cccc:
                   
                    if k.coupon_id:
                       
                        if int(price_rule) in ast.literal_eval(k.coupon_id):
                            print(type(k.coupon_id))
                            cop_id=ast.literal_eval(k.coupon_id)
                            
                            edit_index=cop_id.index(int(price_rule))
                           
                          
                            cop_name=ast.literal_eval(k.coupon_name)
                            cop_name[edit_index] = discount
                            k.coupon_name=str(cop_name)
                           
                            cop_amount=ast.literal_eval(k.amount)   
                            flt_val=float(amount)
                            cop_amount[edit_index] = str(flt_val)
                            k.amount=str(cop_amount)
                            
                            cop_type=ast.literal_eval(k.discount_type)   
                           
                            cop_type[edit_index] = str(discount_type)
                            k.discount_type=str(cop_type)
                            
    
                            
                            Product_information.objects.filter(coupon_id=k.coupon_id).update(coupon_name=k.coupon_name,amount= k.amount,discount_type=k.discount_type)
                influencer_coupon.objects.filter(id=infludb_id).update(influencer_id_id=influencer_id,amount=float(amount),coupon_name=discount,vendor_id=self.request.user.id)
            
                return Response({'message': 'Discount Edit successfully','title': discount,"discount_type":discount_type,'amount':amt,"id":price_rule,"influencer":influencer_id})
            if response.status_code== 422:
               
                return Response({'message': "must be between 0 and 100"}, status=status.HTTP_400_BAD_REQUEST)
        else:
          
            if zzx.status_code== 400:
                return Response({'message': "Coupon already exists"}, status=status.HTTP_400_BAD_REQUEST)
        
        

      

        
        
class Analytics(APIView):
    authentication_classes=[TokenAuthentication]
    permission_classes = [IsAuthenticated] 
    def get(self,request):
        acc_tok=access_token(self,request)
        
       
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')

        url = f"https://{acc_tok[1]}/admin/api/{API_VERSION}/reports.json"
        headers= {"X-Shopify-Access-Token": acc_tok[0]}

        
        now = datetime.now()
        year = now.year
        month = now.month
       

      
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
          
            return Response({'error': 'Failed to fetch total sales'}, status=500)





class ShopifyCouponView(APIView):
    authentication_classes=[TokenAuthentication]
    permission_classes = [IsAuthenticated] 
    def get(self, request):
        single_coupon=[]
        acc_tok=access_token(self,request)
        
        headers= {"X-Shopify-Access-Token": acc_tok[0]}
        endpoint = f"https://{acc_tok[1]}/admin/api/{API_VERSION}/price_rules.json?status=active"
      

        response = requests.get(endpoint, headers=headers)
        if response.status_code == 200:
            coupons = response.json().get("price_rules", [])

            # Filter coupons with no entitled product attached
            coupons_without_entitlement = [
                coupon for coupon in coupons if not coupon.get("entitled_product_ids")
            ]
            for i in coupons_without_entitlement:
                dict={
                    "coupon_name":i["title"],
                    "discout_type":i["value_type"],
                    "amount":i["value"],
                    "id":i["id"]
                }
                single_coupon.append(dict)
            return Response(single_coupon)

        return Response("Failed to retrieve coupons", status=response.status_code)
    
    
    
