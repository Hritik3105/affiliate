from CampaignApp.models import *
from StoreApp.models import *
from rest_framework.response import Response
import ast

def product_details(self,request,val_lst,req_id):
   
    for i in range(len(val_lst)):
           
            product=Product_information()
            product.vendor_id=self.request.user.id
            product.campaignid_id=req_id.id
            product.product_name=val_lst[i]["product_name"]
            product.product_id=val_lst[i]["product_id"]
            product.coupon_name=val_lst[i]["name"]
            product.amount=val_lst[i]["amount"]
            product.discount_type=val_lst[i]["discount_type"]
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
    for i in  range (len(val_lst2)):
        print(type(val_lst2[i]["name"]))
        for j in val_lst2[i]["name"]:         
            match_data=Product_information.objects.filter(coupon_name__contains=j,vendor_id=self.request.user.id).exists()
            dict1={str(val_lst2[i]["name"]):match_data}
            cup_lst.append(dict1)
            coup_lst.append(match_data)
            if True in coup_lst:
                cop=(list(dict1.keys())[0])
                return cop
            