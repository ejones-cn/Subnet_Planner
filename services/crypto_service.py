#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
加密服务模块
使用Windows DPAPI（数据保护API）实现敏感信息的加密和解密
DPAPI将加密绑定到当前Windows用户账户，无需管理密钥

非Windows平台使用cryptography库的Fernet加密方案
"""

import base64
import hashlib
import logging
import os
import sys

from i18n import _

try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    from cryptography.hazmat.backends import default_backend
    _CRYPTOGRAPHY_AVAILABLE = True
except ImportError:
    Fernet = None  # type: ignore[assignment,misc]
    hashes = None  # type: ignore[assignment]
    PBKDF2HMAC = None  # pyright: ignore[reportConstantRedefinition]
    default_backend = None  # type: ignore[assignment]
    _CRYPTOGRAPHY_AVAILABLE = False  # pyright: ignore[reportConstantRedefinition]
    logging.warning(_("cryptography_not_available"))


class CryptoService:
    """加密服务类，提供基于Windows DPAPI的加密解密功能"""

    _instance = None
    _dpapi_available = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        """初始化加密服务，检测DPAPI可用性"""
        if sys.platform == 'win32':
            try:
                # pyright: ignore[reportUnusedImport]
                import ctypes  # noqa: F401
                import ctypes.wintypes  # noqa: F401
                self._dpapi_available = True
            except ImportError:
                self._dpapi_available = False
                logging.warning(_("ctypes_not_available"))
        else:
            self._dpapi_available = False
            logging.info(_("non_windows_platform"))

    def encrypt(self, plaintext: str) -> str:
        """加密明文字符串

        Args:
            plaintext: 要加密的明文

        Returns:
            str: Base64编码的密文，加密失败时返回空字符串
        """
        if not plaintext:
            return ""

        try:
            if self._dpapi_available:
                return self._dpapi_encrypt(plaintext)
            else:
                return self._fallback_encrypt(plaintext)
        except Exception as e:
            logging.error(f"{_("encryption_failed")}: {str(e)}")
            return ""

    def decrypt(self, ciphertext: str) -> str:
        """解密密文字符串

        Args:
            ciphertext: Base64编码的密文

        Returns:
            str: 解密后的明文，解密失败时返回空字符串
        """
        if not ciphertext:
            return ""

        try:
            if self._dpapi_available:
                return self._dpapi_decrypt(ciphertext)
            else:
                return self._fallback_decrypt(ciphertext)
        except Exception as e:
            logging.error(f"{_("decryption_failed")}: {str(e)}")
            return ""

    def _dpapi_encrypt(self, plaintext: str) -> str:
        """使用Windows DPAPI加密数据

        Args:
            plaintext: 要加密的明文

        Returns:
            str: Base64编码的密文，加密失败时返回空字符串
        """
        import ctypes
        import ctypes.wintypes

        class DATA_BLOB(ctypes.Structure):
            _fields_ = [
                ('cbData', ctypes.wintypes.DWORD),
                ('pbData', ctypes.POINTER(ctypes.c_char))
            ]

        plaintext_bytes = plaintext.encode('utf-8')
        input_blob = DATA_BLOB()
        input_blob.cbData = len(plaintext_bytes)
        input_blob.pbData = ctypes.create_string_buffer(plaintext_bytes, len(plaintext_bytes))

        output_blob = DATA_BLOB()

        entropy = self._get_entropy()
        entropy_blob = DATA_BLOB()
        if entropy:
            entropy_bytes = entropy.encode('utf-8')
            entropy_blob.cbData = len(entropy_bytes)
            entropy_blob.pbData = ctypes.create_string_buffer(entropy_bytes, len(entropy_bytes))
            entropy_ptr = ctypes.byref(entropy_blob)
        else:
            entropy_ptr = None

        if not ctypes.windll.crypt32.CryptProtectData(
            ctypes.byref(input_blob),
            None,
            entropy_ptr,
            None,
            None,
            0,
            ctypes.byref(output_blob)
        ):
            raise RuntimeError("CryptProtectData调用失败")

        encrypted_data = ctypes.string_at(output_blob.pbData, output_blob.cbData)
        ctypes.windll.kernel32.LocalFree(output_blob.pbData)

        return base64.b64encode(encrypted_data).decode('ascii')

    def _dpapi_decrypt(self, ciphertext: str) -> str:
        """使用Windows DPAPI解密数据

        Args:
            ciphertext: Base64编码的密文

        Returns:
            str: 解密后的明文，解密失败时返回空字符串
        """
        import ctypes
        import ctypes.wintypes

        class DATA_BLOB(ctypes.Structure):
            _fields_ = [
                ('cbData', ctypes.wintypes.DWORD),
                ('pbData', ctypes.POINTER(ctypes.c_char))
            ]

        encrypted_bytes = base64.b64decode(ciphertext)
        input_blob = DATA_BLOB()
        input_blob.cbData = len(encrypted_bytes)
        input_blob.pbData = ctypes.create_string_buffer(encrypted_bytes, len(encrypted_bytes))

        output_blob = DATA_BLOB()

        entropy = self._get_entropy()
        entropy_blob = DATA_BLOB()
        if entropy:
            entropy_bytes = entropy.encode('utf-8')
            entropy_blob.cbData = len(entropy_bytes)
            entropy_blob.pbData = ctypes.create_string_buffer(entropy_bytes, len(entropy_bytes))
            entropy_ptr = ctypes.byref(entropy_blob)
        else:
            entropy_ptr = None

        if not ctypes.windll.crypt32.CryptUnprotectData(
            ctypes.byref(input_blob),
            None,
            entropy_ptr,
            None,
            None,
            0,
            ctypes.byref(output_blob)
        ):
            raise RuntimeError("CryptUnprotectData调用失败")

        decrypted_data = ctypes.string_at(output_blob.pbData, output_blob.cbData)
        ctypes.windll.kernel32.LocalFree(output_blob.pbData)

        return decrypted_data.decode('utf-8')

    def _get_entropy(self) -> str:
        """获取加密熵值，增加加密强度

        Returns:
            str: 熵值字符串
        """
        app_identifier = "SubnetPlanner_HiddenInfo_v1"
        return app_identifier

    def _fallback_encrypt(self, plaintext: str) -> str:
        """备用加密方案（非Windows平台使用）

        使用cryptography库的Fernet加密方案，安全性较高
        如果cryptography库不可用，回退到XOR加密

        Args:
            plaintext: 要加密的明文

        Returns:
            str: Base64编码的密文，加密失败时返回空字符串
        """
        if _CRYPTOGRAPHY_AVAILABLE:
            return self._fernet_encrypt(plaintext)
        else:
            return self._simple_xor_encrypt(plaintext)

    def _fallback_decrypt(self, ciphertext: str) -> str:
        """备用解密方案（非Windows平台使用）

        Args:
            ciphertext: Base64编码的密文

        Returns:
            str: 解密后的明文
        """
        if _CRYPTOGRAPHY_AVAILABLE:
            return self._fernet_decrypt(ciphertext)
        else:
            return self._simple_xor_decrypt(ciphertext)

    def _fernet_encrypt(self, plaintext: str) -> str:
        """使用Fernet加密方案加密数据

        Args:
            plaintext: 要加密的明文

        Returns:
            str: Base64编码的密文，加密失败时返回空字符串
        """
        try:
            fernet_key = self._derive_fernet_key()
            f = Fernet(fernet_key)  # pyright: ignore[reportOptionalCall]
            encrypted_bytes = f.encrypt(plaintext.encode('utf-8'))
            return encrypted_bytes.decode('ascii')
        except Exception as e:
            logging.error(f"{_("fernet_encryption_failed")}: {str(e)}")
            return ""

    def _fernet_decrypt(self, ciphertext: str) -> str:
        """使用Fernet加密方案解密数据

        Args:
            ciphertext: Base64编码的密文

        Returns:
            str: 解密后的明文，解密失败时返回空字符串
        """
        try:
            fernet_key = self._derive_fernet_key()
            f = Fernet(fernet_key)  # pyright: ignore[reportOptionalCall]
            decrypted_bytes = f.decrypt(ciphertext.encode('utf-8'))
            return decrypted_bytes.decode('utf-8')
        except Exception as e:
            logging.error(f"{_("fernet_decryption_failed")}: {str(e)}")
            return ""

    def _simple_xor_encrypt(self, plaintext: str) -> str:
        """简单XOR加密（备用方案，当cryptography库不可用时使用）

        Args:
            plaintext: 要加密的明文

        Returns:
            str: Base64编码的密文，加密失败时返回空字符串
        """
        key = self._derive_simple_key()
        plaintext_bytes = plaintext.encode('utf-8')
        encrypted_bytes = bytearray()
        for i, byte in enumerate(plaintext_bytes):
            key_byte = key[i % len(key)]
            encrypted_bytes.append(byte ^ key_byte)
        return base64.b64encode(bytes(encrypted_bytes)).decode('ascii')

    def _simple_xor_decrypt(self, ciphertext: str) -> str:
        """简单XOR解密（备用方案，当cryptography库不可用时使用）

        Args:
            ciphertext: Base64编码的密文

        Returns:
            str: 解密后的明文，解密失败时返回空字符串
        """
        key = self._derive_simple_key()
        encrypted_bytes = base64.b64decode(ciphertext)
        decrypted_bytes = bytearray()
        for i, byte in enumerate(encrypted_bytes):
            key_byte = key[i % len(key)]
            decrypted_bytes.append(byte ^ key_byte)
        return bytes(decrypted_bytes).decode('utf-8')

    def _derive_fernet_key(self) -> bytes:
        """派生Fernet加密密钥

        使用PBKDF2HMAC从机器特征和应用标识符派生密钥

        Returns:
            bytes: Fernet格式的密钥（URL安全base64编码的32字节密钥）
        """
        salt = b'SubnetPlanner_Salt_2024'
        password = self._get_machine_identifier().encode('utf-8')
        
        kdf = PBKDF2HMAC(  # pyright: ignore[reportOptionalCall]
            algorithm=hashes.SHA256(),  # pyright: ignore[reportOptionalMemberAccess]
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()  # pyright: ignore[reportOptionalCall]
        )
        key = base64.urlsafe_b64encode(kdf.derive(password))
        return key

    def _derive_simple_key(self) -> bytes:
        """从机器特征派生简单加密密钥（XOR备用方案使用）

        Returns:
            bytes: 派生出的密钥字节
        """
        machine_id = self._get_machine_identifier()
        return hashlib.sha256(machine_id.encode('utf-8')).digest()

    def _get_machine_identifier(self) -> str:
        """获取机器标识符，用于派生加密密钥

        Returns:
            str: 机器标识符字符串
        """
        machine_id = f"{os.name}-{sys.platform}"
        try:
            if sys.platform == 'win32':
                import ctypes
                buffer = ctypes.create_unicode_buffer(256)
                ctypes.windll.kernel32.GetComputerNameW(buffer, ctypes.byref(ctypes.c_ulong(256)))
                machine_id += f"-{buffer.value}"
        except Exception:
            pass
        machine_id += "-SubnetPlanner_HiddenInfo_Key"
        return machine_id

    @staticmethod
    def mask_password(password: str) -> str:
        """将密码进行掩码处理，显示首两位和末两位，中间用*号代替

        Args:
            password: 原始密码

        Returns:
            str: 掩码后的密码字符串
        """
        if not password:
            return ""
        if len(password) <= 4:
            return password[:2] + "**"
        return password[:2] + "*" * (len(password) - 4) + password[-2:]


def get_crypto_service() -> CryptoService:
    """获取加密服务单例

    Returns:
        CryptoService: 加密服务实例
    """
    return CryptoService()
