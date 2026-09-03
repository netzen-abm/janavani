from services.follow_up import (
    FollowUpAction,
    FollowUpContext,
    FollowUpStatus,
    recommend_follow_up,
)


def test_letter_recommends_user_controlled_follow_up_letter():
    result = recommend_follow_up(
        FollowUpContext(case_type="complaint", documents=("letter",))
    )
    assert result.action == FollowUpAction.FOLLOW_UP_LETTER
    assert result.status == FollowUpStatus.DUE


def test_rti_received_recommends_review():
    result = recommend_follow_up(
        FollowUpContext(
            case_type="rti",
            documents=("rti",),
            response_status="received",
        )
    )
    assert result.action == FollowUpAction.REVIEW_RTI_RESPONSE


def test_unsatisfactory_rti_recommends_bsa_related_next_step():
    result = recommend_follow_up(
        FollowUpContext(
            case_type="rti",
            documents=("rti",),
            response_status="unsatisfactory",
        )
    )
    assert result.action == FollowUpAction.BSA_RELATED
    assert result.status == FollowUpStatus.ESCALATION_RECOMMENDED


def test_satisfactory_rti_can_close():
    result = recommend_follow_up(
        FollowUpContext(
            case_type="rti",
            documents=("rti",),
            response_status="satisfactory",
        )
    )
    assert result.action == FollowUpAction.CLOSE


def test_recommendation_does_not_claim_delivery():
    result = recommend_follow_up(
        FollowUpContext(case_type="complaint", documents=("letter",))
    )
    assert "sent" not in result.reason.lower()
    assert "delivered" not in result.reason.lower()
