class JurisdictionService:

    def set_jurisdiction(self, context, mode, countries):
        context.jurisdiction = {
            "mode": mode,
            "countries": countries
        }

        return context