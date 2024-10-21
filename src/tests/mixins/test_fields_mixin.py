from colibri import AcvExploitationOnly, LimitedGenerator


def test_field_mixin() -> None:

    acv: AcvExploitationOnly = AcvExploitationOnly(
        name="acv-1",
        q_consumed={"kitchen": 350},
        co2_impact=25.0,
    )

    lg = LimitedGenerator("lg-1")

    #scheme1 = acv.to_template()
    scheme2 = lg.to_template()

    pass