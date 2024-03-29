#!/usr/bin/env python

import hashlib
import os
import unicodedata
from pathlib import Path
from typing import List

import click
import pkg_resources
from bitstring import BitArray
from blspy import AugSchemeMPL, PrivateKey
from click.utils import LazyFile

from chia_keys.consensus.coinbase import create_puzzlehash_for_pk
from chia_keys.util.bech32m import encode_puzzle_hash
from chia_keys.util.ints import uint32
from chia_keys.wallet.derive_keys import master_sk_to_wallet_sk


def std_hash(b: bytes) -> bytes:
    return hashlib.sha256(b).digest()


def bytes_to_mnemonic(mnemonic_bytes: bytes) -> str:
    if len(mnemonic_bytes) not in [16, 20, 24, 28, 32]:
        raise ValueError(
            f"Data length should be one of the following: [16, 20, 24, 28, 32], but it is {len(mnemonic_bytes)}."
        )
    word_list = bip39_word_list().splitlines()
    CS = len(mnemonic_bytes) // 4

    checksum = BitArray(bytes(std_hash(mnemonic_bytes)))[:CS]

    bitarray = BitArray(mnemonic_bytes) + checksum
    mnemonics = []
    assert len(bitarray) % 11 == 0

    for i in range(0, len(bitarray) // 11):
        start = i * 11
        end = start + 11
        bits = bitarray[start:end]
        m_word_position = bits.uint
        m_word = word_list[m_word_position]
        mnemonics.append(m_word)

    return " ".join(mnemonics)


def bytes_from_mnemonic(mnemonic_str: str) -> bytes:
    mnemonic: List[str] = mnemonic_str.split(" ")
    if len(mnemonic) not in [12, 15, 18, 21, 24]:
        raise ValueError("Invalid mnemonic length")

    word_list = {word: i for i, word in enumerate(bip39_word_list().splitlines())}
    bit_array = BitArray()
    for i in range(0, len(mnemonic)):
        word = mnemonic[i]
        if word not in word_list:
            raise ValueError(f"'{word}' is not in the mnemonic dictionary; may be misspelled")
        value = word_list[word]
        bit_array.append(BitArray(uint=value, length=11))

    CS: int = len(mnemonic) // 3
    ENT: int = len(mnemonic) * 11 - CS
    assert len(bit_array) == len(mnemonic) * 11
    assert ENT % 32 == 0

    entropy_bytes = bit_array[:ENT].bytes
    checksum_bytes = bit_array[ENT:]
    checksum = BitArray(std_hash(entropy_bytes))[:CS]

    assert len(checksum_bytes) == CS

    if checksum != checksum_bytes:
        raise ValueError("Invalid order of mnemonic words")

    return entropy_bytes


def bip39_word_list() -> str:
    return pkg_resources.resource_string(__name__, "util/english.txt").decode()


def token_bytes():
    return os.urandom(32)


def normalize_salt(prefix: str, passphrase: str) -> bytes:
    salt_str: str = prefix + passphrase
    return unicodedata.normalize("NFKD", salt_str).encode("utf-8")


def mnemonic_to_seed(mnemonic: str, passphrase: str) -> bytes:
    """
    Uses BIP39 standard to derive a seed from entropy bytes.
    """
    salt = normalize_salt("mnemonic", passphrase)
    mnemonic_normalized = unicodedata.normalize("NFKD", mnemonic).encode("utf-8")
    seed = hashlib.pbkdf2_hmac("sha512", mnemonic_normalized, salt, 2048)

    assert len(seed) == 64
    return seed


def show(master_seed: bytes, index: int, passphrase: str):
    new_seed: bytes = std_hash(master_seed)
    for i in range(index + 1):
        new_mnemonic: str = bytes_to_mnemonic(new_seed)
        new_entropy: bytes = bytes_from_mnemonic(new_mnemonic)
        assert new_seed == new_entropy
        if i == index:
            final_seed: bytes = mnemonic_to_seed(new_mnemonic, "")
            return (new_entropy, AugSchemeMPL.key_gen(final_seed))
        else:
            new_seed = std_hash(mnemonic_to_seed(new_mnemonic, passphrase))
    raise ValueError(f"Index out of bounds {i}")


def _derive(sk: PrivateKey, index: int):
    wallet_sk: PrivateKey = master_sk_to_wallet_sk(sk, uint32(index))
    wallet_address: str = encode_puzzle_hash(create_puzzlehash_for_pk(wallet_sk.get_g1()), "xch")
    return wallet_address


@click.group()
def cli():
    pass


@cli.command(name="generate")
@click.option('--passphrase', prompt="Your passphrase", default="", hide_input=True, help="Secret passphrase.")
@click.option("--output", type=click.Path(exists=False), default="master.key", help="Output file.")
def cli_generate(passphrase: str, output: str = None):
    if output is not None:
        passphrase_normalized = normalize_salt("", passphrase)
        passphrase_hash = hashlib.sha256(passphrase_normalized).digest()
        master_token: bytes = token_bytes()
        master_mnemonic: str = bytes_to_mnemonic(master_token)
        master_entropy: bytes = bytes_from_mnemonic(master_mnemonic)
        assert master_token == master_entropy
        master_seed = mnemonic_to_seed(master_mnemonic, passphrase)
        master_key: PrivateKey = AugSchemeMPL.key_gen(master_seed)
        master_fingerprint = master_key.get_g1().get_fingerprint()
        path = Path(output)
        if path.is_file():
            print(f"The output file {path.resolve()} already exists.")
        else:
            try:
                with open(output, "w") as file:
                    file.write(master_entropy.hex())
                    print(f"Passphrase  : {passphrase_normalized.hex()} -> sha256({passphrase_hash.hex()})")
                    print(f"Master key has been generated ({master_fingerprint}): {path.resolve()}")
            except FileNotFoundError as err:
                print(err)
    else:
        print(f"Please provide output destination.")


@cli.command(name="show")
@click.option('--passphrase', prompt="Your passphrase", default="", hide_input=True, help="Secret passphrase.")
@click.argument("input", type=click.File("r"))
@click.option("--index", default=0, help="Key index.")
@click.option("--derive", default=0, help="Derive key from spesific index.")
@click.option("--length", default=1, help="Length.")
@click.option("--passphrase-sha256", default=None, help="SHA256 of normalized passphrase.")
def cli_show(passphrase: str, input: LazyFile, index: int, derive: int, length: int, passphrase_sha256: str):
    passphrase_normalized = normalize_salt("", passphrase)
    passphrase_hash = hashlib.sha256(passphrase_normalized).digest()
    if passphrase_sha256 is not None and passphrase_hash != bytes.fromhex(passphrase_sha256):
        print("Invalid passphrase.")
    else:
        master_entropy: bytes = bytes.fromhex(input.readline().strip())
        master_mnemonic: str = bytes_to_mnemonic(master_entropy)
        master_seed: bytes = mnemonic_to_seed(master_mnemonic, passphrase)
        entropy, sk = show(master_seed, index, passphrase)
        print(f"Passphrase      : {passphrase_normalized.hex()} -> sha256({passphrase_hash.hex()})")
        print(f"Mnemonic        : {bytes_to_mnemonic(entropy)}")
        print(f"Private key     : {sk}")
        print(f"Public key      : {sk.get_g1()}")
        print(f"Fingerprint     : {sk.get_g1().get_fingerprint()}")
        print(f"Addresses       : ")
        for i in range(derive, derive + length):
            wallet_address: str = _derive(sk, i)
            print(f"[{index}/{i}]: {wallet_address}")


def main():
    cli()


if __name__ == "__main__":
    main()
