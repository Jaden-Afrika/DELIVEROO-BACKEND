class TestSignup:
    def test_signup_success(self, client, db_session):
        resp = client.post("/auth/signup", json={
            "name": "New User",
            "email": "new@example.com",
            "password": "password123",
            "confirmPassword": "password123",
        })
        assert resp.status_code == 201
        data = resp.get_json()
        assert "access_token" in data
        assert data["user"]["name"] == "New User"
        assert data["user"]["email"] == "new@example.com"
        assert data["user"]["role"] == "user"

    def test_signup_duplicate_email(self, client, seed_users):
        resp = client.post("/auth/signup", json={
            "name": "Dup",
            "email": "test@example.com",
            "password": "password123",
            "confirmPassword": "password123",
        })
        assert resp.status_code == 409

    def test_signup_validation_error(self, client, db_session):
        resp = client.post("/auth/signup", json={"email": "bad"})
        assert resp.status_code == 422


class TestLogin:
    def test_login_success(self, client, seed_users):
        resp = client.post("/auth/login", json={
            "email": "test@example.com",
            "password": "password123",
        })
        assert resp.status_code == 200
        data = resp.get_json()
        assert "access_token" in data
        assert data["user"]["role"] == "user"

    def test_login_wrong_password(self, client, seed_users):
        resp = client.post("/auth/login", json={
            "email": "test@example.com",
            "password": "wrong",
        })
        assert resp.status_code == 401

    def test_login_nonexistent_user(self, client, db_session):
        resp = client.post("/auth/login", json={
            "email": "nobody@example.com",
            "password": "password123",
        })
        assert resp.status_code == 401


class TestMe:
    def test_me_authenticated(self, client, auth_header):
        resp = client.get("/auth/me", headers=auth_header)
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["user"]["email"] == "test@example.com"

    def test_me_unauthenticated(self, client):
        resp = client.get("/auth/me")
        assert resp.status_code == 401


class TestLogout:
    def test_logout(self, client, auth_header):
        resp = client.post("/auth/logout", headers=auth_header)
        assert resp.status_code == 200
