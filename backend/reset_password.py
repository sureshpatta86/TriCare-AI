"""
Password reset utility for TriCare AI users
Usage: python reset_password.py <email> <new_password>
Example: python reset_password.py testuser@gmail.com NewPass123
"""

import sys
import os
import sqlite3
import bcrypt

def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')

def reset_password(email: str, new_password: str):
    # Get database path
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'tricare.db')
    
    if not os.path.exists(db_path):
        print(f"❌ Database not found at {db_path}")
        return False
    
    # Validate password requirements
    if len(new_password) < 8:
        print("❌ Password must be at least 8 characters long")
        return False
    
    if not any(c.isupper() for c in new_password):
        print("❌ Password must contain at least 1 uppercase letter")
        return False
    
    if not any(c.isdigit() for c in new_password):
        print("❌ Password must contain at least 1 number")
        return False
    
    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if user exists
        cursor.execute("SELECT id, email, username FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()
        
        if not user:
            print(f"❌ User with email '{email}' not found")
            print("\nAvailable users:")
            cursor.execute("SELECT email, username FROM users")
            users = cursor.fetchall()
            for user_email, username in users:
                print(f"  - {user_email} (username: {username})")
            return False
        
        user_id, user_email, username = user
        
        # Hash the new password
        hashed_password = hash_password(new_password)
        
        # Update password
        cursor.execute(
            "UPDATE users SET hashed_password = ? WHERE id = ?",
            (hashed_password, user_id)
        )
        conn.commit()
        
        print("=" * 60)
        print("✅ Password reset successful!")
        print("=" * 60)
        print(f"Email:    {user_email}")
        print(f"Username: {username}")
        print(f"New Password: {new_password}")
        print("=" * 60)
        print("\nYou can now login with:")
        print(f"  Email: {user_email}")
        print(f"  Password: {new_password}")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"❌ Error resetting password: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    print("=" * 60)
    print("TriCare AI - Password Reset Utility")
    print("=" * 60)
    
    if len(sys.argv) != 3:
        print("\nUsage: python reset_password.py <email> <new_password>")
        print("\nPassword requirements:")
        print("  - At least 8 characters")
        print("  - At least 1 uppercase letter")
        print("  - At least 1 number")
        print("\nExample:")
        print("  python reset_password.py testuser@gmail.com NewPass123")
        print("=" * 60)
        sys.exit(1)
    
    email = sys.argv[1]
    new_password = sys.argv[2]
    
    reset_password(email, new_password)
