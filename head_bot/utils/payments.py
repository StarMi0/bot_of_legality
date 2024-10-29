import urllib.parse
import requests

from utils.utils import get_expired_time

# Example usage:
base_url = "https://alfa.rbsuat.com/payment"
# orderNumber = "1234567891"
# amount = 5000  # Amount in kopecks (or cents)
returnUrl = "https://t.me/Online_lawyers_bot"
userName = "r-club226061201_vk-api"
password = "r-club226061201_vk*?1"


def create_payment_link(orderNumber, amount):
    # Creating the query parameters dictionary with required fields
    expirationDate = get_expired_time()
    params = {
        "orderNumber": orderNumber,
        "amount": int(amount)*100,
        "returnUrl": returnUrl,
        "expirationDate": expirationDate
    }

    # Adding authentication fields if provided
    if userName:
        params["userName"] = userName
    if password:
        params["password"] = password


    # Encoding the parameters to be included in the URL
    query_string = urllib.parse.urlencode(params)

    # Constructing the full payment URL
    payment_url = f"{base_url}/rest/register.do?{query_string}"
    res = requests.get(url=payment_url, params=params)
    return res.json().get('formUrl')


# Example with username and password
# payment_link_with_auth = create_payment_link(base_url, orderNumber, amount, returnUrl, userName=userName,
#                                              password=password)
# print(payment_link_with_auth)


def check_order_status(orderNumber) -> bool:
    # Ensure one of orderId or orderNumber is provided

    # Creating the payload with required fields
    params = {
        "userName": userName,
        "password": password,
        "orderNumber": orderNumber

    }


    # Constructing the full URL for the status request
    url = f"{base_url}/rest/getOrderStatusExtended.do"

    # Sending the POST request
    response = requests.post(url, params=params)

    # Checking for HTTP request errors
    response.raise_for_status()
    print(response.json())
    status = response.json().get('orderStatus')
    # Returning the response in JSON format
    return True if status == 2 else False


# print(check_order_status(base_url, userName, password, orderNumber))
# Example with token
# payment_link_with_token = create_payment_link(base_url, orderNumber, amount, returnUrl, token=token)
# print(payment_link_with_token)
