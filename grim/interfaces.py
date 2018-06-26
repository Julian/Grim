from zope.interface import Interface


class Piece(Interface):
    """
    A chess piece.
    """

    def capturable_from(square):
        """
        Squares this piece can capture on, regardless of occupation or board.
        """

    def reachable_from(square):
        """
        Squares this piece can reach, regardless of occupation or board.
        """
