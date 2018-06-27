from unittest import TestCase

from hypothesis import given, strategies
from pyrsistent import pmap, s, v
from zope.interface import implementer, verify
import attr

from grim import core, interfaces
from grim.tests.strategies import board, moved_board, pieces, square


class PieceMixin(object):
    def white(self):
        return core.WHITE.piece(piece=self.Piece())

    def black(self):
        return core.BLACK.piece(piece=self.Piece())

    def test_it_is_a_piece(self):
        verify.verifyClass(interfaces.Piece, self.Piece)


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

    def test_empty(self):
        self.assertFalse(set(core.Board.empty().pieces))

    def test_dimensions(self):
        self.assertEqual(core.Board(width=3, height=5).dimensions, v(3, 5))

    @given(data=strategies.data())
    def test_it_is_the_next_players_turn_after_moving(self, data):
        board = core.Board()
        self.assertEqual(board.turn_of, core.WHITE)

        moved = data.draw(moved_board(board=board))
        self.assertEqual(moved.turn_of, core.BLACK)

    def test_movable_from(self):
        square = v(0, 3)
        reachable = {v(0, 0), v(0, 7)}
        capturable = {v(0, 0), v(7, 7)}
        piece = Piece(reachable=reachable, capturable=capturable)
        board = core.Board(pieces=pmap({square: core.WHITE.piece(piece)}))
        self.assertEqual(
            sorted(board.movable_from(square=square)),
            [v(0, 0), v(0, 7), v(7, 7)],
        )

    def test_movable_from_outside_bounds(self):
        square = v(0, 3)
        piece = Piece(reachable=[v(100, 100)], capturable=[v(101, 101)])
        board = core.Board(pieces=pmap({square: core.WHITE.piece(piece)}))
        self.assertEqual(sorted(board.movable_from(square=square)), [])

    def test_movable_from_empty(self):
        self.assertEqual(
            sorted(core.Board.empty().movable_from(square=v(0, 0))),
            [],
        )

    def test_movable_from_capturable(self):
        start, end = v(0, 0), v(0, 3)
        reachable = {end, v(0, 7)}
        capturable = {end, v(7, 7)}
        piece = Piece(reachable=reachable, capturable=capturable)
        board = core.Board(
            pieces=pmap(
                {
                    start: core.WHITE.piece(piece),
                    end: core.BLACK.piece(Piece()),
                },
            ),
        )
        self.assertEqual(
            sorted(board.movable_from(square=start)),
            [v(0, 3), v(0, 7), v(7, 7)],
        )

    def test_movable_from_occupied(self):
        pass

    def test_movable_from_not_your_turn(self):
        pass


class TestPawn(PieceMixin, TestCase):

    Piece = core.Pawn

    @given(data=strategies.data())
    def test_it_can_move_forward(self, data):
        empty = core.Board.empty()

        squares = core.rectangle(v(0, 0), v(empty.width, empty.height - 1))

        start = data.draw(square(board=empty.subboard(squares=squares)))
        end = v(start[0], start[1] + 1)

        board = empty.set(start, self.white())
        moved = board.move(start=start, end=end)

        self.assertEqual(pmap(moved.pieces), pmap({end: self.white()}))

    @given(data=strategies.data())
    def test_it_cannot_move_backwards(self, data):
        empty = core.Board.empty()

        squares = core.rectangle(v(0, 1), empty.dimensions)

        start = data.draw(square(board=empty.subboard(squares=squares)))
        end = v(start[0], start[1] - 1)

        board = empty.set(start, self.white())
        with self.assertRaises(core.IllegalMove):
            board.move(start=start, end=end)

    @given(data=strategies.data())
    def test_it_captures_diagonally(self, data):
        empty = core.Board.empty()

        squares = core.rectangle(v(1, 0), v(empty.width - 1, empty.height - 1))

        start = data.draw(square(board=empty.subboard(squares=squares)))
        end = data.draw(
            strategies.sampled_from(
                [
                    v(start[0] + 1, start[1] + 1),
                    v(start[0] - 1, start[1] + 1),
                ],
            ),
        )

        board = empty.set(start, self.white()).set(end, self.black())
        moved = board.move(start=start, end=end)

        self.assertEqual(pmap(moved.pieces), pmap({end: self.white()}))


class TestEmpty(TestCase):
    def test_it_is_a_piece(self):
        verify.verifyObject(interfaces.Piece, core.Board(pieces=pmap())[0, 0])


class TestRectangle(TestCase):
    @given(data=strategies.data())
    def test_it_is_commutative(self, data):
        empty = core.Board.empty()

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

    _capturable = attr.ib(default=s())
    _reachable = attr.ib(default=s())

    def capturable_from(self, square):
        return self._capturable

    def reachable_from(self, square):
        return self._reachable
