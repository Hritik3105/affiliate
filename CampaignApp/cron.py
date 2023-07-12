from datetime import date
from CampaignApp.models import Campaign
from CampaignApp.models import Product_information
from CampaignApp.models import Product_information
from ShopifyApp.models import influencer_coupon


today = date.today()
def update_campaign_status():
    
    campaigns = Campaign.objects.filter(end_date=today).update(campaign_exp=0)
    # product_info=Product_information.objects.filter(campaignid_id__campaign_exp=0).values_list("coupon_name")
    # for coup in product_info:
    #     delete_coup=influencer_coupon.objects.filter(coupon_name__in=coup).delete()
    
    
    
    
    
    
    
   
    
    
    
    
