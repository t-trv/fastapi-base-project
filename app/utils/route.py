from fastapi.routing import APIRoute

def get_all_api_routes(routes, prefix=""):
    """
    Quét đệ quy cây app.routes của FastAPI để lấy tất cả các cặp (path, methods).
    """
    flat_routes = []
    for route in routes:
        if isinstance(route, APIRoute):
            flat_routes.append((prefix + route.path, route.methods))
        elif hasattr(route, "original_router") and hasattr(route, "include_context"): 
            r_prefix = prefix + (getattr(route.include_context, "prefix", "") or "")
            flat_routes.extend(get_all_api_routes(route.original_router.routes, r_prefix))
        elif hasattr(route, "routes"):
            r_prefix = prefix + getattr(route, "path", getattr(route, "prefix", ""))
            flat_routes.extend(get_all_api_routes(route.routes, r_prefix))
    return flat_routes

def get_full_path_for_route(routes, target_route, prefix=""):
    """
    Duyệt đệ quy cây app.routes của FastAPI để tìm đường dẫn đầy đủ của một route cụ thể.
    """
    for route in routes:
        if route == target_route:
            return prefix + getattr(route, "path", "")
        if hasattr(route, "original_router") and hasattr(route, "include_context"): 
            r_prefix = prefix + (getattr(route.include_context, "prefix", "") or "")
            found = get_full_path_for_route(route.original_router.routes, target_route, r_prefix)
            if found: return found
        elif hasattr(route, "routes"):
            r_prefix = prefix + getattr(route, "path", getattr(route, "prefix", ""))
            found = get_full_path_for_route(route.routes, target_route, r_prefix)
            if found: return found
    return None
