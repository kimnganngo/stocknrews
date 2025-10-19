class LogCounter:
    def __init__(self):
        self.valid = 0
        self.no_ticker = 0
        self.no_date = 0
        self.http_errors = 0
        self.out_of_time = 0

    def as_dict(self):
        return {
            "valid_articles": self.valid,
            "no_ticker": self.no_ticker,
            "no_date": self.no_date,
            "http_errors": self.http_errors,
            "out_of_time": self.out_of_time,
        }
