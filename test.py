

import sys
import pytest

# =====================================================================
# 1. SYSTEM UNDER TEST (SUT) - simplified logic for StudyBuddy modules
# =====================================================================

def validate_todo_title(title: str) -> bool:
    """
    SUT for Boundary Value Analysis (BVA).
    Rules: Todo titles must be between 1 and 50 characters (inclusive).
    """
    length = len(title)
    if length >= 1 and length <= 50:
        return True
    return False


def classify_study_session(duration_minutes: int) -> str:
    """
    SUT for Equivalence Partitioning (EP).
    Rules:
    - Range (< 0 or > 480): Throws ValueError (Invalid session duration)
    - 0 to 45 mins: "Micro Session" (Valid Class A)
    - 46 to 120 mins: "Standard Session" (Valid Class B)
    - 121 to 480 mins: "Deep Work Session" (Valid Class C)
    """
    if duration_minutes < 0 or duration_minutes > 480:
        raise ValueError("Invalid session duration")
    elif duration_minutes <= 45:
        return "Micro Session"
    elif duration_minutes <= 120:
        return "Standard Session"
    else:
        return "Deep Work Session"


def calculate_priority_score(due_in_days: int, is_pinned: bool, subtasks_count: int) -> int:
    """
    SUT for White-Box Path / Branch Coverage.
    This contains multiple conditional branches to verify execution path coverage.
    """
    if due_in_days <= 1:
        # Path 1: Urgent due dates get high score instantly
        return 100
    
    score = 0
    if is_pinned:
        # Path 2: Pinned items get default boost
        score += 40
    else:
        # Path 3 & 4 base branch
        if subtasks_count > 5:
            # Path 3: Complex unpinned tasks get medium boost
            score += 20
        else:
            # Path 4: Simple unpinned tasks
            score += 5
            
    # Add days factor
    score += max(0, 10 - due_in_days)
    return score


def validate_timetable_slot(day: str, start_hour: int, end_hour: int) -> bool:
    """
    SUT for Statement Coverage.
    We must cover every single line/statement of code in our test suite.
    """
    valid_days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    
    # Statement 1
    if day not in valid_days:
        return False
        
    # Statement 2
    if start_hour < 8 or end_hour > 22:
        return False
        
    # Statement 3
    if start_hour >= end_hour:
        return False
        
    # Statement 4
    return True


# =====================================================================
# 2. SQA TEST SUITE
# =====================================================================

# -------------------------------------------------------------
# CONCEPT 1: Boundary Value Analysis (BVA)
# Target Range: 1 to 50 characters (inclusive)
# Boundary Points: Just below lower (0), Lower boundary (1),
#                  Just above lower (2), Middle value (25),
#                  Just below upper (49), Upper boundary (50),
#                  Just above upper (51)
# -------------------------------------------------------------

def test_bva_todo_title_below_lower_bound():
    # Length 0: Just below lower bound (Invalid)
    assert validate_todo_title("") is False

def test_bva_todo_title_at_lower_bound():
    # Length 1: Lower bound boundary (Valid)
    assert validate_todo_title("A") is True

def test_bva_todo_title_above_lower_bound():
    # Length 2: Just above lower bound (Valid)
    assert validate_todo_title("AB") is True

def test_bva_todo_title_nominal():
    # Length 25: Middle value (Valid)
    assert validate_todo_title("Study Quality Assurance  ") is True

def test_bva_todo_title_below_upper_bound():
    # Length 49: Just below upper bound (Valid)
    assert validate_todo_title("x" * 49) is True

def test_bva_todo_title_at_upper_bound():
    # Length 50: Upper bound boundary (Valid)
    assert validate_todo_title("x" * 50) is True

def test_bva_todo_title_above_upper_bound():
    # Length 51: Just above upper bound (Invalid)
    assert validate_todo_title("x" * 51) is False


# -------------------------------------------------------------
# CONCEPT 2: Equivalence Partitioning (EP)
# Classes:
# - Invalid Partition 1: < 0
# - Valid Partition A: 0 - 45 ("Micro Session")
# - Valid Partition B: 46 - 120 ("Standard Session")
# - Valid Partition C: 121 - 480 ("Deep Work Session")
# - Invalid Partition 2: > 480
# -------------------------------------------------------------

def test_ep_invalid_negative_duration():
    # Test case from Invalid Partition 1 (< 0)
    with pytest.raises(ValueError, match="Invalid session duration"):
        classify_study_session(-15)

def test_ep_valid_micro_session():
    # Test case from Valid Partition A (0 - 45)
    assert classify_study_session(30) == "Micro Session"

def test_ep_valid_standard_session():
    # Test case from Valid Partition B (46 - 120)
    assert classify_study_session(90) == "Standard Session"

def test_ep_valid_deep_work_session():
    # Test case from Valid Partition C (121 - 480)
    assert classify_study_session(180) == "Deep Work Session"

def test_ep_invalid_too_long_duration():
    # Test case from Invalid Partition 2 (> 480)
    with pytest.raises(ValueError, match="Invalid session duration"):
        classify_study_session(500)


# -------------------------------------------------------------
# CONCEPT 3: White-Box Path Coverage (Branch Coverage)
# Goal: Execute every distinct branch/path through calculate_priority_score
# -------------------------------------------------------------

def test_path_1_due_date_urgent():
    # Path 1: due_in_days <= 1. Pinned and subtask count are irrelevant here.
    score = calculate_priority_score(due_in_days=1, is_pinned=True, subtasks_count=10)
    assert score == 100

def test_path_2_pinned_task():
    # Path 2: due_in_days > 1, is_pinned = True
    # Expected: score = 40 (pinned) + (10 - 5) (days factor) = 45
    score = calculate_priority_score(due_in_days=5, is_pinned=True, subtasks_count=2)
    assert score == 45

def test_path_3_unpinned_complex_task():
    # Path 3: due_in_days > 1, is_pinned = False, subtasks_count > 5
    # Expected: score = 20 (complex) + (10 - 4) (days factor) = 26
    score = calculate_priority_score(due_in_days=4, is_pinned=False, subtasks_count=8)
    assert score == 26

def test_path_4_unpinned_simple_task():
    # Path 4: due_in_days > 1, is_pinned = False, subtasks_count <= 5
    # Expected: score = 5 (simple) + 0 (due_in_days >= 10, days factor = 0) = 5
    score = calculate_priority_score(due_in_days=12, is_pinned=False, subtasks_count=3)
    assert score == 5


# -------------------------------------------------------------
# CONCEPT 4: Statement Coverage (100% line coverage)
# Goal: Test cases covering every single line of validate_timetable_slot
# -------------------------------------------------------------

def test_statement_1_invalid_day():
    # Trigger first return statement (Day invalid)
    assert validate_timetable_slot("Saturday", 9, 11) is False

def test_statement_2_invalid_hours():
    # Trigger second return statement (Hours outside bounds)
    assert validate_timetable_slot("Monday", 7, 10) is False
    assert validate_timetable_slot("Monday", 9, 23) is False

def test_statement_3_start_after_end():
    # Trigger third return statement (Start hour >= End hour)
    assert validate_timetable_slot("Wednesday", 15, 14) is False
    assert validate_timetable_slot("Wednesday", 12, 12) is False

def test_statement_4_fully_valid():
    # Trigger final return statement (All conditions met)
    assert validate_timetable_slot("Friday", 10, 12) is True


if __name__ == "__main__":
    # If run directly with python test.py, execute pytest automatically
    print("\n--- Running SQA Lab Concept Tests via PyTest ---\n")
    sys.exit(pytest.main(["-v", __file__]))
