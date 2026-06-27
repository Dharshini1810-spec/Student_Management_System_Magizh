"""
Comprehensive backend test script.
Tests all endpoints across every module with proper role-based access.
"""
import urllib.request, json, sys, traceback

BASE = "http://127.0.0.1:8001"
PASS = "StandardPassword123!"
SUPER_EMAIL = "admin@sms.com"
SUPER_PASS = "SuperAdminSecurePassword123!"
PREFIX = "/api/v1"

passed = 0
failed = 0
errors = []

def api(method, path, token=None, data=None, expect=200):
    global passed, failed
    url = f"{BASE}{path}"
    body = json.dumps(data).encode() if data is not None else None
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    try:
        req = urllib.request.Request(url, data=body, headers=headers, method=method)
        r = urllib.request.urlopen(req, timeout=10)
        resp = json.loads(r.read())
        ok = r.status == expect
        status = "PASS" if ok else "FAIL"
        if ok:
            passed += 1
        else:
            failed += 1
            errors.append(f"[{status}] {method} {path} -> expected {expect}, got {r.status}: {resp}")
        print(f"  [{status}] {method} {path} -> {r.status}")
        return resp
    except urllib.error.HTTPError as ex:
        body = ex.read().decode()
        try:
            resp = json.loads(body)
        except:
            resp = {"_raw": body}
        ok = ex.code == expect
        status = "PASS" if ok else "FAIL"
        if ok:
            passed += 1
        else:
            failed += 1
            errors.append(f"[{status}] {method} {path} -> expected {expect}, got {ex.code}: {resp}")
        print(f"  [{status}] {method} {path} -> {ex.code}")
        return resp
    except Exception as ex:
        failed += 1
        errors.append(f"[ERROR] {method} {path} -> {ex}")
        print(f"  [ERROR] {method} {path} -> {ex}")
        return None

def login(email, password):
    r = api("POST", f"{PREFIX}/auth/login", data={"email": email, "password": password})
    if r and r.get("success"):
        return r["data"]["access_token"]
    return None

def test_section(name):
    print(f"\n{'='*60}")
    print(f"  {name}")
    print(f"{'='*60}")

def main():
    global passed, failed
    print("=" * 60)
    print("  STUDENT MANAGEMENT SYSTEM - FULL BACKEND TEST")
    print("=" * 60)

    # ─── 1. HEALTH ─────────────────────────────────────────────
    test_section("1. HEALTH CHECK")
    api("GET", "/health")

    # ─── 2. AUTH ───────────────────────────────────────────────
    test_section("2. AUTH ENDPOINTS")

    # Login as super admin
    token = login(SUPER_EMAIL, SUPER_PASS)
    if not token:
        print("  [FATAL] Cannot login as super admin — aborting")
        sys.exit(1)
    print(f"  Super Admin token: {token[:50]}...")

    # Get current user
    api("GET", f"{PREFIX}/auth/me", token=token)

    # Change password - test with wrong old password (should fail)
    api("POST", f"{PREFIX}/auth/change-password", token=token,
        data={"current_password": "wrong", "new_password": "NewPass123!"}, expect=400)

    # Login with wrong credentials
    api("POST", f"{PREFIX}/auth/login", data={"email": "nonexist@test.com", "password": "x"}, expect=401)

    # ─── 3. ROLES ──────────────────────────────────────────────
    test_section("3. ROLES")
    roles_resp = api("GET", f"{PREFIX}/roles", token=token)
    if roles_resp:
        print(f"    Roles found: {len(roles_resp.get('data', []))}")

    # ─── 4. PERMISSIONS ───────────────────────────────────────
    test_section("4. PERMISSIONS")
    perms_resp = api("GET", f"{PREFIX}/permissions", token=token)
    if perms_resp:
        print(f"    Permissions found: {len(perms_resp.get('data', []))}")

    # ─── 5. USERS CRUD ────────────────────────────────────────
    test_section("5. USERS CRUD")

    # List users
    users_resp = api("GET", f"{PREFIX}/users", token=token)
    if users_resp and isinstance(users_resp, dict):
        data = users_resp.get("data", {})
        users_list = data.get("users", []) if isinstance(data, dict) else data if isinstance(data, list) else []
        count = len(users_list)
        print(f"    Users found: {count}")

    # Create Admin user
    r = api("POST", f"{PREFIX}/users", token=token,
        data={"email": "test-admin@test.com", "password": PASS, "role": "ADMIN", "name": "Test Admin"}, expect=201)
    admin_id = r.get("data", {}).get("id") if r else None
    if admin_id:
        print(f"    Created Admin ID: {admin_id}")

    # Create Mentor user
    r = api("POST", f"{PREFIX}/users", token=token,
        data={"email": "test-mentor@test.com", "password": PASS, "role": "MENTOR", "name": "Test Mentor"}, expect=201)
    mentor_id = r.get("data", {}).get("id") if r else None
    if mentor_id:
        print(f"    Created Mentor ID: {mentor_id}")

    # Create Student user
    r = api("POST", f"{PREFIX}/users", token=token,
        data={"email": "test-student@test.com", "password": PASS, "role": "STUDENT", "name": "Test Student"}, expect=201)
    student_id = r.get("data", {}).get("id") if r else None
    if student_id:
        print(f"    Created Student ID: {student_id}")

    # Duplicate email (should fail)
    api("POST", f"{PREFIX}/users", token=token,
        data={"email": "test-admin@test.com", "password": PASS, "role": "ADMIN"}, expect=400)

    # Get specific user
    if admin_id:
        api("GET", f"{PREFIX}/users/{admin_id}", token=token)

    # Update user
    if admin_id:
        api("PUT", f"{PREFIX}/users/{admin_id}", token=token,
            data={"name": "Updated Admin Name"})

    # Deactivate user
    if admin_id:
        api("PATCH", f"{PREFIX}/users/{admin_id}/deactivate", token=token)

    # Activate user
    if admin_id:
        api("PATCH", f"{PREFIX}/users/{admin_id}/activate", token=token)

    # Soft delete user
    if admin_id:
        api("DELETE", f"{PREFIX}/users/{admin_id}", token=token)

    # Get user permissions
    if mentor_id:
        api("GET", f"{PREFIX}/users/{mentor_id}/permissions", token=token)

    # Grant/revoke permission
    if mentor_id and perms_resp:
        perms = perms_resp.get("data", [])
        if perms:
            perm_id = perms[0]["id"]
            api("POST", f"{PREFIX}/users/{mentor_id}/permissions", token=token,
                data={"permission_id": perm_id})
            api("DELETE", f"{PREFIX}/users/{mentor_id}/permissions/{perm_id}", token=token)

    # Approve student
    if student_id:
        api("POST", f"{PREFIX}/users/{student_id}/approve", token=token)

    # Login as admin
    admin_token = login("test-admin@test.com", PASS)
    if admin_token:
        print("  Admin login OK")

    # Login as mentor
    mentor_token = login("test-mentor@test.com", PASS)
    if mentor_token:
        print("  Mentor login OK")

    # Login as student
    student_token = login("test-student@test.com", PASS)
    if student_token:
        print("  Student login OK")

    # ─── 6. STUDENTS ──────────────────────────────────────────
    test_section("6. STUDENTS")

    # List students
    students_resp = api("GET", f"{PREFIX}/students", token=token)
    created_student = None
    if students_resp and students_resp.get("data"):
        students_list = students_resp["data"]
        if isinstance(students_list, dict):
            students_list = students_list.get("students", [])
        if students_list:
            created_student = students_list[0]
            print(f"    Existing student: {created_student.get('email', created_student.get('id'))}")

    # Get student
    if created_student:
        sid = created_student["id"]
        api("GET", f"{PREFIX}/students/{sid}", token=token)

        # Update student
        api("PUT", f"{PREFIX}/students/{sid}", token=token,
            data={"guardian_name": "Test Guardian"})

        # Assign admin
        if admin_id:
            api("POST", f"{PREFIX}/students/{sid}/assign-admin", token=token,
                data={"admin_id": admin_id})

        # Assign mentor
        if mentor_id:
            api("POST", f"{PREFIX}/students/{sid}/assign-mentor", token=token,
                data={"mentor_id": mentor_id})

        # Delete student
        api("DELETE", f"{PREFIX}/students/{sid}", token=token)

    # ─── 7. ATTENDANCE ────────────────────────────────────────
    test_section("7. ATTENDANCE")

    # Get settings
    api("GET", f"{PREFIX}/attendance/settings", token=token)

    # Update settings (admin only)
    api("POST", f"{PREFIX}/attendance/settings", token=token,
        data={"check_in_deadline": "09:00", "check_out_deadline": "17:00"})

    # Student check-in
    if student_token:
        api("POST", f"{PREFIX}/attendance/check-in", token=student_token, data={})

    # Student check-out
    if student_token:
        api("POST", f"{PREFIX}/attendance/check-out", token=student_token, data={})

    # List attendance logs
    api("GET", f"{PREFIX}/attendance", token=token)

    # Get student history
    if created_student:
        api("GET", f"{PREFIX}/attendance/{created_student['id']}", token=token)

    # List attendance requests
    api("GET", f"{PREFIX}/attendance/requests", token=token)

    # ─── 8. TODOS ─────────────────────────────────────────────
    test_section("8. TODOS")

    # Create todo (admin)
    todo_id = None
    r = api("POST", f"{PREFIX}/todos", token=token,
        data={"title": "Test Admin Todo", "assigned_to": student_id})
    if r and r.get("data"):
        todo_id = r["data"]["id"]

    # List todos
    api("GET", f"{PREFIX}/todos", token=token)

    # Get todo
    if todo_id:
        api("GET", f"{PREFIX}/todos/{todo_id}", token=token)

    # Update todo
    if todo_id:
        api("PUT", f"{PREFIX}/todos/{todo_id}", token=token,
            data={"title": "Updated Todo Title"})

    # Update status (only the assigned user can update status)
    if todo_id and student_token:
        api("PATCH", f"{PREFIX}/todos/{todo_id}/status", token=student_token,
            data={"status": "in_progress"})

    # Mentor creates todo (needs approval)
    mentor_todo_id = None
    if mentor_token:
        r = api("POST", f"{PREFIX}/todos", token=mentor_token,
            data={"title": "Mentor Created Todo", "assigned_to": student_id})
        if r and r.get("data"):
            mentor_todo_id = r["data"]["id"]

    # List pending approval
    api("GET", f"{PREFIX}/todos/pending-approval", token=token)

    # Approve mentor's todo
    if mentor_todo_id:
        api("PATCH", f"{PREFIX}/todos/{mentor_todo_id}/approve", token=token)

    # Reject a todo
    if mentor_token and todo_id:
        # Create another for rejection
        r = api("POST", f"{PREFIX}/todos", token=mentor_token,
            data={"title": "Todo To Reject", "assigned_to": student_id})
        if r and r.get("data"):
            reject_id = r["data"]["id"]
            api("PATCH", f"{PREFIX}/todos/{reject_id}/reject", token=token, data={"approval_status": "rejected"})

    # Delete todo
    if todo_id:
        api("DELETE", f"{PREFIX}/todos/{todo_id}", token=token)

    # Personal todo
    if student_token:
        api("POST", f"{PREFIX}/todos/personal", token=student_token,
            data={"title": "Personal Student Todo"})

    # ─── 9. PROJECTS ──────────────────────────────────────────
    test_section("9. PROJECTS")

    # Create project (admin)
    proj_id = None
    r = api("POST", f"{PREFIX}/projects", token=token,
        data={"title": "Test Admin Project", "description": "A test project", "assigned_to": student_id})
    if r and r.get("data"):
        proj_id = r["data"]["id"]

    # List projects
    api("GET", f"{PREFIX}/projects", token=token)

    # Get project
    if proj_id:
        api("GET", f"{PREFIX}/projects/{proj_id}", token=token)

    # Update project
    if proj_id:
        api("PUT", f"{PREFIX}/projects/{proj_id}", token=token,
            data={"title": "Updated Project Title"})

    # Update status (only assigned user can update)
    if proj_id and student_token:
        api("PATCH", f"{PREFIX}/projects/{proj_id}/status", token=student_token,
            data={"status": "in_progress"})

    # Mentor creates project (needs approval)
    mentor_proj_id = None
    if mentor_token:
        r = api("POST", f"{PREFIX}/projects", token=mentor_token,
            data={"title": "Mentor Project", "description": "Needs approval", "assigned_to": student_id})
        if r and r.get("data"):
            mentor_proj_id = r["data"]["id"]

    # List pending approval
    api("GET", f"{PREFIX}/projects/pending-approval", token=token)

    # Approve mentor's project
    if mentor_proj_id:
        api("PATCH", f"{PREFIX}/projects/{mentor_proj_id}/approve", token=token)

    # Delete project
    if proj_id:
        api("DELETE", f"{PREFIX}/projects/{proj_id}", token=token)

    # ─── 10. DAILY CONTENT ────────────────────────────────────
    test_section("10. DAILY CONTENT")

    dc_id = None
    r = api("POST", f"{PREFIX}/daily-content", token=token,
        data={"title": "Test Content", "content": "Some daily content", "assigned_to": [student_id]})
    if r and r.get("data"):
        if isinstance(r["data"], dict):
            dc_id = r["data"].get("id")

    api("GET", f"{PREFIX}/daily-content", token=token)

    if student_token:
        api("GET", f"{PREFIX}/daily-content/today", token=student_token)

    if dc_id:
        api("GET", f"{PREFIX}/daily-content/{dc_id}", token=token)
        api("PATCH", f"{PREFIX}/daily-content/{dc_id}", token=token,
            data={"title": "Updated Content"})
        api("DELETE", f"{PREFIX}/daily-content/{dc_id}", token=token)

    # ─── 11. STUDENT NOTES ────────────────────────────────────
    test_section("11. STUDENT NOTES")

    sid_for_notes = created_student["id"] if created_student else student_id
    if sid_for_notes:
        note_id = None
        r = api("POST", f"{PREFIX}/students/{sid_for_notes}/notes", token=token,
            data={"content": "Test note about this student"})
        if r and r.get("data"):
            note_id = r["data"].get("id")

        api("GET", f"{PREFIX}/students/{sid_for_notes}/notes", token=token)

        if note_id:
            api("DELETE", f"{PREFIX}/students/{sid_for_notes}/notes/{note_id}", token=token)

    # ─── 12. NOTIFICATIONS ────────────────────────────────────
    test_section("12. NOTIFICATIONS")

    api("GET", f"{PREFIX}/notifications", token=token)
    api("GET", f"{PREFIX}/notifications/unread-count", token=token)
    api("PATCH", f"{PREFIX}/notifications/read-all", token=token)

    # ─── 13. DASHBOARD ────────────────────────────────────────
    test_section("13. DASHBOARD")

    api("GET", f"{PREFIX}/dashboard/super-admin", token=token)
    if admin_token:
        api("GET", f"{PREFIX}/dashboard/admin", token=admin_token)
    if mentor_token:
        api("GET", f"{PREFIX}/dashboard/mentor", token=mentor_token)
    if student_token:
        api("GET", f"{PREFIX}/dashboard/student", token=student_token)

    # ─── 14. ANALYTICS ────────────────────────────────────────
    test_section("14. ANALYTICS")

    api("GET", f"{PREFIX}/analytics/attendance-trend", token=token)
    api("GET", f"{PREFIX}/analytics/project-stats", token=token)
    api("GET", f"{PREFIX}/analytics/student-growth", token=token)

    # ─── 15. REPORTS ──────────────────────────────────────────
    test_section("15. REPORTS")

    api("GET", f"{PREFIX}/reports/summary", token=token)
    api("GET", f"{PREFIX}/reports/attendance", token=token)
    api("GET", f"{PREFIX}/reports/projects", token=token)
    api("GET", f"{PREFIX}/reports/todos", token=token)
    api("GET", f"{PREFIX}/reports/students", token=token)
    api("GET", f"{PREFIX}/reports/activity", token=token)

    # ─── 16. ACTIVITY LOGS ────────────────────────────────────
    test_section("16. ACTIVITY LOGS")

    api("GET", f"{PREFIX}/activity-logs", token=token)
    api("GET", f"{PREFIX}/activity-logs/me", token=token)

    # ─── 17. REFERRAL LINKS ───────────────────────────────────
    test_section("17. REFERRAL LINKS")

    ref_id = None
    r = api("POST", f"{PREFIX}/referral-links", token=token,
        data={"max_uses": 5})
    if r and r.get("data"):
        ref_id = r["data"].get("id")
        print(f"    Created referral code: {r['data'].get('code')}")

    api("GET", f"{PREFIX}/referral-links", token=token)

    if ref_id:
        api("GET", f"{PREFIX}/referral-links/{ref_id}", token=token)
        api("PATCH", f"{PREFIX}/referral-links/{ref_id}", token=token,
            data={"max_uses": 10})
        api("DELETE", f"{PREFIX}/referral-links/{ref_id}", token=token)

    # ─── 18. CROSS-ROLE ACCESS CONTROL ───────────────────────
    test_section("18. CROSS-ROLE ACCESS CONTROL")

    # Admin should be able to list users
    if admin_token:
        print("  Admin listing users...")
        api("GET", f"{PREFIX}/users", token=admin_token)

    # Mentor should NOT be able to create users
    if mentor_token:
        print("  Mentor trying to create user (should fail)...")
        api("POST", f"{PREFIX}/users", token=mentor_token,
            data={"email": "mentor-created@test.com", "password": PASS, "role": "STUDENT"}, expect=403)

    # Student should NOT be able to list users
    if student_token:
        print("  Student trying to list users (should fail)...")
        api("GET", f"{PREFIX}/users", token=student_token, expect=403)

    # Student should be able to view own profile
    if student_token:
        print("  Student viewing own profile...")
        api("GET", f"{PREFIX}/auth/me", token=student_token)

    # No-auth access should fail
    print("  No-auth access (should fail)...")
    api("GET", f"{PREFIX}/users", expect=401)
    api("POST", f"{PREFIX}/todos", data={"title": "x"}, expect=401)

    # ─── SUMMARY ─────────────────────────────────────────────
    test_section("SUMMARY")
    total = passed + failed
    print(f"  Total tests: {total}")
    print(f"  Passed:      {passed}")
    print(f"  Failed:      {failed}")
    if errors:
        print(f"\n  FAILURES:")
        for e in errors[:20]:
            print(f"    {e}")
        if len(errors) > 20:
            print(f"    ... and {len(errors) - 20} more")
    print(f"\n  {'ALL TESTS PASSED' if failed == 0 else 'SOME TESTS FAILED'}")

if __name__ == "__main__":
    main()
