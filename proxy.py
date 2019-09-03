# import sys
# sys.path.append("..")
from api import belong_trackingmore_api, datail_cainiao_api, detail_trackingmore_api
import random


def _choice(r, company):
    if company:
        if company == "jd":
            return True
        if random.randint(0, r):
            return True
    return False


def detail_proxy(code, company=None):
    if _choice(1, company):
        api_com = "tracking"
        result = detail_trackingmore_api.detail(code, company)
    else:
        api_com = "cainiao"
        result = datail_cainiao_api.detail(code)
    return api_com, result


def belong_to_proxy(code):
    try:
        return belong_trackingmore_api.belong(code)
    except:
        return ""

# if __name__ == "__main__":
#     print(detail_proxy("75168316327377", "zto"))
