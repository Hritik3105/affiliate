from django.shortcuts import render
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
from django.db.models import Count
from .utils import *
from django.core.mail import EmailMessage 


# Create your views here.




#To get access token
            
def access_token(self,request):
    user_obj=User.objects.filter(id=self.request.user.id)
    shop=user_obj.values("shopify_url")[0]["shopify_url"]
    acc_tok=Store.objects.filter(store_name=shop).values("access_token")[0]["access_token"] 
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
            email_body= "HI"  +  " "  +  serializer.data["username"] + "your Shop Register Successfully"
        
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
                                return Response({'Success':"Login Successfully",'Token':str(user_key),"shop_url":usr_ins.shopify_url,"admin_dahboard":f"https://admin.shopify.com/store/{store_name}/apps/marketplace-49"}, status=status.HTTP_200_OK)
                            
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
                                return Response({'Success':"Login Successfully",'Token':str(user_token),"shop_url":user.shopify_url,"admin_dahboard":f"https://admin.shopify.com/store/{store_name}/apps/marketplace-49"}, status=status.HTTP_200_OK)
                    
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
            req_id=serializer.save()
            val_lst=(request.data["product_discount"])
            
            if {} in val_lst:
                z=val_lst.remove({})
            else:
                z=""
                
            for i in range(len(val_lst)):
                product=Product_information.objects.filter(campaignid_id =req_id.id,vendor_id=self.request.user.id).delete()
           
          
            #get data from product_discount list          
            if val_lst:
                for i in range(len(val_lst)):
                    product=Product_information()
                    product.vendor_id=self.request.user.id
                    product.campaignid_id=req_id.id
                    product.product_name=val_lst[i]["product_name"]
                    product.product_id=val_lst[i]["product_id"]
                    product.coupon_name=val_lst[i]["name"]
                    product.amount=val_lst[i]["amount"]
                    product.save()
                product=VendorCampaign.objects.filter(campaignid_id =req_id.id,vendor_id=self.request.user.id).delete()

           
                if  "influencer_name" in request.data and Campaign.objects.filter(id =req_id.id,draft_status=0,vendorid_id=self.request.user.id):
                        val_lst1=(request.data["influencer_name"])
                        
                        data_list=val_lst1.split(",")
                
                        int_list = [int(num) for num in data_list]
                        Notification.objects.filter(campaignid_id=req_id.id,vendor_id=self.request.user.id).delete()
                        influencer_details(self,request,int_list,req_id)
                               
            #when there is no product_discount_list    
    
            else:
                product=Product_information.objects.filter(campaignid_id =req_id.id,vendor_id=self.request.user.id).delete()

                arg_id=request.data["product"]
                arg=request.data["product_name"]
                for i in  range(len(arg)):
    
                    product=Product_information()
                    product.vendor_id=self.request.user.id
                    product.campaignid_id=req_id.id
                    product.product_name=arg[i]
                    product.product_id=arg_id[i]
                    product.save()

                

                # product=Product_information()
                # product.vendor_id=self.request.user.id
                # product.campaignid_id=req_id.id
                # product.save()
                if  "influencer_name" in request.data and Campaign.objects.filter(id =req_id.id,draft_status=0,vendorid_id=self.request.user.id):
                    val_lst1=(request.data["influencer_name"])
                
                    data_list=val_lst1.split(",")
            
                    int_list = [int(num) for num in data_list]
                    Notification.objects.filter(campaignid_id=req_id.id,vendor_id=self.request.user.id).delete()
                    influencer_details(self,request,int_list,req_id)  
            if z == None :
                product=Product_information.objects.filter(campaignid_id =req_id.id,vendor_id=self.request.user.id).delete()
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
         
            req_id=serializer.save(draft_status=0,campaign_status=0)
            val_lst=(request.data["product_discount"])
            
            if {} in val_lst:
                z=val_lst.remove({})
            else:
                z=""
                
            for i in range(len(val_lst)):
                product=Product_information.objects.filter(campaignid_id =req_id.id,vendor_id=self.request.user.id).delete()
           
            if val_lst:
               
                    product_details(self,request,val_lst,req_id)
                    if  "influencer_name" in request.data:
                        val_lst1=(request.data["influencer_name"])
                        
                        data_list=val_lst1.split(",")
                
                        int_list = [int(num) for num in data_list]
                    
                        influencer_details(self,request,int_list,req_id)               
            else:
               
                product=Product_information()
                product.vendor_id=self.request.user.id
                product.campaignid_id=req_id.id
                product.save()
                influencer_details(self,request,int_list,req_id)
                        
                
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
            
                req_id=serializer.save(status=2,vendorid_id=self.request.user.id,draft_status=1)
            
                val_lst=(request.data["product_discount"])
                
                while {} in val_lst:
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
                    
                    
                    return Response({"success":"Campaign create successfuwlly","product_details":serializer.data},status=status.HTTP_200_OK)

                
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

        campaign_obj=Campaign.objects.filter(Q(campaign_status=0),draft_status=0,vendorid_id=self.request.user.id,status=2)
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
    
    
    
# API TO GET LIST OF ACTIVE CAMPAIGN    

"""API TO GET LIST OF  ACTIVE CAMPAIGN OF INFLUENCER"""
class  ActiveList(APIView):
    authentication_classes=[TokenAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self,request):
        final_lst1=[] 
        campaign_obj2=VendorCampaign.objects.filter(campaign_status=2,vendor_id=self.request.user.id)
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
        campaign_obj=Campaign.objects.filter(vendorid_id=self.request.user.id,status=2,draft_status=1)
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
class  MarketplaceList(APIView):
    authentication_classes=[TokenAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self,request):
        lst=[]
        final_lst=[]
   
        
        campaign_obj=Campaign.objects.filter(vendorid_id=self.request.user.id,status=1,draft_status=0)
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
     
    
    
    
#API TO GET MARKETPLACE DRAFT    

"""API GET LIST OF MARKETPLACE  DRAFT CAMPAIGN SHOWN IN MARKETPLACE TAB"""
class  MarketplaceDraftList(APIView):
    authentication_classes=[TokenAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self,request):
        lst=[]
        markdraft_lst=[]
        
        campaign_obj=Campaign.objects.filter(vendorid_id=self.request.user.id,status=1,draft_status=1)
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
class InfluencerList(APIView):
    authentication_classes=[TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self,request):
        influ_list = ModashInfluencer.objects.all().values() 
       
        return Response({"data":influ_list},status=status.HTTP_200_OK) 
    
        




#API TO DELETE A CAMPAIGN
"""API TO DELETE CAMPAIGN"""
class DeleteCampaign(APIView): 
    def delete(self, request, id):
            camp_del=Campaign.objects.filter(id=id)
            camp_del.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        
        
# API TO GET Product list

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
        active=VendorCampaign.objects.filter(vendor_id=self.request.user.id,campaign_status=2).count()
        pending=Campaign.objects.filter(vendorid_id=self.request.user.id,campaign_status=0,draft_status=0).count()
        final_pending=pending 
        total=active + pending 
        return Response({"active_campaign":active,"pending_campaign":final_pending,"total":total},status=status.HTTP_200_OK)
    
    

#API TO SEND REQUEST


class RequestSents(APIView):
    authentication_classes=[TokenAuthentication]
    permission_classes = [IsAuthenticated]  
    def post(self,request):
        vendor_status1=User.objects.filter(id=self.request.user.id).values("vendor_status")
        if vendor_status1[0]["vendor_status"] == True:
            serializer=InflCampSerializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                req_id=serializer.save(status=2,vendorid_id=self.request.user.id)
                infll=serializer.data["influencer_name"]
                val_lst=(request.data["product_discount"])
                if {} in val_lst:
                    z=val_lst.remove({})
                else:
                    z=""
                if val_lst:
                    
                    product_details(self,request,val_lst,req_id)
                    val_lst1=(request.data["influencer_name"])
                
                    data_list=val_lst1.split(",")
                
                    int_list = [int(num) for num in data_list]
                
                    influencer_details(self,request,int_list,req_id)
                                
                else:
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
            else:
                dict1={
                    "campaignid_id":camp[i]["campaignid_id"],
                    "product_name":camp[i]["product_name"],
                    "product_id": camp[i]["product_id"],
                    "campaign_name": k.campaignid.campaign_name ,
                    "influencer_visit": k.campaignid.influencer_visit ,
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



#API TO SEARCH COUPONS
class SearchCoupon(APIView):
    authentication_classes=[TokenAuthentication]
    permission_classes = [IsAuthenticated] 
    def post(self, request, format=None):
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

            name = request.data.get('name', None)
            if name:
                coupons = [coupon for coupon in discount_list if name.lower() in coupon['title'].lower()]
            else:
                coupons = discount_list
            return Response(coupons)
    

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
                    price_rules_codes=price_rule.json()['price_rules'][i]["title"]
                    price_rule_value=price_rule.json()['price_rules'][i]['value']
                    price_rule_value_type=price_rule.json()['price_rules'][i]['value_type']
                    product_dict={
                        "product_name":productMapDict[z],
                        "product_id":z,   
                        "name": price_rules_codes,
                        "amount":price_rule_value,   
                        "discout_type":price_rule_value_type,
    
                    }    
                    dataList.append(product_dict)
    
        for product in dataList:

            if product:
                product_id = product["product_id"]
                
                if product_id in product_dict:
                    product_dict[product_id]["name"].append(product["name"])
                    product_dict[product_id]["amount"].append(product["amount"])
                
                else:
                    product_dict[product_id] = {
                        "product_name": product["product_name"],
                        "product_id":product["product_id"],
                        "name": [product["name"]],
                        "amount": [product["amount"]],
                        "discout_type":product["discout_type"],
                        }
         

        for i in lst:
        
            if i in product_dict:
                new_list.append(product_dict[i])
            else:
                

                new_list.append({"product_name": productMapDict[i],
                        "product_id":i,
                        "name":"",
                        "amount": "",
                        "discout_type":""})
            
       
        
        return Response({'product_details':new_list,"product_url":handle_lst,"title_list":title_list},status=status.HTTP_200_OK)       



#Accept by Vendor API
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
        
        
        
        
class VendorApprovalList(APIView):
    authentication_classes=[TokenAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self,request):
       
          
        influ_get=VendorCampaign.objects.exclude(Q(campaign_status=0)|Q(campaign_status=2),vendor_id=self.request.user.id).values_list("influencerid_id",flat=True)
       
     
        
        final_lst1=[] 
      
        campaign_obj2=VendorCampaign.objects.filter(campaign_status=1,vendor_id=self.request.user.id)
      
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
 
 
        
class VendorDeclineList(APIView):
    authentication_classes=[TokenAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self,request):
               
        final_lst1=[] 
      
        campaign_obj2=VendorCampaign.objects.filter(campaign_status=4,vendor_id=self.request.user.id)
      
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
    

class InfluencerNotification(APIView):
    authentication_classes=[TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self,request):
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
class ChangeNotifinflStatus(APIView):
    authentication_classes=[TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self,request):
        notification_obj=Notification.objects.filter(vendor_id=self.request.user.id,send_notification__in=[2,4]).update(send_notification=0)


          
        dict={
            "message":  "Notification status updated"
        }
    
        
        return Response(dict,status=status.HTTP_200_OK)  
    
    
