"""Tests for chunked processing correctness.

Specifically tests that chunk-by-entity grouping prevents an entity's history
from being split across chunks (which would produce duplicate EAVT rows at
chunk boundaries — see Task 3/4 of the public-release-prep plan).
"""

import os
import tempfile
from unittest.mock import patch

import pandas as pd
from eavt_helper.classes.snapshot import Snapshot


class TestSnapshotChunkingByEntity:
    """Verify chunked snapshot->EAVT transformation produces the same output as unchunked."""

    def setup_method(self):
        # 6 entities, each with 3 snapshot rows (same value across rows for
        # attribute `name`; changing value for attribute `age`).
        # If chunking splits an entity's history, we will see duplicate
        # 'name' rows in the EAVT output instead of just one.
        rows = []
        for entity_id in range(1, 7):
            rows.extend(
                [
                    {
                        "user_id": entity_id,
                        "timestamp": "2024-01-01",
                        "name": f"user_{entity_id}",
                        "age": 20,
                    },
                    {
                        "user_id": entity_id,
                        "timestamp": "2024-02-01",
                        "name": f"user_{entity_id}",
                        "age": 21,
                    },
                    {
                        "user_id": entity_id,
                        "timestamp": "2024-03-01",
                        "name": f"user_{entity_id}",
                        "age": 22,
                    },
                ]
            )
        self.df = pd.DataFrame(rows)

        self.tmp = tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False)
        self.df.to_csv(self.tmp.name, index=False)
        self.tmp.close()

    def teardown_method(self):
        if os.path.exists(self.tmp.name):
            os.unlink(self.tmp.name)

    def _eavt_sorted(self, df: pd.DataFrame) -> pd.DataFrame:
        return df.sort_values(["e", "a", "t"]).reset_index(drop=True)

    def test_snapshot_chunking_matches_unchunked(self):
        """Chunked transform must produce the same EAVT rows as unchunked."""
        with patch("click.echo"):
            snap_unchunked = Snapshot(self.tmp.name, "user_id", "timestamp")
            eavt_unchunked = snap_unchunked.transform_to_eavt(chunk_size=None)

            snap_chunked = Snapshot(self.tmp.name, "user_id", "timestamp")
            # chunk_size=5 forces multiple chunks across 18 rows (6 entities * 3 rows)
            eavt_chunked = snap_chunked.transform_to_eavt(chunk_size=5)

        pd.testing.assert_frame_equal(
            self._eavt_sorted(eavt_unchunked),
            self._eavt_sorted(eavt_chunked),
        )

    def test_snapshot_chunking_no_duplicate_name_rows(self):
        """Each entity's 'name' attribute should emit exactly one EAVT row.

        Because 'name' never changes within an entity, only the first
        observation should be emitted. If chunking splits an entity's history,
        the first row of the second chunk re-emits 'name' as a spurious change.
        """
        with patch("click.echo"):
            snap = Snapshot(self.tmp.name, "user_id", "timestamp")
            eavt = snap.transform_to_eavt(chunk_size=5)

        name_rows = eavt[eavt["a"] == "name"]
        per_entity_counts = name_rows.groupby("e").size()
        # Each of the 6 entities should appear exactly once for attribute 'name'.
        assert (per_entity_counts == 1).all(), (
            f"Expected 1 'name' row per entity, got:\n{per_entity_counts}"
        )
