# -*- coding: utf-8 -*-
from pyrsistent import dq, pmap, pset, pvector, s, v
from zope.interface import implementer
import attr

from grim import interfaces


@attr.s(hash=True)
class NoSuchSquare(Exception):

    square = attr.ib()


@attr.s(hash=True)
class IllegalMove(Exception):

    start = attr.ib()
    end = attr.ib()
    board = attr.ib()
    piece = attr.ib()


@implementer(interfaces.Piece)
@attr.s(hash=True)
class _OwnedPiece(object):

    piece = attr.ib()
    player = attr.ib()

    def __unicode__(self):
        return getattr(self.piece, self.player.name + "_character")

    def capturable_from(self, square):
        return self.piece.capturable_from(square)

    def reachable_from(self, square):
        return self.piece.reachable_from(square)

    def can_be_captured_by(self, player):
        return player != self.player


@implementer(interfaces.Piece)
@attr.s(hash=True)
class Pawn(object):

    black_character = u"♙"
    white_character = u"♟"

    def capturable_from(self, square):
        x, y = square
        yield v(x + 1, y + 1)
        yield v(x - 1, y + 1)

    def reachable_from(self, square):
        yield square.set(1, square[1] + 1)


@implementer(interfaces.Piece)
@attr.s(hash=True)
class _Empty(object):
    def __nonzero__(self):
        return False

    def __unicode__(self):
        return " "

    def capturable_from(self, square):
        return s()

    def reachable_from(self, square):
        return s()

    def can_be_captured_by(self, player):
        return True


@attr.s(hash=True)
class Player(object):
    """
    A chess player.
    """

    name = attr.ib()

    def piece(self, piece):
        return _OwnedPiece(player=self, piece=piece)


WHITE = Player(name=u"white")
BLACK = Player(name=u"black")
PLAYERS = dq(WHITE, BLACK)


_STANDARD = pmap(
    [
        (v(0, 1), WHITE.piece(Pawn())),
        (v(1, 1), WHITE.piece(Pawn())),
        (v(2, 1), WHITE.piece(Pawn())),
        (v(3, 1), WHITE.piece(Pawn())),
        (v(4, 1), WHITE.piece(Pawn())),
        (v(5, 1), WHITE.piece(Pawn())),
        (v(6, 1), WHITE.piece(Pawn())),
        (v(7, 1), WHITE.piece(Pawn())),

        (v(0, 6), BLACK.piece(Pawn())),
        (v(1, 6), BLACK.piece(Pawn())),
        (v(2, 6), BLACK.piece(Pawn())),
        (v(3, 6), BLACK.piece(Pawn())),
        (v(4, 6), BLACK.piece(Pawn())),
        (v(5, 6), BLACK.piece(Pawn())),
        (v(6, 6), BLACK.piece(Pawn())),
        (v(7, 6), BLACK.piece(Pawn())),
    ]
)


@attr.s(hash=True)
class Board(object):
    """
    A chess board.
    """

    _pieces = attr.ib(default=_STANDARD, repr=False)
    _players = attr.ib(default=PLAYERS)

    width = attr.ib(default=8)
    height = attr.ib(default=8)

    def __contains__(self, square):
        x, y = square
        return x < self.width and y < self.height

    def __iter__(self):
        for x in range(self.width):
            for y in range(self.height):
                yield v(x, y)


    def __getitem__(self, square):
        if isinstance(square, slice):
            return self.subboard(squares=_rectangle(square.start, square.stop))
        elif not square in self:
            raise NoSuchSquare(square)
        return self._pieces.get(pvector(square)) or _Empty()

    def __unicode__(self):
        return u"\n".join(
            u"".join(
                u" " + unicode(self[i, j]) + u" " for i in xrange(self.width)
            ) for j in xrange(self.height)
        )

    def __str__(self):
        return unicode(self).encode("utf-8")

    @classmethod
    def empty(cls, **kwargs):
        return cls(pieces=pmap(), **kwargs)

    @property
    def dimensions(self):
        return v(self.width, self.height)

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
        piece = self[square]
        reachable = piece.reachable_from(square=square)
        capturable = piece.capturable_from(square=square)
        return pset(self._in_bounds_and_unoccupied(reachable, capturable))

    def _in_bounds_and_unoccupied(self, *squares):
        """
        The squares that are in-bounds and not occupied on this board.
        """
        for each in squares:
            for square in each:
                if (
                    square in self and
                    self[square].can_be_captured_by(player=self.turn_of)
                ):
                    yield square

    def set(self, square, piece):
        """
        Set a piece on the given square (regardless of legality).

        Returns:

            Board:

                a new board with the piece in the requested position

        """

        return attr.evolve(self, pieces=self._pieces.set(square, piece))

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

        piece = self[start]
        if end not in self.movable_from(square=start):
            raise IllegalMove(start=start, end=end, board=self, piece=piece)
        pieces = self._pieces.remove(start).set(end, piece)
        players = self._players.rotate(-1)
        return attr.evolve(self, pieces=pieces, players=players)

    def subboard(self, squares):
        """
        Create a subboard view that contains only the given squares.

        """

        present = []
        leftmost, bottommost = self.dimensions
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



def _rectangle(a, b=None):
    """
    Retrieve all the squares that live between a rectangle bounded by 2 points.

    Inclusive of both points.

    """

    if a is None:
        a = v(0, 0)
    if b is None:
        a, b = v(0, 0), a

    (left_x, left_y), (right_x, right_y) = sorted([a, b])
    bottom_y, top_y = sorted([left_y, right_y])
    for x in xrange(left_x, right_x + 1):
        for y in xrange(bottom_y, top_y + 1):
            yield v(x, y)


PIECES = s(Pawn)
