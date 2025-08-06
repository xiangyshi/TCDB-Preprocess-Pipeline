"""
Unit tests for the Family class.
"""

import pytest
from pathlib import Path
from src.core.family import Family
from src.core.system import System
from src.core.domain import Domain

class TestFamily:
    def make_family(self):
        systems = [
            System(
                fam_id="1.A.1",
                sys_id="sys1",
                sys_len=100,
                domains=[
                    Domain(dom_id="A", start=1, end=50, bitscore=10, coverage=0.5),
                    Domain(dom_id="B", start=51, end=100, bitscore=20, coverage=0.5),
                ],
                accession="P00001",
                sequence="M"*100
            ),
            System(
                fam_id="1.A.1",
                sys_id="sys2",
                sys_len=100,
                domains=[
                    Domain(dom_id="A", start=1, end=60, bitscore=15, coverage=0.6),
                ],
                accession="P00002",
                sequence="M"*100
            ),
        ]
        return Family(
            family_id="1.A.1",
            systems=systems,
            output_directory=Path("/tmp")
        )

    def test_statistics(self):
        family = self.make_family()
        stats = family.statistics
        assert stats['num_systems'] == 2
        assert stats['total_domains'] == 3
        assert set(stats['unique_domains']) == {"A", "B"}
        assert stats['domain_frequencies']['A'] == 2
        assert stats['domain_frequencies']['B'] == 1

    def test_characteristic_domains(self):
        family = self.make_family()
        # A appears in both systems (100%), B in one system (50%)
        # With threshold=0.5, both should be characteristic
        assert "A" in family.characteristic_domains
        assert "B" in family.characteristic_domains  # 50% >= 50% threshold

    def test_get_system_by_id(self):
        family = self.make_family()
        sys = family.get_system_by_id("sys1")
        assert sys is not None
        assert sys.sys_id == "sys1"
        assert family.get_system_by_id("notfound") is None

    def test_get_systems_with_domain(self):
        family = self.make_family()
        systems = family.get_systems_with_domain("A")
        assert len(systems) == 2
        systems = family.get_systems_with_domain("B")
        assert len(systems) == 1

    def test_csv_data(self):
        family = self.make_family()
        csv_rows = family.generate_csv_data()
        assert len(csv_rows) == 2
        assert any("('A', 1, 50," in row[4] for row in csv_rows)
        assert any("('B', 51, 100," in row[4] for row in csv_rows)

    def test_to_dataframe(self):
        family = self.make_family()
        df = family.to_dataframe()
        assert not df.empty
        assert set(df['domain_id']) == {"A", "B"}