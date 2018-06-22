from unittest import TestCase

from hypothesis import given, strategies
from pyrsistent import pmap, v
from zope.interface import verify

from grim import core, interfaces
from grim.tests.strategies import board, pieces, square


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

    def test_cannot_move_on_top(self):
        pass

    def test_cannot_move_when_not_your_turn(self):
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

        self.assertEqual(moved, core.Board(pieces=pmap({end: core.Pawn()})))

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
