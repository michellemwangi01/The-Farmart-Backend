import requests

ENDPOINT = "https://the-farmart-api-flask.onrender.com"


# response = requests.get(ENDPOINT)
# print(response)

# data = response.json
# print(data)


# status_code = response.status_code
# print(status_code)

def test_can_call_endpoint():
    response = requests.get(ENDPOINT)
    assert response.status_code == 200
    pass


def test_can_cart():
    payload = {
        "username": "string",
        "password": "string"
    }
    base_url = "http://localhost:5555"
    cart_response = requests.post(ENDPOINT + "/cart", json=payload)

    assert cart_response.status_code == 200

    data = cart_response.json()
    print(data)

    cart_id = data["cart"]["cart_id"]
    get_cart_response = requests.get(ENDPOINT + f"/cart/{cart_id}", json=payload)

    assert get_cart_response.status_code == 200
    get_cart_data = get_cart_response.json()
    print(get_cart_data)
