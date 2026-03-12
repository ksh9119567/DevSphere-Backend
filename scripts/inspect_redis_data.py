import os
import sys
import json
import asyncio

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.redis_manager import redis_client


def format_ttl(seconds):
    """Format TTL in human-readable format."""
    if seconds < 0:
        return "Expired"
    elif seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        return f"{seconds // 60}m {seconds % 60}s"
    else:
        return f"{seconds // 3600}h {(seconds % 3600) // 60}m"


async def get_all_tokens():
    """Retrieve all access and refresh tokens from Redis with their metadata."""
    try:
        # Get all keys matching token patterns
        access_token_keys = await redis_client.keys("access_token:*")
        refresh_token_keys = await redis_client.keys("refresh_token:*")
        
        tokens_data = {
            "access_tokens": [],
            "refresh_tokens": [],
            "summary": {
                "total_access_tokens": len(access_token_keys),
                "total_refresh_tokens": len(refresh_token_keys)
            }
        }
        
        # Process access tokens
        for key in access_token_keys:
            ttl = await redis_client.ttl(key)
            token_json = await redis_client.get(key)
            
            try:
                token_data = json.loads(token_json)
                tokens_data["access_tokens"].append({
                    "key": key,
                    "user_email": token_data.get("user_email"),
                    "created_at": token_data.get("created_at"),
                    "user_id": token_data.get("user_id"),
                    "is_admin": token_data.get("is_admin"),
                    "is_email_verified": token_data.get("is_email_verified"),
                    "ttl": format_ttl(ttl),
                    "ttl_seconds": ttl
                })
            except json.JSONDecodeError:
                tokens_data["access_tokens"].append({
                    "key": key,
                    "error": "Failed to parse token data",
                    "ttl": format_ttl(ttl)
                })
        
        # Process refresh tokens
        for key in refresh_token_keys:
            ttl = await redis_client.ttl(key)
            token_json = await redis_client.get(key)
            
            try:
                token_data = json.loads(token_json)
                tokens_data["refresh_tokens"].append({
                    "key": key,
                    "user_email": token_data.get("user_email"),
                    "created_at": token_data.get("created_at"),
                    "user_id": token_data.get("user_id"),
                    "is_admin": token_data.get("is_admin"),
                    "is_email_verified": token_data.get("is_email_verified"),
                    "ttl": format_ttl(ttl),
                    "ttl_seconds": ttl
                })
            except json.JSONDecodeError:
                tokens_data["refresh_tokens"].append({
                    "key": key,
                    "error": "Failed to parse token data",
                    "ttl": format_ttl(ttl)
                })
        
        return tokens_data
    
    except Exception as e:
        print(f"Error retrieving tokens: {str(e)}")
        return None


async def display_tokens():
    """Display all tokens in a formatted manner."""
    tokens_data = await get_all_tokens()
    
    if tokens_data is None:
        print("Failed to retrieve token data from Redis")
        return
    
    print("\n" + "="*80)
    print("REDIS TOKEN INSPECTION REPORT")
    print("="*80)
    
    # Summary
    print(f"\nSUMMARY:")
    print(f"  Total Access Tokens: {tokens_data['summary']['total_access_tokens']}")
    print(f"  Total Refresh Tokens: {tokens_data['summary']['total_refresh_tokens']}")
    
    # Access Tokens
    print(f"\n{'-'*80}")
    print("ACCESS TOKENS:")
    print(f"{'-'*80}")
    
    if tokens_data["access_tokens"]:
        for idx, token in enumerate(tokens_data["access_tokens"], 1):
            print(f"\n[{idx}] Key: {token['key']}")
            if "error" in token:
                print(f"    Error: {token['error']}")
            else:
                print(f"    User Email: {token.get('user_email', 'N/A')}")
                print(f"    User ID: {token.get('user_id', 'N/A')}")
                print(f"    Is Admin: {token.get('is_admin', 'N/A')}")
                print(f"    Email Verified: {token.get('is_email_verified', 'N/A')}")
                print(f"    Created At: {token.get('created_at', 'N/A')}")
                print(f"    TTL: {token['ttl']}")
    else:
        print("No access tokens found")
    
    # Refresh Tokens
    print(f"\n{'-'*80}")
    print("REFRESH TOKENS:")
    print(f"{'-'*80}")
    
    if tokens_data["refresh_tokens"]:
        for idx, token in enumerate(tokens_data["refresh_tokens"], 1):
            print(f"\n[{idx}] Key: {token['key']}")
            if "error" in token:
                print(f"    Error: {token['error']}")
            else:
                print(f"    User Email: {token.get('user_email', 'N/A')}")
                print(f"    User ID: {token.get('user_id', 'N/A')}")
                print(f"    Is Admin: {token.get('is_admin', 'N/A')}")
                print(f"    Email Verified: {token.get('is_email_verified', 'N/A')}")
                print(f"    Created At: {token.get('created_at', 'N/A')}")
                print(f"    TTL: {token['ttl']}")
    else:
        print("No refresh tokens found")
    
    print(f"\n{'='*80}\n")


async def delete_all_tokens():
    """Delete all access and refresh tokens from Redis."""
    try:
        # Get all keys matching token patterns
        access_token_keys = await redis_client.keys("access_token:*")
        refresh_token_keys = await redis_client.keys("refresh_token:*")
        
        total_keys = len(access_token_keys) + len(refresh_token_keys)
        
        if total_keys == 0:
            print("No tokens found to delete.")
            return
        
        # Confirm deletion
        print(f"\nWARNING: You are about to delete {total_keys} tokens:")
        print(f"  - {len(access_token_keys)} access tokens")
        print(f"  - {len(refresh_token_keys)} refresh tokens")
        print("\nThis action cannot be undone. All users will be logged out.")
        
        confirmation = input("\nType 'DELETE' to confirm: ").strip()
        
        if confirmation != "DELETE":
            print("Deletion cancelled.")
            return
        
        # Delete access tokens
        deleted_count = 0
        for key in access_token_keys:
            await redis_client.delete(key)
            deleted_count += 1
        
        # Delete refresh tokens
        for key in refresh_token_keys:
            await redis_client.delete(key)
            deleted_count += 1
        
        print(f"\n✓ Successfully deleted {deleted_count} tokens from Redis")
        print(f"  - {len(access_token_keys)} access tokens deleted")
        print(f"  - {len(refresh_token_keys)} refresh tokens deleted")
        
    except Exception as e:
        print(f"Error deleting tokens: {str(e)}")


async def main():
    """Main entry point with command-line argument handling."""
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "inspect":
            await display_tokens()
        elif command == "delete":
            await delete_all_tokens()
        elif command == "help":
            print_help()
        else:
            print(f"Unknown command: {command}")
            print_help()
    else:
        # Default behavior: display tokens
        await display_tokens()


def print_help():
    """Print help message with available commands."""
    help_text = """
Redis Token Inspection Script

Usage: python scripts/inspect_redis_data.py [COMMAND]

Commands:
  inspect    Display all access and refresh tokens (default)
  delete     Delete all access and refresh tokens from Redis
  help       Show this help message

Examples:
  python scripts/inspect_redis_data.py
  python scripts/inspect_redis_data.py inspect
  python scripts/inspect_redis_data.py delete
  python scripts/inspect_redis_data.py help
    """
    print(help_text)


if __name__ == "__main__":
    asyncio.run(main())
