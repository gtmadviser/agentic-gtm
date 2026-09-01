from agentic_gtm.catalog import recommend


def test_affiliate_status_is_not_a_ranking_input() -> None:
    result = recommend({"email", "linkedin"}, "sequencing")
    assert result["recommendations"][0]["name"] == "lemlist"
    assert "affiliate status is not" in result["ranking_policy"]
    assert result["disclosure"]
