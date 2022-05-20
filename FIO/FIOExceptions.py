from requests import Response


class FIOUnknown(Exception):
	def __init__(self, response: Response):
		super().__init__(f"Unknown error with FIO API {response}")


class FIONotAuthenticated(Exception):
	def __init__(self, response: Response):
		super().__init__(f"Attempt to use API entrypoint that requires authentication.")


class FIOBuildingNotFound(Exception):
	def __init__(self, response: Response, ticker: str):
		super().__init__(f"Building `{ticker}` not found.")


class FIOPlanetNotFound(Exception):
	def __init__(self, response: Response, planet: str):
		super().__init__(f"Planet `{planet}` not found.")


class FIOMaterialNotFound(Exception):
	def __init__(self, response: Response, ticker: str):
		super().__init__(f"Material `{ticker}` not found.")
