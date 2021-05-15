import logging
from typing import Tuple
from discord.channel import TextChannel
import rsa
import time
import base64
from src.constants import *

class Crypto:
    def __init__(self, pubkey: rsa.PublicKey = None, privkey: rsa.PrivateKey = None) -> None:
        self.pubkey = pubkey
        self.privkey = privkey
    
    def both_exist(self, x, y):
        """
        Returns true if both variables exist, false if one or neither exists.
        Used to ensure both public keys and private keys are being passed.
        Used for syntactic sugar for logical and.
        """
        return bool(x and y)

    def only_one_exists(self, x, y):
        """
        Returns true if only one variable exists, false if both or neither exists.
        Used to validate that both public keys and private keys are being passed.
        Used for syntactic sugar for logical inverse xor.
        """
        return bool(x) != bool(y)
    
    def load_keys(self, pubkey_path, privkey_path):
        """Load keys from files"""

        if self.only_one_exists(pubkey_path, privkey_path):
            raise SyntaxError('Both pubkey and privkey arguments must exist.')

        logging.info('Loaded pubkey and privkey from file.')
        with open(pubkey_path, 'r') as f:
            self.pubkey = rsa.PublicKey.load_pkcs1(f.read())
            f.close()

        with open(privkey_path, 'r') as f:
            self.privkey = rsa.PrivateKey.load_pkcs1(f.read())
            f.close()

    def generate_keys(self) -> Tuple[rsa.PublicKey, rsa.PrivateKey]:
        """Generates NEW rsa public private key set, sets (overwrites) to self, and returns."""
        pubkey, privkey = rsa.newkeys(1024)
        
        self.pubkey = pubkey
        self.privkey = privkey

        f = open('mbox_public.key', 'wb')
        f.write(pubkey.save_pkcs1())
        f.close()

        f = open('mbox_private.key', 'wb')
        f.write(privkey.save_pkcs1())
        f.close()

        return pubkey, privkey
    
    def save_keys(self, pubkey_save_path = 'mbox_public.key', privkey_save_path = 'mbox_private.key'):
        """Save the keys to file. Include the name in the save path."""
        f = open(pubkey_save_path, 'wb')
        f.write(self.pubkey.save_pkcs1())
        f.close()

        f = open(privkey_save_path, 'wb')
        f.write(self.privkey.save_pkcs1())
        f.close()

    def encrypt_token_time(self, token) -> str:
        """Encrypt token with time with a public key.
        
        Returns base64 encoded encrypted string.
        """
        timestamp = str(int(time.time()))
        token_timestamp = token + timestamp
        message = token_timestamp.encode('utf8')
        crypto = rsa.encrypt(message, self.pubkey)
        crypto_base64 = base64.b64encode(crypto)
        return crypto_base64.decode("utf-8")
    
    def encrypt_token_x(self, token, x) -> str:
        """Encrypt token with time with the provided string.
        
        Returns base64 encoded encrypted string.
        """
        token_x = token + x
        message = token_x.encode('utf8')
        crypto = rsa.encrypt(message, self.pubkey)
        crypto_base64 = base64.b64encode(crypto)
        return crypto_base64.decode("utf-8")

    def decrypt_token_x(self, crypto_base64) -> Tuple[str, str]:
        """decrypts base64 string to two parts, token (0:59) with x (59:)
        x is meant to store time based information or text channel id (default: unix timestamp)

        Args:
            crypto_base64 ([type]): [description]

        Returns:
            Tuple[str, str]: [description]
        """
        crypto = base64.b64decode(crypto_base64)
        message = rsa.decrypt(crypto, self.privkey)
        return message[:59].decode("utf-8"), message[59:].decode("utf-8")
    
class Auth:
    def is_admin_channel(channel: TextChannel, token, crypto: Crypto):
        if channel.name and 'music-box-admin' in channel.name:
            # Check if the admin channel contains the correct secret
            if channel.topic:
                try:
                    decrypt_token, channel_id = crypto.decrypt_token_x(channel.topic)
                    if decrypt_token == token and int(channel_id) == channel.id:
                        return True
                    else:
                        logging.info(f'Token/ID key mismatch at [{channel.guild}]{channel}.')
                except rsa.pkcs1.DecryptionError as e:
                    logging.info(f'{str(e)} at [{channel.guild}]{channel}. Is the key invalid?')
                    return False
        return False

    def validate_timestamp(decrypted_epoch: int, message_epoch: int, spent_epoch: int = 0, startup_epoch: int = None, tolerance = 60 ) -> bool:
        if decrypted_epoch <= spent_epoch:
            logging.warning('A encrypted command message was sent again. (Potential replay attack)')
            return False
        
        if startup_epoch:
            if abs(message_epoch - startup_epoch) <= tolerance:
                # TODO: Fix limitation by saving spent_epoch variable to disk and loading it 
                logging.warning(f'A encrypted command message cannot be sent within {2*tolerance} seconds of bot startup. (Potential replay attack thorugh bypassing spent_epoch)')
                return False
        
        logging.info(f"Message was created {message_epoch-decrypted_epoch} seconds after this key was generated.")

        # check if the decrypted epoch was created within tolerance seconds of the message being sent
        if abs(message_epoch-decrypted_epoch) <= tolerance:
            spent_epoch = decrypted_epoch
            return True

        logging.warning(f"{message_epoch-decrypted_epoch} seconds is not within {tolerance}. Is your system time set accurately? (Potential replay attack)")
        return False