from rest_framework.views import APIView
from rest_framework.response import Response
from CampaignApp.models import *
from CampaignApp.serializer import *
from rest_framework.permissions import IsAuthenticated
from rest_framework import  status
from InfluencerApp.serializer import *
from Affilate_Marketing.settings import SHOPIFY_API_KEY,SHOPIFY_API_SECRET,API_VERSION
import requests
import json
from django.contrib.auth import authenticate, login
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication
from StoreApp.models import *
from django.contrib.auth import get_user_model
from django.db.models import Q
from .utils import *
from django.core.mail import EmailMessage 
from ShopifyApp.models import *
import calendar
from datetime import datetime, timedelta
from django.utils import timezone
import stripe
from Affilate_Marketing import settings
from CampaignApp.utils import *
from AdminApp.models import *

# Create your views here.




#To get access token
            
def access_token(self,request):
    user_obj=User.objects.filter(id=self.request.user.id)
    shop=user_obj.values("shopify_url")[0]["shopify_url"]
    acc_tok=Store.objects.get(store_name=shop).access_token

    return acc_tok,shop

"""API HELP TO GET SHOPIFY ACCESS TOKEN AND SHOPIFY STORE NAME"""



    
#REGISTER INFLUENCER API

"""API TO REGISTER VENOR AND ASSIGN USER TYPE STAUTS = 3"""
class Register(APIView):
    def post(self,request):
        serializer=RegisterSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save(user_type =3)
            infl_id=serializer.data["id"]
            mail_subject = 'Vendor Register'  
            email_body= "HI"  +  " "  +  serializer.data["username"] + " " + "your Shop Register Successfully"
        
            to_email =serializer.data["email"]  
            email = EmailMessage(  
                        mail_subject, email_body, to=[to_email]  
            )  

            email.send()  
            return Response({"Success": "Vendor Register Successfully"},status=status.HTTP_201_CREATED)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    
    
     
#LOGIN INFLUENCER API  

"""API TO VENDOR LOGIN THROUGH SHOP URL OR USERNAME AND PASSWORD"""
class VendorLogin(APIView): 
    def post(self, request):
            shop_url=request.data.get('shop')
            if shop_url:
                user_objects=User.objects.filter(shopify_url=shop_url).values("email","password")
                if user_objects:
                    user_obj=User.objects.filter(email=user_objects[0]["email"],password=user_objects[0]["password"])
                    email1=user_objects[0]["email"]
                    token_id=user_obj.values_list("id",flat=True)[0]
                    user_base = get_user_model()
                    usr_ins=user_base.objects.get(email=email1)
                    shop2=Store.objects.filter(store_name=shop_url)

                    if user_obj:
                        usr=Token.objects.filter(user_id=token_id)
                        if not usr:
                            token = Token.objects.create(user=usr_ins)
                            
                         
                            return Response({'Success':"Login Successfully",'Token':str(token),"shop_url":usr_ins.shopify_url}, status=status.HTTP_200_OK)
                           
                        else:
                            user_key=Token.objects.filter(user_id=token_id).values_list("key",flat=True)[0]
                            if shop2:
                                store_name=usr_ins.shopify_url.split(".")[0]
                               
                                return Response({'Success':"Login Successfully",'Token':str(user_key),"shop_url":usr_ins.shopify_url,"admin_dahboard":f"https://admin.shopify.com/store/{store_name}/apps/marketplace-54"}, status=status.HTTP_200_OK)
                            
                            return Response({'Success':"Login Successfully",'Token':str(user_key),"shop_url":usr_ins.shopify_url}, status=status.HTTP_200_OK)
                    else:
                        return Response({'error': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response({'error': 'Shop url not found'}, status=status.HTTP_400_BAD_REQUEST)
 
            else:
                email = request.data.get('email')    
                password = request.data.get('password')
                user=authenticate(username=email, password=password)
                if user:
                    
                    login(request, user)
                    
                    if user.user_type == "3":
                      
                        usr=Token.objects.filter(user_id=user.id)
                        if not usr:
                            refresh=Token.objects.create(user=user) 
                            return Response({'Success':"Login Successfully",'Token':str(refresh),"shop_url":user.shopify_url}, status=status.HTTP_200_OK)
                        else:
                        
                            user_token=Token.objects.filter(user_id=user.id).values_list("key",flat=True)[0]
                            shop2=User.objects.filter(id=user.id).values_list("shopify_url",flat=True)[0]
                            shop4=Store.objects.filter(store_name=shop2)
                            if shop4:
                                store_name=user.shopify_url.split(".")[0]
                                return Response({'Success':"Login Successfully",'Token':str(user_token),"shop_url":user.shopify_url,"admin_dahboard":f"https://admin.shopify.com/store/{store_name}/apps/marketplace-54"}, status=status.HTTP_200_OK)
                    
                            return Response({'Success':"Login Successfully",'Token':str(user_token),"shop_url":user.shopify_url}, status=status.HTTP_200_OK)
                    else:
                        return Response({'error': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)

                else:
                    return Response({'error': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)
       
        
        
        
#API TO CREATE CAMPAIGN

"""API TO CREATE CAMPAIGN FOR MARKET PLACE DRAFT"""
class CreateCampaign(APIView):
    
    
    authentication_classes=[TokenAuthentication]
    permission_classes = [IsAuthenticated]   
    def post(self,request):
       
        vendor_status1=User.objects.filter(id=self.request.user.id).values("vendor_status")
        if vendor_status1[0]["vendor_status"] == True:
            serializer=CampaignSerializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                
                val_lst2=(request.data["product_discount"])
                coup_lst=[]
                cup_lst=[]
              
                if val_lst2[0]["coupon_name"] !=[None]:
                    final_err=coupon_check(self,request,val_lst2,cup_lst,coup_lst)
                  
                    if final_err:        
                            return Response({"error": final_err},status=status.HTTP_410_GONE)
                    req_id=serializer.save(draft_status=1,vendorid_id=self.request.user.id,status=1)
                    val_lst=(request.data["product_discount"])
                    
                    if {} in val_lst:
                        z=val_lst.remove({})
                    else:
                        z=""
                    if val_lst:
                        product_details(self,request,val_lst,req_id)                            
                    else: 
                        arg=request.data["product_name"]
                        if len(arg)>0:
                            arg_id=request.data["product"]
                            product_name(self,request,req_id,arg,arg_id)
                        else:     
                            product=Product_information()
                            product.vendor_id=self.request.user.id
                            product.campaignid_id=req_id.id
                            product.save()
                    
                        return Response({"success":"Campaign create successfully","product_details":serializer.data},status=status.HTTP_200_OK)
                        
                    return Response({"success":"Campaign create successfully","product_details":serializer.data},status=status.HTTP_200_OK)
                req_id=serializer.save(draft_status=1,vendorid_id=self.request.user.id,status=1)
                val_lst=(request.data["product_discount"])
                product=Product_information()
                product.vendor_id=self.request.user.id
                product.campaignid_id=req_id.id
                product.save()
                return Response({"success":"Campaign create successfully","product_details":serializer.data},status=status.HTTP_200_OK)

                
        else:
            return Response({"error":"Admin Deactive your shop"},status=status.HTTP_401_UNAUTHORIZED)

        return Response({"error":"Campaign not created"},status=status.HTTP_400_BAD_REQUEST)



#API TO SENT  CAMPAIGN TO MARKETPLACE

"""API CREATE A MARKET CAMPAIGN THAT CAN BE SEEN I MARKETPLACE PAGE"""
class RequestCampaign(APIView):
    authentication_classes=[TokenAuthentication]
    permission_classes = [IsAuthenticated]   
    def post(self,request):
        vendor_status1=User.objects.filter(id=self.request.user.id).values("vendor_status")
        if vendor_status1[0]["vendor_status"] == True:
            serializer=CampaignSerializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                val_lst2=(request.data["product_discount"])
                coup_lst=[]
                cup_lst=[]
                dict1={}
                print(val_lst2[0]["coupon_name"])
                if val_lst2[0]["coupon_name"] !=[None]:
                    
                    for i in  range (len(val_lst2)):
                        if val_lst2[i]["coupon_name"]:
                            for j in val_lst2[i]["coupon_name"]:         
                                match_data=Product_information.objects.filter(coupon_name__contains=j,vendor_id=self.request.user.id).exists()
                            
                            
                                dict1={str(val_lst2[i]["coupon_name"]):match_data}
                                
                                cup_lst.append(dict1)
                                coup_lst.append(match_data)
                                

                                if True in coup_lst:
                                    cop=(list(dict1.keys())[0])
                                
                                    cop_lst=ast.literal_eval(cop)
                                    
                                    return Response({"error": cop_lst},status=status.HTTP_410_GONE)
                    req_id=serializer.save(vendorid_id=self.request.user.id,status=1)
                    val_lst=(request.data["product_discount"])
                

                    if {} in val_lst:
                        z=val_lst.remove({})
                    else:
                        z=""
                    if val_lst:
                  
                        product_details(self,request,val_lst,req_id)                          
                    else:
                     
                        arg=request.data["product_name"]
                        if len(arg)>0:
                            arg_id=request.data["product"]
                            
                            product_name(self,request,req_id,arg,arg_id)  
                        else:
                           
                            product=Product_information()
                            product.vendor_id=self.request.user.id
                            product.campaignid_id=req_id.id
                            product.save()
   

                    
                        return Response({"success":"Campaign create successfully","product_details":serializer.data},status=status.HTTP_200_OK)
                    return Response({"success":"Campaign create successfully","product_details":serializer.data},status=status.HTTP_200_OK)
                req_id=serializer.save(vendorid_id=self.request.user.id,status=1)
                val_lst=(request.data["product_discount"])
                
                product=Product_information()
                product.vendor_id=self.request.user.id
                product.campaignid_id=req_id.id
                product.save()
                return Response({"success":"Campaign create successfully","product_details":serializer.data},status=status.HTTP_200_OK)

        else:
            return Response({"error":"Admin Deactive your shop"},status=status.HTTP_401_UNAUTHORIZED)

        return Response({"error":"Campaign not created"},status=status.HTTP_400_BAD_REQUEST)
    


# API TO update CAMPAIGN 

"""API UPDATE BOTH INFLUENCER AND MARKETPLACE CAMPAIGN """
class UpdateCampaign(APIView):
    def put(self,request,pk=None):
        try:
            campaign_get = Campaign.objects.get(Q(pk = pk,status=1)|Q(pk=pk,status=2),vendorid_id=self.request.user.id)  
        except Campaign.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)  
        serializer=CampaignUpdateSerializer(campaign_get,data=request.data)
       
        if serializer.is_valid():
            val_lst2=(request.data["product_discount"])
            coup_lst=[]
            cup_lst=[]
            dict1={}
            if val_lst2:
   
                for i in  range (len(val_lst2)):
                    if val_lst2[i]["coupon_name"]:
                      
                        for j in val_lst2[i]["coupon_name"]:
                        
                            
                            match_data=Product_information.objects.filter(coupon_name__contains=j,vendor_id=self.request.user.id,campaignid_id=pk).exists()
                            if match_data== False:
                            
                                match_data=Product_information.objects.filter(coupon_name__contains=j,vendor_id=self.request.user.id).exists()

                                
                                dict1={str(val_lst2[i]["coupon_name"]):match_data}
                                cup_lst.append(dict1)
                                coup_lst.append(match_data)
                                
                            
                                

                                if True in coup_lst:
                                    cop=(list(dict1.keys())[0])
                                    cop_lst=ast.literal_eval(cop)
                                    return Response({"error": cop_lst},status=status.HTTP_410_GONE)
                        
                req_id=serializer.save()
                val_lst=(request.data["product_discount"])

                if {} in val_lst:
                    z=val_lst.remove({})
                else:
                    z=""
                    
                for i in range(len(val_lst)):
                    product=Product_information.objects.filter(campaignid_id =req_id.id,vendor_id=self.request.user.id).delete()
           
                for i in range(len(val_lst)):
                    product=Product_information()
                    product.vendor_id=self.request.user.id
                    product.campaignid_id=req_id.id
                    product.product_name=val_lst[i]["product_name"]
                    product.product_id=val_lst[i]["product_id"]
                    product.coupon_name=val_lst[i]["coupon_name"]
                    product.amount=val_lst[i]["amount"]
                    product.save()
                product=VendorCampaign.objects.filter(campaignid_id =req_id.id,vendor_id=self.request.user.id).delete()

           
                if  "influencer_name" in request.data and Campaign.objects.filter(id =req_id.id,draft_status=0,vendorid_id=self.request.user.id):
                        val_lst1=(request.data["influencer_name"])
                        
                        data_list=val_lst1.split(",")
                
                        int_list = [int(num) for num in data_list]
                        Notification.objects.filter(campaignid_id=req_id.id,vendor_id=self.request.user.id).delete()
                        influencer_details(self,request,int_list,req_id)
                               
    
            else:
               
                req_id=serializer.save()
                product=Product_information.objects.filter(campaignid_id =req_id.id,vendor_id=self.request.user.id).delete()
               
             
    
                arg=request.data["product_name"]

                if len(arg)>0:
                   
                    for i in  range(len(arg)):
        
                        product=Product_information()
                        product.vendor_id=self.request.user.id
                        product.campaignid_id=req_id.id
                        product.product_name=arg[i]
                        # product.product_id=arg_id[i]
                        product.save()

                    
                    if  "influencer_name" in request.data and Campaign.objects.filter(id =req_id.id,draft_status=0,vendorid_id=self.request.user.id):
                        val_lst1=(request.data["influencer_name"])
                    
                        data_list=val_lst1.split(",")
                
                        int_list = [int(num) for num in data_list]
                        Notification.objects.filter(campaignid_id=req_id.id,vendor_id=self.request.user.id).delete()
                        influencer_details(self,request,int_list,req_id)  
         
                else:
                    val_lst1=(request.data["influencer_name"])

                    data_list=val_lst1.split(",")
                    int_list = [int(num) for num in data_list]
                
                    influencer_details(self,request,int_list,req_id)
                        
                    product=Product_information()
                    product.vendor_id=self.request.user.id
                    product.campaignid_id=req_id.id
                    product.save()
           
                    
            return Response(serializer.data,status=status.HTTP_200_OK)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    
    
    




#API CHANGE STATUS OF CAMPAIGN    
"""API TO CHANGE CAMPAING STATUS FROM DRAFT TO PENDING"""
class DraftStatusUpdate(APIView):
    def put(self,request,pk=None):
        try:
            campaign_get = Campaign.objects.get(Q(pk = pk,status=1)|Q(pk=pk,status=2),vendorid_id=self.request.user.id) 

        except Campaign.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer=CampaignUpdateSerializer(campaign_get,data=request.data)
        if serializer.is_valid():
            val_lst2=(request.data["product_discount"])
            coup_lst=[]
            cup_lst=[]
            dict1={}
            if val_lst2:
                for i in  range (len(val_lst2)):
                    if val_lst2[i]["coupon_name"]:
                        for j in val_lst2[i]["coupon_name"]:
                        
                            
                            match_data=Product_information.objects.filter(coupon_name__contains=j,vendor_id=self.request.user.id,campaignid_id=pk).exists()
                            if match_data== False:
                            
                                match_data=Product_information.objects.filter(coupon_name__contains=j,vendor_id=self.request.user.id).exists()

                                
                                dict1={str(val_lst2[i]["coupon_name"]):match_data}
                                cup_lst.append(dict1)
                                coup_lst.append(match_data)
                                
                            
                                if True in coup_lst:
                                    cop=(list(dict1.keys())[0])
                                    cop_lst=ast.literal_eval(cop)
                                    return Response({"error": cop_lst},status=status.HTTP_410_GONE)
               
                req_id=serializer.save(draft_status=0,campaign_status=0)
                val_lst=(request.data["product_discount"])
                
                if {} in val_lst:
                    z=val_lst.remove({})
                else:
                    z=""
                    
                for i in range(len(val_lst)):
                   
                    product=Product_information.objects.filter(campaignid_id =req_id.id,vendor_id=self.request.user.id).delete()
            
         
                
                product_details(self,request,val_lst,req_id)
                
                if  "influencer_name" in request.data:
                   
                    val_lst1=(request.data["influencer_name"])
                    
                    data_list=val_lst1.split(",")
            
                    int_list = [int(num) for num in data_list]
                
                    influencer_details(self,request,int_list,req_id)               
               
                # else:
                #     print("lets go")
                #     product=Product_information()
                #     product.vendor_id=self.request.user.id
                #     product.campaignid_id=req_id.id
                #     product.save()
                   
                        
                
                if z == None :
                
                    product=Product_information()
                    product.vendor_id=self.request.user.id
                    product.campaignid_id=req_id.id
                    product.save()               
            return Response(serializer.data,status=status.HTTP_200_OK)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)




    
#API TO CREATE INFLUENCER CAMPAIGN

"""API TO CREATE INFLUENCER CAMPAIGN"""
class InfluencerCampaign(APIView):
    authentication_classes=[TokenAuthentication]
    permission_classes = [IsAuthenticated]   
    def post(self,request):
        vendor_status1=User.objects.filter(id=self.request.user.id).values("vendor_status")
        if vendor_status1[0]["vendor_status"] == True:
            serializer=InflCampSerializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
            
             
               
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
                                return Response({"error": cop_lst},status=status.HTTP_410_GONE)
                    req_id=serializer.save(status=2,vendorid_id=self.request.user.id,draft_status=1)
                    val_lst=(request.data["product_discount"])
                    
                    while {} in val_lst:
                        z=val_lst.remove({})
                    else:
                        z=""
                    if val_lst:
                        
                        product_details(self,request,val_lst,req_id)
                            
                else:
                    req_id=serializer.save(status=2,vendorid_id=self.request.user.id,draft_status=1)
                    arg=request.data["product_name"]
                
                    if len(arg)>0:
                        
                        arg_id=request.data["product"]
                        product_name(self,request,req_id,arg,arg_id)
                    
                    else:
                        req_id=serializer.save(status=2,vendorid_id=self.request.user.id,draft_status=1)

                        product=Product_information()
                        product.vendor_id=self.request.user.id
                        product.campaignid_id=req_id.id
                        product.save()
                    
                    
                    return Response({"success":"Campaign create successfully","product_details":serializer.data},status=status.HTTP_200_OK)

                
                return Response({"success":"Campaign create successfully","product_details":serializer.data},status=status.HTTP_200_OK)
        else:
            return Response({"error":"Admin Deactive your shop"},status=status.HTTP_401_UNAUTHORIZED)
        return Response({"error":"Campaign not created"},status=status.HTTP_400_BAD_REQUEST)

    
    

# API TO GET LIST OF CAMPAIGN   
"""API TO GET PENDING LIST OF CAMPAIGN OF INFLUENCER"""
class PendingList(APIView):
    authentication_classes=[TokenAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self,request):
        lst=[]
        final_lst=[]

        campaign_obj=Campaign.objects.filter(Q(campaign_status=0),draft_status=0,vendorid_id=self.request.user.id,status=2,campaign_exp=1)
        if campaign_obj:
            z=(campaign_obj.values("id"))
            for i in z:
                lst.append(i['id'])
        set_data=set(lst)
       
        fin_value=set_data
        for i in fin_value:
            camp=Product_information.objects.filter(vendor_id=self.request.user.id,campaignid_id=i).values()
            campaign_obj59=Product_information.objects.filter(vendor_id=self.request.user.id,campaignid_id=i).select_related("campaignid")
            for k in campaign_obj59:
               pass

        
            for i in range(len(camp)):
                cop=(camp[i]["coupon_name"])
                amt=(camp[i]["amount"])
                discount=(camp[i]["discount_type"])
                if cop:
                  
                    couponlst=ast.literal_eval(cop)
                else:
                    couponlst=cop
                    
                if amt:
                    
                    amtlst=ast.literal_eval(amt)
                else:
                    amtlst=amt
                    
                if discount:
                    
                    disc_type=ast.literal_eval(discount)
                else:
                    disc_type=discount
                    
                    
                dict1={
                    "campaignid_id":camp[i]["campaignid_id"],
                    "campaign_name": k.campaignid.campaign_name ,
                    "offer":k.campaignid.offer,
                    "product":[{
                    "product_name":camp[i]["product_name"],
                    "coupon_name":couponlst,
                    "discount_type":disc_type,
                    "amount":amtlst,
                    "product_id": camp[i]["product_id"],
                }]
                }
    

                final_lst.append(dict1)
       
        result={}
        for i, record in enumerate(final_lst):
         
            if record["campaignid_id"] in result:
                result[record["campaignid_id"]]["product"].append(record["product"][0])
            else:
               
                result[record["campaignid_id"]] = record
                result[record["campaignid_id"]]["product"] = record["product"]
        val=list(result.values())
        return Response({"data":val},status=status.HTTP_200_OK)  
    
    
    
# API TO GET LIST OF ACTIVE CAMPAIGN    

"""API TO GET LIST OF  ACTIVE CAMPAIGN OF INFLUENCER"""
class  ActiveList(APIView):
    authentication_classes=[TokenAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self,request):
        final_lst1=[] 
        campaign_obj2=VendorCampaign.objects.filter(campaign_status=2,vendor_id=self.request.user.id,campaignid__campaign_exp=1)
        influencerid=campaign_obj2.values_list("influencerid",flat=True)
        camp=Product_information.objects.filter(vendor_id=self.request.user.id).values()
   
                     
        for i in campaign_obj2:
                dict1={
                    "campaignid_id":i.campaignid.id,
                    "campaign_name": i.campaignid.campaign_name,
                    "influencer_name":i.influencerid.id,
                  
                }
            
            
                final_lst1.append(dict1)
          
        return Response({"data":final_lst1},status=status.HTTP_200_OK)  
        
     
 
    


# API TO GET LIST OF DRAFT CAMPAIGN    

"""API TO GET LIST OF DRAFT CAMPAIGN OF INFLUENCER"""
class  DraftList(APIView):
    authentication_classes=[TokenAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self,request):
        lst=[]
        final_lst=[]  
        campaign_obj=Campaign.objects.filter(vendorid_id=self.request.user.id,status=2,draft_status=1,campaign_exp=1)
        if campaign_obj:
            z=(campaign_obj.values("id"))
            for i in z:
               
                lst.append(i['id'])
        set_data=set(lst)
     
        fin_value=list(set_data)
        for i in fin_value:
            camp=Product_information.objects.filter(vendor_id=self.request.user.id,campaignid_id=i).values()
            campaign_obj59=Product_information.objects.filter(vendor_id=self.request.user.id,campaignid_id=i).select_related("campaignid")
            for k in campaign_obj59:
               pass
       
        
            for i in range(len(camp)):
                cop=(camp[i]["coupon_name"])
                amt=(camp[i]["amount"])
             
                if cop:
                  
                    couponlst=ast.literal_eval(cop)
                else:
                    couponlst=cop
                    
                if amt:
                   
                    amtlst=ast.literal_eval(amt)
                else:
                    amtlst=amt
                      
                dict1={
                    "campaignid_id":camp[i]["campaignid_id"],
                    "campaign_name": k.campaignid.campaign_name ,
                    "product":[{
                    "product_name":camp[i]["product_name"],
                    "coupon_name":couponlst,
                    "amount":amtlst,
                    "product_id": camp[i]["product_id"],
                }]
                }
                final_lst.append(dict1)
   
        result={}
        for i, record in enumerate(final_lst):
         
            if record["campaignid_id"] in result:
                result[record["campaignid_id"]]["product"].append(record["product"][0])
            else:
               
                result[record["campaignid_id"]] = record
                result[record["campaignid_id"]]["product"] = record["product"]

        val=list(result.values())
        return Response({"data":val},status=status.HTTP_200_OK)   
     
     
     
    
    
# API TO GET LIST OF MARKETPLACE CAMPAIGN    

"""API GET LIST OF MARKETPLACE CAMPAIGN SHOWN IN MARKETPLACE TAB"""
class   MarketplaceList(APIView):
    authentication_classes=[TokenAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self,request):
        lst=[]
        final_lst=[]
        sliced=""
        
        campaign_obj=Campaign.objects.filter(vendorid_id=self.request.user.id,status=1,draft_status=0,campaign_exp=1)
        if campaign_obj:
            z=(campaign_obj.values("id"))
            for i in z:
              
                lst.append(i['id'])
        set_data=set(lst)
     
        fin_value=set_data
        for i in fin_value:
            camp=Product_information.objects.filter(vendor_id=self.request.user.id,campaignid_id=i).values()
            campaign_obj59=Product_information.objects.filter(vendor_id=self.request.user.id,campaignid_id=i).select_related("campaignid")
            for k in campaign_obj59:
              pass

        
            for i in range(len(camp)):
                cop=(camp[i]["coupon_name"])
                amt=(camp[i]["amount"])
                discount=(camp[i]["discount_type"])
             
                if cop:
                   
                    couponlst=ast.literal_eval(cop)
                else:
                    couponlst=cop
                    
                if amt:
                   
                    amtlst=ast.literal_eval(amt)
                    sliced=amtlst[0].replace("-","")
                   
                else:
                    amtlst=amt
                    
                if discount:
                    
                    disc_type=ast.literal_eval(discount)
                else:
                    disc_type=discount
                    
                    
                dict1={
                    "campaignid_id":camp[i]["campaignid_id"],
                    "campaign_name": k.campaignid.campaign_name ,
                    "product":[{
                    "product_name":camp[i]["product_name"],
                    "coupon_name":couponlst,
                    "amount":[sliced],
                    "discount_type":disc_type,
                    "product_id": camp[i]["product_id"],
                }]
                }
    
                final_lst.append(dict1)
                
        result={}
        for i, record in enumerate(final_lst):
         
            if record["campaignid_id"] in result:
                result[record["campaignid_id"]]["product"].append(record["product"][0])
            else:
               
                result[record["campaignid_id"]] = record
                result[record["campaignid_id"]]["product"] = record["product"]

        val=list(result.values())
        return Response({"data":val},status=status.HTTP_200_OK)   
     
    
    
    
#API TO GET MARKETPLACE DRAFT    

"""API GET LIST OF MARKETPLACE  DRAFT CAMPAIGN SHOWN IN MARKETPLACE TAB"""
class  MarketplaceDraftList(APIView):
    authentication_classes=[TokenAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self,request):
        lst=[]
        markdraft_lst=[]
        
        campaign_obj=Campaign.objects.filter(vendorid_id=self.request.user.id,status=1,draft_status=1,campaign_exp=1)
        if campaign_obj:
            z=(campaign_obj.values("id")) 
            for i in z:
               
                lst.append(i['id'])
        set_data=set(lst)
      
        fin_value=set_data
        for i in fin_value:
            camp=Product_information.objects.filter(vendor_id=self.request.user.id,campaignid_id=i).values()
            campaign_obj59=Product_information.objects.filter(vendor_id=self.request.user.id,campaignid_id=i).select_related("campaignid")
            for k in campaign_obj59:
               pass

        
            for i in range(len(camp)):
                cop=(camp[i]["coupon_name"])
                amt=(camp[i]["amount"])
             
                if cop:
                   
                    couponlst=ast.literal_eval(cop)
                else:
                    couponlst=cop
                    
                if amt:
                  
                    amtlst=ast.literal_eval(amt)
                else:
                    amtlst=amt
                    
                    
                dict1={
                    "campaignid_id":camp[i]["campaignid_id"],
                    "campaign_name": k.campaignid.campaign_name ,
                    "product":[{
                    "product_name":camp[i]["product_name"],
                    "coupon_name":couponlst,
                    "amount":amtlst,
                    "product_id": camp[i]["product_id"],
                }]
                }
    
                markdraft_lst.append(dict1)
        result={}
        for i, record in enumerate(markdraft_lst):
         
            if record["campaignid_id"] in result:
                result[record["campaignid_id"]]["product"].append(record["product"][0])
            else:
               
                result[record["campaignid_id"]] = record
                result[record["campaignid_id"]]["product"] = record["product"]

        val=list(result.values())
        return Response({"data":val},status=status.HTTP_200_OK)   
       
    

#SHOW LIST OF INFLUENCER API

"""API TO  SHOW LIST OF INFLUENCER"""
class InfluencerList(APIView):
    authentication_classes=[TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self,request):
        influ_list = ModashInfluencer.objects.filter(admin_approved=1).values() 
       
        return Response({"data":influ_list},status=status.HTTP_200_OK) 
    
        




#API TO DELETE A CAMPAIGN
"""API TO DELETE CAMPAIGN"""
class DeleteCampaign(APIView): 
    def delete(self, request, id):
            camp_del=Campaign.objects.filter(id=id)
            camp_del.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        
        
# API TO GET Product list
"""API TO GET LIST OF PRODUCT"""
class ProductList(APIView):
    authentication_classes=[TokenAuthentication]
    permission_classes = [IsAuthenticated]      
    def get(self,request):
        acc_tok=access_token(self,request)
        headers= {"X-Shopify-Access-Token": acc_tok[0]}
        url=f"https://{acc_tok[1]}/admin/api/{API_VERSION}/products.json?status=active"
        response = requests.get(url, headers=headers)
        return Response({"success":json.loads(response.text)})    



#API TO GET STORED TOKEN

"""API HELP TO GET TOKEN OF PARTICULAR LOGIN USER"""
class GetToken(APIView):
    def post(self,request):
        shop_name=request.data.get("shop_name")
        
        if not shop_name:
                return Response({'error': 'Missing shop parameter'}, status=status.HTTP_404_NOT_FOUND)
        user=User.objects.filter(shopify_url=shop_name).values_list("id",flat=True)
        if user:
            usr_obj=user[0]
            token_obj=Token.objects.filter(user_id=usr_obj).values_list("key",flat=True)[0]
            return Response({"success":"Token get Successfully","user_token":token_obj},status=status.HTTP_200_OK)
        else:
            return Response({'error': 'user not found'}, status=status.HTTP_404_NOT_FOUND)
        
        
        
        
#API TO GET USER ID     

"""API HELP TO GET DETAIL OF LOGIN VENDOR"""   
class GetUserId(APIView):
    authentication_classes=[TokenAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self,request):
        url_path=request.get_host()+"/static/image/"+ str(self.request.user.image)
        return Response({"user_id":self.request.user.id,"username":self.request.user.username,"email":self.request.user.email,"shop_url":self.request.user.shopify_url,"Instagram_url":self.request.user.instagram_url,"image": str(self.request.user.image),"url":url_path},status=status.HTTP_200_OK)
    

    
#API TO GET CAMPAIGN COUNT

"""API HELP TO KEEP THE COUNT OF CAMPAIGN"""
class CountCampaign(APIView):
    authentication_classes=[TokenAuthentication]
    permission_classes = [IsAuthenticated] 
    
    def get(self,request):
        active=VendorCampaign.objects.filter(vendor_id=self.request.user.id,campaign_status=2,campaignid__campaign_exp=1).count()
        pending=Campaign.objects.filter(vendorid_id=self.request.user.id,campaign_status=0,draft_status=0,campaign_exp=1).count()
        final_pending=pending 
        total=active + pending 
        return Response({"active_campaign":active,"pending_campaign":final_pending,"total":total},status=status.HTTP_200_OK)
    
    

#API TO SEND REQUEST

"""API TO SENT REQUSET TO INFLUENCER CAMPAIGN"""
class RequestSents(APIView):
    authentication_classes=[TokenAuthentication]
    permission_classes = [IsAuthenticated]  
    def post(self,request):
        vendor_status1=User.objects.filter(id=self.request.user.id).values("vendor_status")
        if vendor_status1[0]["vendor_status"] == True:
            serializer=InflCampSerializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                val_lst2=(request.data["product_discount"])
                coup_lst=[]
                cup_lst=[]
                dict1={}
                match_cop=[]
                if val_lst2:
                    for i in  range (len(val_lst2)):
                       
                        for j in val_lst2[i]["coupon_name"]:        
                   
                            match_data=Product_information.objects.filter(coupon_name__contains=j,vendor_id=self.request.user.id).exists()
                            if match_data == True:
                            
                                match_cop.append(j)
                                dict3={str(match_cop):match_data}
                                print(dict3)
                               
                                cup_lst.append(dict3)
                                coup_lst.append(match_data)
                
                            if True in coup_lst:
                                cop=(list(dict3.keys())[0])
                                cop_lst=ast.literal_eval(cop)
                                
                                return Response({"error": cop_lst},status=status.HTTP_410_GONE)

                    req_id=serializer.save(status=2,vendorid_id=self.request.user.id)
                    infll=serializer.data["influencer_name"]
                    val_lst=(request.data["product_discount"])
                    if {} in val_lst:
                        z=val_lst.remove({})
                    else:
                        z=""
                
                    product_details(self,request,val_lst,req_id)
                    val_lst1=(request.data["influencer_name"])
                
                    data_list=val_lst1.split(",")
                
                    int_list = [int(num) for num in data_list]
                
                    influencer_details(self,request,int_list,req_id)
                    return Response({"success":"Campaign create successfully","product_details":serializer.data},status=status.HTTP_200_OK)
                   
                                    
                else:
                    
                    req_id=serializer.save(status=2,vendorid_id=self.request.user.id)
                    arg=request.data["product_name"]
                
                    if len(arg)>0:
                       
                        arg_id=request.data["product"]
                        
                        product_name(self,request,req_id,arg,arg_id)
                            
                        val_lst1=(request.data["influencer_name"])
                        data_list=val_lst1.split(",")
                        int_list = [int(num) for num in data_list]
                        
                        influencer_details(self,request,int_list,req_id)

                    
                    else:
                        val_lst1=(request.data["influencer_name"])

                        data_list=val_lst1.split(",")
                        int_list = [int(num) for num in data_list]
                    
                        influencer_details(self,request,int_list,req_id)
                            
                        product=Product_information()
                        product.vendor_id=self.request.user.id
                        product.campaignid_id=req_id.id
                        product.save()
                
                        return Response({"success":"Campaign create successfully","product_details":serializer.data},status=status.HTTP_200_OK)
                    return Response({"success":"Campaign create successfully","product_details":serializer.data},status=status.HTTP_200_OK)        
        else:
            return Response({"error":"Admin Deactive your shop"},status=status.HTTP_401_UNAUTHORIZED)
        return Response({"error":"Campaign not created"},status=status.HTTP_400_BAD_REQUEST)
    
    
    
#API TO GET SINGLE CAMPAIGN

"""API HELP IN GETTING DETAILS OF A SINGLE CAMPAIGN"""
class GetCampaign(APIView):
    authentication_classes=[TokenAuthentication]
    permission_classes = [IsAuthenticated]  
    def get(self,request,id):
        value_lst=[]
        try:
            camp=Product_information.objects.filter(vendor_id=self.request.user.id,campaignid_id=id).values()
            campaign_obj=Product_information.objects.filter(vendor_id=self.request.user.id,campaignid_id=id).select_related("campaignid")
          

        except Campaign.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        for k in campaign_obj:
            pass
        for i in range(len(camp)):
            cop=(camp[i]["coupon_name"])
            amt=(camp[i]["amount"])
            
            if cop:
                
                couponlst=ast.literal_eval(cop)
            else:
                couponlst=cop
                
            if amt:
    
                amtlst=ast.literal_eval(amt)
            else:
                amtlst=amt

           
          
            if k.campaignid.influencer_name:
                dict1={
                    "campaignid_id":camp[i]["campaignid_id"],
                    "product_name":camp[i]["product_name"],
                    "product_id": camp[i]["product_id"],
                    "campaign_name": k.campaignid.campaign_name ,
                    "influencer_visit": k.campaignid.influencer_visit ,
                    "influencer_name": ast.literal_eval(k.campaignid.influencer_name ),
                    "offer": k.campaignid.offer ,
                    "date": k.campaignid.date ,
                    "end_data":k.campaignid.end_date,
                    "description": k.campaignid.description,
                    "influencer_fee": k.campaignid.influencer_fee,
                    "campaign_status":k.campaignid.campaign_status,
                    "draft_status":k.campaignid.draft_status,
                    "product":[{
                        "product_name":camp[i]["product_name"],
                        "coupon_name":couponlst,
                        "amount":amtlst,
                        "product_id": camp[i]["product_id"],
                        "discout_type":camp[i]["discount_type"]
                    }]
                }

                value_lst.append(dict1)
            else:
                dict1={
                    "campaignid_id":camp[i]["campaignid_id"],
                    "product_name":camp[i]["product_name"],
                    "product_id": camp[i]["product_id"],
                    "campaign_name": k.campaignid.campaign_name ,
                    "influencer_visit": k.campaignid.influencer_visit ,
                    "offer": k.campaignid.offer ,
                    "date": k.campaignid.date ,
                    "end_data":k.campaignid.end_date,
                    "description": k.campaignid.description,
                    "influencer_fee": k.campaignid.influencer_fee,
                    "campaign_status":k.campaignid.campaign_status,
                    "draft_status":k.campaignid.draft_status,
                    "product":[{
                        "product_name":camp[i]["product_name"],
                        "coupon_name":couponlst,
                        "amount":amtlst,
                        "product_id": camp[i]["product_id"],
                        "discout_type":camp[i]["discount_type"]
                    }]
                }

                value_lst.append(dict1)
                
                            
        result = {}
        for i, record in enumerate(value_lst):
         
            if record["campaign_name"] in result:
                result[record["campaign_name"]]["product"].append(record["product"][0])
            else:
               
                result[record["campaign_name"]] = record
                result[record["campaign_name"]]["product"] = record["product"]

        val=list(result.values())
        return Response({"data":val},status=status.HTTP_200_OK)
    
    

# UPDATE PROFILE OF VENDOR
"""API HELP IN UPDATING THE PROFILE OF VENDOR"""
class ProfileUpdate(APIView):
    authentication_classes=[TokenAuthentication]
    permission_classes = [IsAuthenticated]
    def put(self,request,id):
        try:
            influencer = User.objects.get(id = id,user_type=3)
        except User.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer=UpdateProfileSerializer(influencer,data=request.data)
        if serializer.is_valid():
            serializer.save(user_type=3)
            get_value=User.objects.filter(id=self.request.user.id).values("image")
            image_val=get_value[0]["image"]
            url_path=request.get_host()+"/static/image/"+ str(image_val)
            profile_val={
                "data":serializer.data,
                "url":url_path
            }
            return Response(profile_val,status=status.HTTP_200_OK)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    
    
    
#INSTAGRAM FOLLOWER API

"""API INTEGRATE MODASH API TO GET INFLUENCER DETAILS"""
class InstagramFollower(APIView):
    def get(self,request):
        user_handler=request.GET.get("user")
        user_handler1 = user_handler.split(',')
        data=[]
       
        headers={"Authorization": "Bearer tZkAyMxbFyyztGzWjGM6PVre8MPe0lBT"}
        for i in user_handler1:
            influencer_obj = ModashInfluencer()
            base_url=f"https://api.modash.io/v1/instagram/profile/@{i}/report"
            response = requests.get(base_url, headers=headers)
           
            influencer_obj.username=response.json()['profile']['profile']['username']
            influencer_obj.fullname=response.json()['profile']['profile']['fullname']
            influencer_obj.isverified=response.json()['profile']['isVerified']

            influencer_obj.follower=response.json()['profile']['profile']['followers']
            influencer_obj.image =response.json()['profile']['profile']['picture']
            influencer_obj.engagements = response.json()['profile']['profile']['engagements']
            engagemente = response.json()['profile']['profile']['engagementRate']
            influencer_obj.engagement_rate = round(engagemente,2)

            
            influencer_obj.save()
    
        return Response({"success":response.json()},status=status.HTTP_200_OK)



#API TO GET PRODUCT URL
"""API HELP TO GET SELECTED PRODUCT URL AND THERE COUPON"""
class ProductUrl(APIView):
    authentication_classes=[TokenAuthentication]
    permission_classes = [IsAuthenticated] 
    def post(self,request):
        product_name=request.data.get('products')
        
    
        lst=[int(x) for x in product_name.split(",")]
      
        acc_tok=access_token(self,request)

        headers= {"X-Shopify-Access-Token":acc_tok[0]}
        
        response = requests.get(f"https://{acc_tok[1]}/admin/api/{API_VERSION}/products.json/?ids={product_name}", headers=headers)
        price_rule = requests.get(f'https://{SHOPIFY_API_KEY}:{SHOPIFY_API_SECRET}@{acc_tok[1]}/admin/api/{API_VERSION}/price_rules.json/?status=active',headers=headers)   

        pro_len=len(response.json()["products"])
       
        handle_lst=[]
        title_list=[] 
        dataList=[]
        productMapDict = {}
        product_dict={}
        new_list=[]
        prd_ids=[]
       
        
        for  i in range(pro_len):
            
            prd_handle=json.loads(response.text)['products'][i]["handle"]
            prd_title=json.loads(response.text)['products'][i]["title"]
            prd_id=json.loads(response.text)['products'][i]["id"]
            title_list.append(prd_title)
            prd_ids.append(prd_id)
            
            handle_lst.append(f"https://{acc_tok[1]}/products/"+str(prd_handle))
            productMapDict = { k:v for (k,v) in zip(prd_ids, title_list)} 

            price_rules_data = price_rule.json()['price_rules']
            pric_len=len(price_rules_data)
            
        for i in range(pric_len):
      

            price_rules_entitle = price_rule.json()['price_rules'][i]["entitled_product_ids"]
            if price_rules_entitle == []:
                 dataList.append({})     
            for z in  price_rules_entitle:
         
                if z in  lst:
                    price_rules_id=price_rule.json()['price_rules'][i]["id"]
                    get_influencer=influencer_coupon.objects.filter(vendor_id=self.request.user.id,coupon_id=price_rules_id).values("influencer_id")
                    influ_id=get_influencer
                    
                    if influ_id:
                    
                        price_rules_codes=price_rule.json()['price_rules'][i]["title"]
                        price_rules_ids=price_rule.json()['price_rules'][i]["id"]
                        price_rule_value=price_rule.json()['price_rules'][i]['value']
                        price_rule_value_type=price_rule.json()['price_rules'][i]['value_type']
                        product_dict={
                            "product_name":productMapDict[z],
                            "product_id":z,   
                            "coupon_name": price_rules_codes,
                            "coupon_id":price_rules_ids,
                            "amount":price_rule_value,   
                            "discout_type":price_rule_value_type,
                            "influencer_id":influ_id[0]["influencer_id"]
                        }    
                        dataList.append(product_dict)
        
     
       
        for product in dataList:
           
            if product:
                product_id = product["product_id"]
                
                if product_id in product_dict:
                    product_dict[product_id]["coupon_name"].append(product["coupon_name"])
                    product_dict[product_id]["coupon_id"].append(product["coupon_id"])
                    product_dict[product_id]["amount"].append(product["amount"])
                    product_dict[product_id]["discout_type"].append(product["discout_type"])
                    product_dict[product_id]["influencer_id"].append(product["influencer_id"])
                
                else:
             
                    product_dict[product_id] = {
                        "product_name": product["product_name"],
                        "product_id":product["product_id"],
                        "coupon_name": [product["coupon_name"]],
                        "coupon_id": [product["coupon_id"]],
                        "amount": [product["amount"]],
                        "discout_type":[product["discout_type"]],
                        "influencer_id":[product["influencer_id"]]
                        }
                             
        for i in lst:
        
            if i in product_dict:
                new_list.append(product_dict[i])
            else:
                

                new_list.append({"product_name": productMapDict[i],
                        "product_id":i,
                        "coupon_name":"",
                        "coupon_id":"",
                        "amount": "",
                        "discout_type":"",
                        "influencer_id":"",
                            })
            
        return Response({'product_details':new_list,"product_url":handle_lst,"title_list":title_list},status=status.HTTP_200_OK)       



#Accept by Vendor API
"""API TO ACCEPT CAMPAIGN REQUEST FROM INFLUENCER"""
class VendorAccept(APIView):
    authentication_classes=[TokenAuthentication]
    permission_classes = [IsAuthenticated]    
    def post(self,request,id,pk):
        try:
           
            cam_dec=VendorCampaign.objects.filter(campaignid_id=id,influencerid_id=pk,vendor_id=self.request.user.id).update(campaign_status=2)
            cam_dec=Notification.objects.filter(campaignid_id=id,influencerid_id=pk,vendor_id=self.request.user.id).update(send_notification=3)
            return Response({"message":"Campaign Accept"},status=status.HTTP_200_OK)
        except:
           
            return Response(status=status.HTTP_400_BAD_REQUEST)
        

#Decline by Vendor API
"""API TO DECLINE CAMPAIGN REQUEST FROM INFLUENCER"""       
class DeclineVendor(APIView):
    authentication_classes=[TokenAuthentication]
    permission_classes = [IsAuthenticated]    
    def post(self,request,id,pk):
        try:
        
            cam_dec=VendorCampaign.objects.filter(campaignid_id=id,influencerid_id=pk,vendor_id=self.request.user.id).update(campaign_status=4)
            cam_dec=Notification.objects.filter(campaignid_id=id,influencerid_id=pk,vendor_id=self.request.user.id).update(send_notification=5)
           
            return Response({"message":"Campaign Decline by Vendor"},status=status.HTTP_200_OK)
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        
        
        
        
#VENDOR APPROVAL LIST
"""API TO SHOW VENDOR APPROVAL LIST"""        
class VendorApprovalList(APIView):
    authentication_classes=[TokenAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self,request):
          
        influ_get=VendorCampaign.objects.exclude(Q(campaign_status=0)|Q(campaign_status=2),vendor_id=self.request.user.id).values_list("influencerid_id",flat=True)
     
        final_lst1=[] 
      
        campaign_obj2=VendorCampaign.objects.filter(campaign_status=1,vendor_id=self.request.user.id,campaignid__campaign_exp=1,campaignid__status=2)
      
        z=campaign_obj2.values_list("campaignid__id","campaignid__campaign_name")
        influencerid=campaign_obj2.values_list("influencerid",flat=True)
        
        for i in campaign_obj2:
           
            dict1={
                "campaignid_id":i.campaignid.id,
                "campaign_name": i.campaignid.campaign_name,
                "influencer_name":i.influencerid.id,
            }
            
            
            
            final_lst1.append(dict1)         
            
            
             
        return Response({"data":final_lst1},status=status.HTTP_200_OK)  
 
 
 
#VENDOR DECLINE LIST
"""API TO SHOW VENDOR DECLINE LIST"""  
class VendorDeclineList(APIView):
    authentication_classes=[TokenAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self,request):
               
        final_lst1=[] 
      
        campaign_obj2=VendorCampaign.objects.filter(campaign_status=4,vendor_id=self.request.user.id,campaignid__campaign_exp=1)
      
        z=campaign_obj2.values_list("campaignid__id","campaignid__campaign_name")
        influencerid=campaign_obj2.values_list("influencerid",flat=True)
        
        for i in campaign_obj2:
           
            dict1={
                "campaignid_id":i.campaignid.id,
                "campaign_name": i.campaignid.campaign_name,
                "influencer_name":i.influencerid.id,
            }
            
    
        
            final_lst1.append(dict1)
            
        return Response({"data":final_lst1},status=status.HTTP_200_OK)  
    


#INFLUENCER NOTIFICATION
"""API TO SHOW NOTIFICATION TO INFLUENCER"""
class InfluencerNotification(APIView):
    authentication_classes=[TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self,request):
        
        ExpiryCoupondelete(self,request)
        notification_obj=Notification.objects.filter(vendor_id=self.request.user.id,send_notification__in=[2,4])
       
        notify_list=[]
        for i in notification_obj:
            if i.send_notification==2:
                
                dict={
                    "message": i.influencerid.username + " accepted your campaign -"  + ":" +  i.campaignid.campaign_name
                }
                notify_list.append(dict)
            else:
                dict={
                    "message": i.influencerid.username + " declined your campaign -"  + ":" +  i.campaignid.campaign_name
                }
            
                notify_list.append(dict)
                
        return Response({"data":notify_list},status=status.HTTP_200_OK)  
    
    
    
#GET LIST OF NOTIFICATION API
"""API TO CHANGE NOTIFICATION STATUS"""
class ChangeNotifinflStatus(APIView):
    authentication_classes=[TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self,request):
        notification_obj=Notification.objects.filter(vendor_id=self.request.user.id,send_notification__in=[2,4]).update(send_notification=0)


          
        dict={
            "message":  "Notification status updated"
        }
    
        
        return Response(dict,status=status.HTTP_200_OK)  
    
    
#ANALYTIC API
"""API TO SHOW TOTAL SALRS AND ORDERS"""
class Analytics(APIView):
    authentication_classes=[TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self,request):
        acc_tok=access_token(self,request)
        headers= {"X-Shopify-Access-Token":acc_tok[0]}
        url = f"https://{acc_tok[1]}/admin/api/2022-10/orders.json?status=active"

        response = requests.get(url, headers=headers)
        if response.status_code == 200:

            order_count = {str(i): 0 for i in range(1, 13)}
            orders = response.json().get("orders", [])
        
            for order in orders:
                created_at = order.get("created_at")
                month = int(created_at.split("-")[1])
            
                order_count[str(month)] += 1
            data = []
            for month in range(1, 13):
                month_name = calendar.month_name[month]
            
                count = order_count[str(month)]
                data.append({"month": month_name, "count": count})
        
        
        
            order_list=list(order_count.values())
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
            sales=list(sales_report.values()) 
   
                  
            return Response({'sales_data': sales,"order":order_list},status=status.HTTP_200_OK)
        else:
            return Response({'error':response.text},status=status.HTTP_400_BAD_REQUEST)
        
        
        
class SalesRecord(APIView):
    authentication_classes=[TokenAuthentication]
    permission_classes = [IsAuthenticated]
        
    def get(self,request):
        acc_tok=access_token(self,request)
        store_url = acc_tok[1]
        api_token = acc_tok[0]

        end_date = datetime.now().date()
        start_date_7_days_ago = end_date - timedelta(days=7)
        start_date_30_days_ago = end_date - timedelta(days=30)
        start_date_year_ago = end_date.replace(year=end_date.year-1, month=1, day=1)


        start_date_7_days_ago_str = start_date_7_days_ago.isoformat()
        start_date_30_days_ago_str = start_date_30_days_ago.isoformat()
        start_date_year_ago_str = start_date_year_ago.isoformat()
        end_date_str = end_date.isoformat()

        
        url = f"https://{store_url}/admin/api/2022-10/orders.json?status=active&created_at_min={start_date_year_ago_str}&created_at_max={end_date_str}"


        headers = {
            'X-Shopify-Access-Token': api_token
        }
        response = requests.get(url, headers=headers)

        
        if response.status_code == 200:
            data = response.json()
          

            sales_7_days = 0
            sales_30_days = 0
            sales_year = 0

            for order in data['orders']:
                created_at = datetime.strptime(order['created_at'], "%Y-%m-%dT%H:%M:%S%z").date()
                if start_date_7_days_ago <= created_at <= end_date:
                    sales_7_days += float(order['total_price'])
                if start_date_30_days_ago <= created_at <= end_date:
                    sales_30_days += float(order['total_price'])
                if start_date_year_ago <= created_at <= end_date:
                    sales_year += float(order['total_price'])

            return Response({"seven_days":sales_7_days,"thirty_days":sales_30_days,"year":sales_year})
        else:
            return Response({"error":response.text})






#SHOW CAMPAIGN SALES
"""API TO SHOW CAMPAIGN SALES"""    
class CampaignSales(APIView):
    authentication_classes=[TokenAuthentication]
    permission_classes = [IsAuthenticated] 
    def get(self,request): 
        acc_tok=access_token(self,request)
        store_url = acc_tok[1]
        api_token = acc_tok[0]
        headers= {"X-Shopify-Access-Token": api_token}   
        url = f'https://{store_url}/admin/api/2022-10/orders.json?status=active'
        response = requests.get(url,headers=headers)
        sales_by_coupon = {}
    
        if response.status_code == 200:
            orders1 = response.json().get('orders', [])
            
            
            for order in orders1:
                line_items = order.get('discount_codes', [])
                
                
                total_price = order.get('total_price')
                    
                if line_items:
                    coupon_code = line_items[0].get('code')
                    
                    
                
                    if coupon_code in sales_by_coupon:
                        sales_by_coupon[coupon_code] += float(total_price)
                        
                    else:
                        
                        sales_by_coupon[coupon_code] = float(total_price)
                        
            sale=list(sales_by_coupon.keys())
            coup_dict={} 
            for  i in sale:    
                check=Product_information.objects.filter(coupon_name__contains=i,vendor_id=self.request.user.id).values("campaignid","coupon_name")
                
                for z in check:
                    if "coupon_name" in z:
                        list_value = eval(z["coupon_name"])
            
                        campaign_id = z["campaignid"]
                        if campaign_id in coup_dict:
                            coup_dict[campaign_id].extend(list_value)
                        else:
                            coup_dict[campaign_id] = list_value

            dict_lst = [coup_dict]
            
            sale_by_id = {}

            for campaign_id, coupon_names in coup_dict.items():
                sale = 0.0
                
                for coupon_name in set(coupon_names):
                    if coupon_name in sales_by_coupon:
                        sale += sales_by_coupon[coupon_name]
                sale_by_id[campaign_id] = sale

                campaign_name = Campaign.objects.filter(id=campaign_id).values_list('campaign_name', flat=True).first() 
                
                sale_by_id[campaign_id] = [sale, campaign_name]
                
                filtered_data = {key: value for key, value in sale_by_id.items() if value[0] > 0}

                print(filtered_data)
            
            return Response({"campaign_sales":filtered_data})
        else:
            return Response({"Message":"unable to fetch data"})

            
       
        
        
        
class VendorStripe(APIView):
    authentication_classes=[TokenAuthentication]
    permission_classes = [IsAuthenticated] 
    
    def post(self,request):
        
        check=VendorStripeDetails.objects.filter(vendor=self.request.user.id).exists()
        if check == True:
            return Response({"error":"Account already exists"},status=status.HTTP_400_BAD_REQUEST)
        seri_obj=VendorStripeSerializer(data=request.data)
        if seri_obj.is_valid(raise_exception=True):
            seri_obj.save(vendor_id=self.request.user.id)
            return Response({"success":" Stripe Details Saved Successfully"},status=status.HTTP_201_CREATED)
        return Response({"error":seri_obj.error_messages},status=status.HTTP_404_NOT_FOUND)
        
    
    
# class ShowStripe(APIView):
#     authentication_classes=[TokenAuthentication]
#     permission_classes = [IsAuthenticated] 
    
#     def get(self,request):
#         val=VendorStripeDetails.objects.filter(vendor=self.request.user.id).values("publishable_key","secret_key")
#         if val:
#             publish_key=val[0][]
    
    
    

class Balance(APIView):
    authentication_classes=[TokenAuthentication]
    permission_classes = [IsAuthenticated] 
    
    def get(self,request):
        api_key=VendorStripeDetails.objects.get(vendor_id=self.request.user.id)
        stripe.api_key =api_key.secret_key
        balance=stripe.Balance.retrieve()
        return Response({"balance":balance},status=status.HTTP_200_OK)
    
    
    
    
class InfluencerStripeDetail(APIView):
    authentication_classes=[TokenAuthentication]
    permission_classes = [IsAuthenticated] 
    
    def get(self,request):
        api_key=StripeDetails.objects.all().values("secret_key","influencer")
      
        for i in api_key:
            stripe.api_key=i["secret_key"]
            account = stripe.Account.retrieve()
            
        return Response({"details":api_key},status=status.HTTP_200_OK)
    

    
    
class TranferMoney(APIView):
    authentication_classes=[TokenAuthentication]
    permission_classes = [IsAuthenticated] 
    
    def post(self,request):
        account=request.data.get("account_id")
        
        influencer=request.data.get("influencer")
    
        amount=request.data.get("amount")

        campaignids=request.data.get("camp_id")
       
        salesdone=request.data.get("sales")
       
        get_account=StripeDetails.objects.filter(vendor_id=self.request.user.id).values("account_id","influencer_id")
        
        
        stripe.api_key = settings.STRIPE_API_KEY  
        
        try:
            payment_method=stripe.PaymentMethod.create(
            type="card",
            card={
               "token": "tok_visa", 
               },
            
            )
        except stripe.error.StripeError as e:
            return Response({"error":e.user_message},status=status.HTTP_400_BAD_REQUEST)
            
        try:
            intent = stripe.PaymentIntent.create(
                amount=int(amount),
                currency='usd',
                payment_method_types=['card'],
                payment_method=payment_method["id"],
            
            )
            
        except stripe.error.StripeError as e:
            return Response({"error":e.user_message},status=status.HTTP_400_BAD_REQUEST)
        
        
        try:    
            confim=stripe.PaymentIntent.confirm(
            intent["id"],
            payment_method="pm_card_visa",
            )
        except stripe.error.StripeError as e:
            return Response({"error":e.user_message},status=status.HTTP_400_BAD_REQUEST)
            
            
    

        if confim.status == 'succeeded':
            try:
                transfer1 = stripe.Transfer.create(
                    amount=int(amount),
                    currency='usd',
                    destination=account,
                    transfer_group=intent.id,
                )     
                
                exists_transfer=transferdetails.objects.filter(vendor=self.request.user.id,influencer=influencer,campaign=campaignids).exists()   
                if exists_transfer == False:
                    transfer_obj=transferdetails()
                    transfer_obj.vendor_id=self.request.user.id
                    transfer_obj.influencer_id=influencer
                    transfer_obj.transferid=transfer1["id"]
                    transfer_obj.amount=transfer1["amount"]
                    transfer_obj.destination=transfer1["destination"]
                    transfer_obj.campaign_id=campaignids
                    transfer_obj.save()

                    pay_value=PaymentDetails.objects.filter(campaign=campaignids,influencer=influencer,vendor=self.request.user.id).values("sales","amount")
                    remaining_amount=amount-transfer1["amount"] 
                   
            
                    
                    PaymentDetails.objects.filter(campaign=campaignids,influencer=influencer,vendor=self.request.user.id).update(amountpaid=transfer1["amount"],salespaid=salesdone,amount=remaining_amount)
                else:  
                   
                    amount_Paid=transferdetails.objects.filter(vendor=self.request.user.id,influencer=influencer,campaign=campaignids).values_list("amount",flat=True)
                    PaymentDetails.objects.filter(campaign=campaignids,influencer=influencer,vendor=self.request.user.id).update(amountpaid=amount_Paid[0],salespaid=salesdone)
  
                    new_amount=int(amount_Paid[0])+int(transfer1["amount"])
                    print(new_amount)
                    amount_Paid=transferdetails.objects.filter(vendor=self.request.user.id,influencer=influencer,campaign=campaignids).update(amount=new_amount)

          
            except stripe.error.StripeError as e:
                return Response({"error":e.user_message},status=status.HTTP_400_BAD_REQUEST)
            try:
                payout=stripe.Payout.create(
                    amount=int(amount),
                    currency="usd",
                    stripe_account=account,
                
                    )
                
               
            except stripe.error.StripeError as e:
                return Response({"error":e.user_message},status=status.HTTP_400_BAD_REQUEST)
            
            return Response({"data":transfer1,"message":"Money transfer Successfully"},status=status.HTTP_200_OK)
        return Response({"error":"not valid"},status=status.HTTP_400_BAD_REQUEST)
    
    
    
    
    
#INFLUECER SALES
"""API TO SHOW TOTAL INFLUENCER SALES"""
class InfluencerCampSale(APIView):
    authentication_classes=[TokenAuthentication]
    permission_classes = [IsAuthenticated] 
    
    
    def get(self,request): 
        acc_tok=access_token(self,request)
        store_url = acc_tok[1]
      
        api_token = acc_tok[0]
        
        headers= {"X-Shopify-Access-Token": api_token}  
        url = f'https://{store_url}/admin/api/2022-10/orders.json?status=active'
        response = requests.get(url,headers=headers)
           
        sales_by_coupon = {}

        if response.status_code == 200:
            orders_details = response.json().get('orders', [])
            for order in orders_details:
                line_items = order.get('discount_codes', [])
                
                
                total_price = order.get('total_price')
                    
                if line_items:
                    coupon_code = line_items[0].get('code')
                    
                    if coupon_code in sales_by_coupon:
                        sales_by_coupon[coupon_code] += float(total_price)
                        
                    else:
                        sales_by_coupon[coupon_code] = float(total_price)
            
            sale=list(sales_by_coupon.keys())
            amount=list(sales_by_coupon.values())
            
          

            campaign_ids =  Campaign.objects.filter(vendorid=self.request.user.id).values_list('id', flat=True) 
          
            influencer_sales_for_campaign = {}
            for coupon_name, sales in sales_by_coupon.items():
                print("coupon_name",coupon_name)
                influencer_ids = influencer_coupon.objects.filter(coupon_name=coupon_name,vendor=self.request.user.id).values("influencer_id", "coupon_name")
               
                for influencer in influencer_ids:
                    influencer_id = influencer["influencer_id"]
                    
                    modash_data = Campaign.objects.filter(influencer_name__contains=influencer_id, id__in=campaign_ids,vendorid=self.request.user.id).values_list("id",flat=True)
                    pro_data=Product_information.objects.filter(coupon_name__contains=coupon_name,campaignid__in=modash_data,vendor=self.request.user.id).values("campaignid")
                    data=pro_data.first()["campaignid"]
                    
                    if influencer_id in influencer_sales_for_campaign:
                            influencer_sales_for_campaign[influencer_id].append({"campaign_id": data, "sales": sales})
                    else:
                        influencer_sales_for_campaign[influencer_id] = [{"campaign_id": data, "sales": sales}]
                    # for modash_entry in pro_data:
                    #     campaign_id = modash_entry["campaignid"]
                    #     if influencer_id in influencer_sales_for_campaign:
                    #         influencer_sales_for_campaign[influencer_id].append({"campaign_id": campaign_id, "sales": sales})
                    #     else:
                    #         influencer_sales_for_campaign[influencer_id] = [{"campaign_id": campaign_id, "sales": sales}]

                              
            lst_data=[]
            
            for key in influencer_sales_for_campaign: 
                for i in influencer_sales_for_campaign[key]:
                  
                    str_detail=StripeDetails.objects.filter(influencer=key,vendor=self.request.user.id).values("account_id")
               
                    check=Campaign.objects.filter(id=i["campaign_id"]).values("influencer_fee","offer","campaign_name")

                    if str_detail:
                        if  check[0]["offer"] == "percentage":
                            amount=i["sales"] * check[0]["influencer_fee"] /100
                            amount=round(amount,2)
                            
                        else:
                            amount=check[0]["influencer_fee"] 
                        
                        
                        infl_dict={
                            "campaing_id":check[0]["campaign_name"],
                            "sales":round(i["sales"],2),
                            "account":str_detail[0]["account_id"],
                            "influencer":key,
                            "influener_fee":check[0]["influencer_fee"],
                            "offer":check[0]["offer"],
                            "amount":amount,  
                            "campaign_detail":i["campaign_id"]        
                        }

                        lst_data.append(infl_dict)  
                    
                    else:
                        
                        if  check[0]["offer"] == "percentage":
                            amount=int(i["sales"]) * check[0]["influencer_fee"] / 100
                            amount=round(amount,2)
                        
                        else:
                            amount=check[0]["influencer_fee"] 
                        
                            
                        infl_dict={
                            "campaing_id":check[0]["campaign_name"],
                            "sales":round(i["sales"],2),
                            "account":"",
                            "influencer":key,
                            "influener_fee":check[0]["influencer_fee"],
                            "offer":check[0]["offer"],
                            "amount":amount,  
                            "campaign_detail":i["campaign_id"]        
                        }
                        
                        lst_data.append(infl_dict)  
 
            campaign_totals = {}
            
        
            for entry in lst_data:
                campaign_id = entry["campaing_id"]
                influencer = entry["influencer"]
                sales = entry["sales"]
                amount = entry["amount"]

                key = (campaign_id, influencer)
                if key in campaign_totals:
                    campaign_totals[key]["sales"] += sales
                    campaign_totals[key]["amount"] += amount
                else:
                    campaign_totals[key] = entry

            combined_sales_list = [value for value in campaign_totals.values()]
            data_max=[]
            for sales_entry in combined_sales_list:
                
                data_max.append(sales_entry)   
          
            print(data_max)
            
            empty=PaymentDetails.objects.all().exists()
           
            if empty == True:
                for i in data_max:
                    
                    emp_check=PaymentDetails.objects.filter(vendor=self.request.user.id,campaign_id=i["campaign_detail"]).exists()
                    print("emp_checkkkkk",emp_check)
                    if emp_check == False:
                        PaymentDetails.objects.create(sales=i["sales"],influencerfee=i["influener_fee"],offer=i["offer"],amount=i["amount"],influencer_id=i["influencer"],vendor_id=self.request.user.id,campaign_id=i["campaign_detail"],account_id=i["account"])
                        
                    else:
                        account_check=PaymentDetails.objects.filter(vendor=self.request.user.id,campaign_id=i["campaign_detail"]).values_list("account_id",flat=True)
                        if account_check[0]== "":                      
                            amount_transfered=PaymentDetails.objects.filter(vendor=self.request.user.id,campaign_id=i["campaign_detail"]).update(account_id=i["account"])

                        amount_transfered=transferdetails.objects.filter(vendor=self.request.user.id,influencer=i["influencer"],campaign=i["campaign_detail"]).values_list("amount",flat=True)
                        
                   
                        amount_deduct=i["amount"]
                        if amount_transfered:
                            amount_deduct=int(i["amount"]-int(amount_transfered[0]))
                        print(amount_deduct)
                        
                        PaymentDetails.objects.filter(vendor=self.request.user.id,campaign_id=i["campaign_detail"]).update(amount=amount_deduct,sales=i["sales"])

                        # print(i["influencer"])
                        # print(i["campaign_detail"])
                        # tranfer_money=transferdetails.objects.filter(vendor=self.request.user.id,influencer=i["influencer"],campaign=i["campaign_detail"]).values("amount")
                        # print("transfer",tranfer_money)
                        # print("amount",i["amount"])
                        # PaymentDetails.objects.filter(vendor=self.request.user.id,campaign_id=i["campaign_detail"]).update(sales=i["sales"],influencerfee=i["influener_fee"],offer=i["offer"],amount=i["amount"],influencer_id=i["influencer"],vendor_id=self.request.user.id,campaign_id=i["campaign_detail"],account_id=i["account"])

                        
                # if emp_check:
                #     for i in data_max:
                #         PaymentDetails.objects.filter(vendor=self.request.user.id,campaign=i["campaign_detail"],influencer=i["influencer"]).update(sales=i["sales"],influencerfee=i["influener_fee"],offer=i["offer"],amount=i["amount"])
                    
                # for data in data_max:
                #     emp_check=PaymentDetails.objects.filter(influencer=data["influencer"],campaign=data["campaign_detail"])
                #     print("emp_checkkkkkkkkkkkkk",emp_check)
                #     if emp_check:
                #         for i in data_max:
                #             PaymentDetails.objects.filter(vendor=self.request.user.id,campaign=i["campaign_detail"],influencer=i["influencer"]).update(sales=i["sales"],influencerfee=i["influener_fee"],offer=i["offer"],amount=i["amount"])     
            else:     
         
                for i in data_max:
                    details_obj=PaymentDetails()
                    details_obj.amount=i["amount"]
                    details_obj.influencer_id=i["influencer"]
                    details_obj.vendor_id=self.request.user.id
                    details_obj.sales=i["sales"]
                    details_obj.influencerfee=i["influener_fee"]
                    details_obj.offer=i["offer"]
                    details_obj.campaign_id=i["campaign_detail"]
                    details_obj.account_id=i["account"]
                    details_obj.save()
                
            upd_data=PaymentDetails.objects.filter(vendor=self.request.user.id,influencer__isnull=False)
        
            
            
            upd_lst=[]
            for pay in upd_data:
                upd_dict={
                    "campaing_id":pay.campaign.campaign_name,
                    "sales":round(pay.sales,2),
                    "account":pay.account_id,
                    "influencer":pay.influencer.id,
                    "influener_fee":pay.influencerfee,
                    "offer":pay.offer,
                    "amount":pay.amount,  
                    "amount_paid":pay.amountpaid,
                    "campaign_detail":pay.campaign.id      
                    
                }
                upd_lst.append(upd_dict)
                
            return Response({"sale_details":upd_lst},status=status.HTTP_200_OK)
        return Response({"error":response.json()},status=status.HTTP_400_BAD_REQUEST)
        


#INFLUENCER EXPIRED LIST
"""API TO SHOW INFLUENCER EXPIRED CAMPAIGN LIST""" 
class CampaignExpList(APIView):
    authentication_classes=[TokenAuthentication]
    permission_classes = [IsAuthenticated] 

    def get(self,request):
        lst=[]
        final_lst=[]  
        campaign_obj=Campaign.objects.filter(vendorid_id=self.request.user.id,status=2,campaign_exp=0)
        if campaign_obj:
            z=(campaign_obj.values("id"))
            for i in z:
               
                lst.append(i['id'])
        set_data=set(lst)
     
        fin_value=list(set_data)
        for i in fin_value:
            camp=Product_information.objects.filter(vendor_id=self.request.user.id,campaignid_id=i).values()
            campaign_obj59=Product_information.objects.filter(vendor_id=self.request.user.id,campaignid_id=i).select_related("campaignid")
            for k in campaign_obj59:
               pass
       
        
            for i in range(len(camp)):
                cop=(camp[i]["coupon_name"])
                amt=(camp[i]["amount"])
             
                if cop:
                  
                    couponlst=ast.literal_eval(cop)
                else:
                    couponlst=cop
                    
                if amt:
                   
                    amtlst=ast.literal_eval(amt)
                else:
                    amtlst=amt
                      
                dict1={
                    "campaignid_id":camp[i]["campaignid_id"],
                    "campaign_name": k.campaignid.campaign_name ,
                    "product":[{
                    "product_name":camp[i]["product_name"],
                    "coupon_name":couponlst,
                    "amount":amtlst,
                    "product_id": camp[i]["product_id"],
                }]
                }
                final_lst.append(dict1)
   
        result={}
        for i, record in enumerate(final_lst):
         
            if record["campaignid_id"] in result:
                result[record["campaignid_id"]]["product"].append(record["product"][0])
            else:
               
                result[record["campaignid_id"]] = record
                result[record["campaignid_id"]]["product"] = record["product"]

        val=list(result.values())
        return Response({"data":val},status=status.HTTP_200_OK)   
    
    
    
#MARKETPLACE EXPIRED LIST
"""API TO SHOW MARKETPLACE EXPIRED CAMPAIGN LIST""" 
class MarketplaceExpList(APIView):
    authentication_classes=[TokenAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self,request):
        lst=[]
        final_lst=[]
   
        
        campaign_obj=Campaign.objects.filter(vendorid_id=self.request.user.id,status=1,campaign_exp=0)
        if campaign_obj:
            z=(campaign_obj.values("id"))
            for i in z:
              
                lst.append(i['id'])
        set_data=set(lst)
     
        fin_value=set_data
        for i in fin_value:
            camp=Product_information.objects.filter(vendor_id=self.request.user.id,campaignid_id=i).values()
            campaign_obj59=Product_information.objects.filter(vendor_id=self.request.user.id,campaignid_id=i).select_related("campaignid")
            for k in campaign_obj59:
              pass

        
            for i in range(len(camp)):
                cop=(camp[i]["coupon_name"])
                amt=(camp[i]["amount"])
             
                if cop:
                   
                    couponlst=ast.literal_eval(cop)
                else:
                    couponlst=cop
                    
                if amt:
                   
                    amtlst=ast.literal_eval(amt)
                else:
                    amtlst=amt
                    
                    
                dict1={
                    "campaignid_id":camp[i]["campaignid_id"],
                    "campaign_name": k.campaignid.campaign_name ,
                    "product":[{
                    "product_name":camp[i]["product_name"],
                    "coupon_name":couponlst,
                    "amount":amtlst,
                    "product_id": camp[i]["product_id"],
                }]
                }
    
                final_lst.append(dict1)
                
        result={}
        for i, record in enumerate(final_lst):
         
            if record["campaignid_id"] in result:
                result[record["campaignid_id"]]["product"].append(record["product"][0])
            else:
               
                result[record["campaignid_id"]] = record
                result[record["campaignid_id"]]["product"] = record["product"]

        val=list(result.values())
        return Response({"data":val},status=status.HTTP_200_OK)   
    
    
    
class MarketplaceWebsiteList(APIView):
    def get(self,request):
        lst=[]
        final_lst=[]
   
        
        campaign_obj=Campaign.objects.filter(status=1,draft_status=0,campaign_exp=1)
        if campaign_obj:
            z=(campaign_obj.values("id"))
            for i in z:
              
                lst.append(i['id'])
        set_data=set(lst)
     
        fin_value=set_data
        for i in fin_value:
            camp=Product_information.objects.filter(campaignid_id=i).values()
            campaign_obj59=Product_information.objects.filter(campaignid_id=i).select_related("campaignid")
            for k in campaign_obj59:
              pass

        
            for i in range(len(camp)):
                cop=(camp[i]["coupon_name"])
                amt=(camp[i]["amount"])
                discount=(camp[i]["discount_type"])
             
                if cop:
                   
                    couponlst=ast.literal_eval(cop)
                else:
                    couponlst=cop
                    
                if amt:
                   
                    amtlst=ast.literal_eval(amt)
                    sliced=amtlst[0].replace("-","")
                   
                else:
                    amtlst=amt
                    
                if discount:
                    
                    disc_type=ast.literal_eval(discount)
                else:
                    disc_type=discount
                    
                    
                dict1={
                    "campaignid_id":camp[i]["campaignid_id"],
                    "campaign_name": k.campaignid.campaign_name ,
                    "product":[{
                    "product_name":camp[i]["product_name"],
                    "coupon_name":couponlst,
                    "amount":[sliced],
                    "discount_type":disc_type,
                    "product_id": camp[i]["product_id"],
                }]
                }
    
                final_lst.append(dict1)
                
        result={}
        for i, record in enumerate(final_lst):
         
            if record["campaignid_id"] in result:
                result[record["campaignid_id"]]["product"].append(record["product"][0])
            else:
               
                result[record["campaignid_id"]] = record
                result[record["campaignid_id"]]["product"] = record["product"]

        val=list(result.values())
        return Response({"data":val},status=status.HTTP_200_OK)   
     
     
#VENDOR APPROVAL LIST
"""API TO SHOW MARKETPLACE APPROVAL LIST"""        
class MarketplaceApprovalList(APIView):
    authentication_classes=[TokenAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self,request):
          
        influ_get=VendorCampaign.objects.exclude(Q(campaign_status=0)|Q(campaign_status=2),vendor_id=self.request.user.id).values_list("influencerid_id",flat=True)
     
        final_lst1=[] 
      
        campaign_obj2=VendorCampaign.objects.filter(campaign_status=1,vendor_id=self.request.user.id,campaignid__campaign_exp=1,campaignid__status=1)
        
        z=campaign_obj2.values_list("campaignid__id","campaignid__campaign_name")
        influencerid=campaign_obj2.values_list("influencerid",flat=True)
        
        for i in campaign_obj2:
            cop_names=Product_information.objects.get(campaignid=i.campaignid.id)
            dict1={
                "campaignid_id":i.campaignid.id,
                "campaign_name": i.campaignid.campaign_name,
                "username":i.influencerid.id,
                "coupon_name":ast.literal_eval(cop_names.coupon_name),
                "amount":ast.literal_eval(cop_names.amount)
               
            }
            
            final_lst1.append(dict1)          
        return Response({"data":final_lst1},status=status.HTTP_200_OK)  
    
    
    
#MARKETPLACE ACCEPT BY VENDOR
class MarketplaceAccept(APIView):
    authentication_classes=[TokenAuthentication]
    permission_classes=[IsAuthenticated]

    def post(self,request,id,pk):
        try:
         
            coupon_name=request.data.get("coupon")
            print(coupon_name)
            amount=request.data.get("amount")
            print(amount)
            assign_coupon=Campaign.objects.filter(id=id).update(influencer_name=[pk])
            print(assign_coupon)
            influencer_cop=influencer_coupon.objects.create(coupon_name=coupon_name,amount=amount,vendor_id=self.request.user.id,influencer_id_id=pk)
            print(influencer_cop)
            cam_dec=VendorCampaign.objects.filter(campaignid_id=id,influencerid_id=pk,vendor_id=self.request.user.id).update(campaign_status=2)
            cam_dec=Notification.objects.filter(campaignid_id=id,influencerid_id=pk,vendor_id=self.request.user.id).update(send_notification=3)
            return Response({"message":"Campaign Accept"},status=status.HTTP_202_ACCEPTED)
        except Exception as e:
            print(e)
            return Response(status=status.HTTP_400_BAD_REQUEST)
        
        
        
#MAKETPLACE DECLINE BY VENDOR
class MarketplaceDecline(APIView):
    authentication_classes=[TokenAuthentication]
    permission_classes = [IsAuthenticated]    
    def post(self,request,id,pk):
        try:
        
            cam_dec=VendorCampaign.objects.filter(campaignid_id=id,influencerid_id=pk,vendor_id=self.request.user.id).update(campaign_status=4)
            cam_dec=Notification.objects.filter(campaignid_id=id,influencerid_id=pk,vendor_id=self.request.user.id).update(send_notification=5)
           
            return Response({"message":"Campaign Decline by Vendor"},status=status.HTTP_200_OK)
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        
        
#MARKETPLACE APPROVAL LIST
"""API TO SHOW MARKETPLACE APPROVAL LIST"""        
class MarketPlaceApprovalList(APIView):
    authentication_classes=[TokenAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self,request):
          
        influ_get=VendorCampaign.objects.exclude(Q(campaign_status=0)|Q(campaign_status=2),vendor_id=self.request.user.id).values_list("influencerid_id",flat=True)
     
        final_lst1=[] 
      
        campaign_obj2=VendorCampaign.objects.filter(campaign_status=2,vendor_id=self.request.user.id,campaignid__campaign_exp=1,campaignid__status=1)
      
        z=campaign_obj2.values_list("campaignid__id","campaignid__campaign_name")
        influencerid=campaign_obj2.values_list("influencerid",flat=True)
        
        for i in campaign_obj2:
           
            dict1={
                "campaignid_id":i.campaignid.id,
                "campaign_name": i.campaignid.campaign_name,
                "influencer_name":i.influencerid.id,
            }
            
            final_lst1.append(dict1)          
        return Response({"data":final_lst1},status=status.HTTP_200_OK)  
    


#MARKETPLACE DECLINE LIST
"""API TO SHOW MARKETPLACE DECLINE LIST"""  
class MarketDeclineList(APIView):
    authentication_classes=[TokenAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self,request):
               
        final_lst1=[] 
      
        campaign_obj2=VendorCampaign.objects.filter(campaign_status=4,vendor_id=self.request.user.id,campaignid__campaign_exp=1,campaignid__status=1)
      
        z=campaign_obj2.values_list("campaignid__id","campaignid__campaign_name")
        influencerid=campaign_obj2.values_list("influencerid",flat=True)
        
        for i in campaign_obj2:
           
            dict1={
                "campaignid_id":i.campaignid.id,
                "campaign_name": i.campaignid.campaign_name,
                "influencer_name":i.influencerid.id,
            }
            
    
        
            final_lst1.append(dict1)
            
        return Response({"data":final_lst1},status=status.HTTP_200_OK)  
    
    
    
#API TO BUY SUBSCRIPTION
class BuySubscription(APIView):
    authentication_classes=[TokenAuthentication]
    permission_classes=[IsAuthenticated]
    def post(self,request):
        try:
            plan=request.query_params.get("plan")
            
            print(plan)
            value=checkout(self,request,plan)
            print(value)

            return Response({"session_url":value.url,"id":value.id})
        except stripe.error.StripeError as e:
            return Response({"error":e.user_message},status=status.HTTP_400_BAD_REQUEST)
        
        
        
        
#API TO SAVE SUBCRIPTION DATA         
class Success(APIView):
    authentication_classes=[TokenAuthentication]
    permission_classes=[IsAuthenticated]
    def get(self,request):
        
        try:
            session_id=request.query_params.get("session_id")
            checkout_session = stripe.checkout.Session.retrieve(session_id)
            subscription_id = checkout_session.subscription
            sub_retrieve=stripe.Subscription.retrieve(subscription_id)
            current_period_end = sub_retrieve["current_period_end"]
            current_period_start = sub_retrieve["current_period_start"]
            end_date = datetime.datetime.fromtimestamp(current_period_end)
            start_date = datetime.datetime.fromtimestamp(current_period_start)

        
            end_date = end_date.strftime('%Y-%m-%d')
            start_date = start_date.strftime('%Y-%m-%d')

            price_id = sub_retrieve["items"]["data"][0]["plan"]["id"]
            amount = sub_retrieve["items"]["data"][0]["plan"]["amount"]
            amount = str(amount)
            amount_len = len(amount)-2
            amount = amount[:amount_len]
            amount = int(amount)
            
            
            
            success(self,request,subscription_id,price_id,start_date,end_date,amount)
            
            
        
            return Response({"success":"Subscription activated"},status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response((e),status=status.HTTP_400_BAD_REQUEST)
    
    
    

#API TO SHOW CANCEL PAGE
class Cancel(APIView):
    authentication_classes=[TokenAuthentication]
    permission_classes=[IsAuthenticated]
    def get(self,request):
        return Response({"error":"Subscription Failed"},status=status.HTTP_400_BAD_REQUEST)
        
       
    
    
class CheckSubscription(APIView):
    authentication_classes=[TokenAuthentication]
    permission_classes=[IsAuthenticated]
    def get(self,request):
        plan=StripeSubscription.objects.filter(vendor_id=self.request.user.id).exists()
        if plan == False:
            return Response({"message":"Please Buy a Subscription"},status=status.HTTP_200_OK)
    
    
class InfluencerProfile(APIView):
    authentication_classes=[TokenAuthentication]
    permission_classes=[IsAuthenticated]
    def get(self,request,id):
        get_data=ModashInfluencer.objects.filter(id=id)
        influencer_data=[]
        for data in get_data:
            dict={
                "username":data.username,
                "followers":data.followers,
                "image":data.image,
                "engagements":data.engagements,
                "engagements_rate":data.engagements_rate,
                "fullname":data.fullname,
                "isverified":data.isverified,
                }
            influencer_data.append(dict)
            
        return Response({"data":dict},status=status.HTTP_200_OK)
    
    
    
class Payout(APIView):
    
    
    
    def get(self,request):
        stripe.api_key = settings.STRIPE_API_KEY

        account = stripe.Account.retrieve()
        stripe_account_id = account.id
        
        print(stripe_account_id)

        # maincustomer=stripe.Customer.create(
        # email="vendor@codenomad.net",
        # name="vendorSood",
        # description="My First Test Customer (created for API docs at https://www.stripe.com/docs/api)",
        # )
        

        # print(maincustomer)
        
        # paymentmethod=stripe.PaymentMethod.create(
        # type="card",
        # card={
        #     'token': 'tok_visa',
        # }
        # )
       
        # attach=stripe.PaymentMethod.attach(
        # paymentmethod.id,
        # customer=maincustomer.id,
        # )

        # customer=stripe.Customer.create(
        # email="Hritik@codenomad.net",
        # name="HritikSood",
        # description="My Second Test Customer (created for API docs at https://www.stripe.com/docs/api)",
        # )
        

        # paymentmethod=stripe.PaymentMethod.create(
        # type="card",
        # card={
        #     'token': 'tok_visa',
        # }
        # )

       
        # attach=stripe.PaymentMethod.attach(
        # paymentmethod.id,
        # customer=customer.id,
        # )
       
        balance_transaction = stripe.BalanceTransaction.create(
                amount=1000,
                currency='usd',
                description='Adding balance to customer',
                customer="cus_OGcfFnF5kPbmoR",
            )

        client_secret = balance_transaction.id
        
        return Response({"data":client_secret},status=status.HTTP_200_OK)
    
    
    
# class Checkout(APIView):
#     def post(self,request):
#         api = CheckoutSdk.builder() \
#         .oauth() \
#         .client_credentials('hritik@codenomad.net', 'Mongodb31') \
#         .environment(Environment.sandbox()) \
#         .scopes([OAuthScopes.ACCOUNTS]) \
#         .build()

#         phone = Phone()
#         phone.country_code = '44'
#         phone.number = '4155552671'

#         address = Address()
#         address.address_line1 = 'CheckoutSdk.com'
#         address.address_line2 = '90 Tottenham Court Road'
#         address.city = 'London'
#         address.state = 'London'
#         address.zip = 'W1T 4TJ'
#         address.country = Country.GB

#         request = OnboardEntityRequest()
#         request.reference = 'reference'
#         request.contact_details = ContactDetails()
#         request.contact_details.phone = phone
#         request.profile = Profile()
#         request.profile.urls = ['https://docs.checkout.com/url']
#         request.profile.mccs = ['0742']
#         request.individual = Individual()
#         request.individual.first_name = 'First'
#         request.individual.last_name = 'Last'
#         request.individual.trading_name = "Batman's Super Hero Masks"
#         request.individual.registered_address = address
#         request.individual.national_tax_id = 'TAX123456'
#         request.individual.date_of_birth = DateOfBirth()
#         request.individual.date_of_birth.day = 5
#         request.individual.date_of_birth.month = 6
#         request.individual.date_of_birth.year = 1996
#         request.individual.identification = Identification()
#         request.individual.identification.national_id_number = 'AB123456C'

#         try:
#             response = api.accounts.create_entity(request)
#             print(response)
#             return Response(response)
#         except CheckoutApiException as err:
#             # API error
#             request_id = err.request_id
#             status_code = err.http_status_code
#             error_details = err.error_details
#             http_response = err.http_response
#         except CheckoutArgumentException as err:
#             print("hello")
#             # Bad arguments

#         except CheckoutAuthorizationException as err:
#             # Invalid authorization
#             print("why")
        
        
#API TO GET SINGLE CAMPAIGN
"""API HELPS US TO GET SINGLE CAMPAIGN DETAILS"""
class ApprovalCampaignDetails(APIView):
    authentication_classes=[TokenAuthentication]
    permission_classes = [IsAuthenticated]  
    def get(self,request,id):
        value_lst=[]
        try:
            camp=Product_information.objects.filter(campaignid_id=id).values()
            campaign_obj=Product_information.objects.filter(campaignid_id=id).select_related("campaignid")
          

        except Campaign.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        for k in campaign_obj:
            pass
        for i in range(len(camp)):
            cop=(camp[i]["coupon_name"])
            amt=(camp[i]["amount"])
           
            
            if cop:
                
                couponlst=ast.literal_eval(cop)
                
            else:
                couponlst=cop
                
            if amt:
    
                amtlst=ast.literal_eval(amt)
            else:
                amtlst=amt
                   
            dict1={
                "campaignid_id":camp[i]["campaignid_id"],
                "product_name":camp[i]["product_name"],
                "campaign_name": k.campaignid.campaign_name ,
                "influencer_visit": k.campaignid.influencer_visit ,
                "influencer_name": k.campaignid.influencer_name ,
                "offer": k.campaignid.offer ,
                "date": k.campaignid.date ,
                "description": k.campaignid.description,
                "influencer_fee": k.campaignid.influencer_fee,
                "campaign_status":k.campaignid.campaign_status,
                "draft_status":k.campaignid.draft_status,
                "product":[{
                    "product_name":camp[i]["product_name"],
                    "name":couponlst,
                   
                    "amount":amtlst,
                    "product_id": camp[i]["product_id"],
                }]
            }

            value_lst.append(dict1)
            
        result = {}
        for i, record in enumerate(value_lst):
         
            if record["campaign_name"] in result:
                result[record["campaign_name"]]["product"].append(record["product"][0])
            else:
               
                result[record["campaign_name"]] = record
                result[record["campaign_name"]]["product"] = record["product"]

        val=list(result.values())
        return Response({"data":val},status=status.HTTP_200_OK)
   
    
    
    
class AdminTransfer(APIView):
    authentication_classes=[TokenAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self,request): 
        admin_account=""
        admin_acc=None
        get_account_id=stripe_details.objects.filter(vendor_id=self.request.user.id).values_list("account_id",flat=True)
        admin_id=stripe_details.objects.filter(vendor_id=self.request.user.id).values_list("user",flat=True)
        
        if admin_id:
            admin_acc=admin_id[0]
        if get_account_id:
            admin_account=get_account_id[0]
        get_commission=commission_charges.objects.all().values_list("commission",flat=True)
        if get_commission:
            commission_val=get_commission[0]
        acc_tok=access_token(self,request)
        store_url = acc_tok[1]
        api_token = acc_tok[0]
        headers= {"X-Shopify-Access-Token": api_token}   
        url = f'https://{store_url}/admin/api/2022-10/orders.json?status=active'
        response = requests.get(url,headers=headers)
        sales_by_coupon = {}
    
        if response.status_code == 200:
            orders1 = response.json().get('orders', [])
            
            
            for order in orders1:
                line_items = order.get('discount_codes', [])
                
                
                total_price = order.get('total_price')
                    
                if line_items:
                    coupon_code = line_items[0].get('code')
                    
                    
                
                    if coupon_code in sales_by_coupon:
                        sales_by_coupon[coupon_code] += float(total_price)
                        
                    else:
                        
                        sales_by_coupon[coupon_code] = float(total_price)
                        
            sale=list(sales_by_coupon.keys())
            coup_dict={} 
            for  i in sale:    
                check=Product_information.objects.filter(coupon_name__contains=i,vendor_id=self.request.user.id).values("campaignid","coupon_name")
                print(check)
                for z in check:
                    if "coupon_name" in z:
                        list_value = eval(z["coupon_name"])
            
                        campaign_id = z["campaignid"]
                        if campaign_id in coup_dict:
                            coup_dict[campaign_id].extend(list_value)
                        else:
                            coup_dict[campaign_id] = list_value

            dict_lst = [coup_dict]
            
            sale_by_id = {}
            admin_tra=[]
            for campaign_id, coupon_names in coup_dict.items():
                sale = 0.0
                
                for coupon_name in set(coupon_names):
                    if coupon_name in sales_by_coupon:
                       
                        sale += sales_by_coupon[coupon_name]
                        admin_part=sale*commission_val/100
                        
                        
                sale_by_id[campaign_id] = sale
                print(sale_by_id)
                # filtered_data = {key: value for key, value in sale_by_id.items() if int(value[0]) > 0}

                # print(filtered_data)
               
                if sale != 0.0:
                    campaign_name = Campaign.objects.filter(id=campaign_id).values_list('campaign_name', flat=True).first() 
            
                    if admin_account and admin_acc !="":
                        admin_tra.append({"campaign_id":campaign_id,"sale":round(sale,2), "campaign_name":campaign_name,"commission":commission_val,"admin_part":round(admin_part,2),"account":admin_account,"offer":"commission","admin_id":admin_acc})
                    else:
                        admin_tra.append({"campaign_id":campaign_id,"sale":round(sale,2), "campaign_name":campaign_name,"commission":commission_val,"admin_part":round(admin_part,2),"account":"","offer":"commission","admin_id":admin_acc})
            print(admin_tra)
            empty=PaymentDetails.objects.filter(vendor=self.request.user.id,admin=admin_acc).exists()
           
            if empty == True:
                for i in admin_tra:
                    
                    emp_check=PaymentDetails.objects.filter(vendor=self.request.user.id,campaign_id=i["campaign_id"]).exists()
                   
                    if emp_check == False :
                        if admin_acc==" ":
                            PaymentDetails.objects.create(sales=i["sale"],influencerfee=i["commission"],offer=i["offer"],amount=admin_acc,admin_id=admin_acc,vendor_id=self.request.user.id,campaign_id=i["campaign_id"],account_id=i["account"])
                        else:
                            PaymentDetails.objects.create(sales=i["sale"],influencerfee=i["commission"],offer=i["offer"],admin_id=admin_acc,vendor_id=self.request.user.id,campaign_id=i["campaign_id"],account_id=i["account"])

                    else:
                        account_check=PaymentDetails.objects.filter(vendor=self.request.user.id,campaign_id=i["campaign_id"]).values_list("account_id",flat=True)
                        if account_check[0]== "":                      
                            amount_transfered=PaymentDetails.objects.filter(vendor=self.request.user.id,campaign_id=i["campaign_id"]).update(account_id=i["account"])

                        amount_transfered=transferdetails.objects.filter(vendor=self.request.user.id,admin=admin_acc,campaign=i["campaign_id"]).values_list("amount",flat=True)
                        
                        print(amount_transfered)
                        amount_deduct=i["admin_part"]
                        if amount_transfered:
                            amount_deduct=int(i["admin_part"]-int(amount_transfered[0]))
                            print(amount_deduct)
                   
                        
                        PaymentDetails.objects.filter(vendor=self.request.user.id,campaign_id=i["campaign_id"]).update(amount=amount_deduct,sales=i["sale"])
            else:
              
                for  i in admin_tra:
                    details_obj=PaymentDetails()
                    details_obj.amount=i["admin_part"]
                    details_obj.admin_id=i["admin_id"]
                    details_obj.vendor_id=self.request.user.id
                    details_obj.sales=i["sale"]
                    # details_obj.influencerfee=i["influener_fee"]
                    details_obj.offer=i["offer"]
                    details_obj.campaign_id=i["campaign_id"]
                    details_obj.account_id=i["account"]
                    details_obj.save()
                    
            upd_data=PaymentDetails.objects.filter(vendor=self.request.user.id,influencer__isnull=True)
          
            
            upd_lst=[]
            for pay in upd_data:
                upd_dict={
                    "campaing_id":pay.campaign.campaign_name,
                    "sales":round(pay.sales,2),
                    "account":pay.account_id,
                    "admin":pay.admin.id,
                    "admin_fee":commission_val,
                    "offer":pay.offer,
                    "amount":pay.amount,  
                    "amount_paid":pay.amountpaid,
                    "campaign_detail":pay.campaign.id      
                    
                }
                upd_lst.append(upd_dict)
                
            return Response({"sale_details":upd_lst},status=status.HTTP_200_OK)
        else:
            return Response({"Message":"unable to fetch data"})
   
        
        
        
        
    
class AdminTranferMoney(APIView):
    authentication_classes=[TokenAuthentication]
    permission_classes = [IsAuthenticated] 
    
    def post(self,request):
        account=request.data.get("account_id")
        
        admin=request.data.get("admin")
        print(admin)
    
        amount=request.data.get("amount")

        campaignids=request.data.get("camp_id")
       
        salesdone=request.data.get("sales")
       
        get_account=StripeDetails.objects.filter(vendor_id=self.request.user.id).values("account_id","influencer_id")
        
        
        stripe.api_key = settings.STRIPE_API_KEY  
        
        try:
            payment_method=stripe.PaymentMethod.create(
            type="card",
            card={
               "token": "tok_visa", 
               },
            
            )
        except stripe.error.StripeError as e:
            return Response({"error":e.user_message},status=status.HTTP_400_BAD_REQUEST)
            
        try:
            intent = stripe.PaymentIntent.create(
                amount=int(amount),
                currency='usd',
                payment_method_types=['card'],
                payment_method=payment_method["id"],
            
            )
            
        except stripe.error.StripeError as e:
            return Response({"error":e.user_message},status=status.HTTP_400_BAD_REQUEST)
        
        
        try:    
            confim=stripe.PaymentIntent.confirm(
            intent["id"],
            payment_method="pm_card_visa",
            )
        except stripe.error.StripeError as e:
            return Response({"error":e.user_message},status=status.HTTP_400_BAD_REQUEST)
            
            
    

        if confim.status == 'succeeded':
            try:
                transfer1 = stripe.Transfer.create(
                    amount=int(amount),
                    currency='usd',
                    destination=account,
                    transfer_group=intent.id,
                )     
                
                exists_transfer=transferdetails.objects.filter(vendor=self.request.user.id,admin=32,campaign=campaignids).exists()   
                print(exists_transfer)
                if exists_transfer == False:
                    transfer_obj=transferdetails()
                    transfer_obj.vendor_id=self.request.user.id
                    transfer_obj.admin_id=admin
                    transfer_obj.transferid=transfer1["id"]
                    transfer_obj.amount=transfer1["amount"]
                    transfer_obj.destination=transfer1["destination"]
                    transfer_obj.campaign_id=campaignids
                    transfer_obj.save()

                    pay_value=PaymentDetails.objects.filter(campaign=campaignids,admin=admin,vendor=self.request.user.id).values("sales","amount")
                    remaining_amount=amount-transfer1["amount"] 
                   
            
                    
                    PaymentDetails.objects.filter(campaign=campaignids,admin=32,vendor=self.request.user.id).update(amountpaid=transfer1["amount"],salespaid=salesdone,amount=remaining_amount)
                else:  
                   
                    amount_Paid=transferdetails.objects.filter(vendor=self.request.user.id,admin=32,campaign=campaignids).values_list("amount",flat=True)
                    PaymentDetails.objects.filter(campaign=campaignids,admin=32,vendor=self.request.user.id).update(amountpaid=amount_Paid[0],salespaid=salesdone)
  
                    new_amount=int(amount_Paid[0])+int(transfer1["amount"])
                    
                  
                    amount_Paid=transferdetails.objects.filter(vendor=self.request.user.id,admin=32,campaign=campaignids).update(amount=new_amount)

          
            except stripe.error.StripeError as e:
                return Response({"error":e.user_message},status=status.HTTP_400_BAD_REQUEST)
            try:
                payout=stripe.Payout.create(
                    amount=int(amount),
                    currency="usd",
                    stripe_account=account,
                
                    )
                
               
            except stripe.error.StripeError as e:
                return Response({"error":e.user_message},status=status.HTTP_400_BAD_REQUEST)
            
            return Response({"data":transfer1,"message":"Money transfer Successfully"},status=status.HTTP_200_OK)
        return Response({"error":"not valid"},status=status.HTTP_400_BAD_REQUEST)
    
    
    
    
class CheckSubscription(APIView):
   authentication_classes=[TokenAuthentication]
   permission_classes = [IsAuthenticated] 
   
   def get(self,request):
       sub_check=StripeDetails.objects.filter(vendor=self.request.user.id).exists()
       if sub_check == True:
           return Response({"message":"please buy subscription"},status=status.HTTP_400_BAD_REQUEST)
       else:
           return Response({"message":"Subscription already buyed"},status=status.HTTP_200_OK)
               
    
    