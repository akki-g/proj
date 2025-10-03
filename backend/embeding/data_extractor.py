from typing import List, Dict, Any
from sqlalchemy import text
from db_manager import DatabaseManager

class DataExtractor:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager

    def extract_teams(self) -> List[Dict[str, Any]]:

        query = """
        SELECT
            team_id, city, name, abbreviation,
            conference, division
        FROM teams
        ORDER BY team_id
        """
        with self.db.get_connection() as conn:
            res = conn.execute(text(query))
            return [dict(row._mapping) for row in res]
        
    def extract_players(self) -> List[Dict[str, Any]]:
        query = """
        SELECT 
            p.player_id, p.team_id, p.first_name, p.last_name,
            p.position, p.height, p.weight, p.birth_date,
            p.draft_year, p.season_exp,
            t.name as team_name, t.abbreviation as team_abbr
        FROM players p
        LEFT JOIN teams t ON p.team_id = t.team_id
        ORDER BY p.player_id
        """ 

        with self.db.get_connection() as conn:
            res = conn.execute(text(query))
            return [dict(row._mapping) for row in res]
        
    def extract_games(self) -> List[Dict[str, Any]]:
        query = """
        SELECT 
            g.game_id, g.season, g.game_timestamp::date as game_date,
            g.home_team_id, g.away_team_id, 
            g.home_points, g.away_points, g.winning_team_id,
            ht.name as home_team_name, ht.abbreviation as 
                home_team_abbr,
            at.name as away_team_name, at.abbreviation as 
                away_team_abbr
            FROM games g
            JOIN teams ht ON g.home_team_id = ht.team_id
            JOIN teams at ON g.away_team_id = at.team_id
            ORDER BY g.game_timestamp DESC
        """

        with self.db.get_connection() as conn:
            res = conn.execute(text(query))
            return [dict(row._mapping) for row in res]
        
    def extract_boxscores(self) -> List[Dict[str, Any]]:
        query = """
        SELECT 
            b.game_id, b.person_id, as player_id, b.team_id,
            b.starter, b.seconds, b.points,
            b.fg2_made, b.fg2_attempted,
            b.fg3_made, b.fg3_attempted,
            b.ft_made, b.ft_attempted,
            b.offensive_reb, b.defensive_reb,
            b.assists, b.steals, b.blocks, b.turnovers,
            b.defensive_fouls, b.offensive_fouls,
            p.first_name, p.last_name, p.position,
            t.name as team_name, t.abbreviation as team_abbr,
            g.season, g.game_timestamp::date as game_date
        FROM player_box_scores b
        JOIN players p ON b.person_id = p.player_id
        JOIN team t ON b.team_id = t.team_id
        JOIN games g ON b.game_id = g.game_id
        ORDER BY g.game_timestamp DESC, b.points DESC
        """

        with self.db.get_connection() as conn:
            res = conn.execute(text(query))
            return [dict(row._mapping) for row in res]