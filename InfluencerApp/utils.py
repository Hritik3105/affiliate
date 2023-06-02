from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils import six   
from rest_framework.views import APIView,View
from rest_framework import generics
from rest_framework import  status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.shortcuts import redirect
from AdminApp.models import *                                       

class TokenGen(PasswordResetTokenGenerator):  
    def _make_hash_value(self, user, timestamp):  

        return (  
            six.text_type(user.id) + six.text_type(timestamp) +  
            six.text_type(user.is_active)  
        )  
account_activation_token = TokenGen()  


class VerificationView(generics.GenericAPIView):
    def get(self,request,token,id):
        user=User.objects.get(id=id)
        if not user.verify_email:
            user.verify_email=True
            user.save()
        return Response({"Success": "Influencer Register Successfully"},status=status.HTTP_201_CREATED)
        
        
