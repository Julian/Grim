from zope.interface import Attribute, Interface


class _Movable(Interface):
    def capturable_from(square):
        """
        Squares this piece can capture on, regardless of occupation or board.
        """

    def reachable_from(square):
        """
        Squares this piece can reach, regardless of occupation or board.
        """


class _OnBoard(_Movable):
    def for_ascii_board():
        """
        Render this on-board entity as unicode text for an ASCII Art board.
        """


class Piece(_Movable):
    """
    A chess piece.
    """

    black_character = Attribute(
        """
        The character to use when this piece is owned by black.
        """,
    )
    white_character = Attribute(
        """
        The character to use when this piece is owned by white.
        """,
    )
