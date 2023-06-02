from django.shortcuts import render,HttpResponse,redirect
from rest_framework.views import APIView
from django.contrib.auth import authenticate, login
from rest_framework.response import Response
from rest_framework import status
from rest_framework import viewsets
from AdminApp.models import *
from StoreApp.models import *
from AdminApp.serializer import *
from rest_framework.authtoken.models import Token
from CampaignApp.models import *
from CampaignApp.serializer import *
from rest_framework.authentication import TokenAuthentication
from django.contrib import auth
from AdminApp.permission import *
from django.contrib.auth.decorators import login_required
from itertools import chain
import requests
from django.http import JsonResponse
from Affilate_Marketing.settings import API_VERSION
from django.utils.crypto import get_random_string
from AdminApp.utils import *
import stripe
from django.conf import settings
from django.shortcuts import render
from django.contrib import messages

# Create your views here.


#FUNCTION TO GET ACCESS TOKEN
def access_token(request,id):
    user_obj=User.objects.filter(id=id)
    shop=user_obj.values("shopify_url")[0]["shopify_url"]
    acc_tok=Store.objects.filter(store_name=shop).values("access_token")[0]["access_token"]
   
    return acc_tok,shop
    
    
def show(request):
    return render(request,'index.html')



def login_user(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(email=email, password=password)
        if user:
            if user.is_superuser==1:
                login(request, user)
                
                return HttpResponse("successfully")
            else:
                return HttpResponse("User is not superadmin")
        else:
            return HttpResponse("Incorrect email or password")
    elif request.user.is_anonymous:
        return render(request,'login.html')
    else:        
        return redirect("dashboard")



"""logout """
def logout_(request):
    auth.logout(request)

    return redirect('login1')

#Login API
class Login(APIView): 
    def post(self, request):
        username = request.data.get('email') 
        
        password = request.data.get('password')
        user = authenticate(username=username, password=password)   
        if user:
            login(request, user)
           
            refresh=Token.objects.create(user=user)
            return Response({'Success':"Login Successfully",'Token':str(refresh)}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)
        
        

class ProfileUpdate(APIView):
    authentication_classes=[TokenAuthentication]
    permission_classes = [IsSuperuser]
    def put(self,request,pk):
        try:
            influencer = User.objects.get(pk = pk)
        except User.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer=UpdateUserSerializer(influencer,data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_200_OK)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)


        
# Influencer api get , create,update ,delete
class InfluencerViewSet(viewsets.ViewSet):
    authentication_classes=[TokenAuthentication]
    permission_classes = [IsSuperuser]
    
    def list(self, request):
        infu_list=User.objects.filter(user_type =2)
        serializer = UserSerializer(infu_list,many=True)
        return Response({"data":serializer.data},status=status.HTTP_200_OK)

    def create(self, request):
        serializer=UserSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save(user_type =2)
            return Response({"Success": "Influencer Created Successfully."},status=status.HTTP_201_CREATED)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        try:
            influencer = User.objects.get(pk = pk,user_type=2)
        except User.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer=UpdateUserSerializer(influencer,data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_200_OK)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        influencer= User.objects.get(pk=pk,user_type=2)
        influencer.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)




#List of Campaign api
class CampaignView(APIView):
    authentication_classes=[TokenAuthentication]
    permission_classes = [IsSuperuser]
    def get(self,request):   
        campaign_list=Campaign.objects.all()
        serializer = CampaignSerializer(campaign_list,many=True)
        return Response({"data":serializer.data},status=status.HTTP_200_OK)


#List of Campaign api get,create,update,delete
class CampaignViewSet(viewsets.ViewSet):
    authentication_classes=[TokenAuthentication]
    permission_classes = [IsSuperuser]
    def list(self, request):
        campaign_list=Campaign.objects.all()
        serializer = CampaignSerializer(campaign_list,many=True)
        return Response({"data":serializer.data},status=status.HTTP_200_OK)

    def create(self, request):
        serializer=CampaignSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response({"success":"Campaign create successfully","product_details":serializer.data},status=status.HTTP_200_OK)
        
        return Response({"error":"Campaign not created"},status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        try:
            campaign_get = Campaign.objects.get(pk = pk)
      
        except Campaign.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer=UpdateCampaignSerializer(campaign_get,data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_200_OK)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        camp_del=Campaign.objects.filter(id=pk)
        camp_del.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)





#Logout api
class LogoutView(APIView):
    permission_classes = [IsSuperuser]
    def post(self, request, format=None):
        request.user.auth_token.delete()
        return Response(status=204)
   
   
   

"""change password"""
@login_required
def profile_update(request):
    user_obj=User.objects.filter(id=request.user.id).values_list("email","username")
    if user_obj:
        data=user_obj
        email=data[0][0]
        username=data[0][1]
    if request.method == "POST":
        password = request.POST.get('password')
        email = request.POST.get('email')
        username = request.POST.get('username') 
        if password:
            user_obj=User.objects.filter(id=request.user.id).update(email=email,password=make_password(password),username=username)
        else:
           
            user_obj=User.objects.filter(id=request.user.id).update(email=email,username=username)
        messages.success(request, "Profile Updated Successfuly")
        return render(request, "profileupdate.html",{"email":email,"username":username})
    return render(request, "profileupdate.html",{"email":email,"username":username})

@login_required
def campaign_list(request):
    lst=[]
    campaign_model=Campaign.objects.filter(status=2)
   
    for i in campaign_model:
        if i.influencer_name:
            # val=ast.literal_eval(i.influencer_name)
            val=ast.literal_eval(i.influencer_name)
            z=ModashInfluencer.objects.filter(id__in=val).values_list("username",flat=True)

            lst.append(z)
    for i in lst:
        pass
    return render(request,"campaignlist.html",{"data":campaign_model,"influencer_name":lst})
    
    
@login_required
def marketplace_list(request):
    lst=[]
    campaign_model=Campaign.objects.filter(status=1)
    return render(request,"campaignlist.html",{"data":campaign_model,"influencer_name":lst})
    
@login_required
def Single_camp(request,id):
    single_obj=Campaign.objects.filter(id=id).values()
    product_data=Product_information.objects.filter(campaignid_id=id).values("product_name")
    
    product_name=[]
    for i in range (len(product_data)):
        product_name.append(product_data[i]["product_name"])
    vendor_name=Campaign.objects.filter(id=id).values("vendorid__username")[0]["vendorid__username"]
   
    campaign_name=single_obj[0]["campaign_name"]
    description=single_obj[0]["description"]
    offer=single_obj[0]["offer"]
    influencer_fee=single_obj[0]["influencer_fee"]
    influencer_lst=[]
    if single_obj[0]["influencer_name"]:
       
        val=ast.literal_eval(single_obj[0]["influencer_name"])
        z=ModashInfluencer.objects.filter(id__in=val).values()
       
        for i in range(len(z)):
            name=z[i]["username"]
           
            influencer_lst.append(name)
    context={"influencer_name":influencer_lst,"camapign_name":campaign_name,"vendor_name":vendor_name,"influencer_fee":influencer_fee,"description":description,"product_name":product_name,"offer":offer}
    return render(request,"singlecamp.html",context)
 
 
@login_required
def Single_Vendor(request,id):
   
    single_obj=User.objects.filter(id=id).values()
    camp_obj=Campaign.objects.filter(vendorid_id=id,draft_status=0,status=2).values()
   
    lst1=[]
    for i in camp_obj:
        if i["influencer_name"]:
            val=ast.literal_eval(i["influencer_name"])
            z=ModashInfluencer.objects.filter(id__in=val).values()
            for k in range(len(z)):
                name=z[k]["username"]
                ids=z[k]["id"]
                
                if i["vendorid_id"]==id:
                    dict1={
                        "influencer_name":name,
                        "id":i["id"],
                        "influencer_id":ids
                    }
                    lst1.append(dict1)
                
   
    product_data1=Product_information.objects.filter(vendor_id=id,campaignid_id__draft_status=0,campaignid_id__status=2)
   
    vendor_campaign=Campaign.objects.filter(vendorid_id=id,draft_status=0,status=2)
    lst=[]
    for i in vendor_campaign:
        dict={
            "campaign_name":i.campaign_name,
            "description":i.description,
            "offer":i.offer,
            "influencer_fee":i.influencer_fee, 
            "product_name":[],
            "amount":[],
            "influencer_name":[],
            "influencer_id":[],
            "id":i.id    
        }
        lst.append(dict)
    
    vendor_campaign1=Campaign.objects.filter(vendorid_id=id,draft_status=0,status=2).values("id")
    result = list(chain(product_data1.values("product_name","campaignid","amount")))
   
    combined_data = []
    
    campaign_ids = set(item['campaignid'] for item in result)
    for campaign_id in campaign_ids:
        
        product_names = [item['product_name'] for item in result if item['campaignid'] == campaign_id]
        for item in result: 
            if item['campaignid'] == campaign_id:
                print(item["amount"])
                
        combined_data.append({'product_name': product_names,"id":campaign_id})
        
        
      
    combined_data1 = []
    
    campaign_ids1 = set(item['id'] for item in lst1)
  
    for campaign_id in campaign_ids1:
        product_names = [item['influencer_name'] for item in lst1 if item['id'] == campaign_id]      
        influencer_id = [item['influencer_id'] for item in lst1 if item['id'] == campaign_id]  
     
        combined_data1.append({'influencer_name': product_names,"id":campaign_id,"influencer_id":influencer_id})
 
    
      
    for i in combined_data1:
        for j in lst:
            if j["id"]== i["id"]:   
                j["influencer_name"]=i["influencer_name"]
                j["influencer_id"]=i["influencer_id"]
                
    
    for i in combined_data:
        for j in lst:
            if j["id"]== i["id"]:   
                j["product_name"]=i["product_name"]
                
    # for i in vendor_campaign1:
    #     product_data=Product_information.objects.filter(vendor_id=id,campaignid_id=i["id"]).values("product_name")
      
    final_lst1=[] 
    campaign_obj2=VendorCampaign.objects.filter(campaign_status=2,vendor_id=id) 
                
    for i in campaign_obj2:
            dict1={
                "campaignid_id":i.campaignid.id,
                "campaign_name": i.campaignid.campaign_name,
                "influencer_name":i.influencerid.id,
                
            }
        
        
            final_lst1.append(dict1)
    
    return render(request,"campaignlist.html",{"vendor":vendor_campaign,"vendor_campaign":lst,"product_data":combined_data,"single_vendor":single_obj,"final_list":final_lst1})


@login_required
def vendor_list(request):
    vendor_data=User.objects.filter(user_type=3)
    return render(request,"vendorlist.html",{"vendor":vendor_data})
   
   

def change_status(request):
    if request.method == "GET":
        value=request.GET.get("status")
      
      
        ids=value[1:]
       
        if value[0]=="a":
            
            User.objects.filter(id=int(ids)).update(vendor_status=True)
            return HttpResponse("User is Active")
        else:
          
            User.objects.filter(id=int(ids)).update(vendor_status=0)
            return HttpResponse("User is Deactivated")
       
       
@login_required  
def Order_list(request,id):
    acc_tok=access_token(request,id)

    created_at_min = '2023-01-01T00:00:00-00:00'
    created_at_max = '2023-09-31T23:59:59-00:00'

    headers= headers= {"X-Shopify-Access-Token":acc_tok[0]}
    base_url=f"https://{acc_tok[1]}/admin/api/{API_VERSION}/orders/count.json?status=any"
    response = requests.get(base_url, headers=headers)
    
    val=response.json()
    
    return render(request,"chart.html",{"count":val['count']})


@login_required
def Influencer_list(request):
    
    Influencer=ModashInfluencer.objects.filter().values()
    return render(request,"Influencerlist.html",{"influencer":Influencer})


def influencer_name(request):
    if request.method == "GET":
        value=request.GET.get("status")
       
        camp_obj=Campaign.objects.filter(id=value,draft_status=0,status=2).values()
       
        lst1=[]
        for i in camp_obj:
          
            if i["influencer_name"]:
               
                val=ast.literal_eval(i["influencer_name"])
                z=ModashInfluencer.objects.filter(id__in=val).values()

                for k in range(len(z)):
                    
                    name=z[k]["username"]
                    ids=z[k]["id"]
                  
                    if i["id"]==int(value):
                        dict1={
                            "influencer_name":name,
                            "id":i["id"],
                            "influencer_id":ids,
                            "status":"Pending",
                        }
                        lst1.append(dict1)
        
        campaign_obj2=VendorCampaign.objects.filter(campaign_status=2,campaignid_id=value) 
        lst2=[]
        for k in lst1:
           
            for j in campaign_obj2:
           
                if k["influencer_id"] == j.influencerid.id:
                    k["status"]="Accepted"


         
        return JsonResponse({"val":lst1})
    

def product_name(request):
    if request.method == "GET":
        value=request.GET.get("status")
        product_list=[]
        product_data1=Product_information.objects.filter(campaignid_id=value,campaignid_id__draft_status=0,campaignid_id__status=2)
        for i in product_data1:
            pro_dict={ 
                      "product_name":i.product_name,
                      "coupon":i.coupon_name,
                      "amount":i.amount
                }
            product_list.append(pro_dict)
            
        return JsonResponse({"val":product_list})
    
    
    
"""forgot password to email link"""

def forgot_password(request):    
    if request.method=='POST':
        email=request.POST.get('email')
        if not User.objects.filter(email=email,is_superuser=1).first():
            return HttpResponse("1")
        token=get_random_string(length=6, allowed_chars='0123456789')
        request.session['token'] = token
        send_forget_password_mail(email,token)    
        return HttpResponse("2")
    return render(request, "forgetpassword.html")


"""forgot password to email link"""
def change_password_link(request,email,token):  
    token2 = request.session['token']
    
    if request.method == "POST":
        password = request.POST.get('password')
        conpassword = request.POST.get('conpassword')
        if int(token) == int(token2):
            if password == conpassword:
                user = User.objects.get(email=email)
                user.set_password(password)
                user.save()
                request.session['token']=0
                msg="password changed successfully"
                return render(request, "login.html", {'msg':msg})
            msg="Your password and confirmation password do not match."   
            return render(request, "changepassword.html", {'msg':msg})
        
        return HttpResponse("invalid link")
    return render(request, "changepassword.html")
    
           
    
    
@login_required
def split_payment(request):
    
    if request.method == "POST":
        amount =1000
       
        recipient1_amount = int(amount * 0.7)
        recipient2_amount = int(amount * 0.3)  

              
        stripe.api_key = settings.STRIPE_API_KEY


        payment_method=stripe.PaymentMethod.create(
        type="card",
        card={
            "number": "4242424242424242",
            "exp_month": 8,
            "exp_year": 2024,
            "cvc": "314",
        },
        
        
        )
   
        intent = stripe.PaymentIntent.create(
            amount=amount,
            currency='usd',
            payment_method_types=['card'],
            payment_method=payment_method["id"],
           
        )
        
        confim=stripe.PaymentIntent.confirm(
        intent["id"],
        payment_method="pm_card_visa",
        )
      
      
        if intent.status == 'requires_payment_method':
            return render(request, 'payment_failure.html')

        if confim.status == 'succeeded':
           
            transfer1 = stripe.Transfer.create(
                amount=recipient1_amount,
                currency='usd',
                destination='acct_1N663eGaS3CgF946',
                transfer_group=intent.id,
            )

            transfer2 = stripe.Transfer.create(
                amount=recipient2_amount,
                currency='usd',
                destination='acct_1N65yo2eF54Yl928',
                transfer_group=intent.id,
            )
                      
            return render(request, 'payment_success.html')
    return render(request, 'payment_success.html',{"STRIPE_PUBLISHABLE_KEY":settings.STRIPE_PUBLISHABLE_KEY})


@login_required
def stripe_data(request):
    
    if request.method=="POST":
        
        stripe_obj=stripe_details()
        publish_key=request.POST.get("publish")
        secret_key=request.POST.get("secret")
        
        stripe_obj.user_id=request.user.id
        stripe_obj.publishable_key=publish_key
        stripe_obj.secret_key=secret_key
        
        if  stripe_details.objects.filter(user_id=request.user.id).exists():
            stripe_details.objects.filter(user_id=request.user.id).update(publishable_key=publish_key,secret_key=secret_key)
        else:
            stripe_obj.save()
        
        stripe_get=stripe_details.objects.filter(user_id=request.user.id).values("publishable_key","secret_key")
        messages.success(request, "Stripe Details Update Successfully" )
        return render(request,"stripe.html",{"publish":stripe_get[0]["publishable_key"],"secret":stripe_get[0]["secret_key"]})
    stripe_get=stripe_details.objects.filter(user_id=request.user.id).values("publishable_key","secret_key")  
    if stripe_get:
        return render(request,"stripe.html",{"publish":stripe_get[0]["publishable_key"],"secret":stripe_get[0]["secret_key"]})
    else:
        return render(request,"stripe.html")


def charge_commission(request):
    admin_commision=commission_charges()
    if request.method=="POST":
        admin_comm=request.POST.get("commission")
        admin_commision.commission=admin_comm
        admin_commision.user_id=request.user.id
        if  commission_charges.objects.filter(user_id=request.user.id).exists():
            commission_charges.objects.filter(user_id=request.user.id).update(commission=admin_comm)
        else:
            admin_commision.save()
        commission_get=commission_charges.objects.filter(user_id=request.user.id).values("commission")  

        messages.success(request, "Commission set Successfully" )
        
        return render(request,"commission.html",{"commission":commission_get[0]["commission"]})
    commission_get=commission_charges.objects.filter(user_id=request.user.id).values("commission")  
    if commission_get:
        return render(request,"commission.html",{"commission":commission_get[0]["commission"]})

    return render(request,"commission.html")
        



