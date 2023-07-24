from django.urls import path
from CampaignApp.views import *

urlpatterns = [
    path('vendor/register/',Register.as_view(),name="vendor"),
    path('vendor/login/',VendorLogin.as_view(),name="vendorlogin"),
    path('create/',CreateCampaign.as_view(),name="campaign"),
    path('inflcampaign/create/',InfluencerCampaign.as_view(),name="inflcampaign"),
    path('active/',ActiveList.as_view(),name="campaignlist"),
    path('pending/',PendingList.as_view(),name="pending"),
    path('delete/<int:id>/',DeleteCampaign.as_view(),name="deletecamp"),
    path('influencer/list/',InfluencerList.as_view(),name="influencer"),
    path('product/list/',ProductList.as_view(),name="productlist"),
    path('get/token/',GetToken.as_view(),name="token"),
    path('update/<int:pk>/',UpdateCampaign.as_view(),name="campaignupdate"),
    path('count/',CountCampaign.as_view(),name="count"),
    path('product/url/',ProductUrl.as_view(),name="url"),
    path('request/',RequestSents.as_view(),name="request"),
    path('market/list/',MarketplaceList.as_view(),name="market"),
    path('single/<int:id>/',GetCampaign.as_view(),name="singlecampaign"),  
    path('profile/<int:id>/',ProfileUpdate.as_view(),name="profile"),
    path('instagram/',InstagramFollower.as_view(),name="instagram"),   
    path('user/id/',GetUserId.as_view(),name="userid"),        
    path('draft/list/',DraftList.as_view(),name="draft"),   
    path('markdraft/list/',MarketplaceDraftList.as_view(),name="markdraft"), 
    path('markplace/camp',RequestCampaign.as_view(),name="requestmark"), 
    path('draft/update/<int:pk>/',DraftStatusUpdate.as_view(),name="draftupdate"), 
    path('vendor/accept/<int:id>/<int:pk>/',VendorAccept.as_view(),name="vendoraccept"), 
    path('vendor/decline/<int:id>/<int:pk>/',DeclineVendor.as_view(),name="vendordecline"), 
    path("vendor_approval/",VendorApprovalList.as_view(),name="vendorapproval"),
    path("vendor_decline/",VendorDeclineList.as_view(),name="vendordecline"),
    path("notification/list/",InfluencerNotification.as_view(),name="Inflnotify"),
    path("change/status/",ChangeNotifinflStatus.as_view(),name="changenotify"),
    path("analytics/",Analytics.as_view(),name="analytics"),
    path("sale_record/",SalesRecord.as_view(),name="sale_record"),
    path("sale_coup/",CampaignSales.as_view(),name="exp_camp"),
    path("detail/",VendorStripe.as_view(),name="detail"),
    path("balance",Balance.as_view(),name="balance"),
    path("infl_stripe",InfluencerStripeDetail.as_view(),name="infl_stripe"),
    path("transfer_money/",TranferMoney.as_view(),name="transfer_money"),
    path("influecercamsale/",InfluencerCampSale.as_view(),name="influecercamsale"),
    path("campaignexp/",CampaignExpList.as_view(),name="campaignexp"),
    path("marketcampaignexp/",MarketplaceExpList.as_view(),name="marketcampaignexp"),
    path("marketplacewebsite/",MarketplaceWebsiteList.as_view(),name="marketplacewebsite"),
    path("marketapproval/",MarketplaceApprovalList.as_view(),name="marketapproval"),
    path("marketplaceaccept/<int:id>/<int:pk>/",MarketplaceAccept.as_view(),name="marketplaceaccept"),
    path("marketplacedecline/<int:id>/<int:pk>/",MarketplaceDecline.as_view(),name="marketplacedecline"),
    path("market_approval/",MarketPlaceApprovalList.as_view(),name="marketapproval"),
    path("market_decline/",MarketDeclineList.as_view(),name="marketdecline"),
    path("checkout_session/",BuySubscription.as_view(),name="checkout_session"),
    path("success/",Success.as_view(),name="success"),
    path("cancel/",Cancel.as_view(),name="cancel"),
    path("InfluencerProfile/",InfluencerProfile.as_view(),name="InfluencerProfile"),
    path("payouts/",Payout.as_view(),name="payouts"),
    # path("entity/",Checkout.as_view(),name="entity"),
    path("approvaldet/<int:id>/",ApprovalCampaignDetails.as_view(),name="approvaldet"),
    path("admintransfer",AdminTransfer.as_view(),name="admintransfer"),
    path("adminmoney/",AdminTranferMoney.as_view(),name="adminmoney"),
   
   
    
]
