from InfluencerApp.serializer import *
from InfluencerApp.models import *
from rest_framework.views import APIView,View
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from AdminApp.views import *
from CampaignApp.serializer import *
import requests
import json
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication
from django.core.mail import EmailMessage  
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.urls import reverse
from .utils import account_activation_token,VerificationView
from django.db.models import Q
from django.core.mail import send_mail as sm
import stripe
from Affilate_Marketing import settings


stripe.api_key = settings.STRIPE_API_KEY
lean_headers={"lean-app-token":"9de351e4-0240-498d-8d8a-c6b8a46de475"}

headers={"Authorization": "Bearer yGrFqiK4YqDtqODbGRZkZrWRIgsjFLZP"}


#REGISTER INFLUENCER API

    
class Register(APIView):
    def post(self, request):
      

        def handle_step_one(self, request):
            infl_id = request.session.get("id")
            if infl_id:
                influencer_obj = ModashInfluencer.objects.get(id=infl_id)
                serializer = InfluencerSerializer(influencer_obj, data=request.data)
            else:
                serializer = InfluencerSerializer(data=request.data)

            if serializer.is_valid(raise_exception=True):
                save_obj = serializer.save(user_type=2)
                infl_id = serializer.data["id"]
                request.session["id"] = infl_id

                uid64 = urlsafe_base64_encode(force_bytes(infl_id))
                current_site_info = get_current_site(request)
                link = reverse(
                    "activate",
                    kwargs={"id": infl_id, "token": account_activation_token.make_token(save_obj)},
                )
                activate_url = (
                    "https://myrefera.com/#/verify/"
                    + account_activation_token.make_token(save_obj)
                    + "/"
                    + str(infl_id)
                )
                email_body = (
                    "HI"
                    + " "
                    + serializer.data["username"]
                    + "please use this link to verify account\n"
                    + activate_url
                )
                mail_subject = "Activate your Account"
                to_email = serializer.data["email"]
                email = EmailMessage(mail_subject, email_body, to=[to_email])
                email.send()

                return Response(
                    {
                        "id": infl_id,
                    },
                    status=status.HTTP_201_CREATED,
                )
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        def handle_step_two(self, request):
            infl_id = request.session.get("id")
            if infl_id:
                influencer_obj = ModashInfluencer.objects.get(id=infl_id)
                serializer = StepTwoSerializer(influencer_obj, data=request.data)
            else:
                serializer = StepTwoSerializer(data=request.data)

            if serializer.is_valid(raise_exception=True):
                infl_id = request.session.get("id")
                serializer.save(influencerid_id=infl_id)
                handle = serializer.data["user_handle"]
                influencer_obj = ModashInfluencer()
                base_url = f"https://api.modash.io/v1/instagram/profile/@{handle}/report"
                response = requests.get(base_url, headers=headers)
                if response.ok:
                    influencer_data = response.json()["profile"]["profile"]
                    influencer_obj.username = influencer_data["username"]
                    influencer_obj.fullname = influencer_data["fullname"]
                    influencer_obj.isverified = influencer_data["isVerified"]
                    influencer_obj.follower = influencer_data["followers"]
                    influencer_obj.image = influencer_data["picture"]
                    influencer_obj.engagements = influencer_data["engagements"]
                    influencer_obj.engagement_rate = round(
                        influencer_data["engagementRate"], 2
                    )
                    influencer_obj.influencerid_id = infl_id
                    influencer_obj.save()
                    return Response(
                        {"Success": response.json()},
                        status=status.HTTP_201_CREATED,
                    )
                else:
                    return Response(
                        {"error": response.json()},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



# class Register(APIView):
#     def post(self, request):
#         serializer = InfluencerSerializer(data=request.data)
#         if serializer.is_valid(raise_exception=True):
#             serializer2 = StepTwoSerializer(data=request.data)
#             if serializer2.is_valid(raise_exception=True):
#                 save_obj = serializer.save(user_type=2)
#                 infl_id = serializer.data["id"]
#                 request.session["id"] = infl_id
#                 handle = serializer.data["user_handle"]
#                 influencer_obj = ModashInfluencer()
#                 base_url = f"https://api.modash.io/v1/instagram/profile/@{handle}/report"
#                 response = requests.get(base_url, headers=headers)
#                 if response.ok:
#                     influencer_data = response.json()["profile"]["profile"]
#                     influencer_obj.username = influencer_data["username"]
#                     influencer_obj.fullname = influencer_data["fullname"]
#                     influencer_obj.isverified = influencer_data["isVerified"]
#                     influencer_obj.follower = influencer_data["followers"]
#                     influencer_obj.image = influencer_data["picture"]
#                     influencer_obj.engagements = influencer_data["engagements"]
#                     influencer_obj.engagement_rate = round(
#                         influencer_data["engagementRate"], 2
#                     )
#                     influencer_obj.influencerid_id = infl_id
#                     influencer_obj.save()
                    
#                 else:
#                     print("enteter",response.json())
#                     return Response(
#                         {"error": "Influencer requirement did not match"},
#                         status=status.HTTP_400_BAD_REQUEST,
#                     )
#                 serializer2.save(influencerid_id=infl_id)

#                 uid64 = urlsafe_base64_encode(force_bytes(infl_id))
#                 current_site_info = get_current_site(request)
#                 link = reverse(
#                     "activate",
#                     kwargs={"id": infl_id, "token": account_activation_token.make_token(save_obj)},
#                 )
#                 activate_url = (
#                     "https://myrefera.com/#/verify/"
#                     + account_activation_token.make_token(save_obj)
#                     + "/"
#                     + str(infl_id)
#                 )
#                 email_body = (
#                     "HI"
#                     + " "
#                     + serializer.data["username"]
#                     + "please use this link to verify account\n"
#                     + activate_url
#                 )
#                 mail_subject = "Activate your Account"
#                 to_email = serializer.data["email"]
#                 email = EmailMessage(mail_subject, email_body, to=[to_email])
#                 email.send()
#                 return Response(
#                     {
#                         "Success": response.json(),
#                         "token": account_activation_token.make_token(save_obj),
#                         "id": infl_id,
#                     },
#                     status=status.HTTP_201_CREATED,
#                 )
#             return Response(serializer2.errors, status=status.HTTP_400_BAD_REQUEST)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class Register(APIView):
    def post(self,request):
        serializer=InfluencerSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            

            serializer2=StepTwoSerializer(data=request.data)
          
            if serializer2.is_valid(raise_exception=True):
                
                save_obj=serializer.save(user_type =2)
                infl_id=serializer.data["id"]
                request.session["id"]=infl_id
                handle=serializer.data["user_handle"]
                influencer_obj = ModashInfluencer()
                base_url=f"https://api.modash.io/v1/instagram/profile/@{handle}/report"
                response = requests.get(base_url, headers=headers)
                print(response.json())
                if response.ok:
                    
                    influencer_obj.username=response.json()['profile']['profile']['username']
                    influencer_obj.fullname=response.json()['profile']['profile']['fullname']
                    influencer_obj.isverified=response.json()['profile']['isVerified']
                    influencer_obj.follower=response.json()['profile']['profile']['followers']
                    influencer_obj.image =response.json()['profile']['profile']['picture']
                    influencer_obj.engagements = response.json()['profile']['profile']['engagements']
                    engagemente = response.json()['profile']['profile']['engagementRate']
                    influencer_obj.engagement_rate = round(engagemente,2)
                    influencer_obj.influencerid_id=serializer.data["id"]

                    influencer_obj.save()
                else:
                    return Response({"error": response.json()},status=status.HTTP_201_CREATED)
                serializer2.save(influencerid_id=serializer.data["id"])
            
                uid64=urlsafe_base64_encode(force_bytes(serializer.data["id"]))
                current_site_info = get_current_site(request)  
                
                link=reverse('activate',kwargs={"id":serializer.data["id"],'token':account_activation_token.make_token(save_obj)})
            
                # activate_url=str(current_site_info) + str(link)
                activate_url="https://myrefera.com/#/verify/"+ account_activation_token.make_token(save_obj)+"/"+ str(serializer.data["id"])
                email_body= "HI"  +  " "  +  serializer.data["username"] + "please use this link to verify account\n" + activate_url
                mail_subject = 'Activate your Account'  
            
        
                to_email =serializer.data["email"]  
                email = EmailMessage(  
                            mail_subject, email_body, to=[to_email]  
                )  
            
                email.send()  
                # User.objects.filter(id=serializer.data["id"]).update(verify_email=1)         
                return Response({"Success": response.json(),"token":account_activation_token.make_token(save_obj),"id":serializer.data["id"]},status=status.HTTP_201_CREATED)
         

            return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    
    
class StepOneAPIView(APIView):
    def post(self, request):
        serializer = InfluencerSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
          
            
            handle = serializer.data["user_handle"]
            influencer_obj = ModashInfluencer()
            base_url = f"https://api.modash.io/v1/instagram/profile/@{handle}/report"
            response = requests.get(base_url, headers=headers)
            if response.ok:
                save_obj = serializer.save(user_type=2)
                infl_id = serializer.data["id"]
                request.session["id"] = infl_id
                influencer_data = response.json()["profile"]["profile"]
                influencer_obj.username = influencer_data["username"]
                influencer_obj.fullname = influencer_data["fullname"]
                influencer_obj.isverified = influencer_data["isVerified"]
                influencer_obj.follower = influencer_data["followers"]
                influencer_obj.image = influencer_data["picture"]
                influencer_obj.engagements = influencer_data["engagements"]
                influencer_obj.engagement_rate = round(influencer_data["engagementRate"], 2)
                influencer_obj.influencerid_id = infl_id
                influencer_obj.save()
                request.session["id"] = infl_id
            else:
                return Response(
                    {"error": response.json()},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            return Response({"id": infl_id}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
    
class StepTwoAPIView(APIView):
    def post(self, request):
        infl_id = request.session.get("id")
        if infl_id:
            influencer_obj = ModashInfluencer.objects.get(id=13)
            serializer = StepTwoSerializer(data=request.data)
        else:
            serializer = StepTwoSerializer(data=request.data)

        if serializer.is_valid(raise_exception=True):
            serializer.save(influencerid_id=72)

            # Send verification email
            infl_id = serializer.data["influencerid"]
            save_obj = User.objects.get(id=infl_id)

            print(save_obj)
            uid64 = urlsafe_base64_encode(force_bytes(infl_id))
            current_site_info = get_current_site(request)
            activate_url = (
                "https://myrefera.com/#/verify/"
                + account_activation_token.make_token(save_obj)
                + "/"
                + str(infl_id)
            )
            email_body = (
                "Hi "
                + save_obj.username
                + ", please use this link to verify your account:\n"
                + activate_url
            )
            
            mail_subject = "Activate your Account"
            to_email = save_obj.email
            email = EmailMessage(mail_subject, email_body, to=[to_email])
            email.send()

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class Details(APIView):
    def post(self,request):
        serializer=StepTwoSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save(influencerid_id=request.session["id"])
            return Response({"Success": "Next Step"},status=status.HTTP_201_CREATED)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    
    
    
#LOGIN INFLUENCER API  
class InfluencerLogin(APIView): 
    def post(self, request):
        username = request.data.get('email')
        password = request.data.get('password')
    
        user = authenticate(username=username, password=password)
        
        if user: 
                
            login(request, user)
        
            if user.verify_email == True:
                usr=Token.objects.filter(user_id=user.id)
                if not usr:
                    refresh=Token.objects.create(user=user)
                    return Response({'Success':"Login Successfully",'Token':str(refresh),"username":user.username}, status=status.HTTP_200_OK)
                
                else:
                    user_key=Token.objects.filter(user_id=user.id).values_list("key",flat=True)[0]
                    if user:
            
                            return Response({'Success':"Login Successfully",'Token':str(user_key),"username":user.username}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Your email is not verified'}, status=status.HTTP_400_BAD_REQUEST)
                
        else:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)
    
            
            
           
           
#SHOW LIST OF INFLUENCER API
class InfluencerList(APIView):
    authentication_classes=[TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self,request):   
        infu_list=User.objects.filter(user_type =2)
        serializer = InfluencerSerializer(infu_list,many=True)
        return Response({"data":serializer.data},status=status.HTTP_200_OK)
    



#YOUTUBER FOLLOWER API
class YoutubeFollower(APIView):
    
    def get(self,request):
        user_handler=request.GET.get("user")
        base_url=f"https://api.modash.io/v1/youtube/profile/{user_handler}/report"
        response = requests.get(base_url, headers=headers)
        return Response({"success":json.loads(response.text)},status=status.HTTP_200_OK)
    
    
    
#INSTAGRAM FOLLOWER API
class InstagramFollower(APIView):
    def get(self,request):
        user_handler=request.GET.get("user")
     
        base_url=f"https://api.modash.io/v1/instagram/profile/{user_handler}/report"
        response = requests.get(base_url, headers=headers)
        return Response({"success":json.loads(response.text)},status=status.HTTP_200_OK)
    
    
#UPDATE INFLUENCER DATA API   
class UpdateInfluencer(APIView):
    authentication_classes=[TokenAuthentication]
    permission_classes = [IsAuthenticated]
    def put(self,request,pk):
        try:
            influencer = User.objects.get(pk = pk)
        except User.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer=UpdateInfluencerSerializer(influencer,data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_200_OK)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    
    
#ACCEPT CAMPAIGN API
class AcceptView(APIView):
    authentication_classes=[TokenAuthentication]
    permission_classes = [IsAuthenticated]    
    def post(self,request,id):
        try:
          
            influencer_data=Campaign.objects.filter(id=id).values_list("vendorid",flat=True)
            vendor=influencer_data[0]
          
            modash_data=ModashInfluencer.objects.filter(influencerid_id=self.request.user.id).values_list("id",flat=True)
            if modash_data:
                camp_accept=Campaign.objects.filter(id=id).update(campaign_status=1)

                infl_accept=Notification.objects.filter(campaignid_id=id,influencerid_id=modash_data[0]).update(send_notification=2)
                influencer_data2=VendorCampaign.objects.filter(campaignid=id,influencerid_id=modash_data[0]).update(campaign_status=1)
            modash_data1=ModashInfluencer.objects.filter(influencerid_id=self.request.user.id).values_list("id",flat=True)
            if modash_data1:
          
                camp_accept=Campaign.objects.filter(id=id).update(campaign_status=1)
                infl_accept=Notification.objects.filter(campaignid_id=id,influencerid_id=modash_data[0]).update(send_notification=2)
                cam_obj2=Campaign_accept.objects.create(influencerid_id=self.request.user.id,campaignid_id=id,campaign_status=1,vendor_id=vendor,modashinfluencer=modash_data[0])

            cam_obj2=Campaign.objects.filter(id=id).values_list("vendorid__email",flat=True)
            
            if cam_obj2:
                email=cam_obj2[0]
         
            res = sm(
            subject = 'Campaign Accepted',
            message = 'Your Campaign is accepted by '+self.request.user.username,
            from_email = 'testsood981@gmail.com',
            recipient_list = [email],
            fail_silently=False,
        )
            
            return Response({"message":"Campaign Accepted"},status=status.HTTP_200_OK)
        except:
            return Response({"error":"Issue in Campaign"},status=status.HTTP_400_BAD_REQUEST)
    
    
#DECLINE CAMPAIGN API
class DeclineView(APIView):
    authentication_classes=[TokenAuthentication]
    permission_classes = [IsAuthenticated]    
    def post(self,request,id):
        try:
            influencer_data=Campaign.objects.filter(id=id).values_list("vendorid",flat=True)
            vendor=influencer_data[0]
            modash_data=ModashInfluencer.objects.filter(influencerid_id=self.request.user.id).values_list("id",flat=True)
            # if modash_data:
            #     camp_accept=Campaign.objects.filter(id=id).update(campaign_status=3)
            #     infl_accept=Notification.objects.filter(campaignid_id=id,influencerid_id=modash_data[0]).update(send_notification=4)

            #     infl_accept=VendorCampaign.objects.filter(campaignid_id=id,influencerid_id=modash_data[0]).update(campaign_status=4)
            #     cam_dec2=Campaign_accept.objects.filter(campaignid_id=id).update(influencerid_id=self.request.user.id,campaign_status=3,vendor_id=vendor)
            modash_data1=ModashInfluencer.objects.filter(influencerid_id=self.request.user.id).values_list("id",flat=True)
            if modash_data1:
                camp_accept=Campaign.objects.filter(id=id).update(campaign_status=3)
                infl_accept=Notification.objects.filter(campaignid_id=id,influencerid_id=modash_data[0]).update(send_notification=4)

                infl_accept=VendorCampaign.objects.filter(campaignid_id=id,influencerid_id=modash_data1[0]).update(campaign_status=4)
                cam_obj2=Campaign_accept.objects.create(influencerid_id=self.request.user.id,campaignid_id=id,campaign_status=3,vendor_id=vendor)            
          
            return Response({"message":"Campaign Decline by Influencer"},status=status.HTTP_200_OK)
        except:
            
            return Response(status=status.HTTP_400_BAD_REQUEST)




#LIST OF CAMPAIGN API
class PendingCampaing(APIView):
    authentication_classes=[TokenAuthentication]
    permission_classes = [IsAuthenticated]    
    def get(self,request):   
        try:
            campaign_list=Campaign.objects.filter(status=0)
            serializer = CampaignSerializer(campaign_list,many=True)
            return Response({"data":serializer.data},status=status.HTTP_200_OK)
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)
    
    
#LOGOUT API
class LogoutView(APIView):
    permission_classes = (IsAuthenticated,)
    def post(self, request, format=None):
        request.user.auth_token.delete()
        return Response(status=204)
    
    
    
class PendingList(APIView):
    authentication_classes=[TokenAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self,request):
        lst=[]
        final_lst=[]
        res=[]
        res2=[]    
        value=ModashInfluencer.objects.filter(influencerid_id=request.user.id).values_list("id",flat=True)[0]
        vendor_codes=VendorCampaign.objects.filter(influencerid_id=value,campaign_status=0)
            
        if vendor_codes.exists():
            res.append(vendor_codes)
        else:
            res=""
        
        if res:
            
            for i in res:
                z=(i.values("campaignid"))
                res2.append(z)
        
  
            for i in res2:
                ids = [q['campaignid'] for q in i]
                for id in ids:
                    lst.append(id)
                    
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
                    "status":k.campaignid.campaign_status,
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
    

    
# GET CAMPAIGN APPROVAL LIST  
class ApprovalList(APIView):
    authentication_classes=[TokenAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self,request):
        lst=[]
        final_lst=[]
        res=[]
        res2=[]    
        value=ModashInfluencer.objects.filter(influencerid_id=request.user.id).values_list("id",flat=True)[0]
        vendor_codes=VendorCampaign.objects.filter(influencerid_id=value,campaign_status=2)
        vendo_camp=vendor_codes.values_list("campaignid_id__id",flat=True)

        campaign_obj1=Campaign_accept.objects.filter(Q(campaign_status=1)|Q(campaign_status=2),Q(influencerid_id=self.request.user.id))
     
        if campaign_obj1.exists():
            res.append(campaign_obj1)
        else:
            res=""
        
        if res:
            
            for i in res:
                z=(i.values("campaignid"))
                res2.append(z)
        
  
            for i in res2:
                ids = [q['campaignid'] for q in i]
                for id in ids:
                    lst.append(id)
                    
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
             
                if cop:
                  
                    couponlst=ast.literal_eval(cop)
                else:
                    couponlst=cop
                    
                if amt:
                    
                    amtlst=ast.literal_eval(amt)
                else:
                    amtlst=amt
                    
               
                
                if camp[i]["campaignid_id"] in vendo_camp:
                    dict1={
                        "campaignid_id":camp[i]["campaignid_id"],
                        "campaign_name": k.campaignid.campaign_name ,
                        "status":k.campaignid.campaign_status,
                        "product":[{
                        "product_name":camp[i]["product_name"],
                        "coupon_name":couponlst,
                        "amount":amtlst,
                        "product_id": camp[i]["product_id"],
                        
                    }]
                    }
                    final_lst.append(dict1)
                    
                else:
                     dict1={
                        "campaignid_id":camp[i]["campaignid_id"],
                        "campaign_name": k.campaignid.campaign_name ,
                        "status":k.campaignid.campaign_status,
                        "product":[{
                        "product_name":camp[i]["product_name"],
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
    
    
#API TO GET SINGLE CAMPAIGN
class GetCampaign(APIView):
    authentication_classes=[TokenAuthentication]
    permission_classes = [IsAuthenticated]  
    def get(self,request,id ):
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
    
    
    
    
# GET CAMPAIGN Decline LIST  
class DeclinelList(APIView):
    authentication_classes=[TokenAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self,request):
        lst=[]
        final_lst=[]
        res=[]
        res2=[]    
        campaign_obj=Campaign.objects.filter(Q(campaign_status=3),Q(influencerid_id=self.request.user.id)| Q(vendorid_id=self.request.user.id),status=2,draft_status=0)
        campaign_obj2=Campaign_accept.objects.filter(Q(campaign_status=3),Q(influencerid_id=self.request.user.id))

        if campaign_obj2.exists():
            res.append(campaign_obj2)
        else:
            res=""
        
        if res:
            
            for i in res:
                z=(i.values("campaignid"))
                res2.append(z)
        

            for i in res2:
                ids = [q['campaignid'] for q in i]
               
                for id in ids:
                  
                    lst.append(id)

     
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
    
    
#GET LIST OF NOTIFICATION API
class VendorNotification(APIView):
    authentication_classes=[TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self,request):
        modash_get=ModashInfluencer.objects.filter(influencerid_id=self.request.user.id,).values_list('id',flat=True)[0]
        
        print("--------------",modash_get)
        notification_obj=Notification.objects.filter(influencerid_id=modash_get,send_notification__in=[1,3,5])
        
        notify_list=[]
        
        for i in notification_obj:
            
            if i.send_notification==1:
                dict={
                    "message": i.vendor.username + "send you request for"  +  i.campaignid.campaign_name
                }
            
                notify_list.append(dict)
            elif i.send_notification==3:
                dict={
                    "message": i.vendor.username + "Approved your request for"  +  i.campaignid.campaign_name
                }
            
                notify_list.append(dict)
            else:
                
                dict={
                    "message": i.vendor.username + "deline your request for"  +  i.campaignid.campaign_name
                }
            
                notify_list.append(dict)
                
        return Response({"data":notify_list},status=status.HTTP_200_OK)  
    
    
#GET LIST OF NOTIFICATION API
class ChangeNotifStatus(APIView):
    authentication_classes=[TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self,request):
        modash_get=ModashInfluencer.objects.filter(influencerid_id=self.request.user.id).values_list('id',flat=True)[0]
        notification_obj=Notification.objects.filter(influencerid_id=modash_get,send_notification__in=[1,4,3,5]).update(send_notification=0)


          
        dict={
            "message":  "Notification status updated"
        }
    
        
        return Response(dict,status=status.HTTP_200_OK)  
    

class StripeConnectAccountView(APIView):
    
    authentication_classes=[TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def post(self, request):  
        first_name=request.data.get("first_name")
        last_name=request.data.get("last_name")
        email=request.data.get("email")
        country=request.data.get("country")
        account_number=request.data.get("account_number")
        routing_number=request.data.get("routing_number")
        account_holder_name=request.data.get("account_holder_name")
        secret=request.data.get("secret")
        
        check_data=StripeDetails.objects.all()
        # if check_data:
            
        #     modash_key=ModashInfluencer.objects.filter(influencerid=self.request.user.id).values("id")
        #     print(modash_key)
            
        #     match_data=StripeDetails.objects.filter(influencer=modash_key[0]["id"],vendor=22).exists()
           
        #     if match_data == True:
        #         return Response({"message":"Account Already exists"},status=status.HTTP_409_CONFLICT)
                
                
        # else:
            
            # try:
            #     stripe.api_key=secret
            #     account = stripe.Account.create(
            #     country="US",
            #     type="custom",
            #     capabilities={"card_payments": {"requested": True}, "transfers": {"requested": True},"us_bank_account_ach_payments":{"requested":True}},
            #     business_type="individual",
            #     business_profile={'mcc':'5734', 'url':'https://www.google.com/'},

            #     individual ={'first_name':"sood",
            #     'last_name':"hritik",
            #     'email': "test@gmail.com",
            #     'phone':"+15555551234",
            #     'ssn_last_4':"0000",
            #     'address':{'city':"NY", 'state':"New York", 'postal_code':10017, 'country': 'US', 'line1':"609 5th Ave"},
            #     'dob':{'day':11 , 'month':11 , 'year' :1999},

            #     },

            #     external_account = {'object':'bank_account',
            #     'country': 'US','currency': 'USD', 
            #     'account_number': "000123456789",
            #     'routing_number': "110000000",
            #     'account_holder_name' : "test",
            #     'account_holder_type': "individual"
            #     },
                
            #     tos_acceptance={"date": 1609798905, "ip": "8.8.8.8"}
            #        )
     
        try:
           
            account = stripe.Account.create(
            country="AE",
            type="custom",
            capabilities={"card_payments": {"requested": True}, "transfers": {"requested": True}},
            business_type="company",
            business_profile={'mcc':'5734', 'url':'https://www.google.com/',
                                "support_phone":"55-798-4597",
                                "product_description":"hello"},

            tos_acceptance={"date": 1609798905, "ip": "8.8.8.8"},
            company={
                "structure": "sole_establishment",
                "name": "hell334o",
                "phone": "555-123-4567",
                "tax_id": "1234",
                "executives_provided": False,
                "owners_provided": False,
                "directors_provided":False
            },
            representative={
                "first_name":"hritik"
            },

            external_account={
            'object': 'bank_account',
            'country': 'AE',
            'currency': 'AED',
            'account_number': 'AE070331234567890123456',
            'account_holder_name': 'test',
            'account_holder_type': 'individual'
        }
        )
            
            print(account)
            
            val=ModashInfluencer.objects.filter(influencerid=self.request.user.id).values("id")

            stripe_details=StripeDetails()
            stripe_details.vendor_id=22
            stripe_details.influencer_id=val[0]["id"]
            stripe_details.account_id=account["id"]
            stripe_details.save()
        except stripe.error.StripeError as e:
            return Response({"error":e.user_message},status=status.HTTP_400_BAD_REQUEST)
                
        return Response({"message":"Account Created",'account_id': account},status=status.HTTP_201_CREATED)
        




class CustomerCreate(APIView):
    def post(self,request):
        global account_id
        global customer_id
    

        customer=stripe.Customer.create(
        name="hritik",
        email="person@example.edu", 
        stripe_account=account_id,

        description="My First Test Customer (created for API docs at https://www.stripe.com/docs/api)",
        )
        customer_id=customer["id"]
        return Response({'account_id': customer}, status=status.HTTP_201_CREATED)
    
    
class CreatePaymentIntent(APIView):
    def post(self,request):
        global account_id
        global customer_id
  


        payment_intent=stripe.PaymentIntent.create(amount=10000, currency="usd", transfer_group="ORDER10",stripe_account=account_id)
      
      
      
        return Response({'account_id': payment_intent}, status=status.HTTP_201_CREATED)
    
    
class StripeToken(APIView):
    def post(self,request):
        global bank_account
        bank=stripe.Token.create(
        bank_account={"country": "US",      
        "currency": "usd",       
        "account_holder_name": "tester",       
        "account_holder_type": "individual",      
        "routing_number": "110000000",       
        "account_number": "000123456789", },

        )
        bank_account=bank["id"]   
        return Response({'account_id': bank}, status=status.HTTP_201_CREATED)
    
    

class Stripeverify(APIView):
    def get(self,request):
        global account_id
        global customer_id
        source = stripe.Customer.retrieve_source(
            customer_id,
            bank_account,
            stripe_account=account_id
            )
        return Response({'account_id': source}, status=status.HTTP_201_CREATED)



class LeanCustomer(APIView):
    def post(self,request):
        customer_name=request.data.get("customer")
        url="https://sandbox.leantech.me/customers/v1/"
        body= {"app_user_id": customer_name}
        response=requests.post(url,headers=lean_headers,json=body)
        return Response({"status":"customer created successfully","response":response.json()},status=status.HTTP_201_CREATED)
  
    
class LeanEndCustomer(APIView):
    def post(self,request):
        customer_name=request.data.get("customer")
        refrence=request.data.get("refrence")
        url="https://sandbox.leantech.me/customers/v1/end-users/"
        body= {"customer_id": customer_name,"reference": refrence}
        
        response=requests.post(url,headers=lean_headers,json=body)
        return Response({"status":"customer created successfully","response":response.json()},status=status.HTTP_201_CREATED)
    
    
class GetCustomer(APIView):
    def get(self,request):
        url="https://sandbox.leantech.me/customers/v1/app-user-id/arpansaini/"
        response=requests.get(url,headers=lean_headers)
        return Response({"status":"Customer data","response":response.json()},status=status.HTTP_201_CREATED)
    
class GetEntity(APIView):
    def get(self,request):
        url="https://sandbox.leantech.me/customers/v1/46e77c5d-e010-4859-a825-9cb77165318e/entities/"
        response=requests.get(url,headers=lean_headers)
        return Response({"status":"Lean Entity","response":response.json()},status=status.HTTP_201_CREATED)
    
    
    
class LeanDestination(APIView):
    def post(self,request):
        cus_destination=request.data.get("destination")
      
        url="https://sandbox.leantech.me/payments/v1/destinations"
        body=cus_destination
        response=requests.post(url,headers=lean_headers,json=body)
        return Response({"status":"customer created successfully","response":response.json()},status=status.HTTP_201_CREATED)



class DestinationList(APIView):
    def get(self,request):
       
        url="https://sandbox.leantech.me/payments/v1/destinations/be2033db-f6e0-4914-a8a0-ab80027262e7/"
        response=requests.get(url,headers=lean_headers)
        return Response({"status":"customer created successfully","response":response.json()},status=status.HTTP_201_CREATED)




class PaymentList(APIView):
    def get(self,request):  
        url="https://sandbox.leantech.me/customers/v1/61023285-db5e-4a84-826c-6cec68f06cc5/payment-sources/"
        response=requests.get(url,headers=lean_headers)
        return Response({"status":"customer created successfully","response":response.json()},status=status.HTTP_201_CREATED)




class BankList(APIView):
    def get(self,request):
        url="https://sandbox.leantech.me/banks/v1/"
        response=requests.get(url,headers=lean_headers)   
        return Response({"status":"List of Banks","response":response.json()},status=status.HTTP_201_CREATED)
    
    
class PaymnetIntentist(APIView):
    def get(self,request):
        url="https://sandbox.leantech.me/payments/v1/intents/ffaf421c-7eeb-475e-8f2f-fc3f080a50a7/"
      
        response=requests.get(url,headers=lean_headers)   
     
        return Response({"status":"List of Banks","response":response.json()},status=status.HTTP_201_CREATED)



class VerifyName(APIView):
    def get(self,request):
        dict1={"entitiy_id":"e5780913-adc5-4488-bde4-8ef30e414898",
               "customer":"arpansaini"}
        url="https://sandbox.leantech.me/insights/v1/name-verification/"
     
        response=requests.post(url,headers=lean_headers)   
     
        return Response({"status":"verify_name","response":response.json()},status=status.HTTP_201_CREATED)

# class LeanPayment(APIView):
    
#     def post(self,request):
#     #     js="""function LeanPayment()
#     #         Lean.connect({
#     #         app_token: "YOUR_APP_TOKEN",
#     #         customer_id: "CUSTOMER_ID",
#     #         permissions: ["payments"],
#     #         payment_destination_id: "SEBASTIANS_DESTINATION_ID", //make sure to include the beneficiary's destination ID or else the default destination (Company's CMA account) will be linked
#     #         sandbox: true
#     #     })
#     #     const value=LeanPayment();
        
#     #     """
#     #     context=js2py.eval_js()
#     #     context.execute
#     #     return Response({"status":"hello"})



def value(request):
    return render(request,"script.html")


class InfluencerStripe(APIView):
    authentication_classes=[TokenAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self,request):
        seri_obj=StripeSerializer(data=request.data)
        if seri_obj.is_valid(raise_exception=True):
            seri_obj.save(influencer_id=self.request.user.id)
            return Response({"success":" Stripe Details Saved Successfully"},status=status.HTTP_201_CREATED)
        return Response({"error":seri_obj.error_messages},status=status.HTTP_201_CREATED)
    
    
    
    
    
class CreateConnectedAccountView(APIView):
    authentication_classes=[TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = CreateConnectedAccountSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data.get('email')
        bank_account_token = serializer.validated_data.get('bank_account_token')
        platform_account_id = serializer.validated_data.get('platform_account_id')

        try:
            account = stripe.Account.create(
                type='standard',
                email=email,
                capabilities={
                    'card_payments': {'requested': True},
                    'transfers': {'requested': True},
                },
                country='AE', 
                business_type='individual',
                external_account=bank_account_token,
                # stripe_account=platform_account_id
            )
            
            return Response(account, status=status.HTTP_200_OK)
        except stripe.error.AuthenticationError as e:
    
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except stripe.error.APIConnectionError as e:
          
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except stripe.error.StripeError as e:
           
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
          
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class create_bank_account_token(APIView):
    
    def post(self, request):
        serializer = BankAccountSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data

        try:
            bank_account_token = stripe.Token.create(
                bank_account={
                    'account_number': data['account_number'],
                    'routing_number': data['routing_number'],
                    'currency': 'aed',  
                    'country': 'AE',  
                }
            )
            
            return Response(bank_account_token, status=status.HTTP_200_OK)
          
        except stripe.error.AuthenticationError as e:
       
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except stripe.error.APIConnectionError as e:
           
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except stripe.error.StripeError as e:
         
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class InfluencerData(APIView):
    authentication_classes=[TokenAuthentication]
    permission_classes = [IsAuthenticated] 
    def get(self,request):
        headers={'clientid':'cli_a82767c340834da9ec112207','token':'9463d65d0d1e5458ea06589e44343e45f9cff35c54552c5c13957d7116af0fdaada7420620e78b47f97f499a370898edf30019c2d87b182936c6be7c19300be1'}
        username=request.data.get("user")
        url=f"https://matrix.sbapis.com/b/instagram/statistics?query={username}"
        
        response=requests.get(url,headers=headers)
        if response.status_code==200:
            followers=response.json()["data"]["statistics"]["total"]["followers"]
            following=response.json()["data"]["statistics"]["total"]["following"]
            engagement_rate=response.json()["data"]["statistics"]["total"]["engagement_rate"]
            username=response.json()["data"]["id"]["display_name"]
            handle_name=response.json()["data"]["id"]["username"]
            profile_pic=response.json()["data"]["general"]["branding"]["avatar"]
            verified=response.json()["data"]["misc"]["sb_verified"]
        
        
            instagram_data={
                "profile_pic":profile_pic,
                "username":username,
                "handle_name":handle_name,
                "followers":followers,
                "following":following,
                "engagement_rate":engagement_rate,
                "verified":verified,
            }
            return Response({"data":instagram_data},status=status.HTTP_200_OK)
        return Response({"error":response.json()},status=status.HTTP_400_BAD_REQUEST)
        
        
        
class Vendorkey(APIView):
    authentication_classes=[TokenAuthentication]
    permission_classes = [IsAuthenticated] 
    def get(self,request):
        try:
            get_key=VendorStripeDetails.objects.all().values("vendor__username","secret_key","vendor")
            key_list=[]
            for i in get_key:
                dict={
                    "vendor_key":i["secret_key"],
                    "vendor":i["vendor__username"],
                    "vendor_id":i["vendor"]
                    
                }
                key_list.append(dict)
            return Response({"data":key_list},status=status.HTTP_200_OK)

        except Exception as e:
          
            return Response({"error":"please try again"},status=status.HTTP_400_BAD_REQUEST)