from colibri import AcvExploitationOnly, LimitedGenerator


def test_field_mixin() -> None:

    acv: AcvExploitationOnly = AcvExploitationOnly(
        name="acv-1",
        q_consumed={"kitchen": 350},
        co2_impact=25.0,
    )

    lg = LimitedGenerator("lg-1")

    #scheme1 = acv.to_template()
    scheme2 = LimitedGenerator.to_template()

    lg2 : LimitedGenerator = LimitedGenerator.from_template(scheme2)
    lg2.initialize()
    lg2.run(1,1)

    print(lg2.q_consumed)
    pass