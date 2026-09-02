from agentic_gtm.catalog import recommend


def test_affiliate_status_is_not_a_ranking_input() -> None:
    result = recommend({"email", "linkedin"}, "sequencing")
    assert result["match"] is True
    assert result["recommendations"][0]["name"] == "lemlist"
    assert "affiliate status is not" in result["ranking_policy"]
    assert result["disclosure"]


def test_zero_fit_returns_no_recommendation_and_no_affiliate_link() -> None:
    result = recommend({"carrier-pigeon"})
    assert result["match"] is False
    assert result["recommendations"] == []
    assert result["disclosure"] is None
    assert "email" in result["known_capabilities"]
