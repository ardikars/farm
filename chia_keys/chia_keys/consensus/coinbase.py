from blspy import G1Element

from chia_keys.types.blockchain_format.sized_bytes import bytes32
from chia_keys.wallet.puzzles.p2_delegated_puzzle_or_hiddle_puzzle import puzzle_for_pk


def create_puzzlehash_for_pk(pub_key: G1Element) -> bytes32:
    return puzzle_for_pk(pub_key).get_tree_hash()
