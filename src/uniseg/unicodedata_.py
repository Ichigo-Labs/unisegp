"""Unicodedata wrapper module."""

try:
    from unicodedata2 import category, east_asian_width  # type: ignore
except ImportError:
    from unicodedata import category, east_asian_width

from uniseg import Unicode_Property

__all__ = [
    'General_Category',
    'GC',
    'East_Asian_Width',
    'EA',
    'general_category_',
    'east_asian_width_'
]


class General_Category(Unicode_Property):
    """Unicode General_Category values."""
    Lu = 'Lu'
    """General_Category=Uppercase_Letter"""
    Ll = 'Ll'
    """General_Category=Lowercase_Letter"""
    Lt = 'Lt'
    """General_Category=Titlecase_Letter"""
    LC = 'LC'
    """General_Category=Cased_Letter"""
    Lm = 'Lm'
    """General_Category=Modifier_Letter"""
    Lo = 'Lo'
    """General_Category=Other_Letter"""
    L = 'L'
    """General_Category=Letter"""
    Mn = 'Mn'
    """General_Category=Nonspacing_Mark"""
    Mc = 'Mc'
    """General_Category=Spacing_Mark"""
    Me = 'Me'
    """General_Category=Enclosing_Mark"""
    M = 'M'
    """General_Category=Mark"""
    Nd = 'Nd'
    """General_Category=Decimal_Number"""
    Nl = 'Nl'
    """General_Category=Letter_Number"""
    No = 'No'
    """General_Category=Other_Number"""
    N = 'N'
    """General_Category=Number"""
    Pc = 'Pc'
    """General_Category=Connector_Punctuation"""
    Pd = 'Pd'
    """General_Category=Dash_Punctuation"""
    Ps = 'Ps'
    """General_Category=Open_Punctuation"""
    Pe = 'Pe'
    """General_Category=Close_Punctuation"""
    Pi = 'Pi'
    """General_Category=Initial_Punctuation"""
    Pf = 'Pf'
    """General_Category=Final_Punctuation"""
    Po = 'Po'
    """General_Category=Other_Punctuation"""
    P = 'P'
    """General_Category=Punctuation"""
    Sm = 'Sm'
    """General_Category=Math_Symbol"""
    Sc = 'Sc'
    """General_Category=Currency_Symbol"""
    Sk = 'Sk'
    """General_Category=Modifier_Symbol"""
    So = 'So'
    """General_Category=Other_Symbol"""
    S = 'S'
    """General_Category=Symbol"""
    Zs = 'Zs'
    """General_Category=Space_Separator"""
    Zl = 'Zl'
    """General_Category=Line_Separator"""
    Zp = 'Zp'
    """General_Category=Paragraph_Separator"""
    Z = 'Z'
    """General_Category=Separator"""
    Cc = 'Cc'
    """General_Category=Control"""
    Cf = 'Cf'
    """General_Category=Format"""
    Cs = 'Cs'
    """General_Category=Surrogate"""
    Co = 'Co'
    """General_Category=Private_Use"""
    Cn = 'Cn'
    """General_Category=Unassigned"""
    C = 'C'
    """General_Category=Other"""


GC = General_Category


class East_Asian_Width(Unicode_Property):
    """Unicode East_Asian_Width values."""
    A = 'A'
    """East_Asian_Width=Ambiguous"""
    F = 'F'
    """East_Asian_Width=Fullwidth"""
    H = 'H'
    """East_Asian_Width=Halfwidth"""
    N = 'N'
    """East_Asian_Width=Neutral"""
    Na = 'Na'
    """East_Asian_Width=Narrow"""
    W = 'W'
    """East_Asian_Width=Wide"""


EA = East_Asian_Width


def general_category_(c: str, /) -> General_Category:
    """Return General_Category property value for `c`."""
    return General_Category[category(c)]


def east_asian_width_(c: str, /) -> East_Asian_Width:
    """Return East_Asian_Width property value for `c`."""
    return East_Asian_Width[east_asian_width(c)]
