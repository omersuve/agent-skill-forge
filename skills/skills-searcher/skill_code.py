"""Skills searcher - searches skills folder for matching skills."""

def run_skill(inputs: dict) -> dict:
    """
    Search for skills matching the query.
    
    Args:
        inputs: Dictionary containing:
            - 'query': Search query string
            - 'search_type': 'name', 'description', or 'all' (default: 'all')
    
    Returns:
        Dictionary with matching skills and metadata.
    """
    query = inputs.get('query', '').lower()
    search_type = inputs.get('search_type', 'all').lower()
    
    if not query:
        return {'error': 'No query provided', 'matches': [], 'count': 0}
    
    # Handle "list all" queries
    list_all_keywords = ['list all', 'show all', 'all skills', 'list skills', 'show skills', 'available skills']
    if any(keyword in query for keyword in list_all_keywords):
        # Return all skills
        try:
            if 'skills_loader' not in globals():
                return {'error': 'skills_loader not available', 'matches': [], 'count': 0}
            
            skills_loader = globals()['skills_loader']
            all_skills = skills_loader.discover_skills()
            matches = []
            
            for skill_name in all_skills:
                metadata = skills_loader.load_metadata(skill_name)
                if metadata:
                    matches.append({
                        'name': metadata.get('name', skill_name),
                        'directory': skill_name,
                        'description': metadata.get('description', '')
                    })
            
            return {
                'matches': matches,
                'count': len(matches),
                'query': query,
                'search_type': 'list_all'
            }
        except Exception as e:
            return {
                'error': str(e),
                'matches': [],
                'count': 0
            }
    
    # Access skills_loader (injected by sandbox)
    try:
        # skills_loader is injected directly into the execution environment by sandbox
        # Access it from the outer scope (sandbox injects it as a global)
        if 'skills_loader' not in globals():
            return {'error': 'skills_loader not available', 'matches': [], 'count': 0}
        
        skills_loader = globals()['skills_loader']
        
        # Discover all skills
        all_skills = skills_loader.discover_skills()
        matches = []
        
        for skill_name in all_skills:
            metadata = skills_loader.load_metadata(skill_name)
            if not metadata:
                continue
            
            skill_name_lower = skill_name.lower()
            skill_display_name = metadata.get('name', '').lower()
            skill_description = metadata.get('description', '').lower()
            
            # Search based on type
            match = False
            if search_type == 'name':
                match = query in skill_name_lower or query in skill_display_name
            elif search_type == 'description':
                match = query in skill_description
            else:  # 'all'
                match = (query in skill_name_lower or 
                        query in skill_display_name or 
                        query in skill_description)
            
            if match:
                matches.append({
                    'name': metadata.get('name', skill_name),
                    'directory': skill_name,
                    'description': metadata.get('description', '')
                })
        
        return {
            'matches': matches,
            'count': len(matches),
            'query': query,
            'search_type': search_type
        }
        
    except Exception as e:
        return {
            'error': str(e),
            'matches': [],
            'count': 0
        }

