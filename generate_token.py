"""
JWT Token Generation and Validation
------------------------------------
Use this to generate proper JWT tokens for your application.
"""

import jwt
from datetime import datetime, timedelta
from typing import Dict, Optional

# ============== Configuration ==============
# IMPORTANT: Store this in environment variables in production!
SECRET_KEY = "your-secret-key-here-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# ============== Token Generation ==============
def create_jwt_token(
    user_id: str,
    username: str,
    email: Optional[str] = None,
    additional_claims: Optional[Dict] = None,
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create a JWT token with user information.
    
    Args:
        user_id: Unique user identifier
        username: Username
        email: User email (optional)
        additional_claims: Any additional data to include in the token
        expires_delta: Custom expiration time
    
    Returns:
        JWT token string
    """
    # Calculate expiration time
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # Build the token payload
    payload = {
        "sub": user_id,          # Subject (user ID)
        "name": username,         # Username
        "iat": datetime.utcnow(), # Issued at
        "exp": expire,            # Expiration time
    }
    
    # Add email if provided
    if email:
        payload["email"] = email
    
    # Add any additional claims
    if additional_claims:
        payload.update(additional_claims)
    
    # Create the JWT token
    encoded_jwt = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# ============== Token Validation ==============
def verify_jwt_token(token: str) -> Dict:
    """
    Verify and decode a JWT token.
    
    Args:
        token: JWT token string
    
    Returns:
        Decoded token payload
    
    Raises:
        jwt.ExpiredSignatureError: If token has expired
        jwt.InvalidTokenError: If token is invalid
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise Exception("Token has expired")
    except jwt.InvalidTokenError:
        raise Exception("Invalid token")

# ============== Example Usage ==============
if __name__ == "__main__":
    print("=" * 60)
    print("JWT Token Generation Example")
    print("=" * 60)
    
    # Example 1: Create a basic token
    print("\n1. Creating a basic JWT token...")
    token = create_jwt_token(
        user_id="1234567890",
        username="John Doe"
    )
    print(f"Token: {token}")
    print(f"Length: {len(token)} characters")
    
    # Example 2: Create a token with additional claims
    print("\n2. Creating a token with additional claims...")
    token_with_claims = create_jwt_token(
        user_id="user_123",
        username="alice",
        email="alice@example.com",
        additional_claims={
            "role": "admin",
            "permissions": ["read", "write", "delete"],
            "organization_id": "org_456"
        }
    )
    print(f"Token: {token_with_claims[:50]}...")
    
    # Example 3: Verify and decode a token
    print("\n3. Verifying and decoding the token...")
    try:
        decoded = verify_jwt_token(token)
        print(f"Decoded payload:")
        for key, value in decoded.items():
            print(f"  {key}: {value}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Example 4: Create a token with custom expiration
    print("\n4. Creating a token with 1-hour expiration...")
    long_lived_token = create_jwt_token(
        user_id="user_789",
        username="bob",
        expires_delta=timedelta(hours=1)
    )
    print(f"Token: {long_lived_token[:50]}...")
    
    # Example 5: Test expired token handling
    print("\n5. Testing expired token...")
    expired_token = create_jwt_token(
        user_id="test",
        username="test",
        expires_delta=timedelta(seconds=-1)  # Already expired
    )
    try:
        verify_jwt_token(expired_token)
    except Exception as e:
        print(f"Expected error: {e}")
    
    print("\n" + "=" * 60)
    print("✅ Examples completed!")
    print("=" * 60)
    
    # Print the token for use in your frontend
    print("\n📋 Use this token in your Next.js frontend:")
    print(f'\nconst userToken = "{token}"')
    print("\nPlace it in your CopilotKit properties:")
    print("<CopilotKit properties={{ authorization: userToken }} />")
    print("\n⚠️  Remember: In production, generate tokens dynamically on login!")