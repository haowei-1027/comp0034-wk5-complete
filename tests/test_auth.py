# Authentication tests


def test_register_success(client, random_user_json):
    """
    GIVEN a valid format email and password for a user not already registered
    WHEN an account is created
    THEN the status code should be 201
    """
    user_register = client.post('/register', json=random_user_json, content_type="application/json")
    assert user_register.status_code == 201


def test_login_success(client, new_user):
    """
    GIVEN a valid format email and password for a user already registered
    WHEN /login is called
    THEN the status code should be 201
    """
    user_register = client.post('/login', json=new_user, content_type="application/json")
    assert user_register.status_code == 201


# TODO: Debug, does not work. Appears not to identify current_user.
def test_user_logged_in_user_can_edit_region(client, new_user, login_token, new_region):
    """
    GIVEN a registered user that is successfully logged in
    AND a route that is protected by login
    AND a new Region that can be edited
    WHEN a PATCH request to /regions/<code> is made
    THEN the HTTP status code should be 200
    AND the response content should include the message 'Region <NOC_code> updated'
    """
    code = new_region['NOC']
    url = f"/regions/{code}"
    new_region_notes = {'notes': 'An updated note'}
    # pass the token in the headers of the HTTP request
    headers = {
        'content-type': "application/json",
        'Authorization': login_token
    }
    response = client.patch(url, json=new_region_notes, headers=headers)
    assert response.json['message'] == 'Region NEW updated.'
    assert response.status_code == 200


def test_user_not_logged_in_cannot_edit_region(client, new_user, new_region):
    """
    GIVEN a registered user that is not logged in
    AND a route that is protected by login
    AND a new Region that can be edited
    WHEN a PATCH request to /regions/<code> is made
    THEN the HTTP response status code should be 401
    """
    new_region_notes = {'notes': 'An updated note'}
    code = new_region['NOC']
    response = client.patch(f"/regions/{code}", json=new_region_notes)
    assert response.status_code == 401
