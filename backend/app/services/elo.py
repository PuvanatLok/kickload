K_FACTOR_LOW = 32   # fewer than 20 games played
K_FACTOR_HIGH = 16  # 20 or more games played
K_THRESHOLD = 20


def expected_score(player_rating: int, opponent_rating: int) -> float:
    """
    Probability of player winning against opponent given their ratings.
    Returns a value between 0 and 1.

    WHY THIS FORMULA:
    Derived from the logistic curve. A 200-point rating gap means the stronger
    player wins ~75% of the time. A 400-point gap means ~91%. This matches
    empirically observed win rates in chess — the system chess has used since 1960.
    """
    return 1 / (1 + 10 ** ((opponent_rating - player_rating) / 400))


def k_factor(games_played: int) -> int:
    """
    Higher K for new players — their rating moves faster to find their true level.
    Lower K for experienced players — their rating is more stable and trustworthy.

    WHY TWO K VALUES NOT ONE:
    A new player's first 20 games are noisy — they might win by luck or lose due
    to unfamiliarity with the app. High K means rating corrects quickly.
    An established player's rating should be stable — small K prevents one bad
    game from erasing months of accurate rating signal.
    FUTURE: add a third tier (K=8) for players above 2000 ELO — protects very
    high ratings from deflation against weaker opponents.
    """
    return K_FACTOR_LOW if games_played < K_THRESHOLD else K_FACTOR_HIGH


def calculate_new_rating(
    player_rating: int,
    opponent_avg_rating: int,
    result: float,
    games_played: int,
) -> int:
    """
    result: 1.0 = win, 0.5 = draw, 0.0 = loss

    WHY OPPONENT_AVG_RATING NOT INDIVIDUAL OPPONENT:
    Football is a team sport — you play against a team, not one player.
    Using the average rating of all opponents on the opposing team is the
    standard adaptation of ELO for team sports.
    ALTERNATIVE: Glicko-2 rating system — accounts for rating deviation
    (confidence in the rating) and rating volatility. More accurate but
    significantly more complex to implement and explain to users.
    """
    k = k_factor(games_played)
    expected = expected_score(player_rating, opponent_avg_rating)
    new_rating = player_rating + k * (result - expected)
    return round(new_rating)


def calculate_match_ratings(
    team_a_players: list[tuple[int, int]],  # [(rating, games_played), ...]
    team_b_players: list[tuple[int, int]],
    team_a_score: int,
    team_b_score: int,
) -> tuple[list[int], list[int]]:
    """
    Returns new ratings for all players in (team_a_new_ratings, team_b_new_ratings).
    """
    team_a_avg = sum(r for r, _ in team_a_players) / len(team_a_players)
    team_b_avg = sum(r for r, _ in team_b_players) / len(team_b_players)

    if team_a_score > team_b_score:
        result_a, result_b = 1.0, 0.0
    elif team_a_score < team_b_score:
        result_a, result_b = 0.0, 1.0
    else:
        result_a, result_b = 0.5, 0.5

    team_a_new = [
        calculate_new_rating(rating, team_b_avg, result_a, games)
        for rating, games in team_a_players
    ]
    team_b_new = [
        calculate_new_rating(rating, team_a_avg, result_b, games)
        for rating, games in team_b_players
    ]

    return team_a_new, team_b_new
