from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from typing import Optional, Dict, Any
import requests
import logging
from functools import lru_cache

from .config import settings

logger = logging.getLogger(__name__)

# Security scheme for Bearer token
security = HTTPBearer()


class CognitoJWTVerifier:
    """
    AWS Cognito JWT token verifier.
    Verifies JWT tokens issued by AWS Cognito using JWKS (JSON Web Key Set).
    """

    def __init__(self, region: str, user_pool_id: str):
        self.region = region
        self.user_pool_id = user_pool_id
        self.jwks_url = f"https://cognito-idp.{region}.amazonaws.com/{user_pool_id}/.well-known/jwks.json"
        self._jwks = None

    @lru_cache(maxsize=1)
    def get_jwks(self) -> Dict[str, Any]:
        """
        Fetch and cache JWKS from Cognito.
        This is cached to avoid repeated network calls.
        """
        try:
            response = requests.get(self.jwks_url, timeout=10)
            response.raise_for_status()
            self._jwks = response.json()
            return self._jwks
        except Exception as e:
            logger.error(f"Error fetching JWKS from Cognito: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Unable to verify authentication"
            )

    def verify_token(self, token: str) -> Dict[str, Any]:
        """
        Verify JWT token from AWS Cognito.

        Args:
            token: JWT token string

        Returns:
            Decoded token payload with user information

        Raises:
            HTTPException: If token is invalid or expired
        """
        try:
            # Get the token header to find the key ID
            unverified_header = jwt.get_unverified_header(token)
            kid = unverified_header.get('kid')

            if not kid:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token: missing kid"
                )

            # Get JWKS and find the matching key
            jwks = self.get_jwks()
            key = None

            for jwk in jwks.get('keys', []):
                if jwk.get('kid') == kid:
                    key = jwk
                    break

            if not key:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token: key not found"
                )

            # Verify and decode the token
            # Skip at_hash validation since we're only using the ID token
            payload = jwt.decode(
                token,
                key,
                algorithms=['RS256'],
                audience=settings.COGNITO_CLIENT_ID,
                issuer=f"https://cognito-idp.{self.region}.amazonaws.com/{self.user_pool_id}",
                options={
                    "verify_at_hash": False  # Skip at_hash validation for ID tokens
                }
            )

            return payload

        except JWTError as e:
            logger.warning(f"JWT validation error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid authentication credentials: {str(e)}"
            )
        except Exception as e:
            logger.error(f"Unexpected error during token verification: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )


# Initialize Cognito verifier
cognito_verifier = None

def get_cognito_verifier() -> CognitoJWTVerifier:
    """Get or create Cognito verifier instance"""
    global cognito_verifier
    if cognito_verifier is None:
        if not settings.COGNITO_REGION or not settings.COGNITO_USER_POOL_ID:
            logger.warning("Cognito settings not configured")
            return None
        cognito_verifier = CognitoJWTVerifier(
            region=settings.COGNITO_REGION,
            user_pool_id=settings.COGNITO_USER_POOL_ID
        )
    return cognito_verifier


class User:
    """User model extracted from JWT token"""

    def __init__(self, payload: Dict[str, Any]):
        self.user_id = payload.get('sub')  # Cognito subject (user ID)
        self.username = payload.get('cognito:username')
        self.email = payload.get('email')
        self.email_verified = payload.get('email_verified', False)
        self.given_name = payload.get('given_name')
        self.family_name = payload.get('family_name')
        self.groups = payload.get('cognito:groups', [])
        self.raw_payload = payload

    def __repr__(self):
        return f"User(user_id={self.user_id}, username={self.username}, email={self.email})"


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> User:
    """
    FastAPI dependency to get current authenticated user.

    This extracts the JWT token from the Authorization header,
    verifies it with AWS Cognito, and returns a User object.

    Usage in endpoints:
        @app.post("/endpoint")
        async def endpoint(user: User = Depends(get_current_user)):
            print(f"User ID: {user.user_id}")
    """
    verifier = get_cognito_verifier()

    if not verifier:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication service not configured"
        )

    token = credentials.credentials
    payload = verifier.verify_token(token)

    return User(payload)


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))
) -> Optional[User]:
    """
    Optional authentication dependency.
    Returns User if token is provided and valid, None otherwise.
    Useful for endpoints that work both authenticated and unauthenticated.
    """
    if not credentials:
        return None

    try:
        verifier = get_cognito_verifier()
        if not verifier:
            return None

        token = credentials.credentials
        payload = verifier.verify_token(token)
        return User(payload)
    except HTTPException:
        return None
