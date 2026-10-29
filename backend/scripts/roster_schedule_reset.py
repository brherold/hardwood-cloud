import os

def delete_file(file_path):
    """Delete a file if it exists."""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"Deleted cached file: {file_path}")
        else:
            print(f"File not found, nothing to delete: {file_path}")
    except Exception as e:
        print(f"Error deleting file {file_path}: {e}")
    

def delete_roster_cache(team_id, season_id):
    """Delete cached roster files for a specific team."""
    cache_folder = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "TeamRosterPage")
    )
    cache_filename = os.path.join(cache_folder, f"{team_id}-{season_id}.html")
    print("Deleting Roster:", team_id, season_id)
    delete_file(cache_filename)

def delete_schedule_cache(team_id, season_id):
    """Delete cached schedule files for a specific team."""
    cache_folder = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "TeamsHTML")
    )
    cache_filename = os.path.join(cache_folder, f"{team_id}-{season_id}.html")
    print("Deleting Team Schedule:", team_id, season_id)
    delete_file(cache_filename)