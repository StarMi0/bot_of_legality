import urllib.parse


def create_payment_link(base_url, orderNumber, amount, returnUrl, userName=None, password=None, token=None):
    # Creating the query parameters dictionary with required fields
    params = {
        "orderNumber": orderNumber,
        "amount": amount,
        "returnUrl": returnUrl
    }

    # Adding authentication fields if provided
    if userName:
        params["userName"] = userName
    if password:
        params["password"] = password
    if token:
        params["token"] = token

    # Encoding the parameters to be included in the URL
    query_string = urllib.parse.urlencode(params)

    # Constructing the full payment URL
    payment_url = f"{base_url}/rest/register.do?{query_string}"

    return payment_url


# Example usage:
base_url = "https://alfa.rbsuat.com/payment"
orderNumber = "1234567890"
amount = 5000  # Amount in kopecks (or cents)
returnUrl = "https://example.com/success"
userName = "your_user_name"
password = "your_password"
token = "your_token"

# Example with username and password
payment_link_with_auth = create_payment_link(base_url, orderNumber, amount, returnUrl, userName=userName,
                                             password=password)
print(payment_link_with_auth)

# Example with token
payment_link_with_token = create_payment_link(base_url, orderNumber, amount, returnUrl, token=token)
print(payment_link_with_token)
