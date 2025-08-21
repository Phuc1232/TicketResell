"""
Message encryption utilities for secure chat
"""

import os
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import logging

class MessageEncryption:
    """Handle message encryption and decryption"""
    
    def __init__(self, password: str = None):
        """Initialize encryption with password or environment variable"""
        if password is None:
            password = os.getenv('CHAT_ENCRYPTION_KEY', 'default-chat-key-change-in-production')
        
        self.password = password.encode()
        self.salt = b'stable_salt_for_chat'  # In production, use random salt per message
        
    def _get_key(self) -> bytes:
        """Generate encryption key from password"""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self.salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(self.password))
        return key
    
    def encrypt_message(self, message: str) -> str:
        """Encrypt a message"""
        try:
            key = self._get_key()
            f = Fernet(key)
            encrypted_message = f.encrypt(message.encode())
            return base64.urlsafe_b64encode(encrypted_message).decode()
        except Exception as e:
            logging.error(f"Error encrypting message: {str(e)}")
            # Return original message if encryption fails (fallback)
            return message
    
    def decrypt_message(self, encrypted_message: str) -> str:
        """Decrypt a message"""
        try:
            key = self._get_key()
            f = Fernet(key)
            
            # Decode from base64
            encrypted_data = base64.urlsafe_b64decode(encrypted_message.encode())
            
            # Decrypt
            decrypted_message = f.decrypt(encrypted_data)
            return decrypted_message.decode()
        except Exception as e:
            logging.error(f"Error decrypting message: {str(e)}")
            # Return encrypted message if decryption fails (fallback)
            return encrypted_message
    
    def is_encrypted(self, message: str) -> bool:
        """Check if a message appears to be encrypted"""
        try:
            # Try to decode as base64
            base64.urlsafe_b64decode(message.encode())
            # If successful and contains typical encrypted data patterns
            return len(message) > 50 and '=' in message
        except:
            return False

# Global encryption instance
message_encryptor = MessageEncryption()

def encrypt_message_content(content: str) -> str:
    """Encrypt message content"""
    return message_encryptor.encrypt_message(content)

def decrypt_message_content(encrypted_content: str) -> str:
    """Decrypt message content"""
    return message_encryptor.decrypt_message(encrypted_content)

def is_message_encrypted(content: str) -> bool:
    """Check if message content is encrypted"""
    return message_encryptor.is_encrypted(content)
