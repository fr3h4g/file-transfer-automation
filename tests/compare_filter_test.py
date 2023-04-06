"""Test compere_filter."""
from filetransferautomation.common import compare_filter


def test_compare_filter():
    """Test compere_filter."""

    assert compare_filter("HOST123", "*HOST*") is True
    assert compare_filter("HOST123", "HOST*") is True
    assert compare_filter("test.txt", "*.txt") is True
    assert compare_filter("test.txt", "*.*") is True
    assert compare_filter("test", "*.*") is True
    assert compare_filter(".test", "*.*") is True
    assert compare_filter("ABCDEFGHILJKLMN", "A*C*E*G*I*J*L*N") is True
    assert compare_filter("ABCDEFGHILJKLMN", "A?C?E?G?I?J?L?N") is True
    assert compare_filter("abc123abc.test", "abc???abc.test") is True
    assert compare_filter("   abc123abc.test   ", "abc???abc.test") is True
    assert compare_filter("   abc123abc.test   ", "    abc???abc.test    ") is True
    assert compare_filter("abc123abc.test", "    abc???abc.test    ") is True
    assert compare_filter("TEST.TXT", "test.txt") is True
    assert compare_filter("TEST.TXT", "*.txt|*.xtx") is True
    assert compare_filter("TEST.XTX", "*.txt|*.xtx") is True
    assert compare_filter("TEST.XTX", "*.txt|*.xtx") is True
    assert (
        compare_filter(
            "Triss_Vykort_B_20230324070003330423.txt", "Triss_Vykort_B_*.txt"
        )
        is True
    )
    assert (
        compare_filter("Triss_Vykort_B_20230324070003330423.txt", "Vykort_B_*.txt")
        is False
    )
    assert (
        compare_filter(
            "SVS_TRISS.iaprod-195135.2021-11-08_104213.C5B_POS.afp_oops.printed.xml",
            "SVS*_oops.*.xml",
        )
        is True
    )

    assert compare_filter("test.xml", "*.xml")
    assert not compare_filter("test.txt", "*.xml")

    assert compare_filter(
        "SVS_TRISS.iaprod-195135.2021-11-08_104213.C5B_POS.afp_oops.printed.xml",
        "SVS*_oops.*.xml",
    )
    assert compare_filter(
        "SVS_TRISS.iaprod-195135.2021-11-08_104213.C5B_POS.afp_oops.printed.xml",
        "svs*_oops.*.xml",
    )

    assert compare_filter(
        "SVS_TRISS.iaprod-195135.2021-11-08_104213.C5B_POS.afp_oops.printed.xml",
        "svs*_oops.*.xml|svs*_oops.printed.xml",
    )
    assert not compare_filter(
        "oops.xml",
        "svs*_oops.*.xml|svs*_oops.printed.xml|*.txt",
    )
    assert compare_filter(
        "oops.txt",
        "svs*_oops.*.xml|svs*_oops.printed.xml|*.txt",
    )

    assert compare_filter(
        "a.txt",
        "a.txt|b.txt|c.txt",
    )
    assert compare_filter(
        "b.txt",
        "a.txt|b.txt|c.txt",
    )
    assert compare_filter(
        "c.txt",
        "a.txt|b.txt|c.txt",
    )

    assert not compare_filter(
        "d.txt",
        "a.txt|b.txt|c.txt",
    )
