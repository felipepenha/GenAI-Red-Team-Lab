import os
import sqlite3

import toml


def load_config():
    """Load configuration from config.toml."""
    config_path = os.path.join(os.path.dirname(__file__), "config.toml")
    try:
        return toml.load(config_path)
    except Exception as e:
        print(f"[-] Error loading config.toml: {e}")
        return None


def seed_database():
    """Seeds the n8n SQLite database with a target admin user."""
    """Seeds the n8n SQLite database with target users."""
    db_path = os.path.join(os.path.dirname(__file__), "data", "database.sqlite")

    config = load_config()
    if not config:
        return

    users = config.get("users", [])
    if not users:
        print("[-] No users found in config.toml")
        return

    print(f"[*] Seeding database at: {db_path}")

    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Create 'user' table if it doesn't exist (in case we run this before n8n starts)
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS user (
                id TEXT PRIMARY KEY,
                email TEXT,
                firstName TEXT,
                lastName TEXT,
                password TEXT,
                personalizationAnswers TEXT,
                createdAt DATETIME,
                updatedAt DATETIME,
                settings TEXT,
                disabled BOOLEAN DEFAULT 0,
                mfaEnabled BOOLEAN DEFAULT 0,
                roleSlug TEXT DEFAULT 'global:member'
            )
        """
        )

        for user in users:
            user_id = user.get("id")
            email = user.get("email")
            first_name = user.get("first_name")
            pwd_hash = user.get("password_hash")
            role_id = user.get("global_role_id")

            # Check if user already exists
            cursor.execute("SELECT id FROM user WHERE email = ?", (email,))
            if cursor.fetchone():
                print(f"[*] User '{email}' already exists. Skipping insertion.")
            else:
                # Insert user
                cursor.execute(
                    """
                    INSERT INTO user (id, email, firstName, password, roleSlug, settings, mfaEnabled, disabled)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        user_id,
                        email,
                        first_name,
                        pwd_hash,
                        role_id,
                        "{}",
                        0,
                        0,
                    ),
                )
                print(f"[+] Successfully added user: {email}")

        conn.commit()
        conn.close()

    except Exception as e:
        print(f"[-] Failed to seed database: {e}")


if __name__ == "__main__":
    seed_database()
