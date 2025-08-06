"""
Unit tests for the System class.
"""

import pytest
from src.core.system import System
from src.core.domain import Domain
from src.core.hole import Hole

class TestSystem:
    def make_simple_system(self):
        domains = [
            Domain(dom_id="A", start=1, end=50, bitscore=10, coverage=0.1),
            Domain(dom_id="B", start=61, end=100, bitscore=20, coverage=0.08),
        ]
        return System(
            fam_id="1.A.1",
            sys_id="sys1",
            sys_len=120,
            domains=domains,
            accession="P00001",
            sequence="M"*120
        )

    def test_domain_map(self):
        system = self.make_simple_system()
        assert "A" in system.domain_map
        assert "B" in system.domain_map
        assert len(system.domain_map["A"]) == 1
        assert len(system.domain_map["B"]) == 1

    def test_hole_detection(self):
        # Domains at 1-50 and 61-100, so hole should be 50-61 (if margin=0, threshold=1)
        domains = [
            Domain(dom_id="A", start=1, end=50, bitscore=10, coverage=0.1),
            Domain(dom_id="B", start=61, end=100, bitscore=20, coverage=0.08),
        ]
        system = System(
            fam_id="1.A.1",
            sys_id="sys1",
            sys_len=120,
            domains=domains,
            accession="P00001",
            sequence="M"*120
        )
        # Re-run hole detection with margin=0, threshold=1
        system._identify_holes(threshold=1, margin=0)
        assert len(system.holes) == 1
        hole = system.holes[0]
        assert hole.start == 50  # current_domain.end + margin = 50 + 0
        assert hole.end == 61    # next_domain.start - margin = 61 - 0
        assert hole.length == 12  # 61 - 50 + 1

    def test_csv_row(self):
        system = self.make_simple_system()
        row = system.generate_csv_row()
        assert row[0] == "P00001"
        assert row[2] == "1.A.1"
        assert row[3] == "sys1"
        assert "A:1-50" in row[4]
        assert "B:61-100" in row[4]

    def test_characteristic_domains(self):
        system = self.make_simple_system()
        assert system.check_characteristic_domains(["A"]) is True
        assert system.check_characteristic_domains(["B"]) is True
        assert system.check_characteristic_domains(["C"]) is False