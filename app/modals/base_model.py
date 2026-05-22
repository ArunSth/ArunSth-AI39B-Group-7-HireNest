from app.database import get_connection


def create_all():
    """Create all required tables for the application if they don't exist.

    Runs a sequence of `CREATE TABLE IF NOT EXISTS` statements using the
    existing PyMySQL connection from `app.database.get_connection()`.
    """
    statements = [
        # Roles
        """
		CREATE TABLE IF NOT EXISTS roles (
			id INT AUTO_INCREMENT PRIMARY KEY,
			name VARCHAR(50) NOT NULL UNIQUE,
			created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
		) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
		""",

        # Users
        """
		CREATE TABLE IF NOT EXISTS users (
			id INT AUTO_INCREMENT PRIMARY KEY,
			email VARCHAR(255) NOT NULL UNIQUE,
			password_hash VARCHAR(255) NOT NULL,
			first_name VARCHAR(100),
			last_name VARCHAR(100),
			role_id INT,
			is_active TINYINT NOT NULL DEFAULT 1,
			is_verified TINYINT NOT NULL DEFAULT 0,
			created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
			updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
			FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE SET NULL
		) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
		""",

        # Profiles (optional extended user info)
        """
		CREATE TABLE IF NOT EXISTS profiles (
			user_id INT PRIMARY KEY,
			bio TEXT,
			phone VARCHAR(30),
			avatar_url VARCHAR(255),
			location VARCHAR(100),
			FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
		) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
		""",

        # Password reset tokens
        """
		CREATE TABLE IF NOT EXISTS password_resets (
			id INT AUTO_INCREMENT PRIMARY KEY,
			user_id INT NOT NULL,
			token VARCHAR(255) NOT NULL UNIQUE,
			expires_at DATETIME NOT NULL,
			used TINYINT NOT NULL DEFAULT 0,
			created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
			FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
		) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
		""",
    ]

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            for stmt in statements:
                cur.execute(stmt)
        conn.commit()
    finally:
        conn.close()


def drop_all():
    """Drop tables in reverse order (useful for local testing)."""
    stmts = [
        "DROP TABLE IF EXISTS password_resets;",
        "DROP TABLE IF EXISTS profiles;",
        "DROP TABLE IF EXISTS users;",
        "DROP TABLE IF EXISTS roles;",
    ]
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            for s in stmts:
                cur.execute(s)
        conn.commit()
    finally:
        conn.close()
