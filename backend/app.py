from db_utils_query import get_connection



def main():
    conn = get_connection()
    cursor = conn.cursor()

    # Example: fetch number of profiles
    cursor.execute("SELECT COUNT(*) FROM profiles")
    count = cursor.fetchone()[0]
    print(f"Total profiles in database: {count}")

    
    # Example: fetch first 5 profiles
    cursor.execute("SELECT * FROM profiles LIMIT 5")
    rows = cursor.fetchall()
    for row in rows:
        print(row)

    # Add any other queries you had here

    conn.close()

if __name__ == "__main__":
    main()