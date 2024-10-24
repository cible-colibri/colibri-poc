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

    lg2 = LimitedGenerator("lg-2")
    lg2.from_template(scheme2)

    pass