from app.database import db


def get_delay_summary():
    pipeline = [
        {
            "$group": {
                "_id": None,
                "total_flights": {"$sum": 1},
                "delayed_flights": {
                    "$sum": {
                        "$cond": [{"$eq": ["$status", "DELAYED"]}, 1, 0]
                    }
                },
                "cancelled_flights": {
                    "$sum": {
                        "$cond": [{"$eq": ["$status", "CANCELLED"]}, 1, 0]
                    }
                },
                "average_departure_delay": {"$avg": "$departure_delay_minutes"},
                "average_arrival_delay": {"$avg": "$arrival_delay_minutes"},
                "max_departure_delay": {"$max": "$departure_delay_minutes"},
            }
        },
        {
            "$project": {
                "_id": 0,
                "total_flights": 1,
                "delayed_flights": 1,
                "cancelled_flights": 1,
                "average_departure_delay": {"$round": ["$average_departure_delay", 2]},
                "average_arrival_delay": {"$round": ["$average_arrival_delay", 2]},
                "max_departure_delay": 1,
            }
        },
    ]

    result = list(db.flights.aggregate(pipeline))

    if not result:
        return {
            "total_flights": 0,
            "delayed_flights": 0,
            "cancelled_flights": 0,
            "average_departure_delay": 0,
            "average_arrival_delay": 0,
            "max_departure_delay": 0,
        }

    return result[0]