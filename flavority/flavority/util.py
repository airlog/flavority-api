
def ViewPager(query, page=1, limit_per_page=10):
    return query.offset(limit_per_page * (page - 1)).limit(limit_per_page)


class Flavority:

    @staticmethod
    def success(**kwargs):
        d = {key: value for key, value in kwargs.items()}
        d['api_result'] = 'success'
        return d

    @staticmethod
    def failure(message=None, code=None):
        return {
            "api_result": "failure",
            "message": message,
            "code": code,
        }


__all__ = ['ViewPager', 'Flavority', ]
