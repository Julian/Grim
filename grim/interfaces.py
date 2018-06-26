from zope.interface import Interface


class Piece(Interface):
    """
    A chess piece.
    """

    def reachable_from(square):
        """
        The squares this piece can reach, regardless of occupation or board.
        """
