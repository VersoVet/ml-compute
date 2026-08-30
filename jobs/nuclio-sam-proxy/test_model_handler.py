"""Unit tests for Nuclio SAM proxy handler helpers."""

from model_handler import _extract_mask, _normalize_box, _normalize_points, mask_to_rle


class TestMaskHelpers:
    """Tests for mask conversion utilities."""

    def test_mask_to_rle_simple(self) -> None:
        """Encode a 2x2 mask with one foreground pixel."""
        mask = [[0, 1], [0, 0]]
        rle = mask_to_rle(mask)
        assert rle[:2] == [1, 1]
        assert rle[-4:] == [0, 0, 1, 1]

    def test_mask_to_rle_block(self) -> None:
        """IOG/CVAT RLE for a 4x4 central block in 10x10."""
        mask = [[0] * 10 for _ in range(10)]
        for y in range(3, 7):
            for x in range(3, 7):
                mask[y][x] = 1
        rle = mask_to_rle(mask)
        assert rle[-4:] == [0, 0, 9, 9]
        assert rle[0] == 33  # 10*3 + 3 leading zeros

    def test_extract_mask_2d(self) -> None:
        """Extract a flat 2D mask list."""
        masks = [[[0, 1], [0, 0]]]
        assert _extract_mask(masks) == [[0, 1], [0, 0]]

    def test_extract_mask_3d(self) -> None:
        """Extract mask when SAM returns batch dimension."""
        masks = [[[[0, 1], [0, 0]]]]
        assert _extract_mask(masks) == [[0, 1], [0, 0]]

    def test_normalize_points(self) -> None:
        """Convert CVAT point lists to integer pairs."""
        assert _normalize_points([[10.5, 20.1], [30, 40]]) == [[10, 20], [30, 40]]

    def test_normalize_box_flat(self) -> None:
        """Accept flat bbox arrays."""
        assert _normalize_box([10, 20, 100, 200]) == [10, 20, 100, 200]

    def test_normalize_box_corners(self) -> None:
        """Accept corner point pairs."""
        assert _normalize_box([[10, 20], [100, 200]]) == [10, 20, 100, 200]
