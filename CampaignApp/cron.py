from datetime import date
from CampaignApp.models import Campaign


today = date.today()
def update_campaign_status():
    
    campaigns = Campaign.objects.filter(end_date=today).update(campaign_exp=0)
    
    
    
    