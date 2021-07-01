import os
import time

import pytest
import rsa

import src.auth


class Test_Crypto:
    def test_init(self):
        crypto = src.auth.Crypto()
        assert crypto.pubkey == None
        assert crypto.privkey == None

        pubkey, privkey = rsa.newkeys(1024)
        crypto = src.auth.Crypto(pubkey, privkey)
        assert crypto.pubkey == pubkey
        assert crypto.privkey == privkey

    def test_both_exists(self):
        pubkey, privkey = rsa.newkeys(1024)
        crypto = src.auth.Crypto()

        # None, None -> False
        assert crypto.both_exist(None, None) == False

        # None, True -> False
        assert crypto.both_exist(None, privkey) == False

        # True, None -> False
        assert crypto.both_exist(pubkey, None) == False

        # True, True -> True
        assert crypto.both_exist(pubkey, privkey) == True

    def test_only_one_exists(self):
        pubkey, privkey = rsa.newkeys(1024)
        crypto = src.auth.Crypto()

        # None, None -> True
        assert crypto.only_one_exists(None, None) == False

        # None, True -> False
        assert crypto.only_one_exists(None, privkey) == True

        # True, None -> False
        assert crypto.only_one_exists(pubkey, None) == True

        # True, True -> True
        assert crypto.only_one_exists(pubkey, privkey) == False

    def test_load_keys(self):
        pubkey_path = "temp_testing_pubkey"
        privkey_path = "temp_testing_privkey"
        # generate temporary key files
        pubkey, privkey = rsa.newkeys(1024)

        # save to temp
        f = open(pubkey_path, "wb")
        f.write(pubkey.save_pkcs1())
        f.close()

        f = open(privkey_path, "wb")
        f.write(privkey.save_pkcs1())
        f.close()

        try:
            # load the files to class
            crypto = src.auth.Crypto()
            crypto.load_keys(
                pubkey_path=pubkey_path, privkey_path=privkey_path
            )

            # verify that keys were loaded
            crypto.pubkey = pubkey
            crypto.privkey = privkey

        finally:  # regardless of test results, delete the test files
            # delete test files
            os.remove(pubkey_path)
            os.remove(privkey_path)

    def test_generate_keys(self):
        pubkey, privkey = rsa.newkeys(1024)
        crypto = src.auth.Crypto(pubkey, privkey)

        assert crypto.pubkey == pubkey
        assert crypto.privkey == privkey

        new_pubkey, new_privkey = crypto.generate_keys()

        # check keys were overwritten
        assert crypto.pubkey != pubkey
        assert crypto.privkey != privkey

        # check new keys returned are ones returned
        assert crypto.pubkey == new_pubkey
        assert crypto.privkey == new_privkey

        # check generated keys are correct type
        assert isinstance(crypto.pubkey, rsa.PublicKey)
        assert isinstance(crypto.privkey, rsa.PrivateKey)

    def test_save_keys(self):
        # save existing keys to file and load them to check equality
        pubkey, privkey = rsa.newkeys(1024)
        crypto = src.auth.Crypto(pubkey, privkey)

        pubkey_path = "temp_testing_pubkey"
        privkey_path = "temp_testing_privkey"
        crypto.save_keys(pubkey_path, privkey_path)

        try:
            with open(pubkey_path, "r") as f:
                pubkey_from_file = rsa.PublicKey.load_pkcs1(f.read())
                f.close()

            with open(privkey_path, "r") as f:
                privkey_from_file = rsa.PrivateKey.load_pkcs1(f.read())
                f.close()

            assert pubkey == pubkey_from_file
            assert privkey == privkey_from_file
        finally:  # regardless of test results, delete the test files
            os.remove(pubkey_path)
            os.remove(privkey_path)

        # generate keys and save them, check for generated key equality with files
        crypto = src.auth.Crypto()
        pubkey_path = "temp_testing_pubkey"
        privkey_path = "temp_testing_privkey"

        pubkey, privkey = crypto.generate_keys()

        crypto.save_keys(pubkey_path, privkey_path)

        try:
            with open(pubkey_path, "r") as f:
                pubkey_from_file = rsa.PublicKey.load_pkcs1(f.read())
                f.close()

            with open(privkey_path, "r") as f:
                privkey_from_file = rsa.PrivateKey.load_pkcs1(f.read())
                f.close()

            assert pubkey == pubkey_from_file
            assert privkey == privkey_from_file
        finally:  # regardless of test results, delete the test files
            os.remove(pubkey_path)
            os.remove(privkey_path)

    def test_encrypt_decrypt(self):
        # test if function outputs the correct token
        token = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
        pubkey, privkey = rsa.newkeys(1024)
        crypto = src.auth.Crypto(pubkey, privkey)

        encryped_token = crypto.encrypt_token_time(token)
        approximated_time = int(time.time())

        decrypt_token, decrypt_time = crypto.decrypt_token_x(encryped_token)

        assert decrypt_token == token
        assert int(decrypt_time) == pytest.approx(approximated_time, 10)
