def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_profile_get_creates_singleton_and_updates(client):
    resp = client.get("/profile")
    assert resp.status_code == 200
    profile = resp.json()
    assert profile["name"] is None

    resp = client.put("/profile", json={**profile, "name": "Jane Doe", "skills": ["python"]})
    assert resp.status_code == 200
    assert resp.json()["name"] == "Jane Doe"
    assert resp.json()["skills"] == ["python"]

    # Getting again returns the same updated singleton, not a new row.
    resp = client.get("/profile")
    assert resp.json()["name"] == "Jane Doe"


def test_preferences_crud(client):
    resp = client.get("/preferences")
    assert resp.status_code == 200
    prefs = resp.json()

    resp = client.put("/preferences", json={**prefs, "remote_only": True, "min_salary": 100000})
    assert resp.status_code == 200
    assert resp.json()["remote_only"] is True
    assert resp.json()["min_salary"] == 100000


def test_jobs_list_empty_initially(client):
    resp = client.get("/jobs")
    assert resp.status_code == 200
    assert resp.json() == []


def test_get_nonexistent_job_returns_404(client):
    resp = client.get("/jobs/does-not-exist")
    assert resp.status_code == 404


def test_application_lifecycle(client):
    # Seed a job directly through aggregation isn't practical here (needs network),
    # so verify the applications API's own validation and CRUD behavior instead.
    resp = client.post("/applications", json={"job_id": "nonexistent-job", "status": "InvalidStatus"})
    assert resp.status_code == 400

    resp = client.patch("/applications/nonexistent-id", json={"status": "Applied"})
    assert resp.status_code == 404

    resp = client.delete("/applications/nonexistent-id")
    assert resp.status_code == 404


def test_dashboard_metrics_on_empty_db(client):
    resp = client.get("/dashboard/metrics")
    assert resp.status_code == 200
    body = resp.json()
    assert body["total_jobs"] == 0
    assert body["applications"] == 0


def test_dashboard_analytics_on_empty_db(client):
    resp = client.get("/dashboard/analytics")
    assert resp.status_code == 200
    body = resp.json()
    assert body["application_success_rate"] == 0.0
    assert body["source_effectiveness"] == {}


def test_resume_upload_rejects_unsupported_format(client):
    resp = client.post(
        "/resume/upload",
        files={"file": ("resume.txt", b"just some text", "text/plain")},
    )
    assert resp.status_code == 400
