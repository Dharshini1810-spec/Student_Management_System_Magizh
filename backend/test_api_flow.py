import urllib.request
import json
import sys
import uuid

API_BASE = "http://127.0.0.1:8000/api/v1"

def api_request(url, method="GET", headers=None, data=None):
    if headers is None:
        headers = {}
    
    req_data = None
    if data is not None:
        req_data = json.dumps(data).encode("utf-8")
        headers["Content-Type"] = "application/json"
    
    req = urllib.request.Request(f"{API_BASE}{url}", headers=headers, method=method, data=req_data)
    
    try:
        with urllib.request.urlopen(req) as response:
            res_body = response.read().decode("utf-8")
            return response.status, json.loads(res_body)
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8")
        try:
            return e.code, json.loads(err_body)
        except Exception:
            return e.code, {"message": err_body}
    except Exception as e:
        return 0, {"message": str(e)}

def test_flow():
    # 1. Login as Super Admin
    print("--- 1. Logging in as Super Admin ---")
    status, res = api_request("/auth/login", "POST", data={
        "email": "admin@sms.com",
        "password": "SuperAdminSecurePassword123!"
    })
    
    if status != 200:
        print("Super Admin login failed, attempting signup...")
        status, res = api_request("/auth/signup", "POST", data={
            "email": "admin@sms.com",
            "password": "SuperAdminSecurePassword123!"
        })
        print("Signup status:", status, res)
        
        status, res = api_request("/auth/login", "POST", data={
            "email": "admin@sms.com",
            "password": "SuperAdminSecurePassword123!"
        })
        print("Login after signup status:", status, res)

    assert status == 200, "Super Admin login failed"
    sa_token = res["data"]["access_token"]
    sa_headers = {"Authorization": f"Bearer {sa_token}"}
    print("Logged in as Super Admin successfully.")

    # 2. Check and Create Demo Admin
    print("\n--- 2. Checking/Creating Demo Admin ---")
    status, res = api_request("/users?role=ADMIN", "GET", headers=sa_headers)
    assert status == 200, "Failed to list users"
    
    admin_id = None
    for u in res["data"]["users"]:
        if u["email"] == "demo_admin@sms.com":
            admin_id = u["id"]
            break
            
    if not admin_id:
        print("Creating demo admin...")
        status, res = api_request("/users", "POST", headers=sa_headers, data={
            "email": "demo_admin@sms.com",
            "role": "ADMIN",
            "name": "Demo Admin"
        })
        assert status in [200, 201], f"Failed to create demo admin: {res}"
        admin_id = res["data"]["id"]
        print("Demo Admin created with ID:", admin_id)
    else:
        print("Demo Admin already exists with ID:", admin_id)

    # 3. Check and Create Demo Student
    print("\n--- 3. Checking/Creating Demo Student ---")
    status, res = api_request("/students", "GET", headers=sa_headers)
    assert status == 200, "Failed to list students"
    
    student_id = None
    for s in res["data"]["students"]:
        if s["email"] == "demo_student@sms.com":
            student_id = s["id"]
            break
            
    if not student_id:
        print("Creating demo student...")
        status, res = api_request("/students", "POST", headers=sa_headers, data={
            "name": "Demo Student",
            "email": "demo_student@sms.com",
            "password": "StandardPassword123!"
        })
        assert status in [200, 201], f"Failed to create demo student: {res}"
        student_id = res["data"]["id"]
        print("Demo Student created with ID:", student_id)
    else:
        print("Demo Student already exists with ID:", student_id)

    # 4. Assign Admin Coordinator to Student
    print("\n--- 4. Assigning Admin Coordinator to Student ---")
    status, res = api_request(f"/students/{student_id}/assign-admin", "POST", headers=sa_headers, data={
        "admin_id": admin_id
    })
    assert status in [200, 201], f"Failed to assign admin: {res}"
    print("Admin assigned to student successfully.")

    # 5. Set custom settings for early checkout testing
    print("\n--- 5. Setting deadlines check-in='09:00', check-out='23:59' to test early check-out ---")
    status, res = api_request("/attendance/settings", "POST", headers=sa_headers, data={
        "check_in_deadline": "09:00",
        "check_out_deadline": "23:59"
    })
    assert status == 200, f"Failed to save settings: {res}"
    print("Deadlines settings saved successfully.")

    # 6. Log in as Student
    print("\n--- 6. Logging in as Student ---")
    status, res = api_request("/auth/login", "POST", data={
        "email": "demo_student@sms.com",
        "password": "StandardPassword123!"
    })
    assert status == 200, f"Student login failed: {res}"
    student_token = res["data"]["access_token"]
    student_headers = {"Authorization": f"Bearer {student_token}"}
    print("Student logged in successfully.")

    # 7. Student Check-in (should create request as current time > 09:00)
    print("\n--- 7. Performing Student Check-in ---")
    status, res = api_request("/attendance/check-in", "POST", headers=student_headers, data={
        "reason": "Late check in due to traffic delay"
    })
    
    checkin_request_id = None
    if status == 400 and "already checked in" in res["message"].lower():
        print("Already checked in today, skipping check-in request test.")
    else:
        assert status == 200, f"Check-in failed: {res}"
        assert res["data"]["status"] == "LATE_REQUEST_PENDING", f"Expected late request pending, got: {res}"
        checkin_request_id = res["data"]["request"]["id"]
        print("Check-in request created. ID:", checkin_request_id)

    # 8. Student Check-out (should create request as current time < 23:59)
    print("\n--- 8. Performing Student Check-out ---")
    status, res = api_request("/attendance/check-out", "POST", headers=student_headers, data={
        "reason": "Leaving early for dental appointment"
    })
    assert status == 200, f"Check-out failed: {res}"
    assert res["data"]["status"] == "LATE_REQUEST_PENDING", f"Expected late request pending (early check-out), got: {res}"
    checkout_request_id = res["data"]["request"]["id"]
    print("Check-out request created. ID:", checkout_request_id)

    # 9. Log in as Admin
    print("\n--- 9. Logging in as Admin ---")
    status, res = api_request("/auth/login", "POST", data={
        "email": "demo_admin@sms.com",
        "password": "StandardPassword123!"
    })
    assert status == 200, f"Admin login failed: {res}"
    admin_token = res["data"]["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    print("Admin logged in successfully.")

    # 10. Admin view requests
    print("\n--- 10. Admin Listing Attendance Requests ---")
    status, res = api_request("/attendance/requests", "GET", headers=admin_headers)
    assert status == 200, f"Failed to list requests: {res}"
    req_ids = [r["id"] for r in res["data"]["requests"]]
    print("Requests found:", len(req_ids))
    if checkin_request_id:
        assert checkin_request_id in req_ids, "Check-in request not visible to Admin"
    assert checkout_request_id in req_ids, "Check-out request not visible to Admin"
    print("Requests are visible to assigned Admin.")

    # 11. Admin Approves Requests
    print("\n--- 11. Admin Approving Requests ---")
    if checkin_request_id:
        status, res = api_request(f"/attendance/requests/{checkin_request_id}/approve", "POST", headers=admin_headers)
        assert status == 200, f"Failed to approve checkin: {res}"
        print("Check-in request approved.")
        
    status, res = api_request(f"/attendance/requests/{checkout_request_id}/approve", "POST", headers=admin_headers)
    assert status == 200, f"Failed to approve checkout: {res}"
    print("Check-out request approved.")

    # 12. Verify Logs as Student
    print("\n--- 12. Student Verifying Logs ---")
    status, res = api_request("/attendance", "GET", headers=student_headers)
    assert status == 200, f"Failed to get attendance: {res}"
    logs = res["data"]["logs"]
    assert len(logs) > 0, "No logs found for student"
    today_log = logs[0]
    print("Today's Attendance log details:")
    print(" Date:", today_log["date"])
    print(" Status:", today_log["status"])
    print(" Check-in Time:", today_log["check_in_time"])
    print(" Check-out Time:", today_log["check_out_time"])
    print(" Late Check-in flag:", today_log["is_late_check_in"])
    print(" Late Check-out flag:", today_log["is_late_check_out"])
    
    assert today_log["status"] == "LATE", f"Expected status LATE, got {today_log['status']}"
    assert today_log["is_late_check_in"] is True, "is_late_check_in should be True"
    assert today_log["is_late_check_out"] is True, "is_late_check_out should be True"
    print("Logs successfully updated and verified.")

    # 13. Revert settings as Super Admin
    print("\n--- 13. Reverting settings check-out='17:00' as Super Admin ---")
    status, res = api_request("/attendance/settings", "POST", headers=sa_headers, data={
        "check_in_deadline": "09:00",
        "check_out_deadline": "17:00"
    })
    assert status == 200, f"Failed to revert settings: {res}"
    print("Reverted settings back to default. All tests passed successfully!")

if __name__ == "__main__":
    try:
        test_flow()
    except AssertionError as e:
        print("\nAssertion Failed:", e)
        sys.exit(1)
    except Exception as e:
        print("\nUnexpected error:", e)
        sys.exit(1)
