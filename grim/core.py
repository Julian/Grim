# -*- coding: utf-8 -*-
from pyrsistent import dq, pmap, pvector, s, v
from zope.interface import implementer
import attr

from grim import interfaces


@attr.s(hash=True)
class IllegalMove(Exception):

    start = attr.ib()
    end = attr.ib()
    board = attr.ib()
    piece = attr.ib()


@implementer(interfaces.Piece)
@attr.s(hash=True)
class Pawn(object):

    white_character = u"♙"

    def reachable_from(self, square):
        yield square.set(1, square[1] + 1)

    def will_move(self, start, end, board):
        moving_backwards = end[1] < start[1]
        if moving_backwards:
            raise IllegalMove(start=start, end=end, board=board, piece=self)


@attr.s(hash=True)
class _Empty(object):

    white_character = u" "

    def __nonzero__(self):
        return False


_STANDARD = pmap(
    [
        (v(0, 1), Pawn()),
        (v(1, 1), Pawn()),
        (v(2, 1), Pawn()),
        (v(3, 1), Pawn()),
        (v(4, 1), Pawn()),
        (v(5, 1), Pawn()),
        (v(6, 1), Pawn()),
        (v(7, 1), Pawn()),

        (v(0, 6), Pawn()),
        (v(1, 6), Pawn()),
        (v(2, 6), Pawn()),
        (v(3, 6), Pawn()),
        (v(4, 6), Pawn()),
        (v(5, 6), Pawn()),
        (v(6, 6), Pawn()),
        (v(7, 6), Pawn()),
    ]
)


@attr.s(hash=True)
class Player(object):
    """
    A chess player.
    """

    name = attr.ib()


@attr.s(hash=True)
class Board(object):
    """
    A chess board.
    """

    _pieces = attr.ib(default=_STANDARD, repr=False)
    _players = attr.ib(
        default=dq(Player(name=u"white"), Player(name=u"black")),
    )

    width = attr.ib(default=8)
    height = attr.ib(default=8)

    def __getitem__(self, square):
        return self._pieces.get(pvector(square)) or _Empty()

    def __unicode__(self):
        return u"\n".join(
            u"".join(
                " " + self[i, j].white_character + " "
                for i in xrange(self.width)
            ) for j in xrange(self.height)
        )

    def __str__(self):
        return unicode(self).encode("utf-8")

    @property
    def pieces(self):
        return self._pieces.iteritems()

    @property
    def turn_of(self):
        """
        The player whose turn it currently is.
        """
        return self._players[0]

    def movable_from(self, square):
        return self[square].reachable_from(square=square)

    def set(self, square, piece):
        """
        Set a piece on the given square (regardless of legality).

        Returns:

            Board:

                a new board with the piece in the requested position

        """

        pieces = self._pieces.set(square, piece)
        return attr.evolve(self, pieces=pieces)

    def move(self, start, end):
        """
        Move a piece from start to end, within the rules of Chess.

        Returns:

            Board:

                a new board with the piece in the requested position

        Raises:

            IllegalMove:

                if the piece on the given start square cannot be moved
                to the end square because the move would be illegal

        """

        piece = self._pieces[start]
        piece.will_move(start=start, end=end, board=self)
        pieces = self._pieces.remove(start).set(end, piece)
        players = self._players.rotate(-1)
        return attr.evolve(self, pieces=pieces, players=players)

    def subboard(self, squares):
        """
        Create a subboard view that contains only the given squares.

        """

        present = []
        leftmost, bottommost = self.width, self.height
        for square in squares:
            x, y = square
            if x < leftmost:
                leftmost = x
            if y < bottommost:
                bottommost = y

            piece = self[square]
            if piece:
                present.append((square, piece))

        pieces = pmap(
            [
                (square.set(0, x - leftmost).set(1, y - bottommost), piece)
                for (x, y), piece in present
            ]
        )
        return attr.evolve(
            self,
            pieces=pieces,
            width=self.width - leftmost,
            height=self.height - bottommost - 1,
        )


def sq(algebraic_notation):
    """
    Calculate the coordinates of a square in algebraic notation (e.g. c3)

    """

    rank = 0
    for i, letter in enumerate(algebraic_notation):
        if letter.isdigit():
            break
        rank += ord(letter.lower()) - ord("a")

    return v(rank, int(algebraic_notation[i:]) - 1)



def rectangle(a, b=None):
    """
    Retrieve all the squares that live between a rectangle bounded by 2 points.

    Inclusive of both points.

    """

    if b is None:
        a, b = v(0, 0), a

    (left_x, left_y), (right_x, right_y) = sorted([a, b])
    bottom_y, top_y = sorted([left_y, right_y])
    for x in xrange(left_x, right_x + 1):
        for y in xrange(bottom_y, top_y + 1):
            yield v(x, y)


PIECES = s(Pawn)
