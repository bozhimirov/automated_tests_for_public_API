import requests

ENDPOINT = 'https://demoqa.com/'


def register_user(data):
    return requests.post(ENDPOINT + 'Account/v1/User', json=data)


def is_user_authorized(data):
    return requests.post(ENDPOINT + 'Account/v1/Authorized', json=data)


def get_books():
    return requests.get(ENDPOINT + 'BookStore/v1/Books')


def get_user(user_id):
    return requests.get(ENDPOINT + f'Account/v1/User/{user_id}')


def authenticate_user(data):
    return requests.post(ENDPOINT + f'Account/v1/GenerateToken', json=data)


def check_if_user_is_already_registered():
    var = 0
    while True:
        data = {
            "userName": f'usr{var}',
            "password": "Pa$sw0rd",
        }
        registered_response = is_user_authorized(data)
        if registered_response.status_code == 404 and registered_response.json()["code"] == "1207":
            break
        else:
            var += 1
    return data


def unused_data():
    data = check_if_user_is_already_registered()
    return data


def test_can_call_endpoint():
    response = requests.get(ENDPOINT)
    assert response.status_code == 200


def test_can_register_user_with_valid_data():
    data = unused_data()
    user = register_user(data)
    assert user.status_code == 201
    user_response = user.json()
    assert user_response["username"] == data["userName"]
    user_check = is_user_authorized(data)
    assert user_check.status_code == 200


def test_cannot_register_user_with_same_username():
    data = unused_data()
    user = register_user(data)
    assert user.status_code == 201
    user_response = user.json()
    assert user_response["username"] == data["userName"]
    same_user = register_user(data)
    assert same_user.status_code == 406
    same_user_response = same_user.json()
    assert same_user_response["code"] == "1204"


def test_cannot_register_user_without_username():
    data = {
        "userName": '',
        "password": "Pa$sw0rd",
    }

    user = register_user(data)
    assert user.status_code == 400
    user_response = user.json()
    assert user_response["code"] == "1200"
    user_check = is_user_authorized(data)
    assert user_check.status_code == 400
    user_check_response = user_check.json()
    assert user_check_response["code"] == "1200"


def test_cannot_register_user_without_pass():
    data = unused_data()
    data["password"] = ""

    user = register_user(data)
    user_response = user.json()
    assert user.status_code == 400
    assert user_response["code"] == "1200"
    user_check = is_user_authorized(data)
    assert user_check.status_code == 400
    user_check_response = user_check.json()
    assert user_check_response["code"] == "1200"


def test_cannot_register_user_with_wrong_pass():

    passwords = {
        "short_pass": "Pa$sw0r",
        "no_capital_letter_pass": "pa$sw0rd",
        "no_sym_pass": "Passw0rd",
        "no_num_pass": "Pa$sword",
    }

    for value in passwords.values():

        data = unused_data()
        data["password"] = value

        user = register_user(data)
        assert user.status_code == 400
        user_response = user.json()
        assert user_response["code"] == "1300"
        user_check = is_user_authorized(data)
        assert user_check.status_code == 404
        user_check_response = user_check.json()
        assert user_check_response["code"] == "1207"


def test_user_cannot_add_imagined_book_to_collection():
    data = unused_data()
    user = register_user(data)
    user_response = user.json()

    assert user_response['books'] == []
    fake_data = {
        'isbn': '007'
    }
    fake_book_data = {
        "userId": user_response["userID"],
        "collectionOfIsbns": [
            {
                "isbn": fake_data['isbn']
            }
        ]
    }
    auth_details = (data["userName"], data["password"])
    r = requests.post(ENDPOINT + f'BookStore/v1/Books', auth=auth_details, json=fake_book_data)
    assert r.status_code == 400
    res_user = requests.get(ENDPOINT + f'Account/v1/User/{user_response["userID"]}', auth=auth_details)
    res_user_data = res_user.json()

    assert res_user_data['books'] == []


def test_can_add_books_to_collection():
    data = unused_data()
    auth_details = (data["userName"], data["password"])
    user = register_user(data)
    user_response = user.json()
    books = get_books()
    assert user_response['books'] == []
    books_response = books.json()
    assert books.status_code == 200
    book_selected = books_response["books"][1]
    book_data = {
        "userId": user_response["userID"],
        "collectionOfIsbns": [
            {
                "isbn": book_selected['isbn']
            }
        ]
    }
    requests.post(ENDPOINT + f'BookStore/v1/Books', auth=auth_details, json=book_data)
    res_user = requests.get(ENDPOINT + f'Account/v1/User/{user_response["userID"]}', auth=auth_details)
    assert book_selected == res_user.json()['books'][0]


def test_can_replace_book_in_collection():
    data = unused_data()
    user = register_user(data)
    user_response = user.json()
    assert user_response['books'] == []
    books = get_books()
    auth_details = (data["userName"], data["password"])
    assert books.status_code == 200
    books_response = books.json()
    selected_book = books_response["books"][0]
    book_data = {
        "userId": user_response["userID"],
        "collectionOfIsbns": [
            {
                "isbn": selected_book['isbn']
            }
        ]
    }
    requests.post(ENDPOINT + f'BookStore/v1/Books', auth=auth_details, json=book_data)
    res_user = requests.get(ENDPOINT + f'Account/v1/User/{user_response["userID"]}', auth=auth_details)
    res_user_data = res_user.json()
    assert selected_book == res_user_data['books'][0]
    new_book = books_response["books"][1]
    new_book_data = {
        "userId": user_response["userID"],
        "isbn": new_book['isbn']
    }
    rr = requests.put(ENDPOINT + f'BookStore/v1/Books/{selected_book["isbn"]}', auth=auth_details, json=new_book_data)
    assert rr.status_code == 200
    res_user_new = requests.get(ENDPOINT + f'Account/v1/User/{user_response["userID"]}', auth=auth_details)
    assert res_user_new.status_code == 200
    res_user_data_new = res_user_new.json()
    assert selected_book != res_user_data_new['books'][0]
    assert new_book == res_user_data_new['books'][0]


def test_can_remove_books_from_collection():
    books = get_books()
    assert books.status_code == 200
    books_response = books.json()
    selected_book = books_response["books"][0]
    data = unused_data()
    user = register_user(data)
    user_response = user.json()
    assert user_response['books'] == []
    book_data = {
        "userId": user_response["userID"],
        "collectionOfIsbns": [
            {
                "isbn": selected_book['isbn']
            }
        ]
    }
    auth_details = (data["userName"], data["password"])
    rr = requests.post(ENDPOINT + f'BookStore/v1/Books', auth=auth_details, json=book_data)
    assert rr.status_code == 201
    res_user = requests.get(ENDPOINT + f'Account/v1/User/{user_response["userID"]}', auth=auth_details)
    res_user_data = res_user.json()
    assert selected_book == res_user_data['books'][0]
    new_book_data = {
       "isbn": selected_book["isbn"],
       "userId": user_response["userID"]
    }
    r = requests.delete(ENDPOINT + f'BookStore/v1/Book', auth=auth_details, json=new_book_data)
    assert r.status_code == 204
    res_user_new = requests.get(ENDPOINT + f'Account/v1/User/{user_response["userID"]}', auth=auth_details)
    res_user_data_new = res_user_new.json()
    assert res_user_data_new['books'] == []


def test_cannot_remove_not_added_book_to_collection():
    data = unused_data()
    user = register_user(data)
    user_response = user.json()
    assert user_response['books'] == []

    books = get_books()
    assert books.status_code == 200
    books_response = books.json()
    selected_book = books_response["books"][0]
    auth_details = (data["userName"], data["password"])
    new_book_data = {
        "isbn": selected_book["isbn"],
        "userId": user_response["userID"]
    }
    r = requests.delete(ENDPOINT + f'BookStore/v1/Book', auth=auth_details, json=new_book_data)
    assert r.status_code == 400
    res_user_new = requests.get(ENDPOINT + f'Account/v1/User/{user_response["userID"]}', auth=auth_details)
    res_user_data_new = res_user_new.json()
    assert res_user_data_new['books'] == []


def test_validate_pages_on_book_from_store():
    books = get_books()
    assert books.status_code == 200
    books_response = books.json()
    for i in range(len(books_response["books"])):
        if books_response["books"][i]["isbn"] == '9781491904244':
            assert books_response["books"][i]["pages"] == 278
