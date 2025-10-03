import hashlib
import json
from typing import Dict, List, Any
from datetime import date, datetime

class DocumentBuilder:

    @staticmethod
    def hash_content(content: str) -> str:
        return hashlib.md5(content.encode()).hexdigest()
    
    @staticmethod
    def json_serialize(obj: Any) -> str:
        
        def default(o):
            if isinstance(o, (date, datetime)):
                return o.isoformat()

            return str(o)
        
        return json.dumps(obj, default=default, sort_keys=True)
    

    def build_team_document(self, team: Dict[str, Any]) -> Dict[str, Any]:
        team_id = team['team_id']

        # structure data for better retrieve
        structured = {
            "entity_type" : "team",
            "team_id" : "team_id",
            "name" : f"{team['city']} {team['name']}",
            "abbreviation" : team['abbreviation'],
            "conference" : team['conference'],
            "division" : team['division']
        }

        # human readable text for sem search
        text_parts = [
            f"The {team['city']} {team['name']} ({team['abbreviation']})",
            f"plays in the {team['conference']} Conference",
            f"and the {team['division']} Division.",
            f"Team info: {team['abbreviation']} - {team['city']} {team['name']} - {team['conference']} {team['division']}"
        ]

        content_text = " ".join(text_parts)
        content_json = self.json_serialize(structured)

        return {
            "id" : f"team_{team_id}_profile",
            "entity_type": "team",
            "entity_id" : str(team_id),
            "team_id" : team_id,
            "game_id" : None, 
            "player_id" : None, 
            "chunk_type" : "profile",
            "content_json" : structured,
            "content_text" : content_text,
            "content_hash" : self.hash_content(content_json),
            "season" : None,
            "game_date" : None
        }
    
    def build_player_document(self, player: Dict[str, Any]) -> Dict[str, Any]:
        """Create player document with biographical and team info"""
        player_id = player['player_id']
        full_name = f"{player['first_name']} {player['last_name']}"
        
        structured = {
            "entity_type": "player",
            "player_id": player_id,
            "name": full_name,
            "team_id": player['team_id'],
            "team_name": player.get('team_name'),
            "position": player['position'],
            "height_inches": player['height'],
            "weight_lbs": player['weight'],
            "draft_year": player['draft_year'],
            "experience_years": player['season_exp']
        }
        
        # Build comprehensive text for semantic search
        text_parts = [f"{full_name}"]
        
        if player['position']:
            text_parts.append(f"plays {player['position']}")
        
        if player.get('team_name'):
            text_parts.append(f"for the {player['team_name']}")
        
        if player['height'] and player['weight']:
            text_parts.append(f"Height: {player['height']} inches, Weight: {player['weight']} lbs")
        
        if player['draft_year']:
            text_parts.append(f"Drafted in {player['draft_year']}")
        
        if player['season_exp']:
            text_parts.append(f"Experience: {player['season_exp']} seasons")
        
        content_text = ". ".join(text_parts) + "."
        content_json = self.json_serialize(structured)
        
        return {
            "id": f"player_{player_id}_profile",
            "entity_type": "player",
            "entity_id": str(player_id),
            "player_id": player_id,
            "team_id": player['team_id'],
            "game_id": None,
            "chunk_type": "profile",
            "content_json": structured,
            "content_text": content_text,
            "content_hash": self.hash_content(content_json),
            "season": None,
            "game_date": None
        }
    
    def build_game_document(self, game: Dict[str, Any]) -> Dict[str, Any]:
        """Create game summary document"""
        game_id = game['game_id']
        
        structured = {
            "entity_type": "game",
            "game_id": game_id,
            "season": game['season'],
            "date": str(game['game_date']),
            "home_team": {
                "id": game['home_team_id'],
                "name": game['home_team_name'],
                "points": game['home_points']
            },
            "away_team": {
                "id": game['away_team_id'],
                "name": game['away_team_name'],
                "points": game['away_points']
            },
            "winner_id": game['winning_team_id']
        }
        
        # Rich text description for semantic search
        winner_name = (game['home_team_name'] if game['winning_team_id'] == game['home_team_id'] 
                      else game['away_team_name'])
        
        text_parts = [
            f"Game on {game['game_date']}:",
            f"{game['away_team_name']} at {game['home_team_name']}.",
            f"Final score: {game['home_team_name']} {game['home_points']},",
            f"{game['away_team_name']} {game['away_points']}.",
            f"{winner_name} won the game.",
            f"Season: {game['season']}"
        ]
        
        content_text = " ".join(text_parts)
        content_json = self.json_serialize(structured)
        
        return {
            "id": f"game_{game_id}_summary",
            "entity_type": "game",
            "entity_id": str(game_id),
            "game_id": game_id,
            "team_id": None,  # Games relate to multiple teams
            "player_id": None,
            "chunk_type": "summary",
            "content_json": structured,
            "content_text": content_text,
            "content_hash": self.hash_content(content_json),
            "season": game['season'],
            "game_date": game['game_date']
        }
    
    def build_boxscore_document(self, boxscore: Dict[str, Any]) -> Dict[str, Any]:
        """Create player performance document for a game"""
        game_id = boxscore['game_id']
        player_id = boxscore['player_id']
        
        # Calculate derived stats
        total_rebounds = (boxscore['offensive_reb'] or 0) + (boxscore['defensive_reb'] or 0)
        minutes = round((boxscore['seconds'] or 0) / 60, 1)
        
        structured = {
            "entity_type": "boxscore",
            "game_id": game_id,
            "player_id": player_id,
            "team_id": boxscore['team_id'],
            "player_name": f"{boxscore['first_name']} {boxscore['last_name']}",
            "team_name": boxscore['team_name'],
            "date": str(boxscore['game_date']),
            "season": boxscore['season'],
            "starter": boxscore['starter'],
            "minutes": minutes,
            "points": boxscore['points'],
            "rebounds": total_rebounds,
            "assists": boxscore['assists'],
            "steals": boxscore['steals'],
            "blocks": boxscore['blocks'],
            "turnovers": boxscore['turnovers'],
            "fg2": {"made": boxscore['fg2_made'], "attempted": boxscore['fg2_attempted']},
            "fg3": {"made": boxscore['fg3_made'], "attempted": boxscore['fg3_attempted']},
            "ft": {"made": boxscore['ft_made'], "attempted": boxscore['ft_attempted']}
        }
        
        # Performance description for semantic search
        player_name = f"{boxscore['first_name']} {boxscore['last_name']}"
        starter_text = "Started" if boxscore['starter'] else "Off the bench"
        
        text_parts = [
            f"{player_name} ({boxscore['team_abbr']}) on {boxscore['game_date']}:",
            f"{starter_text}, played {minutes} minutes.",
            f"Stats: {boxscore['points']} points, {total_rebounds} rebounds,",
            f"{boxscore['assists']} assists, {boxscore['steals']} steals, {boxscore['blocks']} blocks."
        ]
        
        # Add shooting percentages if attempted
        if boxscore['fg2_attempted']:
            fg2_pct = round(100 * boxscore['fg2_made'] / boxscore['fg2_attempted'], 1)
            text_parts.append(f"2PT: {boxscore['fg2_made']}/{boxscore['fg2_attempted']} ({fg2_pct}%)")
        
        if boxscore['fg3_attempted']:
            fg3_pct = round(100 * boxscore['fg3_made'] / boxscore['fg3_attempted'], 1)
            text_parts.append(f"3PT: {boxscore['fg3_made']}/{boxscore['fg3_attempted']} ({fg3_pct}%)")
        
        if boxscore['ft_attempted']:
            ft_pct = round(100 * boxscore['ft_made'] / boxscore['ft_attempted'], 1)
            text_parts.append(f"FT: {boxscore['ft_made']}/{boxscore['ft_attempted']} ({ft_pct}%)")
        
        content_text = " ".join(text_parts)
        content_json = self.json_serialize(structured)
        
        return {
            "id": f"boxscore_{game_id}_{player_id}",
            "entity_type": "boxscore",
            "entity_id": f"{game_id}_{player_id}",
            "game_id": game_id,
            "team_id": boxscore['team_id'],
            "player_id": player_id,
            "chunk_type": "performance",
            "content_json": structured,
            "content_text": content_text,
            "content_hash": self.hash_content(content_json),
            "season": boxscore['season'],
            "game_date": boxscore['game_date']
        }