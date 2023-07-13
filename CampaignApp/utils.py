from CampaignApp.models import *
from StoreApp.models import *
from rest_framework.response import Response
import ast
from ShopifyApp.models import *
from CampaignApp.views import *

def product_details(self,request,val_lst,req_id):
  
    for i in range(len(val_lst)):
            
            product=Product_information()
            product.vendor_id=self.request.user.id
            product.campaignid_id=req_id.id
            product.product_name=val_lst[i]["product_name"]
            product.product_id=val_lst[i]["product_id"]
            product.coupon_name=val_lst[i]["coupon_name"]
            product.amount=val_lst[i]["amount"]
            product.discount_type=val_lst[i]["discout_type"]
            product.save()
     
       
                    
def product_name(self,request,req_id,arg,arg_id):
    
    for i in  range(len(arg)):
    
        product=Product_information()
        product.vendor_id=self.request.user.id
        product.campaignid_id=req_id.id
        product.product_name=arg[i]
        product.product_id=arg_id[i]
        product.save()


def influencer_details(self,request,int_list,req_id):
    
    for i in int_list:
            vendor_obj=VendorCampaign()
            vendor_obj.influencerid_id=i
            vendor_obj.campaignid_id=req_id.id
            vendor_obj.vendor_id=self.request.user.id
            vendor_obj.save()
            
            notification_obj=Notification()
            notification_obj.influencerid_id=i
            notification_obj.send_notification=1
            notification_obj.vendor_id=self.request.user.id
            notification_obj.campaignid_id=req_id.id
            notification_obj.save()
            
            
            
def coupon_check(self,request,val_lst2,cup_lst,coup_lst):
    val_lst2=(request.data["product_discount"])
    coup_lst=[]
    cup_lst=[]
    dict1={}
    if val_lst2:
    
        for i in  range (len(val_lst2)):
          
            for j in val_lst2[i]["coupon_name"]:         
                match_data=Product_information.objects.filter(coupon_name__contains=j,vendor_id=self.request.user.id).exists()
                
            
                dict1={str(val_lst2[i]["coupon_name"]):match_data}
                
                cup_lst.append(dict1)
                coup_lst.append(match_data)
                

                if True in coup_lst:
                    cop=(list(dict1.keys())[0])
                    
                    cop_lst=ast.literal_eval(cop)
                    
                    return cop




def access_token(self,request):
    user_obj=User.objects.filter(id=self.request.user.id)
    shop=user_obj.values("shopify_url")[0]["shopify_url"]
    acc_tok=Store.objects.get(store_name=shop).access_token

    return acc_tok,shop


def ExpiryCoupondelete(self,request):
    
    acc_tok=access_token(self,request)
    
    headers= {"X-Shopify-Access-Token": acc_tok[0]}
    price_rule=request.query_params.get('price')
    product_info=Product_information.objects.filter(campaignid_id__campaign_exp=0,vendor_id=self.request.user.id).values_list("coupon_name",flat=True)
    
    
    
    for coupon in product_info:
        
        if coupon:
            str_lst=ast.literal_eval(coupon)
            print(str_lst)
            cop_id=influencer_coupon.objects.filter(coupon_name__in=str_lst,vendor=self.request.user.id).values_list("coupon_id",flat=True)
            print(cop_id)
            # url =f'https://{SHOPIFY_API_KEY}:{SHOPIFY_API_SECRET}@{acc_tok[1]}/admin/api/{API_VERSION}/price_rules/{price_rule}.json'
    
    
            # response = requests.delete(url,headers=headers)

            # delete_coup=influencer_coupon.objects.filter(coupon_name__in=str_lst).delete()
    return "DONE"