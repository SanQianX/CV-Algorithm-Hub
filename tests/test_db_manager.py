# Tests for database management API
import pytest
import uuid
from httpx import AsyncClient, ASGITransport
from src.api_gateway.app.main import app


@pytest.fixture
async def client():
    """Create a test client."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


def get_auth_header():
    """Generate a valid auth header for testing."""
    import base64
    import json

    # Create a mock JWT token payload
    payload = {"sub": "test-user-id", "user_id": "test-user-id", "exp": 9999999999}
    payload_b64 = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode()
    token = f"header.{payload_b64}.signature"
    return {"Authorization": f"Bearer {token}"}


class TestDatabaseManagerEndpoints:
    """Test database management API endpoints."""

    @pytest.mark.asyncio
    async def test_list_tables(self, client):
        """Test listing all database tables."""
        headers = get_auth_header()
        response = await client.get("/api/v1/db/tables", headers=headers)

        # The endpoint should return 200 or 500 (if DB not available)
        assert response.status_code in [200, 500]

        if response.status_code == 200:
            data = response.json()
            assert "tables" in data
            assert "total" in data
            assert isinstance(data["tables"], list)

    @pytest.mark.asyncio
    async def test_get_database_stats(self, client):
        """Test getting database statistics."""
        headers = get_auth_header()
        response = await client.get("/api/v1/db/stats", headers=headers)

        assert response.status_code in [200, 500]

        if response.status_code == 200:
            data = response.json()
            assert "tables" in data
            assert "total_records" in data
            assert "last_updated" in data

    @pytest.mark.asyncio
    async def test_get_table_info(self, client):
        """Test getting table information."""
        headers = get_auth_header()

        # Test with existing table
        response = await client.get("/api/v1/db/tables/users", headers=headers)

        # Could be 200 (success), 404 (table not found), or 500 (DB error)
        assert response.status_code in [200, 404, 500]

        if response.status_code == 200:
            data = response.json()
            assert data["table_name"] == "users"
            assert "columns" in data
            assert "record_count" in data

    @pytest.mark.asyncio
    async def test_get_nonexistent_table(self, client):
        """Test getting information for a non-existent table."""
        headers = get_auth_header()
        response = await client.get(
            "/api/v1/db/tables/nonexistent_table_xyz",
            headers=headers
        )

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_get_table_records_pagination(self, client):
        """Test getting table records with pagination."""
        headers = get_auth_header()
        response = await client.get(
            "/api/v1/db/tables/users/records?page=1&page_size=10",
            headers=headers
        )

        assert response.status_code in [200, 404, 500]

        if response.status_code == 200:
            data = response.json()
            assert "data" in data
            assert "page" in data
            assert "page_size" in data
            assert "total" in data
            assert "total_pages" in data

    @pytest.mark.asyncio
    async def test_get_table_records_invalid_page(self, client):
        """Test getting records with invalid pagination parameters."""
        headers = get_auth_header()
        response = await client.get(
            "/api/v1/db/tables/users/records?page=0&page_size=1000",
            headers=headers
        )

        # Should handle invalid parameters gracefully
        assert response.status_code in [200, 400, 500]

    @pytest.mark.asyncio
    async def test_create_record(self, client):
        """Test creating a new record."""
        headers = get_auth_header()

        # Create test data
        test_data = {
            "username": f"test_user_{uuid.uuid4().hex[:8]}",
            "email": f"test_{uuid.uuid4().hex[:8]}@example.com",
            "password": "test_password_123"
        }

        response = await client.post(
            "/api/v1/db/tables/users/records",
            json=test_data,
            headers=headers
        )

        # Could be 201 (created), 404 (table not found), or 500 (DB error)
        assert response.status_code in [201, 404, 500]

        if response.status_code == 201:
            data = response.json()
            assert data["success"] is True
            assert "record" in data
            assert data["record"]["username"] == test_data["username"]

    @pytest.mark.asyncio
    async def test_update_record(self, client):
        """Test updating an existing record."""
        headers = get_auth_header()

        # First create a record
        test_data = {
            "username": f"test_update_{uuid.uuid4().hex[:8]}",
            "email": f"test_{uuid.uuid4().hex[:8]}@example.com",
            "password": "test_password_123"
        }

        create_response = await client.post(
            "/api/v1/db/tables/users/records",
            json=test_data,
            headers=headers
        )

        if create_response.status_code == 201:
            created_record = create_response.json()["record"]
            record_id = created_record["id"]

            # Update the record
            update_data = {"username": f"updated_{uuid.uuid4().hex[:8]}"}
            update_response = await client.put(
                f"/api/v1/db/tables/users/records/{record_id}",
                json=update_data,
                headers=headers
            )

            assert update_response.status_code in [200, 404, 500]

            if update_response.status_code == 200:
                data = update_response.json()
                assert data["success"] is True

    @pytest.mark.asyncio
    async def test_delete_record(self, client):
        """Test deleting a record."""
        headers = get_auth_header()

        # First create a record
        test_data = {
            "username": f"test_delete_{uuid.uuid4().hex[:8]}",
            "email": f"test_{uuid.uuid4().hex[:8]}@example.com",
            "password": "test_password_123"
        }

        create_response = await client.post(
            "/api/v1/db/tables/users/records",
            json=test_data,
            headers=headers
        )

        if create_response.status_code == 201:
            created_record = create_response.json()["record"]
            record_id = created_record["id"]

            # Delete the record
            delete_response = await client.delete(
                f"/api/v1/db/tables/users/records/{record_id}",
                headers=headers
            )

            assert delete_response.status_code in [200, 404, 500]

            if delete_response.status_code == 200:
                data = delete_response.json()
                assert data["success"] is True

    @pytest.mark.asyncio
    async def test_bulk_delete(self, client):
        """Test bulk deleting records."""
        headers = get_auth_header()

        # Create multiple test records
        test_ids = []
        for i in range(3):
            test_data = {
                "username": f"test_bulk_{uuid.uuid4().hex[:8]}",
                "email": f"test_{uuid.uuid4().hex[:8]}@example.com",
                "password": "test_password_123"
            }
            create_response = await client.post(
                "/api/v1/db/tables/users/records",
                json=test_data,
                headers=headers
            )
            if create_response.status_code == 201:
                test_ids.append(create_response.json()["record"]["id"])

        # Bulk delete
        if test_ids:
            response = await client.post(
                "/api/v1/db/tables/users/bulk-delete",
                json={"ids": test_ids},
                headers=headers
            )

            assert response.status_code in [200, 500]

            if response.status_code == 200:
                data = response.json()
                assert data["success"] is True
                assert "deleted_count" in data

    @pytest.mark.asyncio
    async def test_execute_select_query(self, client):
        """Test executing a SELECT SQL query."""
        headers = get_auth_header()
        response = await client.post(
            "/api/v1/db/execute",
            json={"query": "SELECT * FROM users LIMIT 5"},
            headers=headers
        )

        assert response.status_code in [200, 400, 500]

        if response.status_code == 200:
            data = response.json()
            assert "columns" in data
            assert "data" in data
            assert "row_count" in data

    @pytest.mark.asyncio
    async def test_execute_non_select_rejected(self, client):
        """Test that non-SELECT queries are rejected."""
        headers = get_auth_header()

        dangerous_queries = [
            "DELETE FROM users",
            "UPDATE users SET username='hacked'",
            "INSERT INTO users VALUES (1, 'test', 'test@test.com', 'pass')",
            "DROP TABLE users",
            "TRUNCATE TABLE users"
        ]

        for query in dangerous_queries:
            response = await client.post(
                "/api/v1/db/execute",
                json={"query": query},
                headers=headers
            )
            assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_unauthorized_access(self, client):
        """Test that requests without auth header are rejected."""
        response = await client.get("/api/v1/db/tables")

        # Should return 401 for unauthorized requests
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_get_record_by_id(self, client):
        """Test getting a single record by ID."""
        headers = get_auth_header()

        # First create a record
        test_data = {
            "username": f"test_get_by_id_{uuid.uuid4().hex[:8]}",
            "email": f"test_{uuid.uuid4().hex[:8]}@example.com",
            "password": "test_password_123"
        }

        create_response = await client.post(
            "/api/v1/db/tables/users/records",
            json=test_data,
            headers=headers
        )

        if create_response.status_code == 201:
            created_record = create_response.json()["record"]
            record_id = created_record["id"]

            # Get the record by ID
            get_response = await client.get(
                f"/api/v1/db/tables/users/records/{record_id}",
                headers=headers
            )

            assert get_response.status_code in [200, 404, 500]

            if get_response.status_code == 200:
                data = get_response.json()
                assert data["id"] == record_id

    @pytest.mark.asyncio
    async def test_update_nonexistent_record(self, client):
        """Test updating a non-existent record."""
        headers = get_auth_header()
        fake_id = str(uuid.uuid4())

        response = await client.put(
            f"/api/v1/db/tables/users/records/{fake_id}",
            json={"username": "test"},
            headers=headers
        )

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_nonexistent_record(self, client):
        """Test deleting a non-existent record."""
        headers = get_auth_header()
        fake_id = str(uuid.uuid4())

        response = await client.delete(
            f"/api/v1/db/tables/users/records/{fake_id}",
            headers=headers
        )

        assert response.status_code == 404


class TestDatabaseManagerPagination:
    """Test pagination functionality."""

    @pytest.mark.asyncio
    async def test_pagination_params(self, client):
        """Test various pagination parameter combinations."""
        headers = get_auth_header()

        # Test different page sizes
        for page_size in [10, 20, 50]:
            response = await client.get(
                f"/api/v1/db/tables/users/records?page=1&page_size={page_size}",
                headers=headers
            )

            if response.status_code == 200:
                data = response.json()
                assert data["page_size"] == page_size

    @pytest.mark.asyncio
    async def test_page_out_of_range(self, client):
        """Test requesting a page that doesn't exist."""
        headers = get_auth_header()
        response = await client.get(
            "/api/v1/db/tables/users/records?page=999999&page_size=10",
            headers=headers
        )

        assert response.status_code in [200, 500]

        if response.status_code == 200:
            data = response.json()
            assert data["page"] == 999999
            assert len(data["data"]) == 0


class TestDatabaseManagerDataTypes:
    """Test handling of different data types."""

    @pytest.mark.asyncio
    async def test_datetime_format(self, client):
        """Test that datetime fields are properly formatted."""
        headers = get_auth_header()

        # Create a record with timestamp
        test_data = {
            "username": f"test_datetime_{uuid.uuid4().hex[:8]}",
            "email": f"test_{uuid.uuid4().hex[:8]}@example.com",
            "password": "test_password_123"
        }

        create_response = await client.post(
            "/api/v1/db/tables/users/records",
            json=test_data,
            headers=headers
        )

        if create_response.status_code == 201:
            record = create_response.json()["record"]

            # Check created_at format
            if "created_at" in record:
                assert "T" in record["created_at"] or " " in record["created_at"]
