from self_healing_framework.ai.provider import RulesBasedAIProvider


def test_rules_based_provider_returns_ranked_locator_suggestions():
    provider = RulesBasedAIProvider()

    suggestions = provider.suggest_locators(
        failed_strategy="css",
        failed_value="#login-btn-old",
        element_name="login",
        dom_snapshot="<button data-testid='login'>Login</button>",
    )

    assert suggestions[0].strategy == "role"
    assert suggestions[0].value == "button::Login"
    assert suggestions[0].confidence > suggestions[-1].confidence
