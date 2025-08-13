from holly_simulator import Assets


# todo: fuzzing tests
# todo: transaction costs
def test_underlying_adjustment():
    """
    Adjusting the underlying share by any amount and then back to the original should keep all values the same.
    """
    total_amount = 10
    unit_cost = 50
    assets = Assets()

    while total_amount <= 100:
        assets.adjust_underlying_share(total_amount, unit_cost)
        previous_underlying = assets.underlying
        previous_option = assets.option
        previous_cash = assets.cash

        assets.adjust_underlying_share(total_amount + 5, unit_cost)
        assets.adjust_underlying_share(total_amount, unit_cost)

        assert assets.underlying == previous_underlying
        assert assets.option == previous_option
        assert assets.cash == previous_cash

        total_amount += 1
        unit_cost += 2
