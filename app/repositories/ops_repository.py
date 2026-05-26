from app.database import db


def _serialize_snapshot(document):
    if not document:
        return None

    document["_id"] = str(document["_id"])

    if "created_at" in document and hasattr(document["created_at"], "isoformat"):
        document["created_at"] = document["created_at"].isoformat()

    return document


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


def get_top_delayed_routes(limit: int = 10, min_flights: int = 5):
    pipeline = [
        {
            "$group": {
                "_id": {
                    "origin": "$origin",
                    "destination": "$destination",
                },
                "total_flights": {"$sum": 1},
                "delayed_flights": {
                    "$sum": {
                        "$cond": [{"$eq": ["$status", "DELAYED"]}, 1, 0]
                    }
                },
                "avg_departure_delay": {"$avg": "$departure_delay_minutes"},
                "max_departure_delay": {"$max": "$departure_delay_minutes"},
            }
        },
        {"$match": {"total_flights": {"$gte": min_flights}}},
        {
            "$addFields": {
                "delay_rate_pct": {
                    "$multiply": [
                        {"$divide": ["$delayed_flights", "$total_flights"]},
                        100,
                    ]
                }
            }
        },
        {
            "$project": {
                "_id": 0,
                "origin": "$_id.origin",
                "destination": "$_id.destination",
                "total_flights": 1,
                "delayed_flights": 1,
                "avg_departure_delay": {"$round": ["$avg_departure_delay", 2]},
                "max_departure_delay": 1,
                "delay_rate_pct": {"$round": ["$delay_rate_pct", 2]},
            }
        },
        {
            "$sort": {
                "delay_rate_pct": -1,
                "avg_departure_delay": -1,
                "total_flights": -1,
            }
        },
        {"$limit": limit},
    ]

    results = list(db.flights.aggregate(pipeline))
    return {
        "limit": limit,
        "min_flights": min_flights,
        "results": results,
    }


def get_cancellations_by_airport(limit: int = 20, min_flights: int = 10):
    pipeline = [
        {
            "$group": {
                "_id": "$origin",
                "total_flights": {"$sum": 1},
                "cancelled_flights": {
                    "$sum": {
                        "$cond": [{"$eq": ["$status", "CANCELLED"]}, 1, 0]
                    }
                },
            }
        },
        {"$match": {"total_flights": {"$gte": min_flights}}},
        {
            "$addFields": {
                "cancellation_rate_pct": {
                    "$multiply": [
                        {"$divide": ["$cancelled_flights", "$total_flights"]},
                        100,
                    ]
                }
            }
        },
        {
            "$project": {
                "_id": 0,
                "origin": "$_id",
                "total_flights": 1,
                "cancelled_flights": 1,
                "cancellation_rate_pct": {"$round": ["$cancellation_rate_pct", 2]},
            }
        },
        {
            "$sort": {
                "cancellation_rate_pct": -1,
                "cancelled_flights": -1,
                "total_flights": -1,
            }
        },
        {"$limit": limit},
    ]

    results = list(db.flights.aggregate(pipeline))
    return {
        "limit": limit,
        "min_flights": min_flights,
        "results": results,
    }


def get_passenger_impact_summary():
    total_itineraries = db.passenger_itineraries.count_documents({})

    impacted_flights = db.flights.distinct(
        "flight_id",
        {"status": {"$in": ["DELAYED", "CANCELLED"]}},
    )

    impacted_itineraries = db.passenger_itineraries.count_documents(
        {"flights": {"$in": impacted_flights}}
    )

    if total_itineraries == 0:
        impact_rate_pct = 0
    else:
        impact_rate_pct = round((impacted_itineraries / total_itineraries) * 100, 2)

    connection_risk_count = db.passenger_itineraries.count_documents(
        {
            "flights": {"$in": impacted_flights},
            "connection_risk": True,
        }
    )

    top_impacted_flights_pipeline = [
        {"$match": {"flights": {"$in": impacted_flights}}},
        {"$unwind": "$flights"},
        {"$match": {"flights": {"$in": impacted_flights}}},
        {
            "$group": {
                "_id": "$flights",
                "impacted_itineraries": {"$sum": 1},
            }
        },
        {"$project": {"_id": 0, "flight_id": "$_id", "impacted_itineraries": 1}},
        {"$sort": {"impacted_itineraries": -1, "flight_id": 1}},
        {"$limit": 10},
    ]

    top_impacted_flights = list(
        db.passenger_itineraries.aggregate(top_impacted_flights_pipeline)
    )

    return {
        "total_itineraries": total_itineraries,
        "impacted_itineraries": impacted_itineraries,
        "impact_rate_pct": impact_rate_pct,
        "connection_risk_count": connection_risk_count,
        "top_impacted_flights": top_impacted_flights,
    }


def get_latest_metrics_snapshot():
    document = db.ops_metrics_snapshots.find_one({}, sort=[("created_at", -1)])
    return _serialize_snapshot(document)


def get_metrics_snapshots(limit: int = 20):
    cursor = db.ops_metrics_snapshots.find({}).sort("created_at", -1).limit(limit)
    return [_serialize_snapshot(document) for document in cursor]
