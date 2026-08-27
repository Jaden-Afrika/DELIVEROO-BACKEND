class TestSignup:
    def test_signup_success(self, client, db):
        resp = client.post("/auth/signup", {
            "name": "New User",
            "email": "new@example.com",
            "password": "password123",
            "confirmPassword": "password123",
        }, format="json")
        assert resp.status_code == 201
        data = resp.json()
        assert "access_token" in data
        assert data["user"]["name"] == "New User"
        assert data["user"]["email"] == "new@example.com"
        assert data["user"]["role"] == "user"

    def test_signup_duplicate_email(self, client, seed_users):
        resp = client.post("/auth/signup", {
            "name": "Dup",
            "email": "test@example.com",
            "password": "password123",
            "confirmPassword": "password123",
        }, format="json")
        assert resp.status_code == 409

    def test_signup_validation_error(self, client, db):
        resp = client.post("/auth/signup", {"email": "bad"}, format="json")
        assert resp.status_code == 422
        assert resp.json()["error"]["code"] == "VALIDATION_ERROR"
        assert "details" in resp.json()["error"]


class TestLogin:
    def test_login_success(self, client, seed_users):
        resp = client.post("/auth/login", {
            "email": "test@example.com",
            "password": "password123",
        }, format="json")
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert data["user"]["role"] == "user"

    def test_login_wrong_password(self, client, seed_users):
        resp = client.post("/auth/login", {
            "email": "test@example.com",
            "password": "wrong",
        }, format="json")
        assert resp.status_code == 401

    def test_login_nonexistent_user(self, client, db):
        resp = client.post("/auth/login", {
            "email": "nobody@example.com",
            "password": "password123",
        }, format="json")
        assert resp.status_code == 401


class TestMe:
    def test_me_authenticated(self, client, auth_header):
        resp = client.get("/auth/me", **auth_header)
        assert resp.status_code == 200
        data = resp.json()
        assert data["user"]["email"] == "test@example.com"

    def test_me_unauthenticated(self, client):
        resp = client.get("/auth/me")
        assert resp.status_code == 401


class TestLogout:
    def test_logout(self, client, auth_header):
        resp = client.post("/auth/logout", **auth_header, format="json")
        assert resp.status_code == 200
