from CampaignApp.models import *
from StoreApp.models import *
from rest_framework.response import Response

def product_details(self,request,val_lst,req_id):
    print("oooooooddoooooooo",val_lst)
    for i in range(len(val_lst)):
            print(i["discount_type"])
            product=Product_information()
            product.vendor_id=self.request.user.id
            product.campaignid_id=req_id.id
            product.product_name=val_lst[i]["product_name"]
            product.product_id=val_lst[i]["product_id"]
            product.coupon_name=val_lst[i]["name"]
            product.amount=val_lst[i]["amount"]
            product.save()
     
       
                    
def product_name(self,request,req_id,arg,arg_id):
    print(arg)
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
            
            
            
