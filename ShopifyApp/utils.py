from AdminApp.models import User
from StoreApp.models import Store
import requests
from Affilate_Marketing.settings import base_url ,headers ,SHOPIFY_API_KEY,SHOPIFY_API_SECRET,API_VERSION


def access_token(self,request):
    user_obj=User.objects.filter(id=self.request.user.id)
    shop=user_obj.values("shopify_url")[0]["shopify_url"]
    acc_tok=Store.objects.filter(store_name=shop).values("access_token")[0]["access_token"]
   
    return acc_tok,shop


def one_time_discount(price_id,shop,headers,discount_code):
    
        discount_code_endpoint = f'https://{SHOPIFY_API_KEY}:{SHOPIFY_API_SECRET}@{shop}/admin/api/{API_VERSION}/price_rules/{price_id}/discount_codes.json'

        discount_code_data = {
            'discount_code': {
                'code': discount_code,
                'usage_limit': None,
                'customer_selection': 'all',
                "once_per_customer": True, 
                'starts_at': '2023-04-06T00:00:00Z',
                'ends_at': '2023-04-30T23:59:59Z'
            }
        }


        discount_code_response = requests.post(discount_code_endpoint, json=discount_code_data,headers=headers)
    
        if discount_code_response.status_code == 201:
            return discount_code_response
        else:
    
            pp=delete_price_rule(price_id,shop, headers)
            return discount_code_response
        
        
def delete_price_rule(price_rule_id, shop, headers):
   
    
    delete_url = f'https://{shop}/admin/api/{API_VERSION}/price_rules/{price_rule_id}.json'
    response = requests.delete(delete_url, headers=headers)

    if response.status_code == 200:
        return True  # Price rule deleted successfully
    else:
        return False  # Failed to delete price rule