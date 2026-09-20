"""Null handling: a missing value used as if it existed crashes.

Matches section 6 (PART C). d.get('email') returns None silently, and
None looks just like a real value until something calls a method on it.
"""

USERS = [{"email": f"user{i}@example.com"} for i in range(99_999)]
USERS.append({})  # one record with no email - the trap


def unsafe_lowercase_all(users: list[dict]) -> list[str]:
    result = []
    for user in users:
        email = user.get("email")
        result.append(email.lower())  # CRASH when email is None
    return result


def safe_lowercase_all(users: list[dict]) -> list[str]:
    result = []
    for user in users:
        email = user.get("email")
        if email is not None:
            result.append(email.lower())
        else:
            result.append("")
    return result


if __name__ == "__main__":
    try:
        unsafe_lowercase_all(USERS)
    except AttributeError as exc:
        print(f"crashed after {len(USERS) - 1} good records: {exc}")

    safe = safe_lowercase_all(USERS)
    print(f"safe run handled all {len(safe)} records")
