from hypothesis import strategies
from pyrsistent import pmap, pvector

from grim import core


@strategies.composite
def square(draw, board, max_rank=None, max_file=None):
    if max_rank is None:
        max_rank = board.height - 1
    if max_file is None:
        max_file = board.width - 1
    return draw(
        strategies.tuples(
            strategies.integers(min_value=0, max_value=max_file),
            strategies.integers(min_value=0, max_value=max_rank),
        ).map(pvector)
    )


@strategies.composite
def piece(draw):
    return draw(
        strategies.one_of(strategies.builds(Piece) for Piece in core.PIECES),
    )


@strategies.composite
def pieces(draw, board, piece=piece(), square=square):
    return draw(
        strategies.dictionaries(
            keys=square(board=board), values=piece,
        ).map(pmap),
    )


def board(empty=core.Board(pieces=pmap()), pieces=pieces):
    return strategies.builds(core.Board, pieces=pieces(board=empty))
