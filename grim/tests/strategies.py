from hypothesis import strategies
from pyrsistent import pdeque, pmap, pvector

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


PIECE = {Piece: strategies.builds(Piece) for Piece in core.PIECES}


def piece():
    return strategies.one_of(PIECE.values())


def pieces(board, piece=piece(), square=square):
    return strategies.dictionaries(
        keys=square(board=board), values=piece,
    ).map(pmap)


def board(empty=core.Board(pieces=pmap()), pieces=pieces):
    return strategies.builds(core.Board, pieces=pieces(board=empty))


@strategies.composite
def legal_move_on(draw, board):
    """
    A legal move (start and end) on the given chess board.
    """
    start, _ = draw(strategies.sampled_from(sorted(board.pieces)))
    end = draw(strategies.sampled_from(sorted(board.movable_from(start))))
    return start, end


def moved_board(board):
    """
    A board that is one move away from the given one.
    """
    return legal_move_on(board=board).map(
        lambda (start, end): board.move(start=start, end=end),
    )


empty_board = strategies.just(core.Board.empty())
