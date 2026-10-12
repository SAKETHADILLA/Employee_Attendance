from datetime import datetime, timezone
import pytest
from app.main import (
    compute_attendance_date,
    compute_late_minutes,
    compute_overtime,
    compute_work_hours,
    compute_half_day,
    round_half_up,
)


def test_health(client):
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json() == {"status": "ok"}


def test_create_employee(client):
    payload = {
        "emp_code": "EMP0001",
        "name": "Asha Rao",
        "email": "asha@example.com",
        "department": "Engineering",
        "shift_start": "09:30",
        "shift_end": "18:30",
        "joined_on": "2026-01-05",
    }
    res = client.post("/employees", json=payload)
    assert res.status_code == 201
    data = res.json()
    assert data["emp_code"] == "EMP0001"
    assert data["name"] == "Asha Rao"
    assert isinstance(data["created_at"], int)

    # Duplicate emp_code -> 409
    res_dup = client.post("/employees", json=payload)
    assert res_dup.status_code == 409

    # Identical shift times -> 422
    invalid_shift = dict(payload, emp_code="EMP0002", shift_start="09:00", shift_end="09:00")
    res_inv = client.post("/employees", json=invalid_shift)
    assert res_inv.status_code == 422


def test_list_employees(client):
    for i in range(1, 4):
        client.post("/employees", json={
            "emp_code": f"EMP000{i}",
            "name": f"Employee {i}",
            "email": f"emp{i}@example.com",
            "department": "Engineering" if i < 3 else "Product",
            "shift_start": "09:30",
            "shift_end": "18:30",
            "joined_on": "2026-01-01",
        })

    # List all
    res = client.get("/employees?page=1&page_size=10")
    assert res.status_code == 200
    body = res.json()
    assert body["total"] == 3
    assert len(body["items"]) == 3
    assert body["items"][0]["emp_code"] == "EMP0001"

    # Filter by department
    res_dept = client.get("/employees?department=Engineering")
    assert res_dept.status_code == 200
    assert res_dept.json()["total"] == 2


def test_punch_lifecycle(client):
    client.post("/employees", json={
        "emp_code": "EMP0010",
        "name": "Rohan Sharma",
        "email": "rohan@example.com",
        "department": "Sales",
        "shift_start": "09:30",
        "shift_end": "18:30",
        "joined_on": "2026-01-01",
    })

    punch_in_ms = 1783310280000
    res_in = client.post("/attendance/punch-in", json={
        "emp_code": "EMP0010",
        "punched_at": punch_in_ms,
        "status": "PRESENT",
    })
    assert res_in.status_code == 201
    in_data = res_in.json()
    assert in_data["date"] == "2026-07-06"
    assert in_data["late_minutes"] == 0
    assert in_data["punch_out"] is None
    assert in_data["work_hours"] is None

    # Double punch in -> 409
    res_in_dup = client.post("/attendance/punch-in", json={
        "emp_code": "EMP0010",
        "punched_at": punch_in_ms + 10000,
    })
    assert res_in_dup.status_code == 409

    punch_out_ms = 1783343100000
    res_out = client.post("/attendance/punch-out", json={
        "emp_code": "EMP0010",
        "punched_at": punch_out_ms,
    })
    assert res_out.status_code == 200
    out_data = res_out.json()
    assert out_data["work_hours"] == 9.12
    assert out_data["late_minutes"] == 0
    assert out_data["overtime_minutes"] == 0  # 5 min is under 30-min threshold
    assert out_data["half_day"] is False

    # Second punch out -> 409
    res_out_dup = client.post("/attendance/punch-out", json={
        "emp_code": "EMP0010",
        "punched_at": punch_out_ms + 1000,
    })
    assert res_out_dup.status_code == 409


def test_regularize_attendance(client):
    client.post("/employees", json={
        "emp_code": "EMP0020",
        "name": "Pooja Verma",
        "email": "pooja@example.com",
        "department": "Engineering",
        "shift_start": "09:30",
        "shift_end": "18:30",
        "joined_on": "2026-01-01",
    })

    in_ms = 1783312500000
    client.post("/attendance/punch-in", json={
        "emp_code": "EMP0020",
        "punched_at": in_ms,
        "status": "PRESENT",
    })

    out_ms = 1783342800000
    client.post("/attendance/punch-out", json={
        "emp_code": "EMP0020",
        "punched_at": out_ms,
    })

    corrected_in_ms = 1783310280000
    res_patch = client.patch(
        "/attendance/EMP0020/2026-07-06",
        json={
            "punch_in": corrected_in_ms,
            "reason": "Biometric device scanner lagged",
            "regularized_by": "hr.manager",
        }
    )
    assert res_patch.status_code == 200
    data = res_patch.json()
    assert data["late_minutes"] == 0
    assert len(data["history"]) == 1
    assert data["history"][0]["by"] == "hr.manager"
    assert "late_minutes" in data["history"][0]["changes"]
    assert data["history"][0]["changes"]["late_minutes"]["from"] == 35
    assert data["history"][0]["changes"]["late_minutes"]["to"] == 0


def test_business_rules_helpers():
    # R2: Late minutes edge cases
    # Shift 09:30 IST on 2026-07-06
    # 09:40:00 IST -> 04:10:00 UTC
    dt_exact_grace = datetime(2026, 7, 6, 4, 10, 0, tzinfo=timezone.utc)
    assert compute_late_minutes(dt_exact_grace, "09:30", "2026-07-06") == 0

    # 09:40:01 IST -> 04:10:01 UTC -> 10 minutes late
    dt_1sec_late = datetime(2026, 7, 6, 4, 10, 1, tzinfo=timezone.utc)
    assert compute_late_minutes(dt_1sec_late, "09:30", "2026-07-06") == 10

    # 10:15:59 IST -> 04:45:59 UTC -> 45 minutes late
    dt_45min_late = datetime(2026, 7, 6, 4, 45, 59, tzinfo=timezone.utc)
    assert compute_late_minutes(dt_45min_late, "09:30", "2026-07-06") == 45

    # R3: Overtime edge cases
    # Shift end 18:30 IST on 2026-07-06 -> 13:00:00 UTC
    # Punch out at 18:59 IST -> 29 min -> under 30 -> 0 overtime
    dt_ot_29 = datetime(2026, 7, 6, 13, 29, 0, tzinfo=timezone.utc)
    assert compute_overtime(dt_ot_29, "09:30", "18:30", "2026-07-06") == 0

    # Punch out at 19:00 IST -> 30 min -> 30 overtime
    dt_ot_30 = datetime(2026, 7, 6, 13, 30, 0, tzinfo=timezone.utc)
    assert compute_overtime(dt_ot_30, "09:30", "18:30", "2026-07-06") == 30

    # R4 & R8: Half-up rounding
    # 2.125 -> 2.13 (half-up, whereas banker's rounding yields 2.12)
    assert round_half_up(2.125, 2) == 2.13
    assert round_half_up(2.124, 2) == 2.12

    # R5: Half day
    assert compute_half_day(4.49) is True
    assert compute_half_day(4.50) is False
    assert compute_half_day(8.00) is False

    # R1: Overnight shift
    # Shift: 22:00 to 06:00
    # Punch in at 05:30 IST on 2026-07-07 belongs to shift starting 2026-07-06
    dt_night_punch = datetime(2026, 7, 7, 0, 0, 0, tzinfo=timezone.utc)  # 05:30 IST
    att_date = compute_attendance_date(dt_night_punch, "22:00", "06:00")
    assert att_date == "2026-07-06"
