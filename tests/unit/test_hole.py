"""
Unit tests for the Hole class.
"""

import pytest
from src.core.hole import Hole
from src.core.domain import Domain

class TestHole:
    def make_hole(self):
        left = Domain(dom_id="A", start=1, end=50, bitscore=10, coverage=0.1)
        right = Domain(dom_id="B", start=61, end=100, bitscore=20, coverage=0.08)
        return Hole(
            sys_id="sys1",
            pos=0,
            names=[],
            ref_doms=[(left, right)],
            start=51,
            end=60,
            sequence="M"*10
        )

    def test_best_name(self):
        hole = self.make_hole()
        assert hole.best_name == "A to B"

    def test_tuple_conversion(self):
        hole = self.make_hole()
        tup = hole.to_tuple()
        assert tup[0] == "A to B"
        assert tup[1] == 51
        assert tup[2] == 60

    def test_str_and_repr(self):
        hole = self.make_hole()
        s = str(hole)
        r = repr(hole)
        assert "sys1" in s
        assert "A to B" in s
        assert "sys1" in r
        assert "A to B" in r

    def test_length(self):
        hole = self.make_hole()
        assert hole.length == 10

    def test_best_name_with_missing_domains(self):
        # No left domain
        right = Domain(dom_id="B", start=61, end=100, bitscore=20, coverage=0.08)
        hole = Hole(
            sys_id="sys1",
            pos=0,
            names=[],
            ref_doms=[(None, right)],
            start=51,
            end=60,
            sequence="M"*10
        )
        assert hole.best_name == "BEGIN to B"
        # No right domain
        left = Domain(dom_id="A", start=1, end=50, bitscore=10, coverage=0.1)
        hole = Hole(
            sys_id="sys1",
            pos=0,
            names=[],
            ref_doms=[(left, None)],
            start=51,
            end=60,
            sequence="M"*10
        )
        assert hole.best_name == "A to END"
        # Neither domain
        hole = Hole(
            sys_id="sys1",
            pos=0,
            names=[],
            ref_doms=[(None, None)],
            start=51,
            end=60,
            sequence="M"*10
        )
        assert hole.best_name == "BEGIN to END"