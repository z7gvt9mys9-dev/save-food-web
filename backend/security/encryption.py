"""Encryption service for sensitive data protection"""

from cryptography.fernet import Fernet
import base64
import os
from typing import Optional


class EncryptionService:
    """Service for encryption/decryption using Fernet (symmetric encryption)"""
    
    def __init__(self):
        # Get encryption key from environment or generate
        key_str = os.getenv("ENCRYPTION_KEY")
        if not key_str:
            # Generate new key (for development only)
            key_str = base64.urlsafe_b64encode(os.urandom(32)).decode()
            print(f"Generated new encryption key: {key_str}")
            print("Add to .env: ENCRYPTION_KEY=<key>")
        
        self.cipher_suite = Fernet(key_str.encode() if isinstance(key_str, str) else key_str)
    
    def encrypt(self, plaintext: str) -> str:
        """Encrypt sensitive data"""
        if not plaintext:
            return plaintext
        
        encrypted = self.cipher_suite.encrypt(plaintext.encode())
        return encrypted.decode()
    
    def decrypt(self, encrypted_text: str) -> Optional[str]:
        """Decrypt sensitive data"""
        if not encrypted_text:
            return encrypted_text
        
        try:
            decrypted = self.cipher_suite.decrypt(encrypted_text.encode())
            return decrypted.decode()
        except Exception as e:
            print(f"Decryption error: {e}")
            return None


# Singleton instance
encryption_service = EncryptionService()
