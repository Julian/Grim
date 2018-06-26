from unittest import TestCase

from hypothesis import given, strategies
from pyrsistent import pmap, s, v
from zope.interface import implementer, verify
import attr

from grim import core, interfaces
from grim.tests.strategies import board, moved_board, pieces, players, square


class TestBoard(TestCase):
    @given(data=strategies.data())
    def test_set(self, data):
        board = core.Board(pieces=pmap())
        contents = data.draw(pieces(board=board))
        for coordinate, piece in contents.iteritems():
            board = board.set(coordinate, piece)
        self.assertEqual(board, core.Board(pieces=contents))

    @given(data=strategies.data())
    def test_rectangular_subboard(self, data):
        superboard = data.draw(board())

        start, end = sorted(
            data.draw(
                strategies.sets(
                    square(board=superboard), min_size=2, max_size=2),
            ),
        )
        subboard = superboard.subboard(squares=core.rectangle(start, end))
        # FIXME

    def test_contains(self):
        board = core.Board()
        self.assertIn(core.sq("A8"), board)

    def test_not_contains_too_right(self):
        board = core.Board()
        self.assertNotIn(core.sq("I1"), board)

    def test_not_contains_too_high(self):
        board = core.Board()
        self.assertNotIn(core.sq("H9"), board)

    @given(data=strategies.data(), players=players)
    def test_it_is_the_next_players_turn_after_moving(self, data, players):
        board = core.Board(players=players)
        moved = data.draw(moved_board(board=board))
        self.assertEqual(moved.turn_of, players[1])

    def test_movable_from(self):
        square = v(0, 3)
        expected = {v(0, 0), v(0, 7), v(7, 0), v(7, 7)}
        board = core.Board(pieces=pmap({square: Piece(reachable=expected)}))
        self.assertEqual(set(board.movable_from(square=square)), expected)

    def test_movable_from_capture(self):
        pass

    def test_movable_from_outside_bounds(self):
        pass

    def test_movable_from_same_square(self):
        pass

    def test_movable_from_occupied(self):
        pass


class TestPawn(TestCase):
    @given(data=strategies.data())
    def test_it_can_move_forward(self, data):
        empty = core.Board(pieces=pmap())

        squares = core.rectangle(v(0, 0), v(empty.width, empty.height - 1))

        start = data.draw(square(board=empty.subboard(squares=squares)))
        end = v(start[0], start[1] + 1)

        board = empty.set(start, core.Pawn())
        moved = board.move(start=start, end=end)

        self.assertEqual(pmap(moved.pieces), pmap({end: core.Pawn()}))

    @given(data=strategies.data())
    def test_it_cannot_move_backwards(self, data):
        empty = core.Board(pieces=pmap())

        squares = core.rectangle(v(0, 1), v(empty.width, empty.height))

        start = data.draw(square(board=empty.subboard(squares=squares)))
        end = v(start[0], start[1] - 1)

        board = empty.set(start, core.Pawn())
        with self.assertRaises(core.IllegalMove):
            board.move(start=start, end=end)

    def test_it_is_a_piece(self):
        verify.verifyClass(interfaces.Piece, core.Pawn)


class TestEmpty(TestCase):
    def test_it_is_a_piece(self):
        verify.verifyObject(interfaces.Piece, core.Board(pieces=pmap())[0, 0])


class TestRectangle(TestCase):
    @given(data=strategies.data())
    def test_it_is_commutative(self, data):
        empty = core.Board(pieces=pmap())

        start = data.draw(square(board=empty))
        end = data.draw(square(board=empty))

        self.assertEqual(
            set(core.rectangle(start, end)),
            set(core.rectangle(end, start)),
        )


@implementer(interfaces.Piece)
@attr.s
class Piece(object):
    """
    A piece that moves to explicit static squares.
    """

    _reachable = attr.ib(default=s())

    def reachable_from(self, square):
        return self._reachable
