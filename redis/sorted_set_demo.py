import redis

def main():
    # Connect to Redis
    try:
        r = redis.Redis(host='localhost', port=6379, db=0)
        r.ping()
    except redis.ConnectionError:
        print("Error: Could not connect to Redis. Make sure Redis server is running.")
        return

    leaderboard_key = 'game_leaderboard'
    
    # Clear existing key for demo purposes
    r.delete(leaderboard_key)

    print(f"--- Adding players to {leaderboard_key} ---")
    # Add players with initial scores
    # Mapping of member: score
    players = {
        'Alice': 100,
        'Bob': 85,
        'Charlie': 110,
        'David': 95,
        'Eve': 105
    }
    r.zadd(leaderboard_key, players)
    print("Players added.")

    print("\n--- Current Leaderboard (Ranked by Score, High to Low) ---")
    # zrevrange returns elements from high to low score
    leaderboard = r.zrevrange(leaderboard_key, 0, -1, withscores=True)
    for rank, (player, score) in enumerate(leaderboard, 1):
        print(f"{rank}. {player.decode('utf-8')}: {int(score)}")

    print("\n--- Updating Score ---")
    print("Bob gains 30 points!")
    # zincrby increments the score of a member
    new_score = r.zincrby(leaderboard_key, 30, 'Bob')
    print(f"Bob's new score: {int(new_score)}")

    print("\n--- Top 3 Players ---")
    top_3 = r.zrevrange(leaderboard_key, 0, 2, withscores=True)
    for rank, (player, score) in enumerate(top_3, 1):
        print(f"{rank}. {player.decode('utf-8')}: {int(score)}")

    print("\n--- Players with score > 100 ---")
    # zrangebyscore (min, max)
    # We use zrevrangebyscore to get them sorted high to low
    high_scorers = r.zrevrangebyscore(leaderboard_key, '+inf', 101, withscores=True)
    for player, score in high_scorers:
        print(f"{player.decode('utf-8')}: {int(score)}")

    print("\n--- Rank of 'David' ---")
    # zrevrank gets the rank (0-based) in descending order
    rank = r.zrevrank(leaderboard_key, 'David')
    if rank is not None:
        print(f"David is currently at rank {rank + 1}")

if __name__ == "__main__":
    main()

"""
https://redis.io/docs/latest/develop/data-types/sorted-sets/

TYPE game_leaderboard
-> ZSET (sorted set)

ZADD game_leaderboard 80 David
// sets David with score of 80. Overwrites value if element “David” already exists
// returns 1 if David does not exist
// returns 0 if David exists

ZINCRBY game_leaderboard 50 David
// increments David's existing score by 50.
// if previously 80, now 130.

ZSCORE game_leaderboard David
// returns David's score

ZREM game_leaderboard David
// remove the element

ZRANK game_leaderboard David
// get position of element “David” in ascending sorted order
// 0 indexed

ZREVRANK game_leaderboard David
// get position of element “David” in descending sorted order
// 0 indexed

ZRANGE game_leaderboard 0 -1 WITHSCORES
// see all items in sorted order with scores

ZREVRANGE game_leaderboard 0 -1 WITHSCORES
// see all items in reverse sorted order with scores
"""